"""
Standardized WebSocket event structure for progress notifications.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Literal
from django.utils import timezone

# Event types
EventType = Literal[
    "validation_result",
    "book_extracted", 
    "preprocessing_complete",
    "chunk_ready",
    "analysis_complete",
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
