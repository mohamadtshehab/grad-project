"""
Celery tasks for authentication-related operations
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
import logging

User = get_user_model()
def _notify_user(user_id: str, payload: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {"type": "job.update", **payload},
    )



@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id, reset_code, user_email, user_name):
    """
    Send password reset email asynchronously
    
    Args:
        user_id: User ID for logging purposes
        reset_code: The 6-digit reset code
        user_email: User's email address
        user_name: User's name for personalization
    """
    try:
        
        # Email subject
        subject = "Password Reset Code - Your Account"
        
        # HTML email template
        html_message = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .code-container {{
                    background-color: #ffffff;
                    border: 2px solid #4CAF50;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                    border-radius: 8px;
                }}
                .reset-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4CAF50;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{user_name}</strong>,</p>
                
                <p>You have requested to reset your password. Please use the following code to complete the process:</p>
                
                <div class="code-container">
                    <div class="reset-code">{reset_code}</div>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important:</strong>
                    <ul>
                        <li>This code will expire in <strong>1 hour</strong></li>
                        <li>This code can only be used <strong>once</strong></li>
                        <li>Do not share this code with anyone</li>
                    </ul>
                </div>
                
                <p>If you didn't request this password reset, please ignore this email and your password will remain unchanged.</p>
                
                <p>For security reasons, this code will automatically expire after 1 hour.</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>Your App Security Team</p>
                <p><em>This is an automated message, please do not reply to this email.</em></p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Password Reset Request
        
        Hello {user_name},
        
        You have requested to reset your password. Please use the following code to complete the process:
        
        Reset Code: {reset_code}
        
        IMPORTANT:
        - This code will expire in 1 hour
        - This code can only be used once
        - Do not share this code with anyone
        
        If you didn't request this password reset, please ignore this email and your password will remain unchanged.
        
        For security reasons, this code will automatically expire after 1 hour.
        
        Best regards,
        Your App Security Team
        
        This is an automated message, please do not reply to this email.
        """
        
        # Send the email
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        return {
            'status': 'success',
            'message': f'Password reset email sent to {user_email}',
            'user_id': user_id
        }
        
    except Exception as exc:
        
        # Retry the task if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
        
        # If we've exceeded max retries, log the failure
        return {
            'status': 'failed',
            'message': f'Failed to send email to {user_email} after retries',
            'error': str(exc),
            'user_id': user_id
        }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id, user_email, user_name):
    """
    Send welcome email to new users
    
    Args:
        user_id: User ID for logging purposes
        user_email: User's email address
        user_name: User's name for personalization
    """
    try:
        
        subject = "Welcome to Our Platform!"
        
        html_message = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2196F3;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 Welcome to Our Platform!</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{user_name}</strong>,</p>
                
                <p>Welcome to our platform! We're excited to have you on board.</p>
                
                <p>Your account has been successfully created and you can now:</p>
                <ul>
                    <li>📚 Upload and manage your EPUB books</li>
                    <li>🔍 Process and analyze your content</li>
                    <li>📊 Track your reading progress</li>
                </ul>
                
                <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                
                <p>Happy reading!</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>The Platform Team</p>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        Welcome to Our Platform!
        
        Hello {user_name},
        
        Welcome to our platform! We're excited to have you on board.
        
        Your account has been successfully created and you can now:
        - Upload and manage your EPUB books
        - Process and analyze your content
        - Track your reading progress
        
        If you have any questions or need assistance, please don't hesitate to contact our support team.
        
        Happy reading!
        
        Best regards,
        The Platform Team
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        return {
            'status': 'success',
            'message': f'Welcome email sent to {user_email}',
            'user_id': user_id
        }
        
    except Exception as exc:
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        return {
            'status': 'failed',
            'message': f'Failed to send welcome email to {user_email} after retries',
            'error': str(exc),
            'user_id': user_id
        }
