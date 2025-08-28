"""
Celery task for complete book processing workflow using AI graph with cancellation support.
"""

from celery import shared_task
from django.utils import timezone
from utils.models import Job
from books.models import Book
from utils.websocket_events import (
    create_workflow_resumes_event,
    create_analysis_complete_event, 
    create_processing_error_event,
    progress_callback
)
import logging
from ai_workflow.src.graphs.orhcestrator.graph_builders import orchestrator_graph
from ai_workflow.src.configs import GRAPH_RECURSION_LIMIT
from ai_workflow.src.schemas.states import create_initial_state
from typing import Dict, Any, Optional, Tuple
import uuid

logger = logging.getLogger(__name__)

def _initialize_job_run(job_id: str) -> Job:
    """Fetches the job and updates its status to RUNNING."""
    job = Job.objects.get(id=job_id)
    if job.status != Job.Status.RUNNING:
        job.status = Job.Status.RUNNING
        job.started_at = job.started_at or timezone.now()
        job.save(update_fields=["status", "started_at", "updated_at"])
    return job

def _configure_graph_execution(
    job: Job,
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Configures the graph by managing the thread_id and preparing the initial state.
    Returns the config dictionary and the initial state (or None for resumed runs).
    """
    thread_id = job.langgraph_thread_id
    initial_state = None
    if not thread_id:  # This is the first run
        logger.info(f"Configuring new AI workflow for job {job.id}")
        thread_id = str(uuid.uuid4())
        job.langgraph_thread_id = thread_id
        job.save(update_fields=["langgraph_thread_id"])
        initial_state = create_initial_state(
            book_id=str(job.book),
            job_id=str(job.id),
            from_http=False
        )
    else:  # This is a resumed run
        logger.info(f"Configuring resumed AI workflow for job {job.id} with thread_id {thread_id}")
        resume_event = create_workflow_resumes_event()
        progress_callback(job_id=str(job.id), event=resume_event)
        logger.info(f"Job {job.id} resumed successfully.")
    
    config = {
        'configurable': {
            'thread_id': str(thread_id)
        },
        'recursion_limit': GRAPH_RECURSION_LIMIT
    }

    return config, initial_state


def _handle_successful_completion(job: Job):
    """Handles the final steps after a graph completes successfully."""
    
    book = Book.objects.get(id=job.book)
    book.processing_status = 'completed'
    book.save()
    
    job.status = Job.Status.COMPLETED
    job.progress = 100
    job.finished_at = timezone.now()
    job.result = {"status": "success"}  # type: ignore
    job.save(update_fields=["status", "progress", "finished_at", "result", "updated_at"])
    
    completion_event = create_analysis_complete_event()
    progress_callback(job_id=str(job.id), event=completion_event)
    logger.info(f"Job {job.id} completed successfully.")
    

def _handle_workflow_failure(exc: Exception, job: Job):
    """Handles the cleanup and notification process when a workflow fails."""
    logger.error(f"Workflow processing failed for job {job.id}: {str(exc)}")
    try:
        job.status = Job.Status.FAILED
        job.error = str(exc)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error", "finished_at", "updated_at"])
        book = Book.objects.get(id=job.book)
        book.processing_status = 'failed'
        book.processing_error = str(exc)
        book.save()
        
        error_event = create_processing_error_event(str(exc))
        progress_callback(job_id=str(job.id), event=error_event)
    except Exception as cleanup_exc:
        logger.error(f"Failed to cleanup after error for job {job.id}: {str(cleanup_exc)}")


@shared_task(bind=True, max_retries=1, default_retry_delay=60)
def process_book_workflow(self, job_id: str):
    """
    Orchestrates the book processing workflow using modular helper functions.
    """
    job = None
    try:
        # Step 1: Initialize the job run
        job = _initialize_job_run(job_id)
        # Step 2: Configure the graph for a new or resumed run
        config, initial_state = _configure_graph_execution(job)

        # Step 3: Invoke the graph
        orchestrator_graph.invoke(initial_state, config=config) #type: ignore
        
        # Step 4: Check the result
        final_snapshot = orchestrator_graph.get_state(config=config) #type: ignore

        if not final_snapshot.next:
            # Handle successful completion
            _handle_successful_completion(job)
            return {"status": "success", "job_id": job_id}
        else:
            # Handle paused state
            logger.info(f"Job {job_id} paused. Next step would be: {final_snapshot.next}")
            return {"status": "paused", "job_id": job_id}
            
    except Exception as exc:
        if job:
            _handle_workflow_failure(exc, job)
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        raise
    

