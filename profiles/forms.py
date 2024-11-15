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
		widgets = {
            'date_profiled': forms.DateInput(attrs={
                'type': 'date',
            }),
            'date_assigned': forms.DateInput(attrs={
                'type': 'date',
            }),
            'date_relieved': forms.DateInput(attrs={
                'type': 'date',
            }),
        }


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
		widgets = {
            'date_profiled': forms.DateInput(attrs={
                'type': 'date',
            }),
            'date_assigned': forms.DateInput(attrs={
                'type': 'date',
            }),
            'date_relieved': forms.DateInput(attrs={
                'type': 'date',
            }),
        }



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
		widgets = {
            'date_profiled': forms.DateInput(attrs={
                'type': 'date',
            }),
            'date_arrested': forms.DateInput(attrs={
                'type': 'date',
            }),
            'date_committed': forms.DateInput(attrs={
                'type': 'date',
            }),
        }



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
		widgets = {
            'date_profiled': forms.DateInput(attrs={
                'type': 'date',
            }),
            'date_arrested': forms.DateInput(attrs={
                'type': 'date',
            }),
            'date_committed': forms.DateInput(attrs={
                'type': 'date',
            }),
        }

class TemplateUploadForm(forms.ModelForm):
	template = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['docx'])])

	class Meta:
		model = Template
		fields = [
			'template_name',
			'template',
		]