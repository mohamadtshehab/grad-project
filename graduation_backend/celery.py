"""
Celery configuration for the graduation_backend project with enhanced graph cancellation support
"""
import os
import signal
import threading
import time
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')

# Create the Celery app
app = Celery('graduation_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Explicitly import task modules to ensure they're registered
app.autodiscover_tasks(['books.tasks'])

# Enhanced configuration for graph cancellation and control
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    task_track_started=True,
    
    # Task execution limits
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Worker configuration for better control
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Enhanced cancellation support
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_always_eager=False,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        'visibility_timeout': 3600,
    },
    
    # Worker shutdown settings
    worker_shutdown_timeout=30.0,
    worker_cancel_long_running_tasks_on_connection_loss=True,
    
    # Task routing with cancellation support
    task_routes={
        'authentication.tasks.send_password_reset_email': {'queue': 'email'},
        'authentication.tasks.send_welcome_email': {'queue': 'email'},
        'books.tasks.process_book_workflow': {'queue': 'ai_processing'},
    },
    
    # Queue configuration
    task_default_queue='default',
    task_queues={
        'default': {'exchange': 'default', 'routing_key': 'default'},
        'email': {'exchange': 'email', 'routing_key': 'email'},
        'ai_processing': {'exchange': 'ai_processing', 'routing_key': 'ai_processing'},
    },
    
    # Worker pool settings for better process control
    worker_pool='prefork',  # Use prefork for better process control
    worker_concurrency=2,  # Limit concurrent tasks for better control
)

# Global cancellation registry for active graph executions
_active_graphs = {}
_graph_lock = threading.Lock()

def register_active_graph(task_id: str, graph_instance, cancellation_event):
    """Register an active graph execution for potential cancellation."""
    with _graph_lock:
        _active_graphs[task_id] = {
            'graph': graph_instance,
            'cancellation_event': cancellation_event,
            'started_at': time.time(),
            'status': 'running'
        }

def unregister_active_graph(task_id: str):
    """Unregister a completed or cancelled graph execution."""
    with _graph_lock:
        _active_graphs.pop(task_id, None)

def cancel_graph_execution(task_id: str):
    """Cancel a specific graph execution."""
    with _graph_lock:
        if task_id in _active_graphs:
            graph_info = _active_graphs[task_id]
            graph_info['cancellation_event'].set()
            graph_info['status'] = 'cancelling'
            return True
    return False

def get_active_graphs():
    """Get information about all active graph executions."""
    with _graph_lock:
        return _active_graphs.copy()

def cancel_all_graphs():
    """Cancel all active graph executions."""
    with _graph_lock:
        cancelled_count = 0
        for task_id, graph_info in _active_graphs.items():
            graph_info['cancellation_event'].set()
            graph_info['status'] = 'cancelling'
            cancelled_count += 1
        return cancelled_count

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals to gracefully stop all graph executions."""
    print(f"\nReceived signal {signum}. Shutting down gracefully...")
    
    try:
        # Cancel all active graph executions
        cancelled_count = cancel_all_graphs()
        print(f"Cancelled {cancelled_count} active graph executions")
        
        # Wait for graphs to finish cancellation (with timeout)
        timeout = 30  # 30 seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            active_count = len(get_active_graphs())
            if active_count == 0:
                break
            print(f"Waiting for {active_count} graphs to finish cancellation...")
            time.sleep(2)
        
        # Force shutdown remaining graphs
        remaining_graphs = get_active_graphs()
        if remaining_graphs:
            print(f"Force shutting down {len(remaining_graphs)} remaining graphs")
            for task_id in list(remaining_graphs.keys()):
                unregister_active_graph(task_id)
        
        print("Graceful shutdown completed.")
        
    except Exception as e:
        print(f"Error during shutdown: {e}")
    
    # Exit the process
    os._exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')

# Task cancellation utilities
@app.task(bind=True)
def cancel_task_execution(self, target_task_id: str):
    """Cancel a specific task execution."""
    try:
        # Cancel the target task
        app.control.revoke(target_task_id, terminate=True, signal='SIGTERM')
        
        # If it's a graph task, also cancel the graph execution
        if cancel_graph_execution(target_task_id):
            return {"status": "success", "message": f"Task {target_task_id} and graph execution cancelled"}
        else:
            return {"status": "success", "message": f"Task {target_task_id} cancelled"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.task(bind=True)
def get_task_status(self, task_id: str):
    """Get detailed status of a task including graph execution status."""
    try:
        # Get Celery task status
        task_result = app.AsyncResult(task_id)
        
        # Get graph execution status
        graph_info = get_active_graphs().get(task_id)
        
        return {
            "task_id": task_id,
            "celery_status": task_result.status,
            "graph_status": graph_info.get('status') if graph_info else None,
            "graph_runtime": time.time() - graph_info['started_at'] if graph_info else None,
            "is_cancellable": graph_info is not None and graph_info['status'] == 'running'
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
