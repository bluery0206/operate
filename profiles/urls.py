from django.urls import path
from . import views

urlpatterns = [
	path("personnels/", views.personnels, name="profiles-personnels"),
	path("inmates/", views.inmates, name="profiles-inmates"),

	path("<str:p_type>/<int:pk>/", views.profile, name="profile"),
	path("<str:p_type>/add/", views.profile_add, name="profile-add"),
	path("<str:p_type>/<int:pk>/edit/", views.profile_update, name="profile-update"),
	path("<str:p_type>/<int:pk>/delete/", views.profile_delete, name="profile-delete"),
	path("<str:p_type>/<int:pk>/download/", views.profile_docx_download, name="profile-docx-download"),
] 