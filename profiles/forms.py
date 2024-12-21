from django import forms
from django.core.validators import FileExtensionValidator

from . import models


COMMON_CLASS = 'form-control'
WIDGETS = {
	'date_profiled'	: forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': COMMON_CLASS,
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'date_arrested'	: forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': COMMON_CLASS,
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'date_committed': forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': COMMON_CLASS,
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'date_assigned'	: forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': COMMON_CLASS,
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'date_relieved'	: forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': COMMON_CLASS,
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'f_name': forms.TextInput(attrs={
		'class': COMMON_CLASS,
		'placeholder': 'First Name',
	}),
	'l_name': forms.TextInput(attrs={
		'class': COMMON_CLASS,
		'placeholder': 'Last Name',
	}),
	'm_name': forms.TextInput(attrs={
		'class': COMMON_CLASS,
		'placeholder': 'Middle Name',
	}),
	'suffix': forms.TextInput(attrs={
		'class': COMMON_CLASS,
		'placeholder': 'Suffix (e.g.: II, Sr., Jr.)',
	}),
	'age': forms.NumberInput(attrs={
		'class': COMMON_CLASS,
	}),
	'address': forms.TextInput(attrs={
		'class': COMMON_CLASS,
	}),
	'civil_status': forms.Select(attrs={
		'class': COMMON_CLASS,
	}),
	'rank': forms.Select(attrs={
		'class': COMMON_CLASS,
	}),
	'designation': forms.TextInput(attrs={
		'class': COMMON_CLASS,
	}),
	'crime_violated': forms.TextInput(attrs={
		'class': COMMON_CLASS,
	}),
}

COMMON_FIELDS = [
	'raw_image',
	'f_name',
	'l_name',
	'm_name',
	'suffix',
	'age',
	'address',
	'civil_status',
	'date_profiled',
]
P_FIELDS = COMMON_FIELDS + [
	'rank',
	'date_assigned',
	'date_relieved',
	'designation',
]
I_FIELDS = COMMON_FIELDS + [
	'date_arrested',
	'date_committed',
	'crime_violated',
]

IMG_VALIDATOR = [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'jfif', 'PNG', 'JPG'])]



class PersonnelForm(forms.ModelForm):
	raw_image = forms.FileField(
		validators=IMG_VALIDATOR,
		allow_empty_file	= True,
		required			= False
		)

	class Meta:
		model 	= models.Personnel
		fields 	= P_FIELDS
		widgets = WIDGETS

class InmateForm(forms.ModelForm):
	raw_image = forms.FileField(
		validators 			= IMG_VALIDATOR,
		allow_empty_file	= True,
		required			= False,
	)

	class Meta:
		model 	= models.Inmate
		fields	= I_FIELDS
		widgets = WIDGETS


