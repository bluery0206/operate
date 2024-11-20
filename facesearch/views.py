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
		"page_title"	: "Facesearch",
		"threshold"		: THRESHOLD,
		"camera"		: 0,
		"search_method" : 1,
		"profiles"		: [],
		"p_type"		: "personnel"
	}

	context['camera'] = int(request.GET.get("camera", 0))

	if request.method == "POST":
		context['threshold'] = float(request.POST.get("threshold", THRESHOLD))

		is_option_camera	= int(request.POST.get("option_camera", 0))
		is_option_upload	= int(request.POST.get("option_upload", 0))
		context['search_method'] = int(request.POST.get("search_method", 0))
		print(f"facesearch(): {is_option_camera = }")
		print(f"facesearch(): {is_option_upload = }")
		print(f"facesearch(): {context['search_method'] = }")

		image_name	= f"{str(timezone.now().strftime("%Y%m%d%H%M%S"))}.png"
		input_path	= f"media/searches/{image_name}"
		print(f"facesearch(): {image_name = }")
		print(f"facesearch(): {input_path = }")

		if is_option_camera:
			context['camera'] = int(request.POST.get("camera", 0))

			is_image_taken, input_image = take_image(context['camera'], True, 200)

			if not is_image_taken:
				return render(request, "facesearch/facesearch.html", context)
			
			save_image(input_path, input_image)

		elif is_option_upload and 'image' in request.FILES: 
			context['form'] = UploadedImageForm(request.POST, request.FILES)
			
			if context['form'].is_valid():
				instance	= context['form'].save()
				input_path	= instance.image.path	

		# print(f"facesearch(): input_image: {"Found" if input_image is not None else "Not found."}")
		# print(f"facesearch(): {input_image.shape = }")
		print(f"facesearch(): {input_path = }")
		
		# get profiles from images
		cand_list	= search(
			input_path	= input_path, 
			threshold	= context['threshold'], 
			by_array	= context['search_method']
		)

		context['profiles']	= get_profiles(
			cand_list=cand_list,
			reverse=True,							 
			by_array= context['search_method']							 
		) if cand_list else None

		# Delete the image after use
		instance = UploadedImage.objects.filter(image__endswith=str(image_name).split("\\")[-1]).first()
		instance.delete() if instance else Path(input_path).unlink()
			

	return render(request, "facesearch/facesearch.html", context)

