from django.dispatch import Signal

# queryset is the whole "base queryset": it does not filter only on those updated
# but filters on a parent key for example. eg. Book -> Chapter: Chapters need to be ordered
# by book, and their ordering is important (can not be shared between all books)
# in that case, you should use a "child model admin" which will allow you to display (and reorder)
# only chapters for a specific books. The queryset sends to signals is filtered with the
# "current book".

# provides args: from_order, to_order, queryset
pre_reorder = Signal()

# provides args: from_order, to_order, queryset
post_reorder = Signal()
