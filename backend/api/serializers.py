import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        """Преобразование/декодирование BASE64-строки"""
        if isinstance(data, str) and data.startswith('data:image'):
            image_format, image_str = data.split(';base64,')
            ext = image_format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_str),
                name=f'temp.{ext}'
            )
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецептов."""
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True,
                            default=serializers.CurrentUserDefault())
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def ingredient_in_recipe_create(self, recipe, ingredients):
        data = []
        for ingredient in ingredients:
            data.append(
                IngredientInRecipe(
                    ingredient=ingredient.get('id'),
                    recipe=recipe,
                    amount=ingredient.get('amount'),
                )
            )
        IngredientInRecipe.objects.bulk_create(data)

    def get_ingredients(self, obj):
        """Метод получения ингредиентов в рецепте и их количество."""
        return IngredientsInRecipeSerializer(
            obj.ingredient_in_recipe.all(),
            many=True
        ).data

    def get_is_favorited(self, obj):
        """Метод определения избранных рецептов текущего пользователя."""
        user = self.context['request'].user
        return (not user.is_anonymous and
                obj.favorite.filter(user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        """
        Метод определения рецептов добавленных в корзину текущего
        пользователя.
        """
        user = self.context['request'].user
        return (not user.is_anonymous and obj.shopping_cart.filter(
            user=user).exists())

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'author', 'text', 'cooking_time',
            'ingredients', 'tags', 'is_favorited', 'is_in_shopping_cart',
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


class RecipeShortSerializer(RecipeSerializer):
    """Укороченный сериализатор получения рецептов."""

    class Meta(RecipeSerializer.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор подписок пользователя."""
    recipes = RecipeShortSerializer(many=True, read_only=True)
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
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializerCreate(RecipeSerializer):
    """Сериализатор создания и редактирования рецепта."""
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        source='IngredientInRecipe',
    )
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True,
                            default=serializers.CurrentUserDefault())

    def ingredient_in_recipe_create(self, recipe, ingredients):
        """Метод добавления ингредиентов рецепта в базу данных."""
        data = []
        for ingredient in ingredients:
            data.append(
                IngredientInRecipe(
                    ingredient=ingredient.get('id'),
                    recipe=recipe,
                    amount=ingredient.get('amount'),
                )
            )
        IngredientInRecipe.objects.bulk_create(data)

    def create(self, validated_data):
        """Метод создания рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('IngredientInRecipe')
        recipe = Recipe.objects.create(**validated_data)
        self.ingredient_in_recipe_create(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('IngredientInRecipe')
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
