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

To apply the orderable feature, extend your model with `Orderable`.
```python
from django.db import models

from wagtailorderable.models import Orderable


class YourModel(Orderable):
    title = models.CharField(max_length=200)
```

Of course you can apply it to Wagtail's `Page` model.
```python
from wagtail.core import fields
from wagtail.core.models import Page

from wagtailorderable.models import Orderable


class YourModel(Page, Orderable):
    description = fields.RichTextField(blank=True)
```

Note that `Orderable` also exists in `wagtail.core.models`, **DO NOT** use that as the mixins require the model from the same package.

To apply the feature support in admin panel. In `wagtail_hooks.py`:
```python
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)

from wagtailorderable.modeladmin.mixins import OrderableMixin

from .models import YourModel


class YourModelAdmin(OrderableMixin, ModelAdmin):
    model = YourModel

    ordering = ['sort_order']

modeladmin_register(YourModelAdmin)
```

Finally, collect the corresponding static file by running
```python
python manage.py collectstatic
```
in your project.

### Change Log
## [Unreleased]
- Add support for Wagtail 3.0 and drop support for all Wagtail versions
   before 2.15
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
