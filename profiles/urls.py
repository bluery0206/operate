from django.urls import path
from . import views

urlpatterns = [
	path("personnel/", views.personnels, name="profiles-personnels"),
	path("inmates/", views.inmates, name="profiles-inmates"),

	path("personnel/<int:pk>/", views.profile_personnel, name="profile-personnel"),
	path("inmate/<int:pk>/", views.profile_inmate, name="profile-inmate"),

	path("personnel/<int:pk>/update/", views.profile_personnel_update, name="profile-personnel-update"),
	path("inmate/<int:pk>/update/", views.profile_inmate_update, name="profile-inmate-update"),

	path("personnel/add/", views.profile_personnel_add, name="profile-personnel-add"),
	path("inmate/add/", views.profile_inmate_add, name="profile-inmate-add"),

	path("personnel/delete/<int:pk>/", views.profile_personnel_delete, name="profile-personnel-delete"),
	path("inmate/delete/<int:pk>/", views.profile_inmate_delete, name="profile-inmate-delete"),
] 