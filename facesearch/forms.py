from django.contrib.auth.models import User
from django import forms
from app.utils import get_full_name
from django.core.validators import FileExtensionValidator
from .models import UploadedImage

class UploadedImageForm(forms.ModelForm):
	image = forms.FileField(
		widget		= forms.FileInput(attrs={'class': 'form-control form-control-primary'}),
		validators	= [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'jfif', 'PNG', 'JPG'])]
	)

	class Meta:
		model	= UploadedImage
		fields	= ['image']
		


