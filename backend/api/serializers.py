import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Ingredient, IngredientInRecipe, Recipe, Tag,)


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
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),)

    class Meta:
        model = Tag
        fields = ('id',)


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


class RecipeSerializerCreate(serializers.ModelSerializer):

    ingredients = IngredientsSerializerCreate(
        many=True,
        source='IngredientInRecipe',
    )

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=False, allow_null=True)

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'ingredients': 'this field required'}
            )
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                {'tags': 'this field required'}
            )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('IngredientInRecipe')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            IngredientInRecipe.objects.create(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=amount,
            )
        recipe.tags.set(tags)
        return recipe

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

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    def get_ingredients(self, obj):
        ingredients_in_recipe = IngredientInRecipe.objects.filter(
            recipe=obj.pk
        )
        return IngredientsInRecipeSerializer(
            ingredients_in_recipe,
            many=True
        ).data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)
