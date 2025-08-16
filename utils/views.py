from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Job
from .serializers import JobSerializer


class JobDetailView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, job_id: str):
		job = get_object_or_404(Job, id=job_id, user=request.user)
		return Response({
			"status": "success",
			"data": JobSerializer(job).data,
		}, status=status.HTTP_200_OK)


