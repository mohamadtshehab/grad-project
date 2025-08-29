"""
Views for chunk-related operations.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.http import Http404
from chunks.models import Chunk
from chunks.serializers import ChunkSerializer
from books.models import Book
from characters.models import ChunkCharacter, Character, CharacterRelationship
from characters.serializers import ChunkCharacterSerializer
from utils.response_utils import ResponseMixin, StandardResponse
import uuid


class ChunkViewSet(viewsets.ReadOnlyModelViewSet, ResponseMixin):
    """
    ViewSet for retrieving book chunks.
    Provides read-only access to chunks for authenticated users.
    """
    serializer_class = ChunkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter chunks by book and user ownership."""
        book_id = self.kwargs.get('book_id')
        
        if book_id:
            # Ensure user owns the book
            book = get_object_or_404(
                Book, 
<<<<<<< HEAD
                book_id=book_id, 
=======
                id=book_id, 
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
                # CORRECTED: Use the model field name 'user', not 'user_id'
                user=self.request.user
            )
            return Chunk.objects.filter(book=book).order_by('chunk_number')

        return Chunk.objects.none()
    
    def list(self, request, book_id=None):
        try:
            queryset = self.get_queryset()
            start = request.query_params.get('start')
            end = request.query_params.get('end')
            if start:
                queryset = queryset.filter(chunk_number__gte=int(start))
            if end:
                queryset = queryset.filter(chunk_number__lte=int(end))
            
            page_size = min(int(request.query_params.get('page_size', 10)), 100)
            paginator = Paginator(queryset, page_size)
            page_number = int(request.query_params.get('page', 1))
            
            try:
                page_obj = paginator.page(page_number)
            except:
                return self.error_response(
                    message_en="Invalid page number",
                    message_ar="رقم الصفحة غير صحيح",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            serializer = self.get_serializer(page_obj, many=True)
            
            return self.success_response(
                message_en="Chunks retrieved successfully",
                message_ar="تم استرجاع الأجزاء بنجاح",
                data={
                    "chunks": serializer.data,
                    "pagination": {
                        "current_page": page_obj.number,
                        "total_pages": paginator.num_pages,
                        "total_chunks": paginator.count,
                    }
                }
            )
        except Exception as e:
            return self.error_response(
                message_en="Failed to retrieve chunks",
                message_ar="فشل في استرجاع الأجزاء",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )
    
    def retrieve(self, request, book_id=None, pk=None):
        try:
            if pk is None:
                return self.error_response(
                    message_en="Chunk number is required",
                    message_ar="رقم الجزء مطلوب",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            chunk_number = int(pk)
            chunk = get_object_or_404(
                self.get_queryset(),
                chunk_number=chunk_number
            )
            serializer = self.get_serializer(chunk)
            return self.success_response(
                message_en="Chunk retrieved successfully",
                message_ar="تم استرجاع الجزء بنجاح",
                data=serializer.data
            )
        except ValueError:
            return self.error_response(
                message_en="Invalid chunk number",
                message_ar="رقم الجزء غير صحيح",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return self.error_response(
                message_en="Failed to retrieve chunk",
                message_ar="فشل في استرجاع الجزء",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )

    @action(detail=False, methods=['get'])
    def search(self, request, book_id=None):
        try:
            query = request.query_params.get('q', '').strip()
            if not query or len(query) < 3:
                return self.error_response(
                    message_en="Search query must be at least 3 characters",
                    message_ar="استعلام البحث يجب أن يكون 3 أحرف على الأقل",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            queryset = self.get_queryset().filter(chunk_text__icontains=query)
            
            # Apply pagination
            page_size = min(int(request.query_params.get('page_size', 10)), 100)
            paginator = Paginator(queryset, page_size)
            page_number = int(request.query_params.get('page', 1))
            
            try:
                page_obj = paginator.page(page_number)
            except:
                return self.error_response(
                    message_en="Invalid page number",
                    message_ar="رقم الصفحة غير صحيح",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            serializer = self.get_serializer(page_obj, many=True)
            
            return self.success_response(
                message_en="Search completed successfully",
                message_ar="تم إكمال البحث بنجاح",
                data={
                    "chunks": serializer.data,
                    "pagination": {
                        "current_page": page_obj.number,
                        "total_pages": paginator.num_pages,
                        "total_chunks": paginator.count,
                    }
                }
            )
        except Exception as e:
            return self.error_response(
                message_en="Failed to perform search",
                message_ar="فشل في إجراء البحث",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chunk_characters(request, chunk_id: str):
    """
    List all characters mentioned in a single chunk.
    """
    try:
        # Assuming your Chunk primary key is a UUIDField named 'chunk_id'
        chunk_uuid = uuid.UUID(chunk_id)
    except ValueError:
        return StandardResponse.error(
            message_en="Invalid chunk ID format",
            message_ar="تنسيق معرف الجزء غير صحيح",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # CORRECTED: Use 'book' and 'book__user' for relationships
        chunk = get_object_or_404(
            Chunk.objects.select_related('book'),
            pk=chunk_uuid, 
            book__user=request.user
        )

        mentions = ChunkCharacter.objects.select_related('character').filter(chunk=chunk).order_by('character__created_at')

        serializer = ChunkCharacterSerializer(mentions, many=True)
        
        return StandardResponse.success(
            message_en="Chunk characters retrieved successfully",
            message_ar="تم استرجاع شخصيات الجزء بنجاح",
            data={
                'chunk_id': str(chunk.pk),
                'book_id': str(chunk.book.pk),
                'characters': serializer.data,
<<<<<<< HEAD
                'count': mentions.count(),
=======
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
            }
        )
    except Http404:
        return StandardResponse.not_found(
            message_en="Chunk not found",
            message_ar="الجزء غير موجود"
        )
    except Exception as e:
        return StandardResponse.server_error(
            message_en="Failed to retrieve chunk characters",
            message_ar="فشل في استرجاع شخصيات الجزء",
            error_detail=str(e)
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chunk_relationships(request, chunk_id: str):
    """
<<<<<<< HEAD
    Get all relationships for characters mentioned in a single chunk.
    
    Returns a list of relationships between characters that appear in the specified chunk.
=======
    Get relationships for characters mentioned in a single chunk.
    
    Query parameters:
    - character_id (optional): Filter relationships to only include the specified character
    
    Returns a list of relationships between characters that appear in the specified chunk.
    If character_id is provided, only relationships involving that character are returned.
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    """
    try:
        # Validate chunk_id format
        chunk_uuid = uuid.UUID(chunk_id)
    except ValueError:
        return StandardResponse.error(
            message_en="Invalid chunk ID format",
            message_ar="تنسيق معرف الجزء غير صحيح",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get the chunk and verify user access
        chunk = get_object_or_404(
            Chunk.objects.select_related('book'),
            pk=chunk_uuid, 
            book__user=request.user
        )
        
<<<<<<< HEAD
=======
        # Check for character_id filter
        character_id_param = request.query_params.get('character_id')
        filter_character = None
        
        if character_id_param:
            try:
                character_uuid = uuid.UUID(character_id_param)
                # Verify the character exists and user has access
                filter_character = get_object_or_404(
                    Character.objects.select_related('book'),
                    id=character_uuid,
                    book__user=request.user
                )
                # Verify the character belongs to the same book as the chunk
                if filter_character.book != chunk.book:
                    return StandardResponse.error(
                        message_en="Character does not belong to the same book as the chunk",
                        message_ar="الشخصية لا تنتمي لنفس الكتاب الذي ينتمي إليه الجزء",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return StandardResponse.error(
                    message_en="Invalid character ID format",
                    message_ar="تنسيق معرف الشخصية غير صحيح",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
        # Get all characters mentioned in this chunk
        chunk_characters = ChunkCharacter.objects.filter(chunk=chunk).values_list('character_id', flat=True)
        
        if not chunk_characters:
            return StandardResponse.success(
                message_en="No characters found in chunk",
                message_ar="لم يتم العثور على شخصيات في الجزء",
                data={
                    'chunk_id': str(chunk.pk),
                    'book_id': str(chunk.book.pk),
                    'relationships': [],
                    'total_relationships': 0,
<<<<<<< HEAD
                }
            )
        
        # Get all relationships between characters in this chunk
        relationships = CharacterRelationship.objects.filter(
            book=chunk.book
        ).filter(
            # Both characters must be in the chunk
            Q(from_character_id__in=chunk_characters) & 
            Q(to_character_id__in=chunk_characters)
        ).select_related(
=======
                    'filtered_character': str(filter_character.id) if filter_character else None
                }
            )
        
        # Build relationship query
        relationships_query = CharacterRelationship.objects.filter(chunk=chunk)
        
        if filter_character:
            # Filter to relationships involving the specific character
            relationships_query = relationships_query.filter(
                Q(from_character=filter_character) | Q(to_character=filter_character)
            )
        else:
            # Get all relationships between characters in this chunk
            relationships_query = relationships_query.filter(
                # Both characters must be in the chunk
                Q(from_character_id__in=chunk_characters) & 
                Q(to_character_id__in=chunk_characters)
            )
        
        relationships = relationships_query.select_related(
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
            'from_character', 
            'to_character'
        ).order_by('created_at')
        
        # Create simplified relationship data
        simplified_relationships = []
        for relationship in relationships:
            simplified_relationships.append({
<<<<<<< HEAD
                'from_character_name': relationship.from_character.name,
                'from_character_id': str(relationship.from_character.character_id),
                'to_character_name': relationship.to_character.name,
                'to_character_id': str(relationship.to_character.character_id),
                'relationship_type': relationship.relationship_type,
                'description': relationship.description
=======
                'from_character_id': str(relationship.from_character.id),
                'to_character_id': str(relationship.to_character.id),
                'relationship_type': relationship.relationship_type,
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
            })
        
        return StandardResponse.success(
            message_en="Chunk relationships retrieved successfully",
            message_ar="تم استرجاع علاقات الجزء بنجاح",
            data={
                'chunk_id': str(chunk.pk),
                'book_id': str(chunk.book.pk),
<<<<<<< HEAD
                'relationships': simplified_relationships,
                'total_relationships': len(simplified_relationships),
                'characters_in_chunk': list(chunk_characters)
=======
                'chunk_number': chunk.chunk_number,
                'relationships': simplified_relationships,
                'total_relationships': len(simplified_relationships),
                'characters_in_chunk': list(chunk_characters),
                'filtered_character': str(filter_character.id) if filter_character else None
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
            }
        )
        
    except Http404:
        return StandardResponse.not_found(
            message_en="Chunk not found",
            message_ar="الجزء غير موجود"
        )
    except Exception as e:
        return StandardResponse.server_error(
            message_en="Failed to retrieve chunk relationships",
            message_ar="فشل في استرجاع علاقات الجزء",
            error_detail=str(e)
        )