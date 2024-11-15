from django.urls import path
from . import views

urlpatterns = [
	path("personnels/", views.personnels, name="profiles-personnels"),
	path("inmates/", views.inmates, name="profiles-inmates"),



	path("<str:p_type>/<int:pk>/", views.profile, name="profile"),
	path("<str:p_type>/<int:pk>/edit/", views.profile_update, name="profile-update"),
    

    
	path("personnel/<int:pk>/", views.profile_personnel, name="profile-personnel"),
	path("inmate/<int:pk>/", views.profile_inmate, name="profile-inmate"),

	path("personnel/<int:pk>/update/", views.profile_personnel_update, name="profile-personnel-update"),
	path("inmate/<int:pk>/update/", views.profile_inmate_update, name="profile-inmate-update"),

	path("personnel/add/", views.profile_personnel_add, name="profile-personnel-add"),
	path("inmate/add/", views.profile_inmate_add, name="profile-inmate-add"),

	path("personnel/delete/<int:pk>/", views.profile_personnel_delete, name="profile-personnel-delete"),
	path("inmate/delete/<int:pk>/", views.profile_inmate_delete, name="profile-inmate-delete"),

	path("generate/inmate/docx/<int:pk>", views.profile_inmate_to_docx, name="profile-inmate-to-docx"),
	path("generate/personnel/docx/<int:pk>", views.profile_personnel_to_docx, name="profile-personnel-to-docx"),

	path("personnel/delete/all/", views.delete_all_personnel, name="delete-all-personnel"),
	path("inmate/delete/all/", views.delete_all_inmate, name="delete-all-inmate"),
] 