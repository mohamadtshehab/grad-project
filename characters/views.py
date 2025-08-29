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
from django.db.models import Q
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




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_character_profiles(request, book_id=None):
    """
    Get the latest discovered profile for all unique characters in a book.

    Query params:
      - book_id: UUID of the book (required)

    Returns a list of characters with their latest profile taken from the most
    recent ChunkCharacter row per character within that book.
    """
    book_id = book_id or request.query_params.get('book_id')
    if not book_id:
        return StandardResponse.validation_error(
            errors={"book_id": ["This query parameter is required."]}
        )

    try:
        # Filter to user's own book
        from books.models import Book
        book = get_object_or_404(Book.objects.filter(user=request.user), id=book_id)

        # Fetch all characters for this book
        characters_qs = Character.objects.filter(book=book)

        # For each character, pick latest non-empty ChunkCharacter by chunk_number
        latest_map = {}
        cc_qs = (
            ChunkCharacter.objects
            .filter(character__in=characters_qs)
            .select_related('character', 'chunk')
            .order_by('character_id', '-chunk__chunk_number')
        )

        for cc in cc_qs:
            cid = str(cc.character.id)
            if cid in latest_map:
                continue
            # Only consider non-empty profiles
            if cc.character_profile and cc.character_profile != {}:
                latest_map[cid] = cc
            else:
                # If this is the first chunk we've seen for this character and it's empty,
                # still include it but mark it as empty
                if cid not in latest_map:
                    latest_map[cid] = cc

        results = []
        for cid, cc in latest_map.items():
            profile = cc.character_profile or {}
            results.append({
                'character_id': cid,
                'character_name': profile.get('name', cid),
                'latest_profile': profile,
                'latest_chunk_number': cc.chunk.chunk_number,
                'latest_chunk_id': str(cc.chunk.id)
            })

        return StandardResponse.success(
            message_en="Latest character profiles retrieved successfully",
            message_ar="تم استرجاع أحدث ملفات الشخصيات بنجاح",
            data={
                'book_id': str(book.id),
                'total_characters': len(results),
                'characters': results
            }
        )
    except Http404:
        return StandardResponse.not_found(
            message_en="Book not found or access denied",
            message_ar="الكتاب غير موجود أو الوصول مرفوض",
            error_detail=f"No book found with ID: {book_id}"
        )
    except Exception as e:
        return StandardResponse.server_error(
            message_en="Failed to retrieve latest character profiles",
            message_ar="فشل في استرجاع أحدث ملفات الشخصيات",
            error_detail=str(e)
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def character_detail(request, character_id):
    """
    Get detailed character information including all profile records and relationships.
    
    Returns:
    - Character basic info
    - All chunk profiles (ordered by chunk number)
    - All relationships across chunks
    """
    try:
        # Validate character_id format
        character_uuid = uuid.UUID(character_id)
    except ValueError:
        return StandardResponse.error(
            message_en="Invalid character ID format",
            message_ar="تنسيق معرف الشخصية غير صحيح",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get the character and verify user access
        character = get_object_or_404(
            Character.objects.select_related('book'),
            id=character_uuid,
            book__user=request.user
        )

        # Get all chunk profiles for this character (ordered by chunk number)
        chunk_profiles = (
            ChunkCharacter.objects
            .filter(character=character)
            .select_related('chunk')
            .order_by('chunk__chunk_number')
        )

        # Get all relationships involving this character
        relationships = (
            CharacterRelationship.objects
            .filter(
                Q(from_character=character) | Q(to_character=character)
            )
            .select_related('from_character', 'to_character', 'chunk')
            .order_by('chunk__chunk_number', 'created_at')
        )

        # Build chunk profiles data
        profiles_data = []
        for cc in chunk_profiles:
            profiles_data.append({
                'chunk_id': str(cc.chunk.id),
                'chunk_number': cc.chunk.chunk_number,
                'profile': cc.character_profile or {},
                'created_at': cc.created_at.isoformat(),
                'updated_at': cc.updated_at.isoformat()
            })

        # Build relationships data
        relationships_data = []
        for rel in relationships:
            # Determine the other character in the relationship
            if rel.from_character == character:
                other_character = rel.to_character
                relationship_direction = 'from'
            else:
                other_character = rel.from_character
                relationship_direction = 'to'

            # Get the other character's name from their latest profile
            other_character_name = get_character_name(other_character)

            relationships_data.append({
                'relationship_id': str(rel.pk),
                'other_character_id': str(other_character.id),
                'other_character_name': other_character_name,
                'relationship_type': rel.relationship_type,
                'relationship_direction': relationship_direction,  # 'from' or 'to'
                'chunk_id': str(rel.chunk.id),
                'chunk_number': rel.chunk.chunk_number,
                'created_at': rel.created_at.isoformat(),
                'updated_at': rel.updated_at.isoformat()
            })

        # Get the character's latest profile
        latest_profile = None
        if chunk_profiles.exists():
            latest_cc = chunk_profiles.last()
            if latest_cc:
                latest_profile = latest_cc.character_profile or {}

        return StandardResponse.success(
            message_en="Character details retrieved successfully",
            message_ar="تم استرجاع تفاصيل الشخصية بنجاح",
            data={
                'character_id': str(character.id),
                'book_id': str(character.book.id),
                'book_title': character.book.title,
                'created_at': character.created_at.isoformat(),
                'updated_at': character.updated_at.isoformat(),
                'latest_profile': latest_profile,
                'total_chunks_appeared': len(profiles_data),
                'total_relationships': len(relationships_data),
                'chunk_profiles': profiles_data,
                'relationships': relationships_data
            }
        )

    except Http404:
        return StandardResponse.not_found(
            message_en="Character not found or access denied",
            message_ar="الشخصية غير موجودة أو الوصول مرفوض",
            error_detail=f"No character found with ID: {character_id}"
        )
    except Exception as e:
        return StandardResponse.server_error(
            message_en="Failed to retrieve character details",
            message_ar="فشل في استرجاع تفاصيل الشخصية",
            error_detail=str(e)
        )