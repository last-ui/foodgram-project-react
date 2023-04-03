from django.contrib.auth import get_user_model
from django.db import models
from django.core import validators

from api.validators import webcolors_validate

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(
        'Название тега',
        max_length=200,
        help_text='Введите название тега',
        unique=True
    )
    color = models.CharField(
        'Цвет',
        default='#FF0000',
        max_length=7,
        null=True,
        help_text='Введите HEX-code цвета',
        validators=(webcolors_validate,),
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        unique=True,
        null=True,
        help_text='Введите слаг тега',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


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

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


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
        validators=(
            validators.MinValueValidator(
                1, message='Время приготовления не может быть меньше 1'),
        )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=["name", "author"], name="unique_recipe",
            ),
        ]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """IngredientInRecipe model."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_in_recipe'
    )
    amount = models.PositiveIntegerField(
        'Количество ингредиента',
        validators=(
            validators.MinValueValidator(
                1,
                message="Минимальное количество ингредиента 1"),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient} - {self.recipe}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user} - {self.recipe}'
