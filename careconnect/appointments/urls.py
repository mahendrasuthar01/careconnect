from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorPackageViewset

router = DefaultRouter()
router.register(r'doctorpackages', DoctorPackageViewset, basename='doctorpackages')

urlpatterns = [
    path('', include(router.urls)),
]