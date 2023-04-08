from django.contrib.auth import get_user_model
from django.db.models import IntegerField, Value
from django_filters import rest_framework as django_filters
from rest_framework import filters

from recipes.models import Recipe, Tag

User = get_user_model()

STATUS_CHOICES = (
    (0, 'False'),
    (1, 'True'),
)


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
        return start_queryset.union(add_queryset).order_by('rank')


class RecipeFilter(django_filters.FilterSet):
    """Фильтерсет рецептов."""
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = django_filters.BooleanFilter()
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=STATUS_CHOICES, method='get_queryset'
    )

    def get_queryset(self, queryset, name, value):
        """Метод получения queryset при фильтрации по параметрам запроса."""
        if name == 'is_favorited' and value == '1':
            return queryset.filter(favorite__user=self.request.user)
        if name == 'is_in_shopping_cart' and value == '1':
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)
