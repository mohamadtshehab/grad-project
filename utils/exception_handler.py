from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied, NotFound
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .response_utils import StandardResponse
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that returns standardized, robust error responses.
    It prioritizes exception types and codes over parsing error strings.
    """
    # Let DRF's default handler process the exception first.
    response = exception_handler(exc, context)

    # Handle specific exception types first for clarity and robustness.
    if isinstance(exc, (InvalidToken, TokenError)):
        # These are the most specific errors for bad/expired tokens.
        return StandardResponse.unauthorized(
            message_en="Invalid or expired token",
            message_ar="الرمز المميز غير صحيح أو منتهي الصلاحية",
            error_detail="Please login again to get a new token."
        )

    if isinstance(exc, AuthenticationFailed):
        # 1. Get the specific error code from the exception.
        errors = exc.detail
        first_error_message = next(iter(errors.values()))[0]

        # 2. Check for the 'user_not_found' code you received.
        if 'user_not_found' in str(first_error_message):
            # 3. Return a specific, translated response for this error.
            return StandardResponse.unauthorized(
                message_en="User not found",
                message_ar="المستخدم غير موجود",
                error_detail="An account with the provided credentials could not be found."
            )
            
        # 4. Handle another common code: invalid username/password during login.
        elif 'no_active_account' in str(first_error_message):
            return StandardResponse.unauthorized(
                message_en="Invalid email or password",
                message_ar="بريد إلكتروني أو كلمة مرور غير صحيحة",
                error_detail="Please check your credentials and try again."
            )

        # 5. Provide a generic fallback for any other AuthenticationFailed errors.
        else:
            return StandardResponse.unauthorized(
            )

    if isinstance(exc, ValidationError):
        # 1. Extract the first error message, just like before.
        errors = exc.detail
        first_error_message = next(iter(errors.values()))[0]

        # 2. Check for specific, known error strings.
        if "New passwords don't match" in str(first_error_message):
            # 3. If it matches, return a specific, translated response for that error.
            return StandardResponse.error(
                message_en="New passwords don't match",
                message_ar="كلمات المرور الجديدة غير متطابقة", # Specific translation
                status_code=status.HTTP_400_BAD_REQUEST,
                error_detail="Input validation failed"
            )
        
        # 4. You can add more `elif` blocks here for other known errors.
        # For example, for the error in your RegisterSerializer
        elif "Passwords don't match" in str(first_error_message):
            return StandardResponse.error(
                message_en="Passwords don't match",
                message_ar="كلمات المرور غير متطابقة", # Specific translation
                status_code=status.HTTP_400_BAD_REQUEST,
                error_detail="Input validation failed"
            )
            
        # 5. For any other validation error that you haven't specified,
        #    return the generic fallback response.
        else:
            return StandardResponse.error(
                message_en=str(first_error_message),
                message_ar="فشل في التحقق من صحة البيانات", # Generic fallback translation
                status_code=status.HTTP_400_BAD_REQUEST,
                error_detail="Input validation failed"
            )

    if isinstance(exc, PermissionDenied):
        return StandardResponse.forbidden(
            message_en="Access forbidden",
            message_ar="الوصول محظور",
            error_detail=str(exc)
        )

    if isinstance(exc, (NotFound, ObjectDoesNotExist)):
        return StandardResponse.not_found(
            message_en="Resource not found",
            message_ar="المورد غير موجود",
            error_detail=str(exc)
        )

    # Fallback for any other exceptions handled by DRF
    if response is not None:
        if response.status_code >= 500:
            return StandardResponse.server_error(
                message_en="Internal server error",
                message_ar="خطأ داخلي في الخادم",
                error_detail="A server error occurred."
            )
        else:
            # Generic catch-all for other client-side errors (4xx)
            # We can use the detail from the default DRF response.
            detail = response.data.get('detail', "An error occurred.") if isinstance(response.data, dict) else str(response.data)
            
            # Clean up any Python object representations
            if 'ErrorDetail' in str(detail) or detail.startswith("{'detail':"):
                detail = "Request failed"
            
            return StandardResponse.error(
                message_en="Request failed",
                message_ar="فشل في الطلب",
                status_code=response.status_code,
                error_detail=str(detail)
            )
            
    # If response is None, it's an unhandled server error.
    # This can happen if an exception occurs before DRF's main handling.
    return StandardResponse.server_error(
        message_en="Unexpected server error",
        message_ar="خطأ غير متوقع في الخادم",
        error_detail="An unexpected server error occurred."
    )
