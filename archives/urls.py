from django.urls import path
from . import views

urlpatterns = [
	path("personnel/", views.personnels, name="archives-personnels"),
	path("inmates/", views.inmates, name="archives-inmates"),

	path("add/<str:p_type>/<int:pk>/", views.archive_add, name="archive-add"),
	path("remove/<str:p_type>/<int:pk>/", views.archive_remove, name="archive-remove"),
	path("add/<str:p_type>/all/", views.archive_add_all, name="archive-add-all"),
	path("remove/<str:p_type>/all/", views.archive_remove_all, name="archive-remove-all"),
]

	# path("archives/remove/<int:pk>/", views.remove, name="archives-remove"),

