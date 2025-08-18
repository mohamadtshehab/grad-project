"""
Views for chunk-related operations.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from chunks.models import Chunk
from chunks.serializers import ChunkSerializer
from books.models import Book


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
                user_id=self.request.user
            )
            return Chunk.objects.filter(book_id=book).order_by('chunk_number')
        return Chunk.objects.none()
    
    def list(self, request, book_id=None):
        """
        List all chunks for a book with optional pagination.
        
        Query Parameters:
        - page: Page number (default: 1)
        - page_size: Number of chunks per page (default: 10, max: 100)
        - start: Start chunk number (inclusive)
        - end: End chunk number (inclusive)
        """
        queryset = self.get_queryset()
        
        # Handle range filtering
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        
        if start:
            try:
                queryset = queryset.filter(chunk_number__gte=int(start))
            except ValueError:
                return Response({
                    "error": "Invalid start parameter. Must be an integer."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end:
            try:
                queryset = queryset.filter(chunk_number__lte=int(end))
            except ValueError:
                return Response({
                    "error": "Invalid end parameter. Must be an integer."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle pagination
        page_size = min(int(request.query_params.get('page_size', 10)), 100)
        page = int(request.query_params.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        
        try:
            chunks_page = paginator.page(page)
        except:
            return Response({
                "error": "Invalid page number."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(chunks_page, many=True)
        
        return Response({
            "chunks": serializer.data,
            "pagination": {
                "current_page": page,
                "total_pages": paginator.num_pages,
                "total_chunks": paginator.count,
                "page_size": page_size,
                "has_next": chunks_page.has_next(),
                "has_previous": chunks_page.has_previous()
            }
        })
    
    def retrieve(self, request, book_id=None, pk=None):
        """
        Retrieve a specific chunk by chunk_number.
        """
        try:
            chunk_number = int(pk)
        except ValueError:
            return Response({
                "error": "Chunk number must be an integer."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        chunk = get_object_or_404(
            self.get_queryset(),
            chunk_number=chunk_number
        )
        
        serializer = self.get_serializer(chunk)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request, book_id=None):
        """
        Search chunks by text content.
        
        Query Parameters:
        - q: Search query
        - page: Page number (default: 1)
        - page_size: Number of results per page (default: 10, max: 50)
        """
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({
                "error": "Search query 'q' parameter is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(query) < 3:
            return Response({
                "error": "Search query must be at least 3 characters long."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in chunk text
        queryset = self.get_queryset().filter(
            chunk_text__icontains=query
        )
        
        # Pagination for search results
        page_size = min(int(request.query_params.get('page_size', 10)), 50)
        page = int(request.query_params.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        
        try:
            chunks_page = paginator.page(page)
        except:
            return Response({
                "error": "Invalid page number."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(chunks_page, many=True)
        
        return Response({
            "query": query,
            "chunks": serializer.data,
            "pagination": {
                "current_page": page,
                "total_pages": paginator.num_pages,
                "total_results": paginator.count,
                "page_size": page_size,
                "has_next": chunks_page.has_next(),
                "has_previous": chunks_page.has_previous()
            }
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request, book_id=None):
        """
        Get statistics about the book's chunks.
        """
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                "error": "No chunks found for this book."
            }, status=status.HTTP_404_NOT_FOUND)
        
        total_chunks = queryset.count()
        total_words = sum(chunk.word_count or 0 for chunk in queryset)
        total_characters = sum(chunk.character_count for chunk in queryset)
        
        avg_words_per_chunk = total_words / total_chunks if total_chunks > 0 else 0
        avg_chars_per_chunk = total_characters / total_chunks if total_chunks > 0 else 0
        
        return Response({
            "total_chunks": total_chunks,
            "total_words": total_words,
            "total_characters": total_characters,
            "average_words_per_chunk": round(avg_words_per_chunk, 2),
            "average_characters_per_chunk": round(avg_chars_per_chunk, 2)
        })
