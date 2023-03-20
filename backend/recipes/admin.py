from django.contrib import admin

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientInline(admin.StackedInline):
    model = IngredientInRecipe
    extra = 5


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cooking_time',)
    inlines = (
        IngredientInline,
    )


admin.site.register(Tag)
admin.site.register(Ingredient)
