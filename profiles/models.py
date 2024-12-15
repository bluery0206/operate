from django.db.models.constraints import UniqueConstraint
from django.utils import timezone
from django.db import models

from app.utils import get_full_name



CIVIL_STATUS_CHOICES = [
	('single', 'Single'),
	('married', 'Married'),
	('widowed', 'Widowed'),
	('legally_separated', 'Legally Separated'),
]
RANKS = [
	('Pat', 'Patrolman/Patrolwoman, Pat'),
	('PCpl', 'Police Corporal, PCpl'),
	('PSSg', 'Police Staff Sergeant, PSSg'),
	('PMSg', 'Police Master Sergeant, PMSg'),
	('PSMS', 'Police Senior Master Sergeant, PSMS'),
	('PCMS', 'Police Chief Master Sergeant, PCMS'),
	('PEMS', 'Police Executive Master Sergeant, PEMS'),
	('PLT', 'Police Lieutenant, PLT'),
	('PCPT', 'Police Captain, PCPT'),
	('PMAJ', 'Police Major, PMAJ'),
	('PLTCOL', 'Police Lieutenant Colonel, PLTCOL'),
	('PCOL', 'Police Colonel, PCOL'),
	('PBGEN', 'Police Brigadier General, PBGEN'),
	('PGEN', 'Police General, PGEN'),
	('PMGEN', 'Police Major General, PMGEN'),
	('PLTGEN', 'Police Lieutenant General, PLTGEN'),
]
NAME_FIELDS = [
	'f_name',
	'l_name',
	'm_name',
	'suffix',
]



class Profile(models.Model):
	date_profiled	= models.DateTimeField(default=timezone.now)
	is_archived		= models.BooleanField(default=False)

	thumbnail = models.FileField(
		upload_to	= "thumbnails",
		default 	= "default.png",
	)
	raw_image = models.FileField(
		upload_to	= "raw_images",
		default 	= "default.png",
	)
	embedding = models.FileField(
		upload_to	="embeddings",
		blank		=True,
		null=True,
	)

	# Common details
	f_name			= models.CharField(max_length=30)
	m_name			= models.CharField(max_length=20, blank=True, default=None)
	l_name			= models.CharField(max_length=20)
	suffix			= models.CharField(max_length=10, blank=True, default=None)

	age 			= models.IntegerField()
	address			= models.CharField(max_length=250)
	civil_status	= models.CharField(blank=True, max_length=20, choices=CIVIL_STATUS_CHOICES, default='single')

	class Meta:
		abstract = True

class Personnel(Profile):
	p_type			= models.CharField(max_length=10, default="personnel")
	rank			= models.CharField(max_length=10, choices=RANKS, default='pat')
	date_assigned	= models.DateTimeField(default=timezone.now)
	date_relieved	= models.DateTimeField(blank=True, null=True)
	designation		= models.CharField(max_length=250)

	class Meta:
		constraints = [
			UniqueConstraint(
				fields = NAME_FIELDS,
				name	= "unique-personnel-profile"
			)
		]

	def __str__(self):
		return get_full_name(self) + "'s Profile"

class Inmate(Profile):
	p_type 			= models.CharField(max_length=10, default="inmate")
	date_arrested	= models.DateTimeField(default=timezone.now)
	date_committed	= models.DateTimeField(null=True, blank=True)
	crime_violated	= models.CharField(max_length=250)

	class Meta:
		# Makes the entire row with specified fields unique.
		constraints = [
			UniqueConstraint(
				fields = NAME_FIELDS,
				name="unique-inmate-profile"
			)
		]

	def __str__(self):
		return get_full_name(self) + "'s Profile"







# P_FIELDS = [
# 	'age',
# 	'address',
# 	'civil_status',
# 	'date_profiled',
# 	'rank',
# 	'date_assigned',
# 	'date_relieved',
# 	'designation'
# ]

# I_FIELDS = [
# 	'address',
# 	'civil_status',
# 	'date_profiled',
# 	'date_arrested',
# 	'date_committed',
# 	'crime_violated'
# ]