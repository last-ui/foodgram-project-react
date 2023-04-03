from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Стандартный пагинатор с пользовательским разбиением страниц."""
    page_size_query_param = 'limit'
