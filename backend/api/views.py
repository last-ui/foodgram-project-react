from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from api.serializers import (IngredientSerializer, RecipeSerializerCreate,
                             RecipeSerializer, TagSerializer)
from recipes.models import Ingredient, Recipe, Tag


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """Метод изменения класса сериализера при разных методах."""
        if (
            self.action == 'create'
            or self.action == 'update'
            or self.action == 'partial_update'
        ):
            return RecipeSerializerCreate
        return RecipeSerializer

