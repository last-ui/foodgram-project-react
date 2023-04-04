from django.contrib import admin
from django.utils.html import format_html

from foodgram_backend import settings
from recipes.models import Favorite, Ingredient, IngredientInRecipe, Recipe, \
    ShoppingCart, Tag


class IngredientInline(admin.TabularInline):
    min_num = 1
    model = IngredientInRecipe
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'author', 'add_to_favorite')
    filter_vertical = ('tags',)
    inlines = (
        IngredientInline,
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'tags__name', 'tags__slug', 'author__username')
    list_per_page = settings.LIST_PER_PAGE

    @admin.display(description='Добавлено в избранное')
    def add_to_favorite(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_per_page = settings.LIST_PER_PAGE


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    list_display = ('name', 'color_code', 'slug')
    fields = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')

    @admin.display(description='Цвет')
    def color_code(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            obj.color,
            obj.color,
        )


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
