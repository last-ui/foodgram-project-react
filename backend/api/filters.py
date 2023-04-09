from django.contrib.auth import get_user_model
from django_filters import rest_framework as django_filters

from recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(django_filters.FilterSet):
    """Фильтерсет рецептов."""
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = django_filters.BooleanFilter(method='get_queryset')
    is_in_shopping_cart = django_filters.BooleanFilter(method='get_queryset')

    def get_queryset(self, queryset, name, value):
        """Метод получения queryset при фильтрации по параметрам запроса."""
        if name == 'is_favorited':
            return queryset.filter(favorite__user=self.request.user)
        if name == 'is_in_shopping_cart':
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
