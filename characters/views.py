from rest_framework import status
<<<<<<< HEAD
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from characters.models import Character, CharacterRelationship
from characters.serializers import SimpleCharacterRelationshipSerializer
from utils.response_utils import StandardResponse
from django.db import models


@api_view(['GET'])
def character_relationships(request, character_id):
    """
    Get all relationships for a specific character.
    
    Returns a simplified list of (character_name, relationship_type) pairs
    for characters that have relationships with the specified character.
    """
    try:
        # Get the character
        character = get_object_or_404(Character, character_id=character_id)
        
        # Get all relationships involving this character
        relationships = CharacterRelationship.objects.filter(
            book=character.book
        ).filter(
=======
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from characters.models import Character, CharacterRelationship, ChunkCharacter
from characters.serializers import SimpleCharacterRelationshipSerializer
from chunks.models import Chunk
from utils.response_utils import StandardResponse
from django.db import models
import uuid


def get_character_name(character):
    """Get character name from latest chunk profile."""
    latest_chunk_char = ChunkCharacter.objects.filter(
        character=character
    ).order_by('-chunk__chunk_number').first()
    
    if latest_chunk_char and latest_chunk_char.character_profile:
        return latest_chunk_char.character_profile.get('name', str(character.id))
    return str(character.id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def character_relationships(request, character_id):
    """
    Get all relationships for a specific character across all chunks.
    
    Returns a list of relationships with chunk context for the specified character.
    """
    try:
        # Get the character and verify user access
        character = get_object_or_404(
            Character.objects.select_related('book'), 
            id=character_id,
            book__user=request.user
        )
        
        # Get all relationships involving this character across all chunks
        relationships = CharacterRelationship.objects.filter(
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
            # Character is either the 'from' or 'to' character
            models.Q(from_character=character) | models.Q(to_character=character)
        ).select_related(
            'from_character', 
<<<<<<< HEAD
            'to_character'
        ).order_by('created_at')
        
        # Create simplified relationship data
        simplified_relationships = []
=======
            'to_character',
            'chunk'
        ).order_by('chunk__chunk_number', 'created_at')
        
        # Create detailed relationship data with chunk context
        detailed_relationships = []
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
        for relationship in relationships:
            if relationship.from_character == character:
                # Current character is the 'from' character
                other_character = relationship.to_character
                relationship_type = relationship.relationship_type
            else:
                # Current character is the 'to' character
                other_character = relationship.from_character
                relationship_type = relationship.relationship_type
            
<<<<<<< HEAD
            simplified_relationships.append({
                'character_name': other_character.name,
                'character_id': str(other_character.character_id),
                'relationship_type': relationship_type
            })
        
        # Serialize the simplified relationships
        serializer = SimpleCharacterRelationshipSerializer(simplified_relationships, many=True)
        
=======
            detailed_relationships.append({
                'character_name': get_character_name(other_character),
                'character_id': str(other_character.id),
                'relationship_type': relationship_type,
                'chunk_id': str(relationship.chunk.id),
                'chunk_number': relationship.chunk.chunk_number,
                'created_at': relationship.created_at.isoformat()
            })
        
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
        return StandardResponse.success(
            message_en="Character relationships retrieved successfully",
            message_ar="تم استرجاع علاقات الشخصية بنجاح",
            data={
<<<<<<< HEAD
                'character_name': character.name,
                'relationships': serializer.data,
                'total_relationships': len(simplified_relationships)
=======
                'character_id': str(character.id),
                'character_name': get_character_name(character),
                'book_id': str(character.book.id),
                'relationships': detailed_relationships,
                'total_relationships': len(detailed_relationships),
                'chunks_with_relationships': len(set(r['chunk_number'] for r in detailed_relationships))
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
            }
        )
        
    except Http404:
        return StandardResponse.not_found(
<<<<<<< HEAD
            message_en="Character not found",
            message_ar="الشخصية غير موجودة",
=======
            message_en="Character not found or access denied",
            message_ar="الشخصية غير موجودة أو الوصول مرفوض",
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
            error_detail=f'No character found with ID: {character_id}'
        )
    except Exception as e:
        return StandardResponse.server_error(
            message_en="Failed to retrieve character relationships",
            message_ar="فشل في استرجاع علاقات الشخصية",
            error_detail=str(e)
        )
<<<<<<< HEAD
=======



>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
