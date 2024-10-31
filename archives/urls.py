from django.urls import path
from . import views

urlpatterns = [
	path("archives/", views.home, name="archives-home")
]