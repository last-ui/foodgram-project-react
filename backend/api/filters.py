from rest_framework import filters


class CustomSearchFilter(filters.SearchFilter):
    """
    Кастомный поиск ингредиентов, обеспечивающий двойную фильтрацию:
     - по вхождению в начало названия;
     - по вхождению в произвольном месте.
    """

    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')
        start_queryset = list(queryset.filter(name__istartswith=name))
        add_queryset = queryset.filter(name__icontains=name)
        start_queryset.extend(
            [item for item in add_queryset if item not in start_queryset]
        )
        return start_queryset
