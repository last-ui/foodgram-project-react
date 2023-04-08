from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe
from users.serializers import UserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('id', 'name', 'color', 'slug',)


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецептов."""
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(default=serializers.CurrentUserDefault())
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        """Метод получения ингредиентов в рецепте и их количество."""
        return IngredientsInRecipeSerializer(
            obj.ingredient_in_recipe.all(),
            many=True
        ).data

    def get_is_favorited(self, obj):
        """Метод определения избранных рецептов текущего пользователя."""
        current_user = self.context['request'].user
        return (
            not current_user.is_anonymous
            and obj.favorite.filter(user=current_user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Метод определения рецептов добавленных в корзину текущего
        пользователя.
        """
        current_user = self.context['request'].user
        return (
            not current_user.is_anonymous
            and obj.shopping_cart.filter(user=current_user).exists()
        )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'author', 'text', 'cooking_time',
            'ingredients', 'tags', 'is_favorited', 'is_in_shopping_cart',
        )
        read_only_fields = (
            'id', 'author', 'tags', 'is_favorited', 'is_in_shopping_cart'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author',),
                message='Рецепт с таким названием вами уже создан!'
            )
        ]


class RecipeShortSerializer(RecipeSerializer):
    """Укороченный сериализатор получения рецептов."""

    class Meta(RecipeSerializer.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор подписок пользователя."""
    recipes = RecipeShortSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    def get_queryset(self, obj):
        """
        Получение выборки рецептов авторов на которых подписан текущий
        пользователь.
        При наличии параметра recipes_limit, возвращается срезанный queryset.
        """
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit:
            return obj.recipes.all()[:int(limit)]
        return obj.recipes.all()

    def get_recipes_count(self, obj):
        """
        Получение общего количества рецептов авторов на которых подписан
        текущий пользователь.
        """
        return obj.recipes.all().count()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializerCreate(RecipeSerializer):
    """Сериализатор создания и редактирования рецепта."""
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    def ingredient_in_recipe_create(self, recipe, ingredients):
        """Метод добавления ингредиентов рецепта в базу данных."""
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=ingredient.get('ingredient'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        """Метод создания рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.ingredient_in_recipe_create(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        for key, value in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.ingredient_in_recipe.all().delete()
        self.ingredient_in_recipe_create(instance, ingredients)
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Метод замены сериализатора выходных данных."""
        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientsInRecipeSerializer(
            instance.ingredient_in_recipe.all(),
            many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags, many=True
        ).data
        return representation

    def validate(self, data):
        """Валидация входных данных ингредиентов и тэгов."""
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'обязательное поле'}
            )
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'обязательное поле'}
            )
        return data

    class Meta(RecipeSerializer.Meta):
        fields = (
            'id', 'name', 'image', 'author', 'text', 'cooking_time',
            'ingredients', 'tags', 'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = (
            'id', 'author', 'is_favorited', 'is_in_shopping_cart'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author',),
                message='Рецепт с таким названием уже создан!'
            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def validate(self, attrs):
        recipe = attrs.get('recipe')
        method = self.context.get('method')
        current_user = attrs.get('user')
        if method == 'POST':
            if recipe.favorite.filter(user=current_user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепт уже в избранном!'}
                )
        elif method == 'DELETE':
            if not recipe.favorite.filter(user=current_user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепта нет в избранном!'}
                )
        return attrs


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

    def validate(self, attrs):
        recipe = attrs.get('recipe')
        method = self.context.get('method')
        current_user = attrs.get('user')
        if method == 'POST':
            if recipe.shopping_cart.filter(user=current_user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепт уже в корзине!'}
                )
        elif method == 'DELETE':
            if not recipe.shopping_cart.filter(user=current_user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепта нет в корзине!'}
                )
        elif method == 'GET':
            if not current_user.shopping_cart.exists():
                raise serializers.ValidationError(
                    {'errors': 'Корзина пуста!'}
                )
        return attrs


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('author', 'user')

    def validate(self, attrs):
        author = attrs.get('author')
        method = self.context.get('method')
        current_user = attrs.get('user')
        if method == 'POST':
            if author == current_user:
                raise serializers.ValidationError(
                    {'errors': 'Подписка на самого себя не возможна!'}
                )
            if current_user.subscriber.filter(author=author).exists():
                raise serializers.ValidationError(
                    {'errors': 'Повторная подписка!'}
                )
        elif method == 'DELETE':
            if author == current_user:
                raise serializers.ValidationError(
                    {'errors': 'Отписаться от самого себя невозможно!'}
                )
            if not current_user.subscriber.filter(author=author).exists():
                raise serializers.ValidationError(
                    {'errors': 'Подписка на автора отсутствует!'}
                )
        return attrs
