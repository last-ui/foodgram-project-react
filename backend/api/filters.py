from rest_framework import filters


class CustomSearchFilter(filters.SearchFilter):
    """
    Кастомный поиск ингредиентов, обеспечивающий двойную фильтрацию:
     - по вхождению в начало названия;
     - по вхождению в произвольном месте.
    """

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset
        start_queryset = queryset.filter(
            name__istartswith=search_terms[0])
        cont_queryset = queryset.filter(name__icontains=search_terms[0])
        cont_queryset = list(cont_queryset.exclude(pk__in=set(
            start_queryset.values_list('pk', flat=True))))
        queryset = list(start_queryset)
        queryset.extend(cont_queryset)
        return queryset
