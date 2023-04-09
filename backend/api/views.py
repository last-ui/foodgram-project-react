from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeSerializer, RecipeSerializerCreate,
                             RecipeShortSerializer, ShoppingCartSerializer,
                             TagSerializer, UserSubscribeSerializer)
from api.utils import download_pdf_file
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscribe

User = get_user_model()


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Метод изменения класса сериализатора при разных методах."""
        if self.request.method in ('POST', 'PATCH'):
            return RecipeSerializerCreate
        return RecipeSerializer

    @action(detail=True,
            permission_classes=(IsAuthenticated,),
            methods=('POST', 'DELETE',))
    def favorite(self, request, pk=None):
        """Добавление/удаление рецептов в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        current_user = self.request.user
        serializer = FavoriteSerializer(
            data={'recipe': pk, 'user': current_user.id},
            context={'method': self.request.method}
        )
        serializer.is_valid(raise_exception=True)
        if self.request.method == 'POST':
            Favorite.objects.create(recipe=recipe, user=self.request.user)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            favorite = recipe.favorite.filter(user=self.request.user)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            permission_classes=(IsAuthenticated,),
            methods=('POST', 'DELETE',))
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецептов в корзину покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        current_user = self.request.user
        serializer = ShoppingCartSerializer(
            data={'recipe': pk, 'user': current_user.id},
            context={'method': self.request.method}
        )
        serializer.is_valid(raise_exception=True)
        if self.request.method == 'POST':
            ShoppingCart.objects.create(recipe=recipe, user=self.request.user)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            shopping_cart = recipe.shopping_cart.filter(user=self.request.user)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=(IsAuthenticated,),
            methods=('GET',))
    def download_shopping_cart(self, request):
        """Скачивание списка покупок для рецептов добавленных в корзину."""
        serializer = ShoppingCartSerializer(
            data={'user': self.request.user.id},
            context={'method': self.request.method}
        )
        serializer.is_valid()
        ingredients = Ingredient.objects.filter(
            recipe__shopping_cart__user=self.request.user
        )
        annotated_results = ingredients.annotate(
            sum_ingredients=Sum('ingredient_in_recipe__amount')
        )
        return download_pdf_file(annotated_results)


class MyUsersViewSet(UserViewSet):
    """Вьюсет подписок пользователей."""
    pagination_class = LimitPageNumberPagination

    @action(detail=True,
            permission_classes=(IsAuthenticated,),
            methods=('POST', 'DELETE',))
    def subscribe(self, request, id=None):
        """Добавление/удаление авторов в подписки."""
        author = get_object_or_404(User, pk=id)
        current_user = request.user
        serializer = FavoriteSerializer(
            data={'author': author.pk, 'user': current_user.id},
            context={'method': self.request.method}
        )
        serializer.is_valid()
        if request.method == 'POST':
            Subscribe.objects.create(user=current_user,
                                     author=author)
            serializer = UserSubscribeSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        subscribe = current_user.subscriber.filter(author=author)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=(IsAuthenticated,),
            methods=('GET',))
    def subscriptions(self, request):
        """
        Получение списка рецептов авторов на которых подписан
        пользователь.
        """
        queryset = User.objects.filter(subscribed__user=request.user)
        serializer = UserSubscribeSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
