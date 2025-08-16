from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet

router = DefaultRouter()
router.register(r'', BookViewSet, basename='books')

app_name = 'books'

urlpatterns = [
    path('', include(router.urls)),
]
