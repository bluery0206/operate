from django import forms
from django.core.validators import FileExtensionValidator

from .models import OperateSetting
from pathlib import Path

exists = OperateSetting.objects.first()
print(exists)

if not exists:
    inmate_template 	= str(list(Path.cwd().glob("media/templates/profile_inmate_templa*.docx"))[0])
    personnel_template 	= str(list(Path.cwd().glob("media/templates/profile_personnel_templa*.docx"))[0])
    model 				= str(list(Path.cwd().glob("media/models/*.onnx"))[0])

    OperateSetting.objects.create(
		personnel_template	= personnel_template, 
		inmate_template		= inmate_template,
		model				= model
	)

WIDGETS = {
	'default_threshold' : forms.NumberInput(attrs={
			'class': 'form-control form-control-primary',
			'min': 0,
			'max': 2000,
			'step': "any",
    }),
	'default_camera' : forms.NumberInput(attrs={
			'class': 'form-control form-control-primary',
			'min': 0,
			'max': 10,
			'step': 1,
	}),
	'default_profiles_per_page' : forms.NumberInput(attrs={
			'class': 'form-control form-control-primary',
			'min': 10,
			'step': 1,
	}),
	'default_thumbnail_size' : forms.NumberInput(attrs={
			'class': 'form-control form-control-primary',
			'min': 100,
			'step': 10,
	}),
	'crop_camera' : forms.Select(attrs={
		'class': 'form-control form-control-primary',
	    },
		choices={('0', 'False'), ('1', 'True')}
	),
	'default_crop_size' : forms.NumberInput(attrs={
			'class': 'form-control form-control-primary',
			'min': 100,
			'step': 10,
	}),
	'default_search_method': forms.Select(attrs={
		'class': 'form-control form-control-primary',
	    },
		choices={('0', 'Image'), ('1', 'Embedding (Faster)')}
	),
	'personnel_template' : forms.FileInput(attrs={
		'class': 'form-control form-control-primary',
	}),
	'inmate_template': forms.FileInput(attrs={
		'class': 'form-control form-control-primary',
	}),
	'model': forms.FileInput(attrs={
		'class': 'form-control form-control-primary',
	}),
}

FIELDS = [
	"default_threshold",
    "default_camera",
    "default_profiles_per_page",
    "default_thumbnail_size",
    "crop_camera",
	"default_crop_size",
    "default_search_method",
    "personnel_template",
    "inmate_template",
    "model",
]

VALIDATOR = [FileExtensionValidator(allowed_extensions=['docx'])]
MODEL_VALIDATOR = [FileExtensionValidator(allowed_extensions=['onnx'])]

class OperateSettingsForm(forms.ModelForm):
	personnel_template  	= forms.FileField(
		validators			= VALIDATOR,
		widget				= forms.FileInput(attrs={'class': 'form-control form-control-primary'}),
		allow_empty_file	= True,
		required			= False
    )
	inmate_template = forms.FileField(
		validators			= VALIDATOR,
		widget				= forms.FileInput(attrs={'class': 'form-control form-control-primary'}),
		allow_empty_file	= True,
		required			= False
    )
	model = forms.FileField(
		validators 			= MODEL_VALIDATOR,
		widget				= forms.FileInput(attrs={'class': 'form-control form-control-primary'}),
		allow_empty_file	= True,
		required			= False
    )
	
	class Meta:
		model 	= OperateSetting
		fields 	= FIELDS
		widgets = WIDGETS
		
		
		
		
		
		
		
		
		