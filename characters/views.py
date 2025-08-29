from rest_framework import status
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
            # Character is either the 'from' or 'to' character
            models.Q(from_character=character) | models.Q(to_character=character)
        ).select_related(
            'from_character', 
            'to_character',
            'chunk'
        ).order_by('chunk__chunk_number', 'created_at')
        
        # Create detailed relationship data with chunk context
        detailed_relationships = []
        for relationship in relationships:
            if relationship.from_character == character:
                # Current character is the 'from' character
                other_character = relationship.to_character
                relationship_type = relationship.relationship_type
            else:
                # Current character is the 'to' character
                other_character = relationship.from_character
                relationship_type = relationship.relationship_type
            
            detailed_relationships.append({
                'character_name': get_character_name(other_character),
                'character_id': str(other_character.id),
                'relationship_type': relationship_type,
                'chunk_id': str(relationship.chunk.id),
                'chunk_number': relationship.chunk.chunk_number,
                'created_at': relationship.created_at.isoformat()
            })
        
        return StandardResponse.success(
            message_en="Character relationships retrieved successfully",
            message_ar="تم استرجاع علاقات الشخصية بنجاح",
            data={
                'character_id': str(character.id),
                'character_name': get_character_name(character),
                'book_id': str(character.book.id),
                'relationships': detailed_relationships,
                'total_relationships': len(detailed_relationships),
                'chunks_with_relationships': len(set(r['chunk_number'] for r in detailed_relationships))
            }
        )
        
    except Http404:
        return StandardResponse.not_found(
            message_en="Character not found or access denied",
            message_ar="الشخصية غير موجودة أو الوصول مرفوض",
            error_detail=f'No character found with ID: {character_id}'
        )
    except Exception as e:
        return StandardResponse.server_error(
            message_en="Failed to retrieve character relationships",
            message_ar="فشل في استرجاع علاقات الشخصية",
            error_detail=str(e)
        )



