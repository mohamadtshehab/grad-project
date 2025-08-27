from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional, Union
from django.utils.translation import gettext as _


class StandardResponse:
    """
    Utility class for creating standardized API responses.
    Maintains consistency across all API endpoints while preserving Arabic messages.
    """
    
    @staticmethod
    def success(
        message_en: str,
        message_ar: str,
        data: Any = None,
        status_code: int = status.HTTP_200_OK,
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Create a standardized success response.
        
        Args:
            message_en: English success message
            message_ar: Arabic success message
            data: Response data (optional)
            status_code: HTTP status code (default: 200)
            extra_fields: Additional fields to include in response (e.g., job_id)
            
        Returns:
            Response object with standardized success format
        """
        response_data = {
            "status": "success",
            "en": message_en,
            "ar": message_ar,
        }
        
        if data is not None:
            response_data["data"] = data
            
        # Add any extra fields (like job_id, etc.)
        if extra_fields:
            response_data.update(extra_fields)
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def accepted(
        message_en: str,
        message_ar: str,
        data: Any = None,
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Create a standardized accepted response (202).
        
        Args:
            message_en: English message
            message_ar: Arabic message
            data: Response data (optional)
            extra_fields: Additional fields (e.g., job_id)
            
        Returns:
            Response object with standardized accepted format
        """
        response_data = {
            "status": "accepted",
            "en": message_en,
            "ar": message_ar,
        }
        
        if data is not None:
            response_data["data"] = data
            
        if extra_fields:
            response_data.update(extra_fields)
            
        return Response(response_data, status=status.HTTP_202_ACCEPTED)
    
    @staticmethod
    def error(
        message_en: str,
        message_ar: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: Any = None,
        error_detail: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Create a standardized error response.
        
        Args:
            message_en: English error message
            message_ar: Arabic error message
            status_code: HTTP status code (default: 400)
            errors: Validation errors (for form/serializer errors)
            error_detail: Additional error details
            extra_fields: Additional fields to include
            
        Returns:
            Response object with standardized error format
        """
        response_data = {
            "status": "error",
            "en": message_en,
            "ar": message_ar,
        }
        
        # Include validation errors if provided
        if errors is not None:
            response_data["errors"] = errors
            
        # Include error details if provided
        if error_detail is not None:
            response_data["error"] = error_detail
            
        # Add any extra fields
        if extra_fields:
            response_data.update(extra_fields)
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def validation_error(
        message_en: str = "Validation failed",
        message_ar: str = "فشل في التحقق من صحة البيانات",
        errors: Any = None
    ) -> Response:
        """
        Create a standardized validation error response (400).
        
        Args:
            message_en: English validation message
            message_ar: Arabic validation message
            errors: Validation errors
            
        Returns:
            Response object with standardized validation error format
        """
        return StandardResponse.error(
            message_en=message_en,
            message_ar=message_ar,
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=errors
        )
    
    @staticmethod
    def not_found(
        message_en: str = "Resource not found",
        message_ar: str = "المورد غير موجود",
        error_detail: Optional[str] = None
    ) -> Response:
        """
        Create a standardized not found error response (404).
        
        Args:
            message_en: English not found message
            message_ar: Arabic not found message
            error_detail: Additional error details
            
        Returns:
            Response object with standardized not found format
        """
        return StandardResponse.error(
            message_en=message_en,
            message_ar=message_ar,
            status_code=status.HTTP_404_NOT_FOUND,
            error_detail=error_detail
        )
    
    @staticmethod
    def unauthorized(
        message_en: str = "Authentication required",
        message_ar: str = "المصادقة مطلوبة",
        error_detail: Optional[str] = None
    ) -> Response:
        """
        Create a standardized unauthorized error response (401).
        
        Args:
            message_en: English unauthorized message
            message_ar: Arabic unauthorized message
            error_detail: Additional error details
            
        Returns:
            Response object with standardized unauthorized format
        """
        return StandardResponse.error(
            message_en=message_en,
            message_ar=message_ar,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_detail=error_detail
        )
    
    @staticmethod
    def forbidden(
        message_en: str = "Access forbidden",
        message_ar: str = "الوصول محظور",
        error_detail: Optional[str] = None
    ) -> Response:
        """
        Create a standardized forbidden error response (403).
        
        Args:
            message_en: English forbidden message
            message_ar: Arabic forbidden message
            error_detail: Additional error details
            
        Returns:
            Response object with standardized forbidden format
        """
        return StandardResponse.error(
            message_en=message_en,
            message_ar=message_ar,
            status_code=status.HTTP_403_FORBIDDEN,
            error_detail=error_detail
        )
    
    @staticmethod
    def server_error(
        message_en: str = "Internal server error",
        message_ar: str = "خطأ داخلي في الخادم",
        error_detail: Optional[str] = None
    ) -> Response:
        """
        Create a standardized server error response (500).
        
        Args:
            message_en: English server error message
            message_ar: Arabic server error message
            error_detail: Additional error details
            
        Returns:
            Response object with standardized server error format
        """
        return StandardResponse.error(
            message_en=message_en,
            message_ar=message_ar,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_detail=error_detail
        )


class ResponseMixin:
    """
    Mixin class to add standardized response methods to ViewSets and APIViews.
    """
    
    def success_response(self, message_en: str, message_ar: str, data: Any = None, 
                        status_code: int = status.HTTP_200_OK, **extra_fields) -> Response:
        """Create a success response using the standardized format."""
        return StandardResponse.success(
            message_en=message_en,
            message_ar=message_ar,
            data=data,
            status_code=status_code,
            extra_fields=extra_fields if extra_fields else None
        )
    
    def accepted_response(self, message_en: str, message_ar: str, 
                         data: Any = None, **extra_fields) -> Response:
        """Create an accepted response using the standardized format."""
        return StandardResponse.accepted(
            message_en=message_en,
            message_ar=message_ar,
            data=data,
            extra_fields=extra_fields if extra_fields else None
        )
    
    def error_response(self, message_en: str, message_ar: str, 
                      status_code: int = status.HTTP_400_BAD_REQUEST,
                      errors: Any = None, error_detail: Optional[str] = None, **extra_fields) -> Response:
        """Create an error response using the standardized format."""
        return StandardResponse.error(
            message_en=message_en,
            message_ar=message_ar,
            status_code=status_code,
            errors=errors,
            error_detail=error_detail,
            extra_fields=extra_fields if extra_fields else None
        )
    
    def validation_error_response(self, errors: Any = None, 
                                 message_en: str = "Validation failed",
                                 message_ar: str = "فشل في التحقق من صحة البيانات") -> Response:
        """Create a validation error response."""
        return StandardResponse.validation_error(
            message_en=message_en,
            message_ar=message_ar,
            errors=errors
        )
    
    def not_found_response(self, message_en: str = "Resource not found",
                          message_ar: str = "المورد غير موجود",
                          error_detail: Optional[str] = None) -> Response:
        """Create a not found error response."""
        return StandardResponse.not_found(
            message_en=message_en,
            message_ar=message_ar,
            error_detail=error_detail
        )
