"""
Views for chunk-related operations.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Sum
from chunks.models import Chunk
from chunks.serializers import ChunkSerializer
from books.models import Book
from characters.models import ChunkCharacter
from characters.serializers import ChunkCharacterSerializer
import uuid


class ChunkViewSet(viewsets.ReadOnlyModelViewSet):
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
                book_id=book_id, 
                # CORRECTED: Use the model field name 'user', not 'user_id'
                user=self.request.user
            )
            return Chunk.objects.filter(book=book).order_by('chunk_number')

        return Chunk.objects.none()
    
    # The 'list' and 'retrieve' methods are well-structured. No changes needed.
    def list(self, request, book_id=None):
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
            return Response({"error": "Invalid page number."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = self.get_serializer(page_obj, many=True)
        
        return Response({
            "chunks": serializer.data,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_chunks": paginator.count,
            }
        })
    
    def retrieve(self, request, book_id=None, pk=None):
        chunk_number = int(pk)
        chunk = get_object_or_404(
            self.get_queryset(),
            chunk_number=chunk_number
        )
        serializer = self.get_serializer(chunk)
        return Response(serializer.data)

    # The 'search' method is well-structured. No changes needed.
    @action(detail=False, methods=['get'])
    def search(self, request, book_id=None):
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 3:
            return Response({"error": "Search query 'q' must be at least 3 characters."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(chunk_text__icontains=query)
        # ... (pagination logic is fine) ...
        return Response(...)
    


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
        return Response({"error": "Invalid chunk_id format"}, status=status.HTTP_400_BAD_REQUEST)

    # CORRECTED: Use 'book' and 'book__user' for relationships
    chunk = get_object_or_404(
        Chunk.objects.select_related('book'),
        pk=chunk_uuid, 
        book__user=request.user
    )

    mentions = ChunkCharacter.objects.select_related('character').filter(chunk=chunk).order_by('character__created_at')

    serializer = ChunkCharacterSerializer(mentions, many=True)
    
    return Response({
        'chunk_id': str(chunk.pk),
        'book_id': str(chunk.book.pk),
        'characters': serializer.data,
        'count': mentions.count(),
    }, status=status.HTTP_200_OK)