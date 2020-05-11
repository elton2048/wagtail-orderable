from django.db import models
from django.db.models import Max


class Orderable(models.Model):
    """
    Orderable class to add drag-and-drop ordering support to the ModelAdmin listing
    view. It is very similar to the Orderable class in
    `wagtail.models.Orderable` excepts it saves the sort_order initially
    if the object is new by checking whether the pk(Default Primary Key) field
    is None or not.

    Extends the model with this class for supporting the above feature.
    """
    sort_order = models.IntegerField(null=True, blank=True, editable=False)
    sort_order_field = 'sort_order'

    def save(self, *args, **kwargs):
        if self.pk is None:
            setattr(self, self.sort_order_field, self.get_sort_order_max() + 1)
        super().save(*args, **kwargs)

    def get_sort_order_max(self):
        """
        Method used to get the max sort_order when a new instance is created.
        If you order depends on a FK (eg. order of books for a specific author),
        you can override this method to filter on the FK.
        ```
        def get_sort_order_max(self):
            qs = self.__class__.objects.filter(author=self.author)
            return qs.aggregate(Max(self.sort_order_field))['sort_order__max'] or 0
        ```
        """
        qs = self.__class__.objects.all()
        return qs.aggregate(Max(self.sort_order_field))['%s__max' % self.sort_order_field] or 0

    class Meta:
        abstract = True
        ordering = ['sort_order']
