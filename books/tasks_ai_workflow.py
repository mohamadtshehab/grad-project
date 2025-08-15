"""
Celery tasks for AI workflow integration with books.
"""

from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from utils.models import Job
from books.models import Book
from ai_workflow.src.django_integration import (
    process_book_with_ai_workflow,
    process_text_chunks_with_ai_workflow,
    get_character_relationships_for_book
)
import logging

logger = logging.getLogger(__name__)


def _notify_user(user_id: str, payload: dict):
    """Send notification to user via WebSocket."""
    try:
        channel_layer = get_channel_layer()
        group_name = f"user_{user_id}"
        
        # Send to user-specific group
        async_to_sync(channel_layer.group_send)(
            group_name, 
            {"type": "job.update", **payload}
        )
        
        # Also send to test group for debugging
        async_to_sync(channel_layer.group_send)(
            "test_group", 
            {"type": "job.update", **payload}
        )
        
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {str(e)}")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def extract_characters_from_book(
    self, 
    job_id: str, 
    user_id: str, 
    book_id: str,
    clear_existing: bool = False
):
    """
    Background task: extract characters from uploaded book using AI workflow.
    
    Args:
        job_id: Job tracking ID
        user_id: User ID for notifications
        book_id: Book ID to process
        clear_existing: Whether to clear existing characters
    """
    try:
        # Get job and book instances
        job = Job.objects.get(id=job_id)
        book = Book.objects.get(book_id=book_id)
        
        # Update job status
        job.status = Job.Status.RUNNING
        job.started_at = timezone.now()
        job.progress = 10
        job.save(update_fields=["status", "started_at", "progress", "updated_at"])
        
        # Notify user of start
        _notify_user(user_id, {
            "event": "character_extraction_started",
            "job_id": job_id,
            "status": "running",
            "progress": 10,
            "message": f"بدأ استخراج الشخصيات من {book.title}"
        })
        
        # Process book with AI workflow
        logger.info(f"Starting character extraction for book {book_id}")
        
        # Update progress periodically (this would ideally be done inside the workflow)
        job.progress = 30
        job.save(update_fields=["progress", "updated_at"])
        _notify_user(user_id, {
            "event": "character_extraction_progress",
            "job_id": job_id,
            "progress": 30,
            "message": "تحليل النص..."
        })
        
        # Run the AI workflow (file path is automatically retrieved from book.file)
        result = process_book_with_ai_workflow(
            book=book,
            clear_existing=clear_existing
        )
        
        # Check if processing was successful
        if result['processing_status'] == 'completed':
            # Prepare success result
            job_result = {
                "book_id": result['book_id'],
                "book_title": result['book_title'],
                "total_characters": result['total_characters'],
                "characters": result['characters_extracted'],
                "is_arabic": result.get('is_arabic', False),
                "text_quality": result.get('text_quality_assessment'),
                "text_classification": result.get('text_classification')
            }
            
            # Update job as completed
            job.result = job_result
            job.status = Job.Status.COMPLETED
            job.progress = 100
            job.finished_at = timezone.now()
            job.save(update_fields=["result", "status", "progress", "finished_at", "updated_at"])
            
            # Notify user of completion
            _notify_user(user_id, {
                "event": "character_extraction_completed",
                "job_id": job_id,
                "status": "completed",
                "result": job_result,
                "message": f"تم استخراج {result['total_characters']} شخصية بنجاح"
            })
            
            logger.info(f"Successfully extracted {result['total_characters']} characters from book {book_id}")
            
            return {"status": "success", "job_id": job_id, "characters_count": result['total_characters']}
            
        else:
            # Processing failed
            raise Exception(result.get('error', 'Unknown error during processing'))
            
    except Exception as exc:
        logger.error(f"Failed to extract characters from book {book_id}: {str(exc)}")
        
        try:
            job = Job.objects.get(id=job_id)
            job.status = Job.Status.FAILED
            job.error = str(exc)
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at", "updated_at"])
            
            _notify_user(user_id, {
                "event": "character_extraction_failed",
                "job_id": job_id,
                "status": "failed",
                "error": str(exc),
                "message": f"فشل استخراج الشخصيات: {str(exc)}"
            })
        except Exception:
            pass
        
        # Retry if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        raise


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def analyze_character_relationships(
    self,
    job_id: str,
    user_id: str,
    book_id: str
):
    """
    Background task: analyze relationships between characters in a book.
    
    Args:
        job_id: Job tracking ID
        user_id: User ID for notifications
        book_id: Book ID to analyze
    """
    try:
        # Get job and book instances
        job = Job.objects.get(id=job_id)
        book = Book.objects.get(book_id=book_id)
        
        # Update job status
        job.status = Job.Status.RUNNING
        job.started_at = timezone.now()
        job.progress = 10
        job.save(update_fields=["status", "started_at", "progress", "updated_at"])
        
        # Notify user of start
        _notify_user(user_id, {
            "event": "relationship_analysis_started",
            "job_id": job_id,
            "status": "running",
            "progress": 10,
            "message": f"بدأ تحليل العلاقات بين الشخصيات في {book.title}"
        })
        
        # Get character relationships
        logger.info(f"Analyzing character relationships for book {book_id}")
        relationships = get_character_relationships_for_book(book)
        
        # Prepare result
        job_result = {
            "book_id": str(book.book_id),
            "book_title": book.title,
            "total_relationships": len(relationships),
            "relationships": relationships
        }
        
        # Update job as completed
        job.result = job_result
        job.status = Job.Status.COMPLETED
        job.progress = 100
        job.finished_at = timezone.now()
        job.save(update_fields=["result", "status", "progress", "finished_at", "updated_at"])
        
        # Notify user of completion
        _notify_user(user_id, {
            "event": "relationship_analysis_completed",
            "job_id": job_id,
            "status": "completed",
            "result": job_result,
            "message": f"تم تحليل {len(relationships)} علاقة بين الشخصيات"
        })
        
        logger.info(f"Successfully analyzed {len(relationships)} relationships for book {book_id}")
        
        return {"status": "success", "job_id": job_id, "relationships_count": len(relationships)}
        
    except Exception as exc:
        logger.error(f"Failed to analyze relationships for book {book_id}: {str(exc)}")
        
        try:
            job = Job.objects.get(id=job_id)
            job.status = Job.Status.FAILED
            job.error = str(exc)
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at", "updated_at"])
            
            _notify_user(user_id, {
                "event": "relationship_analysis_failed",
                "job_id": job_id,
                "status": "failed",
                "error": str(exc),
                "message": f"فشل تحليل العلاقات: {str(exc)}"
            })
        except Exception:
            pass
        
        # Retry if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        raise
