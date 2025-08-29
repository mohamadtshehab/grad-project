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
from utils.response_utils import ResponseMixin
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile

class BookViewSet(viewsets.ModelViewSet, ResponseMixin):
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
                        book=book,
                        status=Job.Status.PENDING,
                        progress=0,
                    )

                    # Enqueue new workflow Celery task
                    try:
                        process_book_workflow.delay(
                            job_id=str(job.id),
                        )
                    except Exception as e:
                        job.status = Job.Status.FAILED
                        job.error = str(e)
                        job.finished_at = timezone.now()
                        job.save(update_fields=["status", "error", "finished_at", "updated_at"])
                        return self.error_response(
                            message_en="Failed to enqueue processing job",
                            message_ar="فشل في جدولة مهمة المعالجة",
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            error_detail=str(e),
                            job_id=str(job.id)
                        )

                # Return 202 with job id and basic book info
                return self.accepted_response(
                    message_en="Book upload accepted; processing started",
                    message_ar="تم قبول رفع الكتاب؛ بدأت المعالجة",
                    data={"book_id": str(book.id),
                          "job_id": str(job.id)},
                )
            
            else:
                return self.validation_error_response(
                    message_en="Invalid book data",
                    message_ar="بيانات الكتاب غير صحيحة",
                    errors=serializer.errors
                )
                
        except Exception as e:
            return self.error_response(
                message_en="Failed to upload book",
                message_ar="فشل في رفع الكتاب",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )
    
    def list(self, request, *args, **kwargs):
        """Get user's books with optional filtering"""
        try:
            queryset = self.get_queryset()
            
            # Optional filtering by processing status
            status_filter = request.query_params.get('status')
            if status_filter and status_filter in ['pending', 'processing', 'completed', 'failed']:
                queryset = queryset.filter(processing_status=status_filter)
            
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                message_en="Books retrieved successfully",
                message_ar="تم استرجاع الكتب بنجاح",
                data={
                    "books": serializer.data,
                    "count": queryset.count()
                }
            )
            
        except Exception as e:
            return self.error_response(
                message_en="Failed to retrieve books",
                message_ar="فشل في استرجاع الكتب",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )
    
    def retrieve(self, request, *args, **kwargs):
        """Get detailed book information"""
        try:
            book = self.get_object()
            serializer = self.get_serializer(book)
            
            return self.success_response(
                message_en="Book details retrieved successfully",
                message_ar="تم استرجاع تفاصيل الكتاب بنجاح",
                data=serializer.data
            )
            
        except Exception as e:
            return self.error_response(
                message_en="Failed to get book details",
                message_ar="فشل في الحصول على تفاصيل الكتاب",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a book"""
        try:
            book = self.get_object()
            book.is_deleted = True
            book.save()
            
            
            return self.success_response(
                message_en="Book deleted successfully",
                message_ar="تم حذف الكتاب بنجاح"
            )
            
        except Exception as e:
            return self.error_response(
                message_en="Failed to delete book",
                message_ar="فشل في حذف الكتاب",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download book file"""
        try:
            book = self.get_object()
            
            # Check if file exists
            if not book.file or not book.file.name:
                return self.not_found_response(
                    message_en="Book file not found",
                    message_ar="ملف الكتاب غير موجود"
                )
            
            # Get file path
            file_path = book.file.path
            
            if not os.path.exists(file_path):
                return self.not_found_response(
                    message_en="Book file not found on server",
                    message_ar="ملف الكتاب غير موجود على الخادم"
                )
            
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
            return self.error_response(
                message_en="Failed to download book",
                message_ar="فشل في تحميل الكتاب",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get book processing status"""
        try:
            book = self.get_object()
            serializer = BookStatusSerializer(book)
            
            return self.success_response(
                message_en="Book status retrieved successfully",
                message_ar="تم استرجاع حالة الكتاب بنجاح",
                data=serializer.data
            )
            
        except Exception as e:
            return self.error_response(
                message_en="Failed to get book status",
                message_ar="فشل في الحصول على حالة الكتاب",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )



