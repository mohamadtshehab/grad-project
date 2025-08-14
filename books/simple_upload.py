"""
Simple upload view that bypasses DRF parsers entirely
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model
import json
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def get_user_from_token(request):
    """Extract user from JWT token"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except (InvalidToken, User.DoesNotExist):
        return None


@csrf_exempt
@require_http_methods(["POST"])
def simple_upload_view(request):
    """
    Simple upload view that bypasses DRF entirely
    """
    try:
        # Check authentication
        user = get_user_from_token(request)
        if not user:
            return JsonResponse({
                "status": "error",
                "message": "Authentication required"
            }, status=401)
        
        # Log request details
        logger.info("=== SIMPLE UPLOAD DEBUG ===")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Method: {request.method}")
        logger.info(f"FILES: {list(request.FILES.keys())}")
        logger.info(f"POST: {list(request.POST.keys())}")
        
        # Check if file is present
        if 'file' not in request.FILES:
            return JsonResponse({
                "status": "error",
                "message": "No file provided",
                "debug": {
                    "files": list(request.FILES.keys()),
                    "post": list(request.POST.keys()),
                    "content_type": request.content_type
                }
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Log file details
        logger.info(f"File name: {uploaded_file.name}")
        logger.info(f"File size: {uploaded_file.size}")
        logger.info(f"File content type: {uploaded_file.content_type}")
        
        # Basic validation
        if not uploaded_file.name.lower().endswith('.epub'):
            return JsonResponse({
                "status": "error",
                "message": "Only EPUB files are allowed"
            }, status=400)
        
        return JsonResponse({
            "status": "success",
            "message": "File received successfully!",
            "data": {
                "filename": uploaded_file.name,
                "size": uploaded_file.size,
                "content_type": uploaded_file.content_type,
                "user": user.email
            }
        })
        
    except Exception as e:
        logger.error(f"Simple upload error: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Upload error: {str(e)}"
        }, status=500)
