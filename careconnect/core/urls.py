from django.urls import path, include
from .views import FavoriteViewSet, LocationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'locations', LocationViewSet, basename='location')

urlpatterns = [
    path('', include(router.urls)),
    
 ]