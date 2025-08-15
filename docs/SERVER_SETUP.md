# Server Setup Guide

This guide explains how to run Redis, Celery, and Daphne servers for the graduation project.

## Overview

The project uses multiple services:
- **Redis**: Message broker for Celery and WebSocket channel layer
- **Celery**: Background task processing (AI workflow, email tasks)
- **Daphne**: ASGI server for HTTP and WebSocket connections
- **Django**: Web application framework

## Prerequisites

Make sure you have the project dependencies installed:
```bash
uv sync
```

## 1. Redis Server

Redis is required for:
- Celery message broker
- Django Channels (WebSocket support)
- Caching (optional)

### Installation

#### Windows:
1. **Option A: Using Windows Subsystem for Linux (WSL)**
   ```bash
   # Install WSL if not already installed
   wsl --install
   
   # In WSL terminal:
   sudo apt update
   sudo apt install redis-server
   ```

2. **Option B: Using Docker**
   ```bash
   # Install Docker Desktop for Windows
   # Then run Redis container:
   docker run -d --name redis -p 6379:6379 redis:latest
   ```

3. **Option C: Redis for Windows (unofficial)**
   - Download from: https://github.com/tporadowski/redis/releases
   - Extract and run `redis-server.exe`

#### macOS:
```bash
# Using Homebrew
brew install redis

# Start Redis
brew services start redis
```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# CentOS/RHEL
sudo yum install redis
```

### Running Redis

#### Start Redis Server:
```bash
# Default start (port 6379)
redis-server

# With custom configuration
redis-server /path/to/redis.conf

# Using Docker
docker run -d --name redis -p 6379:6379 redis:latest
```

#### Verify Redis is Running:
```bash
# Test connection
redis-cli ping
# Should return: PONG

# Check status
redis-cli info server
```

#### Stop Redis:
```bash
# Graceful shutdown
redis-cli shutdown

# Using Docker
docker stop redis
```

## 2. Celery Workers

Celery handles background tasks like:
- AI workflow character extraction
- Email sending
- File processing

### Starting Celery Worker

#### Development (Single Worker):
```bash
# Navigate to project root
cd C:\Programming\Python\Django\grad-project

# Start Celery worker
uv run celery -A graduation_backend worker --loglevel=info

# For Windows, add --pool=solo
uv run celery -A graduation_backend worker --loglevel=info --pool=solo
```

#### Production (Multiple Workers):
```bash
# Start multiple workers
uv run celery -A graduation_backend worker --loglevel=info --concurrency=4

# Start worker with specific queues
uv run celery -A graduation_backend worker --loglevel=info --queues=ai_workflow,email
```

#### Monitor Celery Tasks:
```bash
# Start Celery monitoring tool
uv run celery -A graduation_backend flower

# Access web interface at: http://localhost:5555
```

### Celery Beat (Scheduled Tasks)

If you have periodic tasks:
```bash
# Start Celery beat scheduler
uv run celery -A graduation_backend beat --loglevel=info
```

### Useful Celery Commands

```bash
# Check active tasks
uv run celery -A graduation_backend inspect active

# Check registered tasks
uv run celery -A graduation_backend inspect registered

# Purge all tasks
uv run celery -A graduation_backend purge

# Check worker statistics
uv run celery -A graduation_backend inspect stats
```

## 3. Daphne Server

Daphne is the ASGI server that handles both HTTP and WebSocket connections.

### Starting Daphne

#### Development:
```bash
# Navigate to project root
cd C:\Programming\Python\Django\grad-project

# Start Daphne server
uv run daphne -b 0.0.0.0 -p 8000 graduation_backend.asgi:application

# With verbose logging
uv run daphne -b 0.0.0.0 -p 8000 -v 2 graduation_backend.asgi:application
```

#### Production:
```bash
# With access logs and better configuration
uv run daphne -b 0.0.0.0 -p 8000 \
  --access-log /var/log/daphne/access.log \
  --application-close-timeout 60 \
  --proxy-headers \
  graduation_backend.asgi:application
```

#### Custom Port:
```bash
# Run on different port
uv run daphne -b 0.0.0.0 -p 8080 graduation_backend.asgi:application
```

### Daphne Configuration Options

```bash
# Common options:
-b, --bind          # Bind address (default: 127.0.0.1)
-p, --port          # Port number (default: 8000)
-v, --verbosity     # Verbosity level (0-3)
--access-log        # Access log file path
--proxy-headers     # Enable proxy header parsing
--root-path         # Root path for the application
```

## 4. Complete Startup Sequence

### For Development:

1. **Terminal 1 - Redis:**
   ```bash
   # Start Redis
   redis-server
   ```

2. **Terminal 2 - Celery Worker:**
   ```bash
   cd C:\Programming\Python\Django\grad-project
   uv run celery -A graduation_backend worker --loglevel=info --pool=solo
   ```

3. **Terminal 3 - Daphne Server:**
   ```bash
   cd C:\Programming\Python\Django\grad-project
   uv run daphne -b 0.0.0.0 -p 8000 graduation_backend.asgi:application
   ```

4. **Optional Terminal 4 - Celery Monitoring:**
   ```bash
   cd C:\Programming\Python\Django\grad-project
   uv run celery -A graduation_backend flower
   ```

### For Production:

Create systemd services or use process managers like supervisord:

#### Example systemd service for Celery:
```ini
# /etc/systemd/system/celery.service
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
EnvironmentFile=/path/to/your/.env
WorkingDirectory=/path/to/grad-project
ExecStart=/path/to/venv/bin/celery -A graduation_backend worker --loglevel=info --detach
ExecStop=/path/to/venv/bin/celery -A graduation_backend control shutdown
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
Restart=always

[Install]
WantedBy=multi-user.target
```

## 5. Environment Variables

Create a `.env` file in your project root:
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3

# AI Workflow Settings
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
```

## 6. Testing the Setup

### Test Redis Connection:
```bash
uv run python manage.py shell -c "
from django.core.cache import cache
cache.set('test', 'hello')
print(cache.get('test'))
"
```

### Test Celery Tasks:
```bash
uv run python manage.py shell -c "
from books.tasks import extract_characters_from_book
result = extract_characters_from_book.delay('job-id', 'user-id', 'book-id')
print(f'Task ID: {result.id}')
"
```

### Test WebSocket Connection:
```javascript
// In browser console at http://localhost:8000
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');
ws.onopen = () => console.log('WebSocket connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
```

### Test AI Workflow:
```bash
# Get a book ID from your database
uv run python manage.py shell -c "
from books.models import Book
book = Book.objects.first()
print(f'Test with book ID: {book.book_id}')
"

# Test the AI workflow
uv run python ai_workflow/src/main.py --book-id <book-id-from-above>
```

## 7. Troubleshooting

### Common Issues:

#### Redis Connection Error:
```
redis.exceptions.ConnectionError: Error connecting to Redis
```
**Solution**: Make sure Redis is running on port 6379

#### Celery Import Error:
```
ModuleNotFoundError: No module named 'graduation_backend'
```
**Solution**: Make sure you're in the project root directory

#### Daphne Port Already in Use:
```
OSError: [Errno 98] Address already in use
```
**Solution**: Use a different port or kill the process using the port

#### WebSocket Connection Failed:
**Solution**: Check that Daphne is running and CHANNEL_LAYERS is configured in settings.py

### Logs and Debugging:

```bash
# Check Redis logs
redis-cli monitor

# Check Celery worker logs
uv run celery -A graduation_backend worker --loglevel=debug

# Check Daphne logs
uv run daphne -v 3 graduation_backend.asgi:application

# Check Django logs
tail -f /path/to/django.log
```

## 8. Production Deployment

For production deployment, consider:

1. **Use a process manager** (systemd, supervisord, or Docker)
2. **Configure proper logging** with log rotation
3. **Set up monitoring** (Flower for Celery, Prometheus/Grafana)
4. **Use a reverse proxy** (Nginx) in front of Daphne
5. **Configure Redis persistence** and security
6. **Set up SSL/TLS** for WebSocket connections
7. **Use environment-specific settings** (production.py)

### Example Docker Compose:
```yaml
version: '3.8'
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
  
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    command: daphne -b 0.0.0.0 -p 8000 graduation_backend.asgi:application
  
  celery:
    build: .
    depends_on:
      - redis
    command: celery -A graduation_backend worker --loglevel=info
```

This setup provides a robust foundation for running your Django application with real-time features and background task processing!
