from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the error response format
        if isinstance(response.data, dict):
            # If it's already a dict, ensure it has the right structure
            if 'detail' not in response.data:
                response.data = {'detail': str(exc)}
        else:
            # If it's not a dict, convert it to our standard format
            response.data = {'detail': str(response.data)}
    
    return response
