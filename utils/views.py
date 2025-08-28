from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Job
from .serializers import JobSerializer
from .response_utils import ResponseMixin
from books.tasks import process_book_workflow


class JobDetailView(APIView, ResponseMixin):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, job_id: str):
		job = get_object_or_404(Job, id=job_id, user=request.user)
		return self.success_response(
			message_en="Job details retrieved successfully",
			message_ar="تم استرجاع تفاصيل المهمة بنجاح",
			data=JobSerializer(job).data
		)


class PauseJobView(APIView, ResponseMixin):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, job_id: str):
		"""
		Pause a job by changing its status to PAUSED.
		Only the job owner can pause their own jobs.
		"""
		job = get_object_or_404(Job, id=job_id, user=request.user)
		
		# Check if the job can be paused
		if job.status == Job.Status.PAUSED:
			return self.error_response(
				message_en="Job is already paused",
				message_ar="المهمة متوقفة بالفعل",
				status_code=status.HTTP_400_BAD_REQUEST
			)
		
		if job.status == Job.Status.COMPLETED:
			return self.error_response(
				message_en="Cannot pause a completed job",
				message_ar="لا يمكن إيقاف مهمة مكتملة",
				status_code=status.HTTP_400_BAD_REQUEST
			)
		
		if job.status == Job.Status.FAILED:
			return self.error_response(
				message_en="Cannot pause a failed job",
				message_ar="لا يمكن إيقاف مهمة فاشلة",
				status_code=status.HTTP_400_BAD_REQUEST
			)
		
		# Update job status to paused
		job.status = Job.Status.PAUSED
		job.save()
		
		return self.success_response(
			message_en="Job paused successfully",
			message_ar="تم إيقاف المهمة بنجاح",
			data=JobSerializer(job).data
		)
	
 


class ResumeJobView(APIView, ResponseMixin):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, job_id: str):
		"""
		Resume a paused job by calling the process_book_workflow task.
		Only the job owner can resume their own jobs.
		"""
		job = get_object_or_404(Job, id=job_id, user=request.user)
		
		# Check if the job can be resumed
		if job.status != Job.Status.PAUSED:
			return self.error_response(
				message_en="Only paused jobs can be resumed",
				message_ar="يمكن استئناف المهام المتوقفة فقط",
				status_code=status.HTTP_400_BAD_REQUEST
			)
		
		# Check if the job has a book_id
		if not job.book:
			return self.error_response(
				message_en="No book associated with this job",
				message_ar="لا يوجد كتاب مرتبط بهذه المهمة",
				status_code=status.HTTP_400_BAD_REQUEST
			)
		
		try:
			# Call the process_book_workflow task
			process_book_workflow.delay(
				job_id=str(job.id),
			)
			
			# Update job status to indicate it's running
			job.status = Job.Status.RUNNING
			job.save()
			
			return self.success_response(
				message_en="Job resumed successfully",
				message_ar="تم استئناف المهمة بنجاح",
				data=JobSerializer(job).data
			)
			
		except Exception as e:
			return self.error_response(
				message_en=f"Failed to resume job: {str(e)}",
				message_ar=f"فشل في استئناف المهمة: {str(e)}",
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
			)
	
 


