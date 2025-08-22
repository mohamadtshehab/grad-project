"""
ASGI config for graduation_backend project with enhanced graph cancellation support.
"""

import os
import signal
import sys
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from .routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')

django_asgi_app = get_asgi_application()

def signal_handler(signum, frame):
    """Handle shutdown signals to gracefully stop all graph executions."""
    print(f"\nReceived signal {signum}. Shutting down gracefully...")
    
    try:
        # Import cancellation utilities
        from .celery import cancel_all_graphs, get_active_graphs
        
        # Cancel all active graph executions
        cancelled_count = cancel_all_graphs()
        print(f"Cancelled {cancelled_count} active graph executions")
        
        # Wait for graphs to finish cancellation (with timeout)
        import time
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
                from .celery import unregister_active_graph
                unregister_active_graph(task_id)
        
        print("Graceful shutdown completed.")
        
    except Exception as e:
        print(f"Error during shutdown: {e}")
    
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
