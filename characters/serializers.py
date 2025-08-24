from rest_framework import serializers
from characters.models import Character
from characters.models import ChunkCharacter


class CharacterSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Character model.
    """
    name = serializers.ReadOnlyField()

    class Meta:
        model = Character
        fields = [
            'character_id',
            'name',
            'profile',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['character_id', 'created_at', 'updated_at']



class CharacterForMentionSerializer(serializers.ModelSerializer):
    """A simplified Character serializer for nesting."""
    class Meta:
        model = Character
        fields = ['character_id', 'profile']

class ChunkCharacterSerializer(serializers.ModelSerializer):
    """Serializer for a character mention within a chunk."""
    # Use the nested serializer here
    character = CharacterForMentionSerializer(read_only=True)

    class Meta:
        model = ChunkCharacter
        fields = ['character', 'mention_count', 'position_info']