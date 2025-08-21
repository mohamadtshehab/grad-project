from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import FileResponse
import os
import mimetypes
from books.tasks import process_book_workflow

from .models import Book, epub_to_raw_html_string
from .serializers import (
    BookListSerializer, BookDetailSerializer, 
    BookUploadSerializer, BookStatusSerializer
)
from utils.models import Job
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile

class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling book CRUD operations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return books for the authenticated user only"""
        return Book.objects.filter(
            user_id=self.request.user,
            is_deleted=False
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return BookUploadSerializer
        elif self.action == 'list':
            return BookListSerializer
        else:
            return BookDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """Upload a new book"""
        try:
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                
                book = serializer.save()
                
                # Ensure a corresponding TXT file exists next to the EPUB
                if getattr(book, 'file', None) and not getattr(book, 'txt_file', None):
                    epub_path = book.file.path
                    raw_html_content = epub_to_raw_html_string(epub_path)
                    base_filename = os.path.basename(epub_path)
                    txt_filename = os.path.splitext(base_filename)[0] + '.txt'
                    # Save the generated TXT content to the model's txt_file field
                    book.txt_file.save(
                        txt_filename,
                        ContentFile(raw_html_content.encode('utf-8')),
                        save=False
                    )
                    book.save(update_fields=['txt_file'])
                # if has chunks and characters, delete them
                if book.chunks.exists() or book.characters.exists():
                    book.chunks.all().delete()
                    book.characters.all().delete()
                    book.save(update_fields=['chunks', 'characters'])
                
                # Create a Job for complete book workflow processing
                with transaction.atomic():
                    job = Job.objects.create(
                        user=request.user,
                        job_type="book_workflow_process",
                        status=Job.Status.PENDING,
                        progress=0,
                    )

                    # Enqueue new workflow Celery task
                    try:
                        process_book_workflow.delay(
                            job_id=str(job.id),
                            user_id=str(request.user.id),
                            book_id=str(book.book_id),
                        )
                    except Exception as e:
                        job.status = Job.Status.FAILED
                        job.error = str(e)
                        job.finished_at = timezone.now()
                        job.save(update_fields=["status", "error", "finished_at", "updated_at"])
                        return Response({
                            "status": "error",
                            "errors": str(e),
                            "en": "Failed to enqueue processing job",
                            "ar": "فشل في جدولة مهمة المعالجة",
                            "job_id": str(job.id),
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Return 202 with job id and basic book info
                return Response({
                    "status": "accepted",
                    "en": "Book upload accepted; processing started",
                    "ar": "تم قبول رفع الكتاب؛ بدأت المعالجة",
                    "job_id": str(job.id),
                    "data": {"book_id": str(book.book_id)},
                }, status=status.HTTP_202_ACCEPTED)
            
            else:
                return Response({
                    "status": "error",
                    "en": "Invalid book data",
                    "ar": "بيانات الكتاب غير صحيحة",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                "status": "error",
                "en": "Failed to upload book",
                "ar": "فشل في رفع الكتاب",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """Get user's books with optional filtering"""
        try:
            queryset = self.get_queryset()
            
            # Optional filtering by processing status
            status_filter = request.query_params.get('status')
            if status_filter and status_filter in ['pending', 'processing', 'completed', 'failed']:
                queryset = queryset.filter(processing_status=status_filter)
            
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                "status": "success",
                "en": "Books retrieved successfully",
                "ar": "تم استرجاع الكتب بنجاح",
                "data": {
                    "books": serializer.data,
                    "count": queryset.count()
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "error",
                "en": "Failed to retrieve books",
                "ar": "فشل في استرجاع الكتب",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Get detailed book information"""
        try:
            book = self.get_object()
            serializer = self.get_serializer(book)
            
            return Response({
                "status": "success",
                "en": "Book details retrieved successfully",
                "ar": "تم استرجاع تفاصيل الكتاب بنجاح",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "error",
                "en": "Failed to get book details",
                "ar": "فشل في الحصول على تفاصيل الكتاب",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a book"""
        try:
            book = self.get_object()
            book.is_deleted = True
            book.save()
            
            
            return Response({
                "status": "success",
                "en": "Book deleted successfully",
                "ar": "تم حذف الكتاب بنجاح",
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "error",
                "en": "Failed to delete book",
                "ar": "فشل في حذف الكتاب",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download book file"""
        try:
            book = self.get_object()
            
            # Check if file exists
            if not book.file or not book.file.name:
                return Response({
                    "status": "error",
                    "en": "Book file not found",
                    "ar": "ملف الكتاب غير موجود",
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get file path
            file_path = book.file.path
            
            if not os.path.exists(file_path):
                return Response({
                    "status": "error",
                    "en": "Book file not found on server",
                    "ar": "ملف الكتاب غير موجود على الخادم",
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/epub+zip'
            
            # Create file response
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type,
                as_attachment=True,
                filename=os.path.basename(book.file.name)
            )
            
            
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "en": "Failed to download book",
                "ar": "فشل في تحميل الكتاب",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get book processing status"""
        try:
            book = self.get_object()
            serializer = BookStatusSerializer(book)
            
            return Response({
                "status": "success",
                "en": "Book status retrieved successfully",
                "ar": "تم استرجاع حالة الكتاب بنجاح",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "error",
                "en": "Failed to get book status",
                "ar": "فشل في الحصول على حالة الكتاب",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



