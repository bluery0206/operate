from django import forms
from django_password_eye.fields import PasswordEye
from django.contrib.auth.models import User

from django.contrib.auth.forms import AuthenticationForm
# Create your models here.

class LoginForm(AuthenticationForm):
    password = PasswordEye(label='')

    class Meta: 
        model = User

        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={
                'class': 'form-control form-control-primary',
            }),
        }
