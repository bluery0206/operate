from django import forms
from django.core.validators import FileExtensionValidator
from django.conf import settings

from . import models as app_models

DJANGO_SETTINGS 	= settings
OPERATE_SETTINGS 	= app_models.Setting

COMMON_ATTRS    = {'class': 'form-control form-control-primary'}

class DefaultSettingsForm(forms.ModelForm):
	docx_validator	= [FileExtensionValidator(allowed_extensions=['docx'])]
	
	personnel_template = forms.FileField(
		validators			= docx_validator,
		widget				= forms.FileInput(attrs={'class': COMMON_ATTRS}),
		allow_empty_file	= True,
		required			= False
    )
	inmate_template = forms.FileField(
		validators			= docx_validator,
		widget				= forms.FileInput(attrs={'class': COMMON_ATTRS}),
		allow_empty_file	= True,
		required			= False
    )
	model = forms.FileField(
		validators 			= [FileExtensionValidator(allowed_extensions=['onnx'])],
		widget				= forms.FileInput(attrs={'class': COMMON_ATTRS}),
		allow_empty_file	= True,
		required			= False
    )
	
	class Meta:
		model 	= OPERATE_SETTINGS
		widgets	= {
			'default_threshold': forms.NumberInput(attrs={
					'class' : 'form-control form-control-primary',
					'min'   : 0,
					'max'   : 2000,
					'step'  : "any",
			}),
			'default_camera' : forms.NumberInput(attrs={
					'class' : 'form-control form-control-primary',
					'min'   : 0,
					'max'   : 10,
					'step'  : 1,
			}),
			'default_profiles_per_page': forms.NumberInput(attrs={
					'class' : 'form-control form-control-primary',
					'min'   : 10,
					'max'   : 50,
					'step'  : 1,
			}),
			'default_thumbnail_size': forms.NumberInput(attrs={
					'class' : 'form-control form-control-primary',
					'min'   : 100,
					'step'  : 10,
			}),
			'crop_camera': forms.Select(attrs={
					'class': 'form-control form-control-primary',
				},
				choices={('0', 'False'), ('1', 'True')}
			),
			'default_crop_size': forms.NumberInput(attrs={
					'class' : 'form-control form-control-primary',
					'min'   : 100,
					'step'  : 10,
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
		fields 	= [
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


class SearchImageForm(forms.ModelForm):
	image = forms.FileField(
		validators	= [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'jfif', 'PNG', 'JPG'])],
		widget		= forms.FileInput(attrs={'class': COMMON_ATTRS}),
	)

	class Meta:
		model	= app_models.SearchImage
		fields	= ['image']
		












# from django import forms
# from django_password_eye.fields import PasswordEye
# from django.contrib.auth.models import User

# from django.contrib.auth.forms import AuthenticationForm
# # Create your models here.

# class LoginForm(AuthenticationForm):
#     password = PasswordEye(label='')

#     class Meta: 
#         model = User

#         fields = ['username', 'password']
#         widgets = {
#             'password': forms.PasswordInput(attrs={
#                 'class': 'form-control form-control-primary',
#             }),
#         }
