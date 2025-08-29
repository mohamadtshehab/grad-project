"""
Serializers for chunk-related models.
"""

from rest_framework import serializers
from chunks.models import Chunk


class ChunkSerializer(serializers.ModelSerializer):
    """
    Serializer for Chunk model.
    """
    
    class Meta:
        model = Chunk
        fields = [
            'id',
            'chunk_text', 
            'chunk_number',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChunkSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for chunk summaries (without full text).
    """
    preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Chunk
        fields = [
            'id',
            'chunk_number', 
            'preview',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_preview(self, obj):
        """Get a preview of the chunk text (first 100 characters)."""
        return obj.get_preview(100)
