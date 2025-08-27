from rest_framework import status
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
            # Character is either the 'from' or 'to' character
            models.Q(from_character=character) | models.Q(to_character=character)
        ).select_related(
            'from_character', 
            'to_character'
        ).order_by('created_at')
        
        # Create simplified relationship data
        simplified_relationships = []
        for relationship in relationships:
            if relationship.from_character == character:
                # Current character is the 'from' character
                other_character = relationship.to_character
                relationship_type = relationship.relationship_type
            else:
                # Current character is the 'to' character
                other_character = relationship.from_character
                relationship_type = relationship.relationship_type
            
            simplified_relationships.append({
                'character_name': other_character.name,
                'character_id': str(other_character.character_id),
                'relationship_type': relationship_type
            })
        
        # Serialize the simplified relationships
        serializer = SimpleCharacterRelationshipSerializer(simplified_relationships, many=True)
        
        return StandardResponse.success(
            message_en="Character relationships retrieved successfully",
            message_ar="تم استرجاع علاقات الشخصية بنجاح",
            data={
                'character_name': character.name,
                'relationships': serializer.data,
                'total_relationships': len(simplified_relationships)
            }
        )
        
    except Http404:
        return StandardResponse.not_found(
            message_en="Character not found",
            message_ar="الشخصية غير موجودة",
            error_detail=f'No character found with ID: {character_id}'
        )
    except Exception as e:
        return StandardResponse.server_error(
            message_en="Failed to retrieve character relationships",
            message_ar="فشل في استرجاع علاقات الشخصية",
            error_detail=str(e)
        )
