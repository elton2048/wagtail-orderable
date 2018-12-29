from django.db import models


class Orderable(models.Model):
    """
    Orderable class to add drag-and-drop ordering support to the ModelAdmin listing
    view. It is very similar to the Orderable class in
    `wagtail.core.models.Orderable` excepts it saves the sort_order initially
    if the object is new by checking whether the pk(Default Primary Key) field
    is None or not.

    Extends the model with this class for supporting the above feature.
    """
    sort_order = models.IntegerField(null=True, blank=True, editable=False)
    sort_order_field = 'sort_order'

    def save(self, *args, **kwargs):
        if self.pk == None:
            self.sort_order = self.__class__.objects.count() + 1
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['sort_order']
