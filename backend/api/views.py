from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import CustomSearchFilter
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
    filter_backends = (CustomSearchFilter,)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get_queryset(self):
        """Метод получения queryset при фильтрации по параметрам запроса."""
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author_id=author)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart and is_in_shopping_cart == '1':
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        is_favorited = self.request.query_params.get(
            'is_favorited'
        )
        if is_favorited and is_favorited == '1':
            queryset = queryset.filter(favorite__user=self.request.user)
        return queryset

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
        serializer.is_valid()
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
        serializer.is_valid()
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
        if request.method == 'DELETE':
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

