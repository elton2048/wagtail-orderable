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
```
INSTALLED_APPS = [
    # ...
    'wagtailorderable',
    # ...
]
```

### Usage

To apply the orderable feature, extends your model with `Orderable`.
```
from django.db import models

from wagtailorderable.models import Orderable


class YourModel(models.Model, Orderable):
    title = models.CharField(max_length=200)
```

Of course you can apply it to `Page` model from Wagtail.
```
from wagtail.core import fields
from wagtail.core.models import Page

from wagtailorderable.models import Orderable


class YourModel(Page, Orderable):
    description = fields.RichTextField(blank=True)
```

Note that `Orderable` also exists in `wagtail.core.models`, **DO NOT** use that as the mixins requires model from the same package.

To apply the feature support in admin panel. In `wagtail_hooks.py`:
```
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)

from wagtailorderable.modeladmin.mixins import OrderableMixin

from .models import YourModel


class YourModelAdmin(ModelAdmin, OrderableMixin):
    model = YourModel
    
    ordering = ['sort_order']
    
modeladmin_register(YourModelAdmin)
```

Last coolect corresponding static file by
```
python manage.py collectstatic
```
in your project

### Acknowledgement
Most of the contribution comes from this [commit](https://github.com/rkhleics/wagtail/commit/08df07689af1096ce4a6fa96325dbfb7fab9240d) which attempts to integrate the solution in Wagtail project. Though it is not being used in Wagtail now it provides great skeleton for the feature which helps me created this mixin.

Thanks the contribution from [Andy Babic](https://github.com/ababic).

Contirbution for this project are all welcome :)