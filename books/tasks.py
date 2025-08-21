"""
Celery task for complete book processing workflow using AI graph with cancellation support.
"""

import threading
import time
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from utils.models import Job
from books.models import Book
from utils.websocket_events import WebSocketEvent
import logging
from ai_workflow.src.graphs.orhcestrator.graph_builders import orchestrator_graph
from ai_workflow.src.configs import GRAPH_CONFIG
from ai_workflow.src.schemas.states import create_initial_state

# Import cancellation utilities
from graduation_backend.celery import register_active_graph, unregister_active_graph

logger = logging.getLogger(__name__)

def _send_event(user_id: str, job_id: str, event: WebSocketEvent):
    """Send standardized WebSocket event to user."""
    try:
        channel_layer = get_channel_layer()
        group_name = f"user_{user_id}"
        
        # Send to user-specific group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "job_update", "job_id": job_id, **event.to_dict()}
        )
        
        # Send to test group for development
        async_to_sync(channel_layer.group_send)(
            "test_group",
            {"type": "job_update", "job_id": job_id, **event.to_dict()}
        )
        
    except Exception as e:
        logger.error(f"Failed to send standardized event to user {user_id}: {str(e)}")


def _create_progress_callback(user_id: str, job_id: str):
    """Create a standardized progress callback function for the AI workflow graph."""
    def progress_callback(event: WebSocketEvent):
        """
        Standardized callback function to send progress updates via WebSocket.
        
        Args:
            event: WebSocketEvent object with standardized structure
        """
        try:
            _send_event(user_id, job_id, event)
        except Exception as e:
            logger.error(f"Standardized progress callback error: {str(e)}")
    
    return progress_callback

class CancellableGraphExecutor:
    """Wrapper for graph execution with cancellation support."""
    
    def __init__(self, graph, initial_state, config):
        self.graph = graph
        self.initial_state = initial_state
        self.config = config
        self.cancellation_event = threading.Event()
        self.execution_thread = None
        self.result = None
        self.error = None
        
    def execute(self):
        """Execute the graph in a separate thread with cancellation support."""
        def _execute():
            try:
                # Check for cancellation before starting
                if self.cancellation_event.is_set():
                    self.error = "Graph execution was cancelled before start"
                    return
                
                # Execute the graph with periodic cancellation checks
                self.result = self._execute_with_cancellation_checks()
                
            except Exception as e:
                self.error = str(e)
                logger.error(f"Graph execution error: {e}")
        
        self.execution_thread = threading.Thread(target=_execute)
        self.execution_thread.start()
        self.execution_thread.join()
        
        if self.cancellation_event.is_set():
            raise Exception("Graph execution was cancelled")
        
        if self.error:
            raise Exception(self.error)
        
        return self.result
    
    def _execute_with_cancellation_checks(self):
        """Execute graph with periodic cancellation checks."""
        # For LangGraph, we need to implement cancellation at the node level
        # This is a simplified approach - you may need to modify your graph nodes
        
        # Create a modified config with cancellation support
        modified_config = self.config.copy()
        modified_config['configurable'] = modified_config.get('configurable', {})
        modified_config['configurable']['cancellation_event'] = self.cancellation_event
        
        # Execute the graph
        return self.graph.invoke(self.initial_state, config=modified_config)
    
    def cancel(self):
        """Cancel the graph execution."""
        self.cancellation_event.set()
        if self.execution_thread and self.execution_thread.is_alive():
            # Wait for thread to finish (with timeout)
            self.execution_thread.join(timeout=10)
            
            # Force terminate if still running
            if self.execution_thread.is_alive():
                logger.warning("Graph execution thread did not terminate gracefully")

@shared_task(bind=True, max_retries=1, default_retry_delay=60)
def process_book_workflow(self, job_id: str, user_id: str, book_id: str):
    """
    Process uploaded book through complete AI workflow graph with cancellation support.
    
    Args:
        job_id: Job tracking ID
        user_id: User ID for notifications
        book_id: Book ID to process
    """
    graph_executor = None
    
    try:
        # Get job and book instances
        job = Job.objects.get(id=job_id)
        book = Book.objects.get(book_id=book_id)
        
        # Update job status
        job.status = Job.Status.RUNNING
        job.started_at = timezone.now()
        job.progress = 10
        job.save(update_fields=["status", "started_at", "progress", "updated_at"])
                
        progress_callback = _create_progress_callback(user_id, job_id)
        
        # Prepare initial state for the graph
        initial_state = create_initial_state(
            book_id=str(book_id), 
            progress_callback=progress_callback
        )
        
        logger.info(f"Starting AI workflow for book {book_id}")
        
        # Create cancellable graph executor
        graph_executor = CancellableGraphExecutor(
            orchestrator_graph, 
            initial_state, 
            GRAPH_CONFIG
        )
        
        # Register the graph execution for potential cancellation
        register_active_graph(self.request.id, graph_executor, graph_executor.cancellation_event)
        
        # Execute the graph
        result = graph_executor.execute()
        
        # Process the results
        if result.get('no_more_chunks', True):  # Assume success if not specified
            
            book.processing_status = 'completed'
            book.save()
            
            # Update job
            job.status = Job.Status.COMPLETED
            job.progress = 100
            job.finished_at = timezone.now()
            job.result = {
                "status": "success",
            }
            job.save(update_fields=["status", "progress", "finished_at", "result", "updated_at"])
            
            # Send final completion notification using standardized event
            from utils.websocket_events import create_analysis_complete_event
            completion_event = create_analysis_complete_event()
            _send_event(user_id, job_id, completion_event)
                    
            return {"status": "success", "job_id": job_id}
        else:
            raise Exception("Graph execution returned no result")
            
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
            
            # Notify user of failure using standardized event
            from utils.websocket_events import create_processing_error_event
            error_event = create_processing_error_event(str(exc))
            _send_event(user_id, job_id, error_event)
            
        except Exception as cleanup_exc:
            logger.error(f"Failed to cleanup after error: {str(cleanup_exc)}")
        
        # Retry if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        raise
        
    finally:
        # Always unregister the graph execution
        if graph_executor:
            unregister_active_graph(self.request.id)
