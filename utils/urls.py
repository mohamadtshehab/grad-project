from django.urls import path
from .views import JobDetailView, PauseJobView, ResumeJobView, UserJobsListView

urlpatterns = [
	path('jobs/', UserJobsListView.as_view(), name='user-jobs'),
	path('jobs/<uuid:job_id>/', JobDetailView.as_view(), name='job-detail'),
	path('jobs/<uuid:job_id>/pause/', PauseJobView.as_view(), name='pause-job'),
	path('jobs/<uuid:job_id>/resume/', ResumeJobView.as_view(), name='resume-job'),
]


