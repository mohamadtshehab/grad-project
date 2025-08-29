from django.db import models
from django.conf import settings
import uuid
from books.models import Book

class Job(models.Model):
	"""Represents a long-running background job processed by Celery."""

	class Status(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		RUNNING = 'RUNNING', 'Running'
		PAUSED = 'PAUSED', 'Paused'
		COMPLETED = 'COMPLETED', 'Completed'
		FAILED = 'FAILED', 'Failed'

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="jobs",
		null=True,
		blank=True,
	)
	job_type = models.CharField(max_length=100, db_index=True)
 
	book = models.ForeignKey(
		Book,
		on_delete=models.CASCADE,
		related_name="jobs",
		null=True,
		blank=True,
		)
 
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
	progress = models.PositiveSmallIntegerField(default=0)
	result = models.JSONField(null=True, blank=True)
	error = models.TextField(blank=True)
	started_at = models.DateTimeField(null=True, blank=True)
	finished_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	langgraph_thread_id = models.CharField(
			max_length=255, 
			unique=True, 
			blank=True, 
			null=True,
			help_text="The unique thread ID for the LangGraph execution state."
		)

	def __str__(self) -> str:
		return f"Job<{self.id}> {self.job_type} [{self.status}]"

	class Meta:
		indexes = [
			models.Index(fields=["user", "job_type"]),
			models.Index(fields=["status", "created_at"]),
		]
