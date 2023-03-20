from django.contrib.auth.models import User
from django.db import models


class Tag(models.Model):
    """Tag model."""
    name = models.CharField(
        'Название тега',
        max_length=200,
        help_text='Введите название тега',
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        null=True,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        unique=True,
        null=True,
        help_text='Введите слаг тега',
    )


class Ingredient(models.Model):
    """Ingredient model."""
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения',
    )


class Recipe(models.Model):
    """Recipe model."""
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        help_text='Введите название рецепта',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='media/',
        null=True,
        default=None

    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    text = models.TextField(
        'Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        help_text='Введите время приготовления',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингридиенты',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagInRecipe',
        verbose_name='Теги',
        related_name='recipes'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagInRecipe(models.Model):
    """IngredientInRecipe model."""
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class IngredientInRecipe(models.Model):
    """IngredientInRecipe model."""
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        'Количество ингредиента'
    )
