"""
Serializers for chunk-related models.
"""

from rest_framework import serializers
from chunks.models import Chunk


class ChunkSerializer(serializers.ModelSerializer):
    """
    Serializer for Chunk model.
    """
    character_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Chunk
        fields = [
            'chunk_id',
            'chunk_text', 
            'chunk_number',
            'word_count',
            'character_count',
            'start_position',
            'end_position',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['chunk_id', 'created_at', 'updated_at']


class ChunkSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for chunk summaries (without full text).
    """
    character_count = serializers.ReadOnlyField()
    preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Chunk
        fields = [
            'chunk_id',
            'chunk_number', 
            'word_count',
            'character_count',
            'preview',
            'created_at'
        ]
        read_only_fields = ['chunk_id', 'created_at']
    
    def get_preview(self, obj):
        """Get a preview of the chunk text (first 100 characters)."""
        return obj.get_preview(100)
