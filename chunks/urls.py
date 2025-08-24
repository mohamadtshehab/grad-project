"""
URL configuration for chunks app.
"""

from django.urls import path
from chunks.views import chunk_characters, chunk_relationships

urlpatterns = [
    path('<slug:chunk_id>/characters/', chunk_characters, name='chunk-characters'),
    path('<slug:chunk_id>/relationships/', chunk_relationships, name='chunk-relationships'),
]
