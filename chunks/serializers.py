"""
Serializers for chunk-related models.
"""

from rest_framework import serializers
from chunks.models import Chunk


class ChunkSerializer(serializers.ModelSerializer):
    """
    Serializer for Chunk model.
    """
<<<<<<< HEAD
    character_count = serializers.ReadOnlyField()
=======
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    
    class Meta:
        model = Chunk
        fields = [
<<<<<<< HEAD
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
=======
            'id',
            'chunk_text', 
            'chunk_number',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96


class ChunkSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for chunk summaries (without full text).
    """
<<<<<<< HEAD
    character_count = serializers.ReadOnlyField()
=======
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Chunk
        fields = [
<<<<<<< HEAD
            'chunk_id',
            'chunk_number', 
            'word_count',
            'character_count',
            'preview',
            'created_at'
        ]
        read_only_fields = ['chunk_id', 'created_at']
=======
            'id',
            'chunk_number', 
            'preview',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    
    def get_preview(self, obj):
        """Get a preview of the chunk text (first 100 characters)."""
        return obj.get_preview(100)
