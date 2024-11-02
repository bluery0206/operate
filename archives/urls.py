from django.urls import path
from . import views

urlpatterns = [
	path("personnel/", views.personnels, name="archives-personnels"),
	path("inmates/", views.inmates, name="archives-inmates"),

	path("personnel/profile/<int:pk>/", views.archive_profile_personnel, name="archive-personnel-profile"),
	path("inmate/profile/<int:pk>/", views.archive_profile_inmate, name="archive-inmate-profile"),

	path("personnel/add/<int:pk>/", views.archive_personnel_add, name="archive-personnel-add"),
	path("inmate/add/<int:pk>/", views.archive_inmate_add, name="archive-inmate-add"),
	
	path("personnel/remove/<int:pk>/", views.archive_personnel_remove, name="archive-personnel-remove"),
	path("inmate/remove/<int:pk>/", views.archive_inmate_remove, name="archive-inmate-remove"),

	# path("archives/remove/<int:pk>/", views.remove, name="archives-remove"),

]