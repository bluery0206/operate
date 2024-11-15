from django.shortcuts import render
from pathlib import Path

from .forms import UploadedImageForm
from .utils import *

DATABASE_PATH		= Path().cwd().joinpath("media/raw_images")
SEARCH_IMAGE_PATH 	= Path().cwd().joinpath("media/searches")

THRESHOLD = 10

def facesearch(request):
	context = {
		"form": UploadedImageForm()
	}

	if request.method == "POST":
		is_option_camera = request.POST.get("open_camera", 0)

		if is_option_camera:
			input_path	= take_image()

			if not input_path:	return render(request, "facesearch/facesearch.html", context)

			input_path = Path(input_path)
		else:
			context['form'] = UploadedImageForm(request.POST, request.FILES)
			
			# change to-save image's name
			time		= timezone.now().strftime("%Y%m%d%H%M%S")
			input_path	= SEARCH_IMAGE_PATH.joinpath(f"{time}.jpg")
			request.FILES['image'].name = input_path
			
			if context['form'].is_valid():	context['form'].save()

		cand_list = search(input_path, DATABASE_PATH, THRESHOLD)

		context["profiles"] = get_profiles(cand_list, DATABASE_PATH) if cand_list else None

		# Delete the image after use
		input_path.unlink()

	return render(request, "facesearch/facesearch.html", context)

