from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet
from chunks.views import ChunkViewSet

router = DefaultRouter()
router.register(r'', BookViewSet, basename='books')

app_name = 'books'

urlpatterns = [
    path('', include(router.urls)),
    # Nested chunk endpoints under books
    path('<uuid:book_id>/chunks/', ChunkViewSet.as_view({
        'get': 'list'
    }), name='book-chunks-list'),
    path('<uuid:book_id>/chunks/<int:pk>/', ChunkViewSet.as_view({
        'get': 'retrieve'
    }), name='book-chunks-detail'),
    path('<uuid:book_id>/chunks/search/', ChunkViewSet.as_view({
        'get': 'search'
    }), name='book-chunks-search'),
    path('<uuid:book_id>/chunks/stats/', ChunkViewSet.as_view({
        'get': 'stats'
    }), name='book-chunks-stats'),
]
