from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet
from characters.views import latest_character_profiles
from chunks.views import ChunkViewSet

router = DefaultRouter()
router.register(r'', BookViewSet, basename='books')

app_name = 'books'

urlpatterns = [
    path('<slug:book_id>/characters/', latest_character_profiles, name='book-characters-latest'),
    path('<slug:book_id>/chunks/', ChunkViewSet.as_view({
        'get': 'list'
    }), name='book-chunks-list'),
    path('<slug:book_id>/chunks/<int:pk>/', ChunkViewSet.as_view({
        'get': 'retrieve'
    }), name='book-chunks-detail'),
    path('<slug:book_id>/chunks/search/', ChunkViewSet.as_view({
        'get': 'search'
    }), name='book-chunks-search'),
    
    path('', include(router.urls)),
]
