"""
Standardized WebSocket event structure for progress notifications.
"""

import uuid
<<<<<<< HEAD
from datetime import datetime
from typing import Dict, Any, Optional, Literal
from django.utils import timezone
=======
from typing import Dict, Any, Optional, Literal, TYPE_CHECKING
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
from utils.models import Job

# Type checking imports
if TYPE_CHECKING:
    from channels.layers import BaseChannelLayer

# Set up logger
logger = logging.getLogger(__name__)
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96

# Event types
EventType = Literal[
    "validation_result",
    "book_extracted", 
    "preprocessing_complete",
    "chunk_ready",
    "analysis_complete",
<<<<<<< HEAD
=======
    "workflow_paused",
    "workflow_resumes",
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    "unexpected_error"
]

# Status types
StatusType = Literal["success", "error", "progress"]

# Validation stages
ValidationStage = Literal["language_check", "book_classification", "text_quality"]

# Error codes
ErrorCode = Literal[
    "LANGUAGE_NOT_SUPPORTED",
    "INVALID_GENRE", 
    "POOR_TEXT_QUALITY",
    "PROCESSING_FAILED",
    "VALIDATION_FAILED",
    "UNEXPECTED_ERROR"
]

class WebSocketEvent:
    """Standardized WebSocket event structure."""
    
    def __init__(
        self,
        event_type: EventType,
        status: StatusType,
        data: Dict[str, Any],
        event_id: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.status = status
        self.timestamp = timestamp or timezone.now().isoformat()
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for WebSocket transmission."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "status": self.status,
            "timestamp": self.timestamp,
            "data": self.data
        }
<<<<<<< HEAD
=======
    
    def send_to_user(self, user_id: str, job_id: str):
        """Send this event to a specific user via WebSocket."""
        try:
            channel_layer: Optional['BaseChannelLayer'] = get_channel_layer()
            if channel_layer:
                group_name = f"user_{user_id}"
                
                # Send to user-specific group
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {"type": "job_update", "job_id": job_id, **self.to_dict()}
                )
                
                # Send to test group for development
                async_to_sync(channel_layer.group_send)(
                    "test_group",
                    {"type": "job_update", "job_id": job_id, **self.to_dict()}
                )
            else:
                logger.error("Channel layer not available")
                
        except Exception as e:
            logger.error(f"Failed to send event to user {user_id}: {str(e)}")
    
    @staticmethod
    def create_progress_callback(user_id: str, job_id: str):
        """Create a standardized progress callback function for the AI workflow graph."""
        def progress_callback(event: 'WebSocketEvent'):
            """
            Standardized callback function to send progress updates via WebSocket.
            
            Args:
                event: WebSocketEvent object with standardized structure
            """
            try:
                event.send_to_user(user_id, job_id)
            except Exception as e:
                logger.error(f"Standardized progress callback error: {str(e)}")
        
        return progress_callback
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96


# Event factory functions
def create_validation_error_event(
    validation_stage: ValidationStage,
    error_code: ErrorCode,
    message: str,
    details: str,
    user_action: str
) -> WebSocketEvent:
    """Create a validation error event."""
    return WebSocketEvent(
        event_type="validation_result",
        status="error",
        data={
            "validation_stage": validation_stage,
            "error_code": error_code,
            "message": message,
            "details": details,
            "user_action": user_action
        }
    )


def create_validation_success_event() -> WebSocketEvent:
    """Create a validation success event."""
    return WebSocketEvent(
        event_type="validation_result",
        status="success",
        data={}
    )


def create_book_extracted_event(
    book_name: str,
    confidence: Optional[str] = None
) -> WebSocketEvent:
    """Create a book name extracted event."""
    data = {"book_name": book_name}
    if confidence:
        data["confidence"] = confidence
        
    return WebSocketEvent(
        event_type="book_extracted",
        status="success",
        data=data
    )


def create_preprocessing_complete_event(
    total_chunks: int,
    chunk_size: Optional[int] = None
) -> WebSocketEvent:
    """Create a preprocessing complete event."""
    data = {"total_chunks": total_chunks}
    if chunk_size:
        data["chunk_size"] = chunk_size
        
    return WebSocketEvent(
        event_type="preprocessing_complete",
        status="success",
        data=data
    )


def create_chunk_ready_event(chunk_number: int, chunk_id: str) -> WebSocketEvent:
    """Create a chunk ready event."""
    return WebSocketEvent(
        event_type="chunk_ready",
        status="success",
        data={"chunk_number": chunk_number, "chunk_id": chunk_id}
    )


def create_analysis_complete_event() -> WebSocketEvent:
    """Create an analysis complete event."""
    return WebSocketEvent(
        event_type="analysis_complete",
        status="success",
        data={}
    )


def create_processing_error_event(
    error_message: str,
    error_code: str = "PROCESSING_FAILED"
) -> WebSocketEvent:
    """Create a processing error event."""
    return WebSocketEvent(
        event_type="validation_result",  # Using validation_result for consistency
        status="error",
        data={
            "validation_stage": "processing",
            "error_code": error_code,
            "message": error_message,
            "details": "An error occurred during book processing",
            "user_action": "Please try uploading the book again"
        }
    )


def create_unexpected_error_event(
    error_message: str
) -> WebSocketEvent:
    """Create an unexpected error event."""
    return WebSocketEvent(
        event_type="unexpected_error",
        status="error",
        data={
            "error_code": "UNEXPECTED_ERROR",
            "message": "حدث خطأ غير متوقع",
            "details": error_message,
            "user_action": "يرجى المحاولة مرة أخرى أو التواصل مع الدعم"
        }
    )
<<<<<<< HEAD
=======


def create_workflow_paused_event(
    reason: str = 'Paused by user'
) -> WebSocketEvent:
    """Create a workflow paused event."""
        
    return WebSocketEvent(
        event_type="workflow_paused",
        status="progress",
        data={'reason': reason}
    )


def create_workflow_resumes_event(
    resumed_at: Optional[str] = None
) -> WebSocketEvent:
    """Create a workflow resumes event."""
    data = {
        "resumed_at": resumed_at or timezone.now().isoformat()
    }
        
    return WebSocketEvent(
        event_type="workflow_resumes",
        status="progress",
        data=data
    )


def _send_event(job_id: str, event: WebSocketEvent):
    """Send standardized WebSocket event to user."""
    try:
        job = Job.objects.get(id=job_id)
        user_id = job.user.id  # type: ignore
        if not user_id:
            logger.error(f"User not found for job {job_id}")
            return
        channel_layer: Optional['BaseChannelLayer'] = get_channel_layer()
        if channel_layer:
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
        else:
            logger.error("Channel layer not available")
            
    except Exception as e:
        logger.error(f"Failed to send standardized event to user {user_id}: {str(e)}")


def progress_callback(job_id: str, event: WebSocketEvent):
    """
    Standardized callback function to send progress updates via WebSocket.
    
    Args:
        event: WebSocketEvent object with standardized structure
    """
    try:
        _send_event(job_id, event)
    except Exception as e:
        logger.error(f"progress callback error: {str(e)}")


>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
