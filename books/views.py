from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.conf import settings
import os
import mimetypes
import logging

from .models import Book
from .serializers import (
    BookListSerializer, BookDetailSerializer, 
    BookUploadSerializer, BookStatusSerializer
)
from utils.models import Job
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

logger = logging.getLogger(__name__)





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
                
                # Log successful upload
                logger.info(f"Book uploaded successfully: {book.book_id} by user {request.user.id}")
                
                # Create a Job for novel name extraction and enqueue task
                with transaction.atomic():
                    job = Job.objects.create(
                        user=request.user,
                        job_type="novel_name_extract",
                        status=Job.Status.PENDING,
                        progress=0,
                    )

                    # Enqueue Celery task
                    try:
                        from books.tasks import extract_novel_name
                        extract_novel_name.delay(
                            job_id=str(job.id),
                            user_id=str(request.user.id),
                            book_id=str(book.book_id),
                            filename=book.file.name.split('/')[-1],
                        )
                    except Exception as e:
                        logger.error(f"Failed to enqueue extract_novel_name for book {book.book_id}: {e}")
                        job.status = Job.Status.FAILED
                        job.error = str(e)
                        job.finished_at = timezone.now()
                        job.save(update_fields=["status", "error", "finished_at", "updated_at"])
                        return Response({
                            "status": "error",
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
            logger.error(f"Error uploading book for user {request.user.id}: {str(e)}")
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
            logger.error(f"Error retrieving books for user {request.user.id}: {str(e)}")
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
            logger.error(f"Error getting book details for user {request.user.id}: {str(e)}")
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
            
            # Log deletion
            logger.info(f"Book soft deleted: {book.book_id} by user {request.user.id}")
            
            return Response({
                "status": "success",
                "en": "Book deleted successfully",
                "ar": "تم حذف الكتاب بنجاح",
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting book for user {request.user.id}: {str(e)}")
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
            
            # Log download
            logger.info(f"Book downloaded: {book.book_id} by user {request.user.id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error downloading book for user {request.user.id}: {str(e)}")
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
            logger.error(f"Error getting book status for user {request.user.id}: {str(e)}")
            return Response({
                "status": "error",
                "en": "Failed to get book status",
                "ar": "فشل في الحصول على حالة الكتاب",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



