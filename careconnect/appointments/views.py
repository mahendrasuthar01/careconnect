from .models import DoctorPackage
from .serializers import DoctorPackageSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Create your views here.
class DoctorPackageViewset(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = DoctorPackage.objects.all()
    serializer_class = DoctorPackageSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            package = self.get_object()
            package.delete()
            return Response({"message": "Package deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Package not found"}, status=status.HTTP_404_NOT_FOUND)