from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorPackageViewset, AppointmentViewset, AppointmentCancellationView

router = DefaultRouter()
router.register(r'doctorpackages', DoctorPackageViewset, basename='doctorpackages')
router.register(r'appointments', AppointmentViewset, basename='appointments')

urlpatterns = [
    path('', include(router.urls)),
    path('cancellation/', AppointmentCancellationView.as_view({'patch': 'partial_update'}), name='cancellation'),
]