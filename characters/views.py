from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from characters.models import Character, CharacterRelationship
from characters.serializers import SimpleCharacterRelationshipSerializer
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
        
        return Response({
            'character_name': character.name,
            'relationships': serializer.data,
            'total_relationships': len(simplified_relationships)
        }, status=status.HTTP_200_OK)
        
    except Http404:
        return Response({
            'error': 'Character not found',
            'details': f'No character found with ID: {character_id}'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve character relationships',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
