from django.db.models.constraints import UniqueConstraint
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from profiles.models import (
	Personnel,
	Inmate
)

from home.utils import get_full_name


class Archive(models.Model):
	# Common details
	archive_date 	= models.DateTimeField(default=timezone.now)
	archive_by		= models.ForeignKey(User, null=True, on_delete=models.SET_NULL, default=None)

	class Meta:
		abstract = True


class Personnel(Archive):
	profile = models.OneToOneField(
		Personnel, 
		on_delete = models.CASCADE,
		related_name='archive'
	)

	def __str__(self):
		return get_full_name(self.profile) + "'s Archived Profile"



class Inmate(Archive):
	profile = models.OneToOneField(
		Personnel, 
		on_delete = models.CASCADE,
		related_name='archive'
	)

	def __str__(self):
		return get_full_name(self.profile) + "'s Archived Profile"