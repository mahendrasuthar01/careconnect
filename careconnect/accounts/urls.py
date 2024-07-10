"""
URL configuration for careconnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CustomLoginView, VerifyOTPView, RequestPasswordResetView, ResetPasswordView, PatientViewSet, PatientsByUserView
from .consumers import UserChatConsumer

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'patients', PatientViewSet, basename='patient')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('forgot-password/', RequestPasswordResetView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('patients/by-user/<user_id>/', PatientsByUserView.as_view(), name='patients_by_user'),
]

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    path('ws/chat/user/<str:room_name>', UserChatConsumer.as_asgi()),
]