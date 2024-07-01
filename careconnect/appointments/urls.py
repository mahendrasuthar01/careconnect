from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorPackageViewset, AppointmentViewset

router = DefaultRouter()
router.register(r'doctorpackages', DoctorPackageViewset, basename='doctorpackages')
router.register(r'appointments', AppointmentViewset, basename='appointments')

urlpatterns = [
    path('', include(router.urls)),
    # path('<str:appointment_id>/cancel/', AppointmentCancellationView.as_view(), name='appointment_cancellation'),
]