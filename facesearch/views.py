from django.shortcuts import render
from pathlib import Path

from .forms import UploadedImageForm
from .models import UploadedImage
from .utils import *
from settings.views import OPERATE_SETTINGS

logger = logging.getLogger(__name__)

DATABASE_PATH		= Path().cwd().joinpath("media/raw_images")
SEARCH_IMAGE_PATH 	= Path().cwd().joinpath("media/searches")

def facesearch(request):
	context = {
		"form"			: UploadedImageForm(),
		"page_title"	: "Facesearch",
		"threshold"		: OPERATE_SETTINGS.default_threshold,
		"camera"		: OPERATE_SETTINGS.default_camera,
		"search_method" : OPERATE_SETTINGS.default_search_method,
		"profiles"		: [],
		"p_type"		: "personnel"
	}

	context['camera'] = int(request.GET.get("camera", OPERATE_SETTINGS.default_camera))

	if request.method == "POST":
		context['threshold'] = float(request.POST.get("threshold", OPERATE_SETTINGS.default_threshold))

		is_option_camera	= int(request.POST.get("option_camera", 0))
		is_option_upload	= int(request.POST.get("option_upload", 0))
		context['search_method'] = int(request.POST.get("search_method", OPERATE_SETTINGS.default_search_method))
		print(f"facesearch(): {is_option_camera = }")
		print(f"facesearch(): {is_option_upload = }")
		print(f"facesearch(): {context['search_method'] = }")

		image_name	= f"{str(timezone.now().strftime("%Y%m%d%H%M%S"))}.png"
		input_path	= f"media/searches/{image_name}"
		print(f"facesearch(): {image_name = }")
		print(f"facesearch(): {input_path = }")

		if is_option_camera:
			context['camera'] = int(request.POST.get("camera", OPERATE_SETTINGS.default_camera))

			is_image_taken, input_image = take_image(context['camera'], OPERATE_SETTINGS.crop_camera, OPERATE_SETTINGS.default_crop_size)

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
			cand_list	= cand_list,
			reverse		= True,							 
			by_array	= context['search_method']							 
		) if cand_list else None

		# Delete the image after use
		instance = UploadedImage.objects.filter(image__endswith=str(image_name).split("\\")[-1]).first()
		instance.delete() if instance else Path(input_path).unlink()
			

	return render(request, "facesearch/facesearch.html", context)

