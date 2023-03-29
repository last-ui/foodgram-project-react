from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             RecipeSerializerCreate, RecipeShortSerializer,
                             TagSerializer, UserSubscribeSerializer)
from api.utils import download_pdf_file
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscribe, User


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
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

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Метод изменения класса сериализатора при разных методах."""
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeSerializerCreate
        return RecipeSerializer

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['POST', 'DELETE'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            if recipe.favorite.filter(user=self.request.user).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(recipe=recipe, user=self.request.user)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                recipe=recipe, user=self.request.user
            )
            if not favorite:
                return Response(
                    {'errors': 'Рецепта нет в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            if recipe.shopping_cart.filter(user=self.request.user).exists():
                return Response(
                    {'errors': 'Рецепт уже в корзине!'},
                    status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(recipe=recipe, user=self.request.user)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(
                recipe=recipe, user=self.request.user
            )
            if not shopping_cart:
                return Response(
                    {'errors': 'Рецепта нет в корзине!'},
                    status=status.HTTP_400_BAD_REQUEST)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods=['GET'])
    def download_shopping_cart(self, request):
        if not self.request.user.shopping_cart.exists():
            return Response(
                {'errors': 'Корзина пуста!'},
                status=status.HTTP_400_BAD_REQUEST)
        ingredients = Ingredient.objects.filter(
            recipe__shopping_cart__user=self.request.user
        )
        annotated_results = ingredients.annotate(
            sum_ingredients=Sum('ingredient_in_recipe__amount')
        )
        return download_pdf_file(annotated_results)


class MyUsersViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    @action(detail=True,
            permission_classes=[IsAuthenticated],
            methods=['POST', 'DELETE'])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        current_user = request.user
        if request.method == 'POST':
            if author == current_user:
                return Response(
                    {'errors': 'Подписка на самого себя не возможна!'},
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscribe.objects.filter(
                    user=current_user, author=author
            ).exists():
                return Response({'errors': 'Повторная подписка!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Subscribe.objects.create(user=current_user,
                                     author=author)
            serializer = UserSubscribeSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if author == current_user:
                return Response(
                    {'errors': 'Отписаться от самого себя не возможно!'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscribe = Subscribe.objects.filter(
                user=current_user, author=author
            )
            if subscribe:
                subscribe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Подписка на автора отсутствует!'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods=['GET'])
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribed__user=request.user)
        serializer = UserSubscribeSerializer(
            self.paginate_queryset(queryset),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

