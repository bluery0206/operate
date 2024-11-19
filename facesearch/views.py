from django.shortcuts import render
from pathlib import Path
import logging

from .forms import UploadedImageForm
from .models import UploadedImage
from .utils import *

logger = logging.getLogger(__name__)

DATABASE_PATH		= Path().cwd().joinpath("media/raw_images")
SEARCH_IMAGE_PATH 	= Path().cwd().joinpath("media/searches")

THRESHOLD = 1.0

def facesearch(request):
	context = {
		"form"			: UploadedImageForm(),
		"page_title"	: "OPERATE | Facesearch",
		"threshold"		: THRESHOLD,
		"camera"		: 0
	}

	if request.method == "POST":
		threshold = float(request.POST.get("threshold", THRESHOLD))
		
		is_option_camera = request.POST.get("open_camera", 0)

		if is_option_camera:
			camera			= int(request.POST.get("camera", 0))
			is_image_taken	= take_image(camera)

			context["camera"] =	camera

			if is_image_taken:
				image_path, frame = is_image_taken
				save_image(image_path, frame)	
				input_path = Path(image_path)
			else:
				return render(request, "facesearch/facesearch.html", context)

		else:
			context['form'] = UploadedImageForm(request.POST, request.FILES)
			
			# change to-save image's name
			time		= timezone.now().strftime("%Y%m%d%H%M%S")
			input_path	= SEARCH_IMAGE_PATH.joinpath(f"{time}.jpg")
			request.FILES['image'].name = input_path

			if context['form'].is_valid(): context['form'].save()

		# get profiles from images
		cand_list			= search(input_path, DATABASE_PATH, threshold)
		context["profiles"] = get_profiles(cand_list, DATABASE_PATH) if cand_list else None

		# Delete the image after use
		instance = UploadedImage.objects.filter(image__endswith=str(input_path).split("\\")[-1]).first()
		instance.delete() if instance else input_path.unlink()

	return render(request, "facesearch/facesearch.html", context)

