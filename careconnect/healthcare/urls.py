from django.urls import path, include
from .views import CategoryViewSet, WorkingTimeViewSet, HospitalViewSet, DoctorViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'working-time', WorkingTimeViewSet, basename='working-time')
router.register(r'hospitals', HospitalViewSet, basename='hospital')
router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns = [
    path('', include(router.urls)),
    
 ]