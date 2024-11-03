from django.contrib.auth.models import User
from django import forms
from home.utils import get_full_name
from django.core.validators import FileExtensionValidator

from .models import (
	Personnel, 
	Inmate,
	Template
)

class CreatePersonnel(forms.ModelForm):
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


class UpdatePersonnel(forms.ModelForm):
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


class CreateInmate(forms.ModelForm):
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


class UpdateInmate(forms.ModelForm):
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

class TemplateUploadForm(forms.ModelForm):
	template = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['docx'])])

	class Meta:
		model = Template
		fields = [
			'template_name',
			'template',
		]