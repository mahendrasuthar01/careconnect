from django.urls import path, include
from .views import CategoryViewSet, WorkingTimeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

app = DefaultRouter()
app.register(r'working-time', WorkingTimeViewSet, basename='working-time')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(app.urls)),
    path('healthcare/working-time/', WorkingTimeViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),

    path('healthcare/working-time/<str:pk>/', WorkingTimeViewSet.as_view({
        'put': 'update',
        'delete': 'destroy'
     })),
]