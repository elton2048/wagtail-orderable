# Wagtail Orderable

Simple orderable mixin to add drag-and-drop ordering support to the `ModelAdmin` listing view.

It attempts to provide the [feature request](https://github.com/wagtail/wagtail/issues/2941) in Wagtail project without modifying the project code as it seems not a high priority item for the project.

### Installation

Install the package
```
pip install wagtail-orderable
```

### Settings
In your settings file, add `wagtailorderable` to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'wagtailorderable',
    # ...
]
```

### Usage

#### Extend with `Orderable` (optional)

To apply the orderable feature, you can extend your model with `Orderable` which will add
a `sort_order` `IntegerField` to your model but if you already have a field to store
an index value, **this is not required**.

```python
from django.db import models

from wagtailorderable.models import Orderable


class YourModel(Orderable):
    title = models.CharField(max_length=200)
```

Of course you can apply it to Wagtail's `Page` model.
```python
from wagtail import fields
from wagtail.models import Page

from wagtailorderable.models import Orderable


class YourModel(Page, Orderable):
    description = fields.RichTextField(blank=True)
```


Or just use your model with your personal ordering field.

```python
from django.db import models


class YourOtherModel(models.Model):
    title = models.CharField(max_length=200)
    my_custom_order_field = models.IntegerField(null=False, blank=True, default=0, editable=False)
```

Note that `Orderable` also exists in `wagtail.models`, **DO NOT** use that as the mixins require the model from the same package.

To apply the feature support in admin panel. In `wagtail_hooks.py`:
```python
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)

from wagtailorderable.modeladmin.mixins import OrderableMixin

from .models import YourModel, YourOtherModel


class YourModelAdmin(OrderableMixin, ModelAdmin):
    model = YourModel


class YourOtherModelAdmin(OrderableMixin, ModelAdmin):
    model = YourOtherModel
    sort_order_field = 'my_custom_order_field'

modeladmin_register(YourModelAdmin)
modeladmin_register(YourOtherModelAdmin)
```

Note that `sort_order_field` is optional if you extend your model with `Orderable`
or if your Model has a `sort_order_field` attribute.

Finally, collect the corresponding static file by running
```shell
python manage.py collectstatic
```
in your project.

### Change Log

1.1.0
---
- Extending `Orderable` is no more mandatory if you want to use your own order field (#27)
- Add `Orderable.get_sort_order_max()` to get the max "order" when instance is being created (#27)
- Fix keeping current filters when sorting was reset (#27)
- Fix class names (`get_extra_class_names_for_field_col` parameters were inverted) (#27)
- Fix CSS which had SCSS syntax (#27)

1.0.4
---
- Provide Github Actions script to build and publish package in PyPI
- Add support for Wagtail 3.0 and drop support for all Wagtail versions
   before 2.15 (#32)
- Use `pk` instead of `id` for duplicate positions (#31)

1.0.3
---
- Fix `TypeError` when creating the first Orderable object (#21)

1.0.2
---
- Fix `sort_order` duplication for items
- Fix wrong `return` syntax

1.0.1
---
- `get_list_display` handles any iterable
- Support for filters in ModelAdmin
- Style updated

### Acknowledgement
Most of the contribution comes from this [commit](https://github.com/rkhleics/wagtail/commit/08df07689af1096ce4a6fa96325dbfb7fab9240d) which attempts to integrate the solution in Wagtail project. Though it is not being used in Wagtail now it provides great skeleton for the feature which helps me created this mixin.

Thanks the contribution from [Andy Babic](https://github.com/ababic).

Contirbution for this project are all welcome :)
