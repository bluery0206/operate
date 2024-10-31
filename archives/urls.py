from django.urls import path
from . import views

urlpatterns = [
	path("personnel/", views.personnel, name="archived-personnels"),
	path("inmates/", views.inmate, name="archived-inmates"),

	path("profile/<int:pk>", views.profile, name="archived-profile"),
]