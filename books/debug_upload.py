"""
Debug script to help troubleshoot EPUB upload issues.
This can be used to test the upload endpoint and see what's being sent.
"""

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .parsers import FlexibleMultiPartParser
import logging

logger = logging.getLogger(__name__)

class DebugUploadView(APIView):
    """
    Debug view to help troubleshoot upload issues
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [FlexibleMultiPartParser, FormParser]
    
    def post(self, request):
        """Debug upload request"""
        try:
            # Log request details
            logger.info("=== DEBUG UPLOAD REQUEST ===")
            logger.info(f"Content-Type: {request.content_type}")
            logger.info(f"META: {request.META.get('CONTENT_TYPE', 'Not set')}")
            logger.info(f"Files: {list(request.FILES.keys())}")
            logger.info(f"Data: {list(request.data.keys())}")
            
            # Check if file is present
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                logger.info(f"File name: {uploaded_file.name}")
                logger.info(f"File size: {uploaded_file.size}")
                logger.info(f"File content type: {uploaded_file.content_type}")
            else:
                logger.warning("No 'file' found in request.FILES")
            
            return Response({
                "status": "success",
                "message": "Debug info logged",
                "data": {
                    "content_type": request.content_type,
                    "files": list(request.FILES.keys()),
                    "data_keys": list(request.data.keys()),
                    "file_info": {
                        "name": request.FILES['file'].name if 'file' in request.FILES else None,
                        "size": request.FILES['file'].size if 'file' in request.FILES else None,
                        "content_type": request.FILES['file'].content_type if 'file' in request.FILES else None,
                    } if 'file' in request.FILES else None
                }
            })
            
        except Exception as e:
            logger.error(f"Debug upload error: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Debug error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
