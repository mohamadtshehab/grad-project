"""
URL configuration for chunks app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chunks.views import ChunkViewSet

# Create router for nested routes under books
router = DefaultRouter()

# Chunks will be accessed via /api/books/{book_id}/chunks/
# This will be included in the main URLs with the book_id parameter

urlpatterns = [
    # Chunks endpoints will be registered in the main URL config
    # to handle the nested route structure properly
]
