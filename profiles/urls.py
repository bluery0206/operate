from django.urls import path
from . import views

urlpatterns = [
	path("profile/all/", views.home, name="profiles")
]