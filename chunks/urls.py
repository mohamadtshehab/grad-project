"""
URL configuration for chunks app.
"""

from django.urls import path
from chunks.views import chunk_characters

urlpatterns = [
    path('<slug:chunk_id>/characters/', chunk_characters, name='chunk-characters'),
]
