from django.shortcuts import render
from pathlib import Path

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
		"camera"		: 0,
		"profiles"		: []
	}

	if request.method == "POST":
		context['threshold'] = float(request.POST.get("threshold", THRESHOLD))

		is_option_camera = request.POST.get("option_camera", 0)
		is_option_upload = request.POST.get("option_upload", 0)

		image_name	= f"{str(timezone.now().strftime("%Y%m%d%H%M%S"))}.png"
		input_path	= f"media/searches/{image_name}"

		if is_option_camera:
			context['camera'] = int(request.POST.get("camera", 0))

			is_image_taken, input_image = take_image(context['camera'])

			if not is_image_taken:
				return render(request, "facesearch/facesearch.html", context)
			
			save_image(input_path, input_image)

		elif is_option_upload and 'image' in request.FILES: 
			context['form'] = UploadedImageForm(request.POST, request.FILES)
			
			if context['form'].is_valid():
				instance		= context['form'].save()
				input_path	= instance.image.path	

				print(f"{instance=}")
				print(f"{input_path=}")

		print(f"Outisoide{input_path=}")
		
		# get profiles from images
		cand_list	= search(input_path, DATABASE_PATH, context['threshold'])
		context['profiles']	= get_profiles(cand_list, DATABASE_PATH) if cand_list else None

		# Delete the image after use
		instance = UploadedImage.objects.filter(image__endswith=str(image_name).split("\\")[-1]).first()
		instance.delete() if instance else Path(input_path).unlink()
			

	return render(request, "facesearch/facesearch.html", context)

