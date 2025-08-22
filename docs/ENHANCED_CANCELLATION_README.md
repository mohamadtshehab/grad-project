# Enhanced Graph Cancellation System

This document explains the enhanced cancellation system implemented for the graduation project, which provides reliable control over LangSmith graph executions running through Celery.

## Problem Solved

Previously, stopping the Daphne server or Celery workers would not reliably stop running LangSmith graph executions because:

1. **Graph processes run independently** - LangGraph can spawn separate processes that aren't immediately terminated
2. **Redis-only shutdown is insufficient** - Stopping the message broker doesn't stop running graph executions
3. **Loss of control** - No way to gracefully cancel long-running graph operations

## Solution Overview

The enhanced system implements:

1. **Thread-based graph execution** with cancellation events
2. **Global graph registry** for tracking active executions
3. **Signal handlers** for graceful shutdown
4. **Management commands** for task control
5. **Enhanced Celery configuration** with better process control

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Daphne Server │    │  Celery Worker  │    │  LangSmith Graph│
│   (ASGI)        │    │  (Task Queue)   │    │  (Execution)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Signal Handlers │    │ Graph Registry  │    │ Cancellation    │
│ (Ctrl+C, SIGTERM)│   │ (Active Graphs) │    │ Events          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Graceful Shutdown     │
                    │   (Timeout + Force)      │
                    └───────────────────────────┘
```

## Key Components

### 1. Enhanced Celery Configuration (`graduation_backend/celery.py`)

- **Graph Registry**: Tracks all active graph executions
- **Cancellation Functions**: `cancel_graph_execution()`, `cancel_all_graphs()`
- **Signal Handlers**: Graceful shutdown on Ctrl+C/SIGTERM
- **Enhanced Worker Settings**: Better process control and cancellation support

### 2. Cancellable Graph Executor (`books/tasks.py`)

- **Thread-based Execution**: Runs graphs in separate threads for cancellation control
- **Cancellation Events**: Uses threading.Event for clean cancellation
- **Graceful Termination**: Waits for threads to finish with timeout

### 3. Enhanced ASGI Configuration (`graduation_backend/asgi.py`)

- **Signal Handling**: Integrates with Celery cancellation system
- **Graceful Shutdown**: Ensures all graphs are cancelled before exit

### 4. Management Commands (`graduation_backend/management/commands/control_tasks.py`)

- **Task Control**: List, cancel, and monitor tasks and graphs
- **Graph Status**: Real-time information about active graph executions
- **Bulk Operations**: Cancel all tasks and graphs at once

## Usage

### Starting Services

#### Option 1: PowerShell Script (Recommended for Windows)
```powershell
# Run from project root directory
.\start_services.ps1
```

#### Option 2: Manual Startup
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker (with enhanced configuration)
celery -A graduation_backend worker --loglevel=info --pool=prefork --concurrency=2

# Terminal 3: Daphne Server
daphne -b 0.0.0.0 -p 8000 graduation_backend.asgi:application
```

### Controlling Tasks and Graphs

#### List Active Tasks and Graphs
```bash
python manage.py control_tasks list
```

#### Get Status of Specific Task
```bash
python manage.py control_tasks status --task-id <task-id>
```

#### Cancel Specific Task and Graph
```bash
python manage.py control_tasks cancel --task-id <task-id>
```

#### Cancel All Tasks and Graphs
```bash
python manage.py control_tasks cancel-all
```

### Graceful Shutdown

When you press `Ctrl+C` in the Daphne terminal:

1. **Signal received** by ASGI application
2. **All active graphs cancelled** via cancellation events
3. **Wait for graceful completion** (30 second timeout)
4. **Force shutdown** remaining processes if necessary
5. **Clean exit** with all resources released

## Configuration Options

### Celery Worker Settings

```python
# Enhanced worker configuration
worker_pool='prefork',           # Better process control
worker_concurrency=2,            # Limit concurrent tasks
worker_shutdown_timeout=30.0,    # Graceful shutdown timeout
worker_cancel_long_running_tasks_on_connection_loss=True
```

### Task Routing

```python
# Separate queues for different task types
task_routes={
    'books.tasks.process_book_workflow': {'queue': 'ai_processing'},
    'authentication.tasks.send_password_reset_email': {'queue': 'email'},
    'authentication.tasks.send_welcome_email': {'queue': 'email'},
}
```

### Cancellation Timeouts

```python
# Configurable timeouts for graceful shutdown
timeout = 30  # 30 seconds to wait for graph cancellation
worker_shutdown_timeout = 30.0  # Celery worker shutdown timeout
```

## Monitoring and Debugging

### Real-time Graph Status

```bash
# Check active graph executions
python manage.py control_tasks list

# Output example:
# Active Graph Executions:
#   - Task ID: abc123-def456
#     Status: running
#     Runtime: 45.2s
```

### Task Details

```bash
# Get comprehensive task information
python manage.py control_tasks status --task-id abc123-def456

# Output example:
# Celery Task Status:
#   Task ID: abc123-def456
#   Status: STARTED
#   Result: None
# 
# Graph Execution Status:
#   Status: running
#   Runtime: 45.2s
#   Cancellable: True
```

### Logs and Debugging

```bash
# Enhanced Celery worker logging
celery -A graduation_backend worker --loglevel=debug --pool=prefork

# Daphne server with verbose logging
daphne -b 0.0.0.0 -p 8000 -v 2 graduation_backend.asgi:application
```

## Troubleshooting

### Common Issues

#### 1. Graphs Not Cancelling
- **Symptom**: Graph continues running after cancellation
- **Solution**: Check if graph nodes support cancellation events
- **Debug**: Use `control_tasks status` to verify cancellation state

#### 2. Worker Shutdown Hanging
- **Symptom**: Celery worker doesn't stop on Ctrl+C
- **Solution**: Ensure `--pool=prefork` is used
- **Debug**: Check worker logs for stuck processes

#### 3. Redis Connection Issues
- **Symptom**: Tasks fail to start or cancel
- **Solution**: Verify Redis is running on port 6379
- **Debug**: Test Redis connection with `redis-cli ping`

### Debug Commands

```bash
# Check Redis connection
redis-cli ping

# Check Celery worker status
celery -A graduation_backend inspect active

# Check graph registry
python manage.py shell -c "
from graduation_backend.celery import get_active_graphs
print(get_active_graphs())
"
```

## Performance Considerations

### Worker Concurrency
- **Default**: 2 concurrent tasks
- **Adjustment**: Increase for high-throughput, decrease for better control
- **Formula**: `worker_concurrency = CPU_cores * 2`

### Cancellation Overhead
- **Minimal**: Cancellation events are lightweight
- **Timeout**: 30-second graceful shutdown timeout
- **Fallback**: Force termination for unresponsive graphs

### Memory Usage
- **Graph Registry**: Minimal memory overhead
- **Thread Management**: One thread per active graph
- **Cleanup**: Automatic cleanup on task completion

## Security Considerations

### Signal Handling
- **OS Signals**: Only SIGINT (Ctrl+C) and SIGTERM handled
- **Process Isolation**: Each graph runs in separate thread
- **Resource Cleanup**: Ensures no orphaned processes

### Task Isolation
- **Queue Separation**: Different task types use separate queues
- **Worker Isolation**: Prefork pool provides process isolation
- **Cancellation Scope**: Only affects registered graph executions

## Future Enhancements

### Planned Features
1. **Web-based Monitoring**: Real-time graph execution dashboard
2. **Advanced Cancellation**: Node-level cancellation within graphs
3. **Metrics Collection**: Performance and cancellation statistics
4. **API Endpoints**: REST API for task control

### Extensibility
- **Custom Cancellation Logic**: Implement in graph nodes
- **Plugin System**: Add cancellation handlers for different graph types
- **Integration**: Support for other async frameworks

## Conclusion

The enhanced cancellation system provides reliable control over LangSmith graph executions while maintaining performance and stability. It addresses the core issue of losing control over running graphs and ensures clean, graceful shutdowns in all scenarios.

For questions or issues, refer to the troubleshooting section or check the Celery and Daphne logs for detailed error information.
