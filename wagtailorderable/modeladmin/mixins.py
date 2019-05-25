from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import F
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wagtailorderable.models import Orderable

class OrderableMixin(object):
    """
    Mixin class to add drag-and-drop ordering support to the ModelAdmin listing
    view when the model extends the `wagtailorderable.models.Orderable`
    abstract model class.
    """
    def __init__(self, parent=None):
        super(OrderableMixin, self).__init__(parent)
        """
        Don't allow initialisation unless self.model subclasses
        `wagtail.wagtailcore.models.Orderable`
        """
        if not issubclass(self.model, Orderable):
            raise ImproperlyConfigured(
                u"You are using OrderableMixin for your '%s' class, but the "
                "django model specified is not a sub-class of "
                "'wagtail.wagtailcore.models.Orderable." %
                self.__class__.__name__,)

    def get_list_display(self, request):
        """Add `index_order` as the first column to results"""
        list_display = super(OrderableMixin, self).get_list_display(request)
        order_col_prepend = ['index_order']
        return order_col_prepend + list_display

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


    def get_extra_class_names_for_field_col(self, field_name, obj):
        """
        Add the `visible-on-drag` class to certain columns
        """
        classnames = super(OrderableMixin, self).get_extra_class_names_for_field_col(
            field_name, obj)
        if field_name in ('index_order', self.list_display[0], 'admin_thumb',
                          self.list_display_add_buttons or ''):
            classnames.append('visible-on-drag')
        return classnames

    def index_order(self, obj):
        """Content for the `index_order` column"""
        return mark_safe(
            '<div class="handle icon icon-grip text-replace ui-sortable-handle">Drag</div>'
        )
    index_order.admin_order_field = 'sort_order'
    index_order.short_description = _('Order')

    def reorder_view(self, request, instance_pk):
        """
        Very simple view functionality for updating the `sort_order` values
        for objects after a row has been dragged to a new position.
        """
        obj_to_move = get_object_or_404(self.model, pk=instance_pk)
        if not self.permission_helper.user_can_edit_obj(request.user, obj_to_move):
            raise PermissionDenied
        position = request.GET.get('position', self.model.objects.count())

        # if sort_order doens't exist on existing entry
        if obj_to_move.sort_order:
            old_position = obj_to_move.sort_order
        else:
            old_position = -1
        
        if int(position) < old_position:
            self.model.objects.filter(
                sort_order__lt=old_position,
                sort_order__gte=int(position)
            ).update(sort_order=F('sort_order') + 1)
        elif int(position) > old_position:
            self.model.objects.filter(
                sort_order__gt=old_position,
                sort_order__lte=int(position)
            ).update(sort_order=F('sort_order') - 1)
        obj_to_move.sort_order = position
        obj_to_move.save()
        return HttpResponse('Reordering was successful')

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
            url(
                self.url_helper.get_action_url_pattern('reorder'),
                view=self.reorder_view,
                name=self.url_helper.get_action_url_name('reorder')
            ),
        )
        return urls
