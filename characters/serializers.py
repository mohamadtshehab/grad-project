from rest_framework import serializers
from characters.models import Character
from characters.models import ChunkCharacter
from characters.models import CharacterRelationship


class CharacterSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Character model.
    """
    name = serializers.ReadOnlyField()

    class Meta:
        model = Character
        fields = [
<<<<<<< HEAD
            'character_id',
            'name',
            'profile',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['character_id', 'created_at', 'updated_at']
=======
            'id',
            'name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96



class CharacterForMentionSerializer(serializers.ModelSerializer):
    """A simplified Character serializer for nesting."""
    class Meta:
        model = Character
<<<<<<< HEAD
        fields = ['character_id', 'profile']
=======
        fields = ['id']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96

class ChunkCharacterSerializer(serializers.ModelSerializer):
    """Serializer for a character mention within a chunk."""
    # Use the nested serializer here
    character = CharacterForMentionSerializer(read_only=True)

    class Meta:
        model = ChunkCharacter
<<<<<<< HEAD
        fields = ['character', 'mention_count', 'position_info']
=======
        fields = ['character']
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96


class CharacterRelationshipSerializer(serializers.ModelSerializer):
    """Serializer for character relationships."""
    from_character = CharacterForMentionSerializer(read_only=True)
    to_character = CharacterForMentionSerializer(read_only=True)
    
    class Meta:
        model = CharacterRelationship
        fields = [
            'from_character',
            'to_character',
            'relationship_type',
<<<<<<< HEAD
            'description',
=======
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SimpleCharacterRelationshipSerializer(serializers.Serializer):
    """Simplified serializer for character relationships - only name, id and type."""
    character_name = serializers.CharField()
    character_id = serializers.CharField()
    relationship_type = serializers.CharField()