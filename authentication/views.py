from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
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

