from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet
from .debug_upload import DebugUploadView

# Create router and register the ViewSet
router = DefaultRouter()
router.register(r'', BookViewSet, basename='books')

app_name = 'books'

urlpatterns = [
    # Debug upload (temporary)
    path('debug-upload/', DebugUploadView.as_view(), name='debug_upload'),
    
    # Include router URLs
    path('', include(router.urls)),
]
