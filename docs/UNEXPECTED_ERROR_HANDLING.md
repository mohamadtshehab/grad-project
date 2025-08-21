# Unexpected Error Handling

## Overview

Simple system for handling unexpected errors in AI workflow nodes while keeping workflows running.

## Rules

1. **Server-side logging**: Full error details logged for debugging
2. **Client communication**: Simple, user-friendly message in Arabic
3. **Workflow continues**: Unless it's a truly critical issue (TBD)
4. **No stopping**: Unexpected errors don't stop the workflow

## Usage Pattern

```python
from utils.websocket_events import create_unexpected_error_event
import logging

logger = logging.getLogger(__name__)

def your_workflow_node(state: State):
    try:
        # Your existing logic here
        result = some_operation()
        return {'result': result}
        
    except Exception as e:
        # Log full error server-side for debugging
        logger.error(f"Unexpected error in your_workflow_node: {str(e)}")
        
        # Send simple event to client
        if 'progress_callback' in state:
            error_event = create_unexpected_error_event(
                error_message="فشل في معالجة هذه المرحلة"  # User-friendly Arabic message
            )
            state['progress_callback'](error_event)
        
        # Continue workflow with fallback value
        return {'result': 'fallback_value', 'operation_failed': True}
```

## Client Receives

```json
{
  "event_type": "unexpected_error",
  "status": "error", 
  "data": {
    "error_code": "UNEXPECTED_ERROR",
    "message": "حدث خطأ غير متوقع",
    "details": "فشل في معالجة هذه المرحلة",
    "user_action": "يرجى المحاولة مرة أخرى أو التواصل مع الدعم"
  }
}
```

## Example Implementation

See `ai_workflow/src/graphs/subgraphs/validator/nodes/regular_nodes.py` - `language_checker()` function for a complete example.

## When NOT to Use

- **Validation errors**: Use specific validation error events
- **Expected failures**: Handle with appropriate error types
- **Critical errors**: Use when you identify truly workflow-stopping issues (future)
