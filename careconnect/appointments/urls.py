from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorPackageViewset, AppointmentViewset, AppointmentsByUserView, AppointmentCancellationView

router = DefaultRouter()
router.register(r'doctorpackages', DoctorPackageViewset, basename='doctorpackages')
router.register(r'appointments', AppointmentViewset, basename='appointments')

urlpatterns = [
    path('', include(router.urls)),
    path('cancellation/', AppointmentCancellationView.as_view({'patch': 'partial_update'}), name='cancellation'),
    # path('<str:appointment_id>/cancel/', AppointmentCancellationView.as_view(), name='appointment_cancellation'),
    path('appointments/by-user/<str:user_id>/', AppointmentsByUserView.as_view(), name='appointments-by-user'),
]