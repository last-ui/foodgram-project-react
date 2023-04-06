from django.urls import include, path

from api.views import (IngredientsViewSet, MyUsersViewSet, RecipesViewSet,
                       TagsViewSet)
from rest_framework import routers

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register('recipes', RecipesViewSet, basename='recipes')
router_v1.register('users', MyUsersViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
