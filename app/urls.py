from django.urls import path
from . import views

urlpatterns = [
	path("", views.index, name="operate-index"),
	path("settings/", views.settings, name="operate-settings")
]
