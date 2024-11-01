from django.urls import path
from . import views

urlpatterns = [
	path("archives/personnel/", views.personnel, name="archives-personnels"),
	path("archives/inmates/", views.inmate, name="archives-inmates"),

	path("profile/<int:pk>/", views.profile, name="archives-profile"),

	path("archives/add/<int:pk>/", views.archive, name="archive-add"),
	path("archives/remove/<int:pk>/", views.remove, name="archives-remove"),

]