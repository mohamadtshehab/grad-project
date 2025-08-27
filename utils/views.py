from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Job
from .serializers import JobSerializer
from .response_utils import ResponseMixin


class JobDetailView(APIView, ResponseMixin):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, job_id: str):
		job = get_object_or_404(Job, id=job_id, user=request.user)
		return self.success_response(
			message_en="Job details retrieved successfully",
			message_ar="تم استرجاع تفاصيل المهمة بنجاح",
			data=JobSerializer(job).data
		)


