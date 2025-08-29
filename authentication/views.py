from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .permissions import IsNotAuthenticated
from .throttling import PasswordResetThrottle
from .serializers import (
    RegisterSerializer, LoginSerializer, ProfileSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, AccountDeletionSerializer
)

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import PasswordResetCode
from .tasks import send_password_reset_email, send_welcome_email
from utils.response_utils import ResponseMixin
import logging

User = get_user_model()

class RegisterView(APIView, ResponseMixin):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Queue welcome email (do not fail registration if queueing fails)
        try:
            welcome_task = send_welcome_email.delay(
                user_id=str(user.id),
                user_email=user.email,
                user_name=user.name
            )
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to enqueue welcome email: {e}")
        
        return self.success_response(
            message_en="User registered successfully",
            message_ar="تم تسجيل المستخدم بنجاح",
            data=ProfileSerializer(user).data,
            status_code=status.HTTP_201_CREATED
        )


class LoginView(TokenObtainPairView, ResponseMixin):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return self.success_response(
                message_en="Logged in successfully",
                message_ar="تم تسجيل الدخول بنجاح",
                data=response.data
            )
        except Exception as e:
            # Handle JWT authentication errors and return standardized responses
            error_message = str(e)
            
            # Common JWT authentication error messages
            if "No active account found with the given credentials" in error_message:
                return self.error_response(
                    message_en="Invalid email or password",
                    message_ar="بريد إلكتروني أو كلمة مرور غير صحيحة",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    error_detail="Please check your credentials and try again"
                )
            elif "User account is disabled" in error_message:
                return self.error_response(
                    message_en="Account is disabled",
                    message_ar="الحساب معطل",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    error_detail="Your account has been disabled. Please contact support."
                )
            else:
                # Generic authentication error
                return self.error_response(
                    message_en="Authentication failed",
                    message_ar="فشل في المصادقة",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    error_detail=error_message
                )


class ProfileView(APIView, ResponseMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return self.success_response(
            message_en="Profile retrieved successfully",
            message_ar="تم استرجاع الملف الشخصي بنجاح",
            data=ProfileSerializer(request.user).data
        )

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success_response(
            message_en="Profile updated successfully",
            message_ar="تم تحديث الملف الشخصي بنجاح",
            data=serializer.data
        )



class LogoutView(APIView, ResponseMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Logout user by blacklisting the refresh token"""
        try:
            # Get the refresh token from the request
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return self.error_response(
                    message_en="Refresh token is required",
                    message_ar="الرمز المميز للتحديث مطلوب",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_detail="Please provide a valid refresh token"
                )
                
            # Create a RefreshToken instance and blacklist it
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return self.success_response(
                message_en="Logged out successfully",
                message_ar="تم تسجيل الخروج بنجاح"
            )
        except Exception as e:
            return self.error_response(
                message_en="Logout failed",
                message_ar="فشل في تسجيل الخروج",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_detail=str(e)
            )

class PasswordChangeView(APIView, ResponseMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return self.error_response(
                message_en="Current password is incorrect",
                message_ar="كلمة المرور الحالية غير صحيحة",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_detail="Please enter your current password correctly"
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return self.success_response(
            message_en="Password changed successfully",
            message_ar="تم تغيير كلمة المرور بنجاح"
        )


class PasswordResetRequestView(APIView, ResponseMixin):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        """Request password reset - only for unauthenticated users"""
        
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        
        try:
            user = User.objects.get(email=email)
            
            # Create a new password reset code
            reset_code = PasswordResetCode.create_for_user(user)
            
            # Queue the email sending task
            try:
                # Send email asynchronously using Celery
                task = send_password_reset_email.delay(
                    user_id=str(user.id),
                    reset_code=reset_code.code,
                    user_email=user.email,
                    user_name=user.name
                )
                
                
                return self.success_response(
                    message_en="Password reset code is being sent to your email",
                    message_ar="يتم إرسال رمز إعادة تعيين كلمة المرور إلى بريدك الإلكتروني",
                    data={
                        "message": f"A {len(reset_code.code)}-digit code is being sent to {email}",
                        "task_id": task.id  # Include task ID for tracking
                    }
                )
                
            except Exception as e:
                # Delete the created code if queuing fails
                reset_code.delete()
                
                return self.error_response(
                    message_en="Failed to send reset code",
                    message_ar="فشل في إرسال رمز إعادة التعيين",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    error_detail="Please try again later"
                )
                
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return self.success_response(
                message_en="If an account with this email exists, a reset code has been sent",
                message_ar="إذا كان هناك حساب بهذا البريد الإلكتروني، تم إرسال رمز إعادة التعيين",
                data={"message": "Check your email for password reset instructions"}
            )
    



class PasswordResetConfirmView(APIView, ResponseMixin):
    permission_classes = [AllowAny]

    def post(self, request):
        """Confirm password reset with code - only for unauthenticated users"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(email=email)
            
            # Find the most recent valid reset code for this user
            try:
                reset_code = PasswordResetCode.objects.filter(
                    user=user,
                    code=code,
                    is_used=False
                ).latest('created_at')
                
                # Check if the code is still valid
                if not reset_code.is_valid():
                    return self.error_response(
                        message_en="Reset code has expired or is invalid",
                        message_ar="رمز إعادة التعيين منتهي الصلاحية أو غير صحيح",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update the user's password
                user.set_password(new_password)
                user.save()
                
                # Mark the code as used
                reset_code.mark_as_used()
                
                # Invalidate any other unused codes for this user
                PasswordResetCode.objects.filter(
                    user=user,
                    is_used=False
                ).update(is_used=True)
                
                return self.success_response(
                    message_en="Password reset successful",
                    message_ar="تم إعادة تعيين كلمة المرور بنجاح",
                    data={"message": "You can now login with your new password"}
                )
                
            except PasswordResetCode.DoesNotExist:
                return self.error_response(
                    message_en="Invalid reset code",
                    message_ar="رمز إعادة التعيين غير صحيح",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
        except User.DoesNotExist:
            return self.error_response(
                message_en="User with this email does not exist",
                message_ar="لا يوجد مستخدم بهذا البريد الإلكتروني",
                status_code=status.HTTP_404_NOT_FOUND
            )


class AccountDeletionView(APIView, ResponseMixin):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Delete user account"""
        serializer = AccountDeletionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['password']):
            return self.error_response(
                message_en="Password is incorrect",
                message_ar="كلمة المرور غير صحيحة",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete the user
        user.delete()
        
        return self.success_response(
            message_en="Account deleted successfully",
            message_ar="تم حذف الحساب بنجاح"
        )

