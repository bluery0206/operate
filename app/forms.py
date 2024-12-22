from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.core.validators import FileExtensionValidator
from django.conf import settings as DJANGO_SETTINGS
from django import forms

from django_password_eye.widgets import PasswordEyeWidget
from django_password_eye.fields import PasswordEye

from .models import  (
	Setting 	as OPERATE_SETTINGS,
	SearchImage
)



COMMON_CLASS = 'form-control'



class OperateSettingsForm(forms.ModelForm):
	docx_validator	= [FileExtensionValidator(allowed_extensions=['docx'])]
	
	template_personnel = forms.FileField(
		validators			= docx_validator,
		widget				= forms.FileInput(attrs={'class': COMMON_CLASS}),
		allow_empty_file	= True,
		required			= False
    )
	template_inmate = forms.FileField(
		validators			= docx_validator,
		widget				= forms.FileInput(attrs={'class': COMMON_CLASS}),
		allow_empty_file	= True,
		required			= False
    )
	model = forms.FileField(
		validators 			= [FileExtensionValidator(allowed_extensions=['onnx'])],
		widget				= forms.FileInput(attrs={'class': COMMON_CLASS}),
		allow_empty_file	= True,
		required			= False
    )
	
	class Meta:
		model 	= OPERATE_SETTINGS
		widgets	= {
			'profiles_per_page': forms.NumberInput(attrs={
					'class' : COMMON_CLASS,
					'min'   : 10,
					'max'   : 50,
					'step'  : 1,
			}),
			'thumbnail_size': forms.NumberInput(attrs={
					'class' : COMMON_CLASS,
					'min'   : 100,
					'step'  : 1,
			}),
			'camera' : forms.NumberInput(attrs={
					'class' : COMMON_CLASS,
					'min'   : 0,
					'max'   : 10,
					'step'  : 1,
			}),
			'clip_camera': forms.Select(attrs={
					'class': COMMON_CLASS,
				},
				choices=[(False, 'Use camera size'), (True, 'Clip camera')]
			),
			'clip_size': forms.NumberInput(attrs={
					'class' : COMMON_CLASS,
					'min'   : 100,
					'step'  : 1,
			}),
			'threshold': forms.NumberInput(attrs={
					'class' : COMMON_CLASS,
					'min'   : 0,
					'max'   : 2000,
					'step'  : "any",
			}),
			'search_mode': forms.Select(attrs={
					'class': COMMON_CLASS,
				},
			),
			'template_personnel' : forms.FileInput(attrs={
				'class': COMMON_CLASS,
			}),
			'template_inmate': forms.FileInput(attrs={
				'class': COMMON_CLASS,
			}),
			'model': forms.FileInput(attrs={
				'class': COMMON_CLASS,
			}),
		}
		fields 	= [
			"profiles_per_page",
			"thumbnail_size",
			"camera",
			"clip_camera",
			"clip_size",
			"threshold",
			"search_mode",
			"template_personnel",
			"template_inmate",
			"model",
		]



class SearchImageForm(forms.ModelForm):
	image = forms.FileField(
		validators	= [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'jfif', 'PNG', 'JPG'])],
		widget		= forms.FileInput(attrs={'class': COMMON_CLASS}),
	)

	class Meta:
		model	= SearchImage
		fields	= ['image']
		


class LoginForm(AuthenticationForm):
    password = PasswordEye(label='', widget=PasswordEyeWidget(independent=True))

    class Meta: 
        model 	= User
        fields 	= ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={
                'class': COMMON_CLASS,
            }),
            'username': forms.TextInput(attrs={
                'class': COMMON_CLASS,
            }),
        }



class PasswordResetForm(SetPasswordForm):
    new_password1 = PasswordEye(label='', widget=PasswordEyeWidget(independent=True))
    new_password2 = PasswordEye(label='', widget=PasswordEyeWidget(independent=True))

    class Meta: 
        model 	= User
        fields 	= ['new_password1', 'new_password2']
        widgets = {
            'new_password1': forms.PasswordInput(attrs={
                'class': COMMON_CLASS,
            }),
            'new_password2': forms.PasswordInput(attrs={
                'class': COMMON_CLASS,
            }),
        }