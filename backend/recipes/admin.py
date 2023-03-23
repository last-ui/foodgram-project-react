from django.contrib import admin
# from import_export import resources
# from import_export.admin import ImportExportModelAdmin

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 3


class TagInline(admin.TabularInline):
    model = Tag
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cooking_time',)
    inlines = (
        IngredientInline,
    )


# class IngredientResource(resources.ModelResource):
#     class Meta:
#         model = Ingredient
#
#
# class IngredientAdmin(ImportExportModelAdmin):
#     resource_class = IngredientResource


# admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Ingredient)
admin.site.register(Tag)
