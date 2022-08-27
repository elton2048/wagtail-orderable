from django.urls import re_path
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured, PermissionDenied
from django.db import connections, transaction
from django.db.models import F, Count
from django.db.models.expressions import Case, Value, When
from django.db.models.functions import Cast
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ..signals import pre_reorder, post_reorder


class OrderableMixinMetaClass(type):
    """
    index_order method needs to be completed with an `admin_order_field` but as sort_order_field
    is not yet known in the class, we need this meta class to get it from other final class args
    """
    def __new__(cls, name, bases, attrs):
        model = attrs.get('model', None)
        sort_order_field = attrs.get('sort_order_field', None)
        if model and not sort_order_field:
            sort_order_field = getattr(model, 'sort_order_field', None)
        if sort_order_field:
            # unfortunately, wagtail IndexView._get_default_ordering is currently using
            # `model_admin.ordering` instead of `model_admin.get_ordering()`
            # So we need to automagically set it here
            if 'ordering' not in attrs:
                attrs['ordering'] = (sort_order_field, )
            elif sort_order_field not in attrs['ordering']:
                attrs['ordering'] = (sort_order_field, ) + tuple(attrs['ordering'])

            # set the "sorting" column
            if 'index_order' not in attrs:
                def index_order(self, obj):
                    """Content for the `index_order` column"""
                    return mark_safe((
                        '<div class="handle icon icon-grip text-replace ui-sortable-handle">'
                        '%s</div>'
                    ) % _('Drag'))
                index_order.admin_order_field = sort_order_field
                index_order.short_description = _('Order')
                attrs['index_order'] = index_order
        return type.__new__(cls, name, bases, attrs)


class OrderableMixin(object, metaclass=OrderableMixinMetaClass):
    sort_order_field = None

    """
    Mixin class to add drag-and-drop ordering support to the ModelAdmin listing
    view when the model extends the `wagtailorderable.models.Orderable`
    abstract model class.
    """

    def __init__(self, parent=None):
        super(OrderableMixin, self).__init__(parent)
        """
        Don't allow initialisation unless self.model subclasses
        `wagtail.models.Orderable` or sort_order_field is set
        """
        if not self.sort_order_field and hasattr(self.model, 'sort_order_field'):
            self.sort_order_field = getattr(self.model, 'sort_order_field', None)

        if not self.sort_order_field:
            raise ImproperlyConfigured(
                u"You are using OrderableMixin for your '%(cls)s' class, but the "
                "django model specified is not a sub-class of "
                "'wagtail.models.Orderable and you did not set "
                "'%(cls)s.sort_order_field'." % {'cls': self.__class__.__name__}
            )
        try:
            self.model._meta.get_field(self.sort_order_field)
        except FieldDoesNotExist:
            raise ImproperlyConfigured(
                u"You are using OrderableMixin for your '%s' class, but the "
                "'sort_order_field' is set to '%s' which does not exists "
                "into your model." %
                (self.__class__.__name__, self.sort_order_field))

    def get_ordering(self, request):
        """
        Returns a sequence defining the default ordering for results in the
        list view.
        """
        if not self.ordering:
            return (self.sort_order_field, )
        elif self.sort_order_field not in self.ordering:
            return (self.sort_order_field, ) + tuple(self.ordering)
        return self.ordering

    def get_list_display(self, request):
        """Add `index_order` as the first column to results"""
        list_display = list(super().get_list_display(request))
        if self.sort_order_field in list_display:
            # Used JS need one and only one order field displayed in the list
            list_display.remove(self.sort_order_field)
        return ('index_order', *list_display)

    def get_list_display_add_buttons(self, request):
        """
        If `list_display_add_buttons` isn't set, ensure the buttons are not
        added to the `index_order` column.
        """
        col_field_name = super(
            OrderableMixin, self).get_list_display_add_buttons(request)
        if col_field_name == 'index_order':
            list_display = self.get_list_display(request)
            return list_display[1]
        return col_field_name

    def get_extra_attrs_for_field_col(self, obj, field_name):
        """
        Add data attributes to the `index_order` column that can be picked
        up via JS. The width attribute helps the column remain at a fixed size
        while dragging and the title is used for generating a success message
        on completion reorder completion.
        """
        attrs = super(OrderableMixin, self).get_extra_attrs_for_field_col(
            obj, field_name)
        if field_name == 'index_order':
            attrs.update({
                'data-title': obj.__str__(),
                'width': 20,
            })
        return attrs

    def get_extra_class_names_for_field_col(self, obj, field_name):
        """
        Add the `visible-on-drag` class to certain columns
        """
        classnames = super(OrderableMixin, self).get_extra_class_names_for_field_col(
            obj, field_name
        )
        if field_name in ('index_order', self.list_display[0], 'admin_thumb',
                          self.list_display_add_buttons or ''):
            classnames.append('visible-on-drag')
        return classnames

    def _get_position(self, pk):
        try:
            obj = self.model.objects.get(pk=pk)
            return getattr(obj, self.sort_order_field), obj
        except self.model.DoesNotExist:
            return None, None

    @transaction.atomic
    def reorder_view(self, request, instance_pk):
        """
        Very simple view functionality for updating the `sort_order` values
        for objects after a row has been dragged to a new position.
        """
        self.fix_duplicate_positions(request)

        obj_to_move = get_object_or_404(self.model, pk=instance_pk)
        if not self.permission_helper.user_can_edit_obj(request.user, obj_to_move):
            raise PermissionDenied

        # determine the start position
        old_position = getattr(obj_to_move, self.sort_order_field) or 0

        # determine the destination position
        after_position, after = self._get_position(request.GET.get('after'))
        before_position, before = self._get_position(request.GET.get('before'))
        if after:
            position = after_position or 0
            response = _('"%s" moved after "%s"') % (obj_to_move, after)
        elif before:
            position = before_position or 0
            response = _('"%s" moved before "%s"') % (obj_to_move, before)
        else:
            return HttpResponseBadRequest(_('"%s" not moved') % obj_to_move)

        qs = self.get_filtered_queryset(request)
        signal_kwargs = {'sender': self.__class__, 'queryset': qs}
        # move the object from old_position to new_position
        if position < old_position:
            if position == after_position:
                position += 1
            qs = qs.filter(**{'%s__lt' % self.sort_order_field: old_position,
                              '%s__gte' % self.sort_order_field: position})
            update_value = F(self.sort_order_field) + 1
            signal_kwargs.update({'from_order': position, 'to_position': old_position + 1})
        elif position > old_position:
            if position == before_position:
                position -= 1
            qs = qs.filter(**{'%s__gt' % self.sort_order_field: old_position,
                              '%s__lte' % self.sort_order_field: position})
            update_value = F(self.sort_order_field) - 1
            signal_kwargs.update({'from_order': old_position - 1, 'to_position': position})

        # let's signal we will reorder some instances.
        pre_reorder.send(**signal_kwargs)
        # reorder all previous|next
        qs.update(**{self.sort_order_field: update_value})
        # reorder current one
        self.model.objects.filter(pk=obj_to_move.pk)\
                          .update(**{self.sort_order_field: position})
        # let's signal we just reorder some instances.
        post_reorder.send(**signal_kwargs)
        return HttpResponse(response)

    def get_filtered_queryset(self, request):
        parent_field = getattr(self, 'parent_field', None)
        if not parent_field or parent_field not in request.GET:
            return self.get_queryset(request)
        return self.get_queryset(request).filter(**{parent_field: request.GET.get(parent_field)})

    @transaction.atomic
    def fix_duplicate_positions(self, request):
        """
        Low level function which updates each element to have sequential sort_order values
        if the database contains any duplicate values (gaps are ok).
        """
        qs = self.get_filtered_queryset(request)
        first_duplicate = qs.values(self.sort_order_field)\
                            .annotate(index_order_count=Count(self.sort_order_field))\
                            .filter(index_order_count__gt=1)\
                            .order_by(self.sort_order_field).first()
        if not first_duplicate:
            return

        # let's retrieve all next the first duplicate found
        lookups = {'%s__gte' % self.sort_order_field: first_duplicate[self.sort_order_field]}
        to_reorder = qs.filter(**lookups).order_by(self.sort_order_field)\
                       .values_list('pk', self.sort_order_field)[1:]
                       # first one has the good order value, so we don't get it

        # let's prepare our custom bulk_update to reorder the wring ordered ones
        # (we don't use django's native bulk_update which require real model instances which is
        # overkill in our case). When django's bulk_update will be able to accept iterable of dicts
        # we won't need this custom bulk_update anymore.
        field = self.model._meta.get_field(self.sort_order_field)
        when_statements = []
        pks = []
        bulk_update_qs = self.get_filtered_queryset(request)
        new_order = first_duplicate['index_order_count']
        for pk, current_order in to_reorder:
            new_order += 1
            if current_order > new_order:
                # we are ok with gaps, this one does not need to be updated
                new_order = current_order + 1
                continue
            if current_order == new_order:
                # neither this one
                continue
            pks.append(pk)
            when_statements.append(When(pk=pk, then=Value(new_order, output_field=field)))
        case_statement = Case(*when_statements, output_field=field)
        if connections[bulk_update_qs.db].features.requires_casted_case_in_updates:
            case_statement = Cast(case_statement, output_field=field)
        # let's signal we will reorder some instances.
        pre_reorder.send(
            sender=self.__class__,
            from_order=first_duplicate['index_order_count'] + 1,
            to_order=new_order,
            queryset=bulk_update_qs,
        )
        bulk_update_qs.filter(pk__in=pks).update(**{self.sort_order_field: case_statement})
        # let's signal we just reorder some instances.
        post_reorder.send(
            sender=self.__class__,
            from_order=first_duplicate['index_order_count'] + 1,
            to_order=new_order,
            queryset=bulk_update_qs,
        )

    def get_index_view_extra_css(self):
        css = super(OrderableMixin, self).get_index_view_extra_css()
        css.append('wagtailorderable/modeladmin/css/orderablemixin.css')
        return css

    def get_index_view_extra_js(self):
        js = super(OrderableMixin, self).get_index_view_extra_js()
        js.append('wagtailorderable/modeladmin/js/orderablemixin.js')
        return js

    def get_admin_urls_for_registration(self):
        urls = super(OrderableMixin, self).get_admin_urls_for_registration()
        urls += (
            re_path(
                self.url_helper.get_action_url_pattern('reorder'),
                view=self.reorder_view,
                name=self.url_helper.get_action_url_name('reorder')
            ),
        )
        return urls
