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
import logging

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Queue welcome email
        welcome_task = send_welcome_email.delay(
            user_id=str(user.id),
            user_email=user.email,
            user_name=user.name
        )
        
        return Response({
            "status": "success",
            "en": "User registered successfully",
            "ar": "تم تسجيل المستخدم بنجاح",
            "data": ProfileSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({
            "status": "success",
            "en": "Logged in successfully",
            "ar": "تم تسجيل الدخول بنجاح",
            "data": response.data,
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "status": "success",
            "en": "Profile retrieved successfully",
            "ar": "تم استرجاع الملف الشخصي بنجاح",
            "data": ProfileSerializer(request.user).data,
        })

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "success",
            "en": "Profile updated successfully",
            "ar": "تم تحديث الملف الشخصي بنجاح",
            "data": serializer.data,
        })



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Logout user by blacklisting the refresh token"""
        try:
            # Get the refresh token from the request
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({
                    "status": "error",
                    "en": "Refresh token is required",
                    "ar": "الرمز المميز للتحديث مطلوب",
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Create a RefreshToken instance and blacklist it
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                "status": "success",
                "en": "Logged out successfully",
                "ar": "تم تسجيل الخروج بنجاح",
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "en": "Logout failed",
                "ar": "فشل في تسجيل الخروج",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                "status": "error",
                "en": "Current password is incorrect",
                "ar": "كلمة المرور الحالية غير صحيحة",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            "status": "success",
            "en": "Password changed successfully",
            "ar": "تم تغيير كلمة المرور بنجاح",
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
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
                
                
                return Response({
                    "status": "success",
                    "en": "Password reset code is being sent to your email",
                    "ar": "يتم إرسال رمز إعادة تعيين كلمة المرور إلى بريدك الإلكتروني",
                    "message": f"A {len(reset_code.code)}-digit code is being sent to {email}",
                    "task_id": task.id  # Include task ID for tracking
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                # Delete the created code if queuing fails
                reset_code.delete()
                
                return Response({
                    "status": "error",
                    "en": "Failed to send reset code",
                    "ar": "فشل في إرسال رمز إعادة التعيين",
                    "message": "Please try again later"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response({
                "status": "success",
                "en": "If an account with this email exists, a reset code has been sent",
                "ar": "إذا كان هناك حساب بهذا البريد الإلكتروني، تم إرسال رمز إعادة التعيين",
                "message": "Check your email for password reset instructions"
            }, status=status.HTTP_200_OK)
    



class PasswordResetConfirmView(APIView):
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
                    return Response({
                        "status": "error",
                        "en": "Reset code has expired or is invalid",
                        "ar": "رمز إعادة التعيين منتهي الصلاحية أو غير صحيح",
                    }, status=status.HTTP_400_BAD_REQUEST)
                
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
                
                return Response({
                    "status": "success",
                    "en": "Password reset successful",
                    "ar": "تم إعادة تعيين كلمة المرور بنجاح",
                    "message": "You can now login with your new password"
                }, status=status.HTTP_200_OK)
                
            except PasswordResetCode.DoesNotExist:
                return Response({
                    "status": "error",
                    "en": "Invalid reset code",
                    "ar": "رمز إعادة التعيين غير صحيح",
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "en": "User with this email does not exist",
                "ar": "لا يوجد مستخدم بهذا البريد الإلكتروني",
            }, status=status.HTTP_404_NOT_FOUND)


class AccountDeletionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Delete user account"""
        serializer = AccountDeletionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['password']):
            return Response({
                "status": "error",
                "en": "Password is incorrect",
                "ar": "كلمة المرور غير صحيحة",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete the user
        user.delete()
        
        return Response({
            "status": "success",
            "en": "Account deleted successfully",
            "ar": "تم حذف الحساب بنجاح",
        }, status=status.HTTP_200_OK)

