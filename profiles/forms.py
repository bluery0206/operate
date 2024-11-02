from django.contrib.auth.models import User
from django.forms import ModelForm
from home.utils import get_full_name

from .models import (
	Personnel, 
	Inmate
)

class CreatePersonnel(ModelForm):
	class Meta:
		model = Personnel
		fields = [
			'raw_image',
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
			'designation',
		]


class UpdatePersonnel(ModelForm):
	class Meta:
		model = Personnel
		fields = [
			'raw_image',
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
			'designation',
		]


class CreateInmate(ModelForm):
	class Meta:
		model = Inmate
		fields = [
			'raw_image',
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
			'crime_violated',
		]


class UpdateInmate(ModelForm):
	class Meta:
		model = Inmate
		fields = [
			'raw_image',
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
			'crime_violated',
		]

