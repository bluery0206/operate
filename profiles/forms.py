from django.contrib.auth.models import User
from django import forms
from home.utils import get_full_name
from django.core.validators import FileExtensionValidator

from .models import (
	Personnel, 
	Inmate,
	Template
)

WIDGETS = {
	'date_profiled'	: forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': 'form-control form-control-primary',
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'date_arrested'	: forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': 'form-control form-control-primary',
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'date_committed': forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': 'form-control form-control-primary',
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'date_assigned'	: forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': 'form-control form-control-primary',
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'date_relieved'	: forms.DateInput(
		attrs	= {
			'type': 'datetime-local',
			'class': 'form-control form-control-primary',
			}, 
		format 	= '%Y-%m-%dT%H:%M'
	),
	'f_name': forms.TextInput(attrs={
		'class': 'form-control form-control-primary',
		'placeholder': 'First Name',
	}),
	'l_name': forms.TextInput(attrs={
		'class': 'form-control form-control-primary',
		'placeholder': 'Last Name',
	}),
	'm_name': forms.TextInput(attrs={
		'class': 'form-control form-control-primary',
		'placeholder': 'Middle Name',
	}),
	'suffix': forms.TextInput(attrs={
		'class': 'form-control form-control-primary',
		'placeholder': 'Suffix (e.g.: II, Sr., Jr.)',
	}),
	'age': forms.NumberInput(attrs={
		'class': 'form-control form-control-primary',
	}),
	'address': forms.TextInput(attrs={
		'class': 'form-control form-control-primary',
	}),
	'civil_status': forms.Select(attrs={
		'class': 'form-control form-control-primary',
	}),
	'rank': forms.Select(attrs={
		'class': 'form-control form-control-primary',
	}),
	'designation': forms.TextInput(attrs={
		'class': 'form-control form-control-primary',
	}),
	'crime_violated': forms.TextInput(attrs={
		'class': 'form-control form-control-primary',
	}),
}

class CreatePersonnel(forms.ModelForm):
	raw_image = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'jfif', 'PNG', 'JPG'])])

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
		widgets = WIDGETS

class UpdatePersonnel(forms.ModelForm):
	raw_image = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'jfif', 'PNG', 'JPG'])])
	
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
		widgets = WIDGETS

class CreateInmate(forms.ModelForm):
	raw_image = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'jfif', 'PNG', 'JPG'])])
	
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
		widgets = WIDGETS

class UpdateInmate(forms.ModelForm):
	raw_image = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'jfif', 'PNG', 'JPG'])])
	
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
		widgets = WIDGETS

class TemplateUploadForm(forms.ModelForm):
	template = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['docx'])])

	class Meta:
		model = Template
		fields = [
			'template_name',
			'template',
		]