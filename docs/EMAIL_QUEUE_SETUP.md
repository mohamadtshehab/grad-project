# Email Queue Setup with Celery

## Overview
The email system has been upgraded to use Celery for asynchronous email processing. This improves performance and reliability by queuing email tasks instead of sending them synchronously during API requests.

## Features Implemented

### 1. **Asynchronous Email Tasks** ✅
- Password reset emails are now queued and processed in background
- Welcome emails sent to new users asynchronously
- Improved API response times (no waiting for email delivery)

### 2. **Professional Email Templates** ✅
- Beautiful HTML email templates with proper styling
- Plain text fallback for all emails
- Responsive design that works on all email clients
- Bilingual support (English/Arabic)

### 3. **Retry Logic & Error Handling** ✅
- Automatic retry on email sending failures (max 3 retries)
- Exponential backoff for retry attempts
- Comprehensive error logging
- Graceful degradation (app continues working if email fails)

### 4. **Task Monitoring** ✅
- Task IDs returned in API responses for tracking
- Detailed logging for debugging
- Management command for testing email tasks

## Email Types

### Password Reset Email
- **Trigger**: When user requests password reset
- **Content**: 6-digit reset code with 1-hour expiration
- **Template**: Professional HTML with security warnings
- **Queue**: `email` queue with retry logic

### Welcome Email
- **Trigger**: When new user registers
- **Content**: Welcome message with platform features
- **Template**: Branded HTML with feature highlights
- **Queue**: `email` queue (non-blocking registration)

## Setup Instructions

### 1. **Redis Setup** (Required for Celery)
```bash
# Install Redis (if not already installed)
# Windows: Download from https://redis.io/download
# Linux: sudo apt-get install redis-server
# macOS: brew install redis

# Start Redis server
redis-server
```

### 2. **Start Celery Worker**
```bash
# In your project directory, activate virtual environment
# Then start the Celery worker
celery -A graduation_backend worker --loglevel=info

# For development, you can also use:
celery -A graduation_backend worker --loglevel=debug --concurrency=1
```

### 3. **Optional: Start Celery Flower (Web Monitoring)**
```bash
# Install flower if not already installed
pip install flower

# Start flower for task monitoring
celery -A graduation_backend flower

# Access at http://localhost:5555
```

## Configuration

### Celery Settings (Already Configured)
```python
# graduation_backend/settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Dubai'
```

### Email Settings (Update with your SMTP details)
```python
# graduation_backend/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'  # Update with your SMTP host
EMAIL_HOST_USER = 'your-smtp-user'       # Update with your credentials
EMAIL_HOST_PASSWORD = 'your-smtp-password'
EMAIL_PORT = '2525'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

## Testing

### 1. **Test Email Tasks**
```bash
# Test both welcome and reset emails
python manage.py test_email_tasks --email test@example.com --task both

# Test only password reset email
python manage.py test_email_tasks --email test@example.com --task reset

# Test only welcome email
python manage.py test_email_tasks --email test@example.com --task welcome
```

### 2. **Test via API**
```bash
# Register a new user (triggers welcome email)
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "testpass123", "password_confirm": "testpass123"}'

# Request password reset (triggers reset email)
curl -X POST http://localhost:8000/api/auth/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## API Changes

### Password Reset Request Response
```json
{
    "status": "success",
    "en": "Password reset code is being sent to your email",
    "ar": "يتم إرسال رمز إعادة تعيين كلمة المرور إلى بريدك الإلكتروني",
    "message": "A 6-digit code is being sent to user@example.com",
    "task_id": "abc123-def456-ghi789"
}
```

Note the change from "sent" to "is being sent" to reflect the asynchronous nature.

## Monitoring & Debugging

### 1. **Check Celery Worker Status**
```bash
# Check if worker is running
celery -A graduation_backend inspect active

# Check registered tasks
celery -A graduation_backend inspect registered

# Check task statistics
celery -A graduation_backend inspect stats
```

### 2. **Monitor Task Execution**
```bash
# Watch worker logs
celery -A graduation_backend worker --loglevel=info

# Use Flower web interface
celery -A graduation_backend flower
# Then visit http://localhost:5555
```

### 3. **Django Logs**
Check Django logs for task queuing information:
```python
# Look for log messages like:
# "Password reset email queued for user@example.com, task ID: abc123"
# "Welcome email queued for user@example.com, task ID: def456"
```

## Production Deployment

### 1. **Supervisor Configuration**
Create `/etc/supervisor/conf.d/celery.conf`:
```ini
[program:celery]
command=/path/to/venv/bin/celery -A graduation_backend worker --loglevel=info
directory=/path/to/project
user=your-user
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
killasgroup=true
priority=998
```

### 2. **Systemd Service**
Create `/etc/systemd/system/celery.service`:
```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=your-user
Group=your-group
EnvironmentFile=/path/to/project/.env
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A graduation_backend worker --loglevel=info --detach
ExecStop=/path/to/venv/bin/celery -A graduation_backend control shutdown
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

## Benefits

### 1. **Performance**
- API responses are now faster (no waiting for email delivery)
- Non-blocking user registration and password reset
- Better user experience with immediate feedback

### 2. **Reliability**
- Automatic retry on email failures
- Emails won't be lost if SMTP server is temporarily down
- Graceful error handling doesn't break user flows

### 3. **Scalability**
- Can handle high email volumes
- Easy to add more email workers
- Queue-based processing prevents email bottlenecks

### 4. **Monitoring**
- Task tracking with unique IDs
- Comprehensive logging
- Web-based monitoring with Flower

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis server is running
   - Check Redis connection settings

2. **Tasks Not Processing**
   - Verify Celery worker is running
   - Check worker logs for errors
   - Ensure task modules are properly imported

3. **Email Not Sending**
   - Verify SMTP settings in Django settings
   - Check email task logs for specific errors
   - Test SMTP connection manually

4. **Task Stuck in Queue**
   - Check worker capacity and health
   - Look for task execution errors
   - Consider restarting Celery worker

This email queuing system provides a robust, scalable foundation for all email communications in your application! 🚀
