from django.urls import path
from . import views

urlpatterns = [
	path("personnel/all/", views.all_personnel, name="profiles-all-personnel"),
	path("inmate/all/", views.all_inmate, name="profiles-all-inmate"),

	path("<str:p_type>/add/", views.profile_add, name="profile-add"),
	path("<str:p_type>/<int:pk>/", views.profile, name="profile"),
	path("<str:p_type>/<int:pk>/edit/", views.profile_update, name="profile-update"),
	path("<str:p_type>/<int:pk>/delete/", views.profile_delete, name="profile-delete"),
	path("<str:p_type>/all/delete/", views.profile_delete_all, name="profile-delete-all"),
	# path("<str:p_type>/<int:pk>/download/", views.profile_docx_download, name="profile-docx-download"),
    

	path("add/<str:p_type>/<int:pk>/", views.archive_add, name="archive-add"),
	path("remove/<str:p_type>/<int:pk>/", views.archive_remove, name="archive-remove"),
	path("add/<str:p_type>/all/", views.archive_add_all, name="archive-add-all"),
	path("remove/<str:p_type>/all/", views.archive_remove_all, name="archive-remove-all"),
] 