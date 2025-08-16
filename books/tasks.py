from celery import shared_task
from django.utils import timezone
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from utils.models import Job
from books.models import Book
from ai_workflow.src.extractors.book_name_extractor import extract_book_name_from_file
import logging


def _notify_user(user_id: str, payload: dict):
	try:
		channel_layer = get_channel_layer()
		group_name = f"user_{user_id}"		
		# Send to user-specific group
		async_to_sync(channel_layer.group_send)(group_name, {"type": "job.update", **payload})
		
		# Also send to test group for debugging
		async_to_sync(channel_layer.group_send)("test_group", {"type": "job.update", **payload})
		
		
	except Exception as e:
		raise


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def extract_novel_name(self, job_id: str, user_id: str, book_id: str, filename: str):
	"""Background task: extract novel name from uploaded book."""
	try:
		job = Job.objects.get(id=job_id)
		job.status = Job.Status.RUNNING
		job.started_at = timezone.now()
		job.progress = 5
		job.save(update_fields=["status", "started_at", "progress", "updated_at"])

		book = Book.objects.get(book_id=book_id)

		# Extract book name using LLM
		try:
			extraction_result = extract_book_name_from_file(book, filename)
		except Exception as e:
			# Fallback: use filename as title
			result = {
				"suggested_title": filename.rsplit('.', 1)[0],
				"confidence": "منخفض",
				"reasoning": f"فشل في استخراج الاسم من المحتوى: {str(e)}. تم استخدام اسم الملف كبديل.",
			}
			# Update job and book directly
			job.result = result
			job.status = Job.Status.COMPLETED
			job.progress = 100
			job.finished_at = timezone.now()
			job.save(update_fields=["result", "status", "progress", "finished_at", "updated_at"])
			
			book.title = result["suggested_title"]
			book.save(update_fields=["title", "updated_at"])
			
			_notify_user(user_id, {
				"event": "novel_name_extracted",
				"job_id": job_id,
				"status": "completed",
				"result": result,
			})
			
			return {"status": "success", "job_id": job_id}
		
		result = {
			"suggested_title": extraction_result.book_name,
			"confidence": extraction_result.confidence,
			"reasoning": extraction_result.reasoning,
		}

		job.result = result
		job.status = Job.Status.COMPLETED
		job.progress = 100
		job.finished_at = timezone.now()
		job.save(update_fields=["result", "status", "progress", "finished_at", "updated_at"])
		
		# Update the book with the extracted title
		book.title = result["suggested_title"]
		book.save(update_fields=["title", "updated_at"])

		_notify_user(user_id, {
			"event": "novel_name_extracted",
			"job_id": job_id,
			"status": "completed",
			"result": result,
		})

		return {"status": "success", "job_id": job_id}

	except Exception as exc:
		try:
			job = Job.objects.get(id=job_id)
			job.status = Job.Status.FAILED
			job.error = str(exc)
			job.finished_at = timezone.now()
			job.save(update_fields=["status", "error", "finished_at", "updated_at"])
			_notify_user(user_id, {
				"event": "novel_name_extracted",
				"job_id": job_id,
				"status": "failed",
				"error": str(exc),
			})
		except Exception:
			pass
		if self.request.retries < self.max_retries:
			raise self.retry(exc=exc)
		raise


