from rest_framework import filters
from django.db.models import Value, IntegerField

# from models import Ingredient


class CustomSearchFilter(filters.SearchFilter):
    """
    Кастомный поиск ингредиентов, обеспечивающий двойную фильтрацию:
     - по вхождению в начало названия;
     - по вхождению в произвольном месте.
    """

    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')
        start_queryset = queryset.annotate(
            rank=Value(1, IntegerField())
        ).filter(name__istartswith=name)
        add_queryset = queryset.annotate(
            rank=Value(2, IntegerField())
        ).filter(name__icontains=name)
        add_queryset = add_queryset.exclude(
            pk__in=[query.pk for query in start_queryset]
        )
        queryset = start_queryset.union(add_queryset).order_by('rank')
        return queryset
