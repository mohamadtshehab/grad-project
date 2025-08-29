from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
	class Meta:
		model = Job
		fields = [
			"id",
			"user",
<<<<<<< HEAD
=======
			"book",
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
			"job_type",
			"status",
			"progress",
			"result",
			"error",
			"created_at",
			"updated_at",
			"started_at",
			"finished_at",
		]
		read_only_fields = fields

