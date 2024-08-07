from django.urls import path, include
from .views import CategoryViewSet, WorkingTimeViewSet, HospitalViewSet, DoctorViewSet, CombinedDoctorsHospitalsListView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .consumer import DoctorHospitalConsumer

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'working-time', WorkingTimeViewSet, basename='working-time')
router.register(r'hospitals', HospitalViewSet, basename='hospital')
router.register(r'doctors', DoctorViewSet, basename='doctor')
# router.register(r'combined', CombinedViewSet, basename='combined')

urlpatterns = [
    path('', include(router.urls)),    
    path('doctor-hospital-combined-list/', CombinedDoctorsHospitalsListView.as_view(), name='combined-list'),
]

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>', DoctorHospitalConsumer.as_asgi()),
]