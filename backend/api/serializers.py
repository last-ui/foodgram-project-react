import base64

import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import (
    UserCreateSerializer as BaseUserRegistrationSerializer
)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Ingredient, IngredientInRecipe, Recipe, Tag, )
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',)
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and obj.subscribed.filter(
            user=user).exists()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class TagCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), )

    class Meta:
        model = Tag
        fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients_in_recipe = IngredientInRecipe.objects.filter(
            recipe=obj.pk
        )
        return IngredientsInRecipeSerializer(
            ingredients_in_recipe,
            many=True
        ).data

    def get_is_favorited(self, obj):
        return obj.favorite.filter(user=self.context['request'].user).exists()

    def get_is_in_shopping_cart(self, obj):
        return obj.shopping_cart.filter(
            user=self.context['request'].user
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'author', 'text', 'cooking_time',
            'ingredients', 'tags', 'is_favorited', 'is_in_shopping_cart'
        )


class RecipeShortSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_queryset(self, obj):
        """Получение выборки рецептов текущего пользователя."""
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit:
            return obj.recipes.all()[:int(limit)]
        return obj.recipes.all()

    def get_recipes(self, obj):
        return RecipeShortSerializer(
            self.get_queryset(obj),
            many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password',)
        read_only_fields = ('id',)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            image_format, image_str = data.split(';base64,')
            ext = image_format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_str),
                name=f'temp.{ext}'
            )
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientsSerializerCreate(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializerCreate(RecipeSerializer):

    ingredients = IngredientsSerializerCreate(
        many=True,
        source='IngredientInRecipe',
    )

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=False, allow_null=True)
    # author = UserSerializer(read_only=True)

    def ingredient_in_recipe_create(self, recipe, ingredients):
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'ingredients': 'обязательное поле'}
            )
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                {'tags': 'обязательное поле'}
            )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('IngredientInRecipe')
        recipe = Recipe.objects.create(**validated_data)
        self.ingredient_in_recipe_create(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('IngredientInRecipe')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        IngredientInRecipe.objects.filter(recipe_id=instance.id).delete()
        self.ingredient_in_recipe_create(instance, ingredients)
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientsInRecipeSerializer(
            IngredientInRecipe.objects.filter(recipe=instance), many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags, many=True
        ).data
        return representation

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
