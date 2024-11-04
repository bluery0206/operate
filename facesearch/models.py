from django.db import models
import uuid

class UploadedImage(models.Model):
	image = models.FileField(
		upload_to = "searches"
	)