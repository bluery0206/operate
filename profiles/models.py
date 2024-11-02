from django.db.models.constraints import UniqueConstraint
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models


from home.utils import get_full_name

CIVIL_STATUS_CHOICES = [
	('single', 'Single'),
	('married', 'Married'),
	('widowed', 'Widowed'),
	('legally_separated', 'Legally Separated '),
]

RANKS = [
	('pgen', 'Police General, PGEN'),
	('pltgen', 'Police Lieutenant General, PLTGEN'),
	('pmgen', 'Police Major General, PMGEN'),
	('pbgen', 'Police Brigadier General, PBGEN'),
	('pcol', 'Police Colonel, PCOL'),
	('pltcol', 'Police Lieutenant Colonel, PLTCOL'),
	('pmaj', 'Police Major, PMAJ'),
	('pcpt', 'Police Captain, PCPT'),
	('plt', 'Police Lieutenant, PLT'),
	('pems', 'Police Executive Master Sergeant, PEMS'),
	('pcms', 'Police Chief Master Sergeant, PCMS'),
	('psms', 'Police Senior Master Sergeant, PSMS'),
	('pmsg', 'Police Master Sergeant, PMSg'),
	('pssg', 'Police Staff Sergeant, PSSg'),
	('pcpl', 'Police Corporal, PCpl'),
	('pat', 'Patrolman/Patrolwoman, Pat')
]

P_FIELDS = [
	'f_name',
	'l_name',
	'm_name',
	'suffix',
	'age',
	'address',
	'civil_status',
	'date_profiled',
	'rank',
	'date_assigned',
	'date_relieved',
	'designation'
]

I_FIELDS = [
	'f_name',
	'l_name',
	'm_name',
	'suffix',
	'age',
	'address',
	'civil_status',
	'date_profiled',
	'date_arrested',
	'date_committed',
	'crime_violated'
]

class Profile(models.Model):
	RANKS = RANKS

	# Images
	thumbnail = models.FileField(
		default		= "default.png", 
		upload_to	= "thumbnails"
	)
	raw_image = models.FileField(
		default 	= "default.png", 
		upload_to	= "raw_images"
	)

	# Common details
	f_name			= models.CharField(max_length=30)
	m_name			= models.CharField(max_length=20, blank=True, default=None)
	l_name			= models.CharField(max_length=20)
	suffix			= models.CharField(max_length=10, blank=True, default=None)
	age 			= models.IntegerField()
	address			= models.TextField()
	civil_status	= models.CharField(blank=True, max_length=20, choices=CIVIL_STATUS_CHOICES, default='single')
	date_profiled = models.DateTimeField(default=timezone.now)

	class Meta:
		abstract = True

class Personnel(Profile):
	p_type	= models.CharField(max_length=10, default="personnel")
	rank	= models.CharField(max_length=10, choices=RANKS, default='pat')
	date_assigned	= models.DateTimeField()
	date_relieved	= models.DateTimeField(blank=True, null=True)
	designation		= models.TextField()

	class Meta:
		# Makes the entire row with specified fields unique.
		constraints = [
			UniqueConstraint(
				fields = P_FIELDS,
				name="unique-personnel-profile"
			)
		]

	def __str__(self):
		return get_full_name(self) + "'s Profile"

class Inmate(Profile):
	p_type = models.CharField(max_length=10, default="inmate")
	date_arrested	= models.DateTimeField()
	date_committed	= models.DateTimeField(null=True, blank=True)
	crime_violated	= models.TextField()

	class Meta:
		# Makes the entire row with specified fields unique.
		constraints = [
			UniqueConstraint(
				fields = I_FIELDS,
				name="unique-inmate-profile"
			)
		]

	def __str__(self):
		return get_full_name(self) + "'s Profile"
