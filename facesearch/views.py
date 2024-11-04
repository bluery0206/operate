from django.shortcuts import render
from .forms import UploadedImageForm
# Create your views here.
def upload_image(request):
	if request.method == "POST":
		form = UploadedImageForm(request.POST, request.FILES)

		if form.is_valid():
			form.save()
	else:
		form = UploadedImageForm()
	return render(request, "facesearch/upload_image.html", {"form": form})