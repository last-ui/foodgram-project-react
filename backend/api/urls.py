from django.urls import include, path
from rest_framework import routers

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('', include(router_v1.urls)),
]