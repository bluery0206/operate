from django.urls import path
from . import views

urlpatterns = [
	path("archives/personnel/", views.personnel, name="archives-personnels"),
	path("archives/inmates/", views.inmate, name="archives-inmates"),
	path("archives/add/<int:pk>/", views.archive, name="archives-add"),

	path("profile/<int:object>/", views.profile, name="archived-profile"),
]