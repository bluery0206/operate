from django.urls import path
from . import views

urlpatterns = [
	path("personnel/", views.personnels, name="profiles-personnels"),
	path("inmates/", views.inmates, name="profiles-inmates"),

	path("profile/<int:pk>", views.profile, name="profile"),
]