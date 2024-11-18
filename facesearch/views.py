from django.shortcuts import render
from pathlib import Path
import logging

from .forms import UploadedImageForm
from .models import UploadedImage
from .utils import *

logger = logging.getLogger(__name__)

DATABASE_PATH		= Path().cwd().joinpath("media/raw_images")
SEARCH_IMAGE_PATH 	= Path().cwd().joinpath("media/searches")

THRESHOLD = 1000

def facesearch(request):
	context = {
		"form": UploadedImageForm(),
		'page_title'	: "OPERATE | Facesearch"
	}

	if request.method == "POST":
		
		try:
			is_option_camera = request.POST.get("open_camera", 0)

			if is_option_camera:
				camera = request.POST.get("camera", 0)

				input_path = take_image(camera)

				if input_path:	
					input_path = Path(input_path)
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
			cand_list			= search(input_path, DATABASE_PATH, THRESHOLD)
			context["profiles"] = get_profiles(cand_list, DATABASE_PATH) if cand_list else None

			# Delete the image after use
			instance = UploadedImage.objects.filter(image__endswith=str(input_path).split("\\")[-1]).first()
			instance.delete() if instance else input_path.unlink()

		except BrokenPipeError:
			logging.error("Client disconnected before response was fully sent.")

	return render(request, "facesearch/facesearch.html", context)

