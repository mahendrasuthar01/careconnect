from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .serializers import CategorySerializer, WorkingTimeSerializer, HospitalSerializer, DoctorSerializer
from rest_framework.permissions import AllowAny

# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class WorkingTimeViewSet(viewsets.ModelViewSet):
    queryset = WorkingTime.objects.all()
    serializer_class = WorkingTimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        try:
            working_time = self.get_object()
            working_time.delete()
            return Response({"message": "Working-Time deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Working-Time not found"}, status=status.HTTP_404_NOT_FOUND)


class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [AllowAny]

    def destroy(self, request, *args, **kwargs):
        try:
            hospital = self.get_object()
            hospital.delete()
            return Response({"message": "Hospital deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Hospital not found"}, status=status.HTTP_404_NOT_FOUND)
    
    

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]
     
    def destroy(self, request, *args, **kwargs):
        try:
            doctor = self.get_object()
            doctor.delete()
            return Response({"message": "Doctor deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)