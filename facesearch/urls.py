from django.urls import path
from . import views

urlpatterns = [
	path("upload_image/", views.upload_image, name="facesearch-upload_image"),
	# path("open_camera/", views.open_camera, name="facesearch-open_camera"),
]