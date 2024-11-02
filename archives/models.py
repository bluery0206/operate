from django.db.models.constraints import UniqueConstraint
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

from home.utils import get_full_name
from profiles.models import (
	Personnel,
	Inmate
)


class Archive(models.Model):
	# Common details
	archive_date 	= models.DateTimeField(default=timezone.now)
	archive_by		= models.ForeignKey(User, null=True, on_delete=models.SET_NULL, default=None)

	class Meta:
		abstract = True


class ArchivePersonnel(Archive):
	profile = models.OneToOneField(
		Personnel, 
		on_delete = models.CASCADE,
		related_name='archivepersonnel'
	)

	def __str__(self):
		return get_full_name(self.profile) + "'s Archived Profile"

class ArchiveInmate(Archive):
	profile = models.OneToOneField(
		Inmate, 
		on_delete = models.CASCADE,
		related_name='archiveinmate'
	)

	def __str__(self):
		return get_full_name(self.profile) + "'s Archived Profile"