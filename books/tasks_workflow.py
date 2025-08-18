"""
Celery task for complete book processing workflow using AI graph.
"""

from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from utils.models import Job
from books.models import Book
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


def _create_progress_callback(user_id: str, job_id: str):
    """Create a progress callback function for the AI workflow graph."""
    
    # Store validation results to combine them later
    validation_results = {}
    
    def progress_callback(event_type: str, node_name: str = None, result: dict = None, message: str = None):
        """
        Callback function to send progress updates via WebSocket.
        
        Args:
            event_type: Type of event (validation_progress, name_extraction_completed, etc.)
            node_name: Name of the graph node
            result: Result data from the node
        """
        try:
            # Handle different event types
            if event_type == "validation_progress":
                # Store validation results from each node
                validation_results[node_name] = result
                
                # Send individual validation progress for debugging
                _notify_user(user_id, {
                    "event": "validation_step_completed",
                    "job_id": job_id,
                    "node": node_name,
                    "result": result
                })
                
                # Send grouped validation completed event after text_classifier (last validation node)
                if node_name == "text_classifier":
                    _notify_user(user_id, {
                        "event": "validation_completed",
                        "job_id": job_id,
                        "status": "validation_passed",
                        "results": {
                            "language": validation_results.get("language_checker", {}),
                            "quality": validation_results.get("text_quality_assessor", {}), 
                            "classification": validation_results.get("text_classifier", {})
                        }
                    })
            
            elif event_type == "name_extraction_completed":
                _notify_user(user_id, {
                    "event": "name_extraction_completed",
                    "job_id": job_id,
                    "result": result
                })
            
            elif event_type == "chunking_completed":
                _notify_user(user_id, {
                    "event": "chunking_completed", 
                    "job_id": job_id,
                    "result": result
                })
            
            elif event_type == "chunk_processed":
                _notify_user(user_id, {
                    "event": "chunk_processed",
                    "job_id": job_id,
                    "chunk_number": result.get("chunk_number"),
                    "total_chunks": result.get("total_chunks"),
                    "message": f"تم معالجة الجزء {result.get('chunk_number')} من {result.get('total_chunks')}"
                })
                
        except Exception as e:
            logger.error(f"Progress callback error: {str(e)}")
            logger.error(f"Event type: {event_type}, Node: {node_name}")
            logger.error(f"Result type: {type(result)}, Result: {result}")
    
    return progress_callback


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_book_workflow(self, job_id: str, user_id: str, book_id: str, filename: str):
    """
    Process uploaded book through complete AI workflow graph.
    
    Args:
        job_id: Job tracking ID
        user_id: User ID for notifications
        book_id: Book ID to process
        filename: Original filename for context
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
        
        # Send processing started notification
        _notify_user(user_id, {
            "event": "processing_started",
            "job_id": job_id,
            "status": "running",
            "message": f"بدأ تحليل الملف {filename}"
        })
        
        # Create progress callback for the graph
        progress_callback = _create_progress_callback(user_id, job_id)
        
        # Import and invoke the AI workflow
        from ai_workflow.src.main import invoke_workflow
        from ai_workflow.src.schemas.states import create_initial_state
        # Prepare initial state for the graph
        initial_state = create_initial_state(book_id=str(book_id), file_path=book.file.path, progress_callback=progress_callback)
        
        logger.info(f"Starting AI workflow for book {book_id}")
        
        # Run the AI workflow graph
        result = invoke_workflow(initial_state)
        
        # Process the results
        if result.get('success', True):  # Assume success if not specified
            # Filter out non-serializable objects from result before processing
            filtered_result = {}
            for key, value in result.items():
                if not hasattr(value, '__next__'):  # Skip generators and iterators
                    try:
                        # Test if it's JSON serializable
                        import json
                        json.dumps(value)
                        filtered_result[key] = value
                    except (TypeError, ValueError):
                        # Skip non-serializable objects
                        logger.debug(f"Skipping non-serializable result key: {key}")
                        continue
            
            # Update book with extracted information
            if 'book_name_result' in filtered_result:
                book.title = filtered_result['book_name_result']['suggested_title']
            
            if 'text_quality_assessment' in filtered_result:
                book.quality_score = filtered_result['text_quality_assessment'].quality_score
            
            if 'is_arabic' in filtered_result:
                book.detected_language = 'ar' if filtered_result['is_arabic'] else 'unknown'
                book.language_confidence = 1.0 if filtered_result['is_arabic'] else 0.0
            
            if 'text_classification' in filtered_result:
                book.text_classification = {
                    "is_literary": filtered_result['text_classification'].is_literary,
                    "classification": filtered_result['text_classification'].classification,
                    "confidence": filtered_result['text_classification'].confidence
                }
            
            book.processing_status = 'completed'
            book.save()
            
            # Update job
            job.status = Job.Status.COMPLETED
            job.progress = 100
            job.finished_at = timezone.now()
            job.result = {
                "status": "success",
                "book_title": book.title,
                "total_chunks": filtered_result.get('total_raw_chunks', 0)
            }
            job.save(update_fields=["status", "progress", "finished_at", "result", "updated_at"])
            
            # Send final completion notification
            _notify_user(user_id, {
                "event": "processing_completed",
                "job_id": job_id,
                "status": "success",
                "message": "تم الانتهاء من معالجة الكتاب بنجاح"
            })
            
        else:
            # Handle workflow failure
            error_message = result.get('error', 'Unknown workflow error')
            
            book.processing_status = 'failed'
            book.processing_error = error_message
            book.save()
            
            job.status = Job.Status.FAILED
            job.error = error_message
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at", "updated_at"])
            
            _notify_user(user_id, {
                "event": "processing_failed",
                "job_id": job_id,
                "error": error_message,
                "status": "failed"
            })
        
        return {"status": "success", "job_id": job_id}
        
    except Exception as exc:
        logger.error(f"Workflow processing failed for job {job_id}: {str(exc)}")
        
        try:
            # Update job status
            job = Job.objects.get(id=job_id)
            job.status = Job.Status.FAILED
            job.error = str(exc)
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at", "updated_at"])
            
            # Update book status
            book = Book.objects.get(book_id=book_id)
            book.processing_status = 'failed'
            book.processing_error = str(exc)
            book.save()
            
            # Notify user of failure
            _notify_user(user_id, {
                "event": "processing_failed",
                "job_id": job_id,
                "status": "failed",
                "error": str(exc)
            })
            
        except Exception as cleanup_exc:
            logger.error(f"Failed to cleanup after error: {str(cleanup_exc)}")
        
        # Retry if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        raise
