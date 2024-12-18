from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings as DJANGO_SETTINGS

from pathlib import Path

from .utils import *

from . import (
    models 	as app_models,
    forms 	as app_forms,
)
from profiles.models import (
    Personnel, 
    Inmate
)

OPERATE_SETTINGS = app_models.Setting

DEFAULT_SETTINGS_FORM 	= app_forms.DefaultSettingsForm
DEFAULT_SETTINGS 		= app_models.Setting

IMAGE_SEARCH_FORM		= app_forms.SearchImageForm


@login_required
def index(request):
	# Get five (5) recently created profiles that are not archived
	personnels 	= Personnel.objects.filter(is_archived=False).order_by("-date_profiled")[:5]
	inmates 	= Inmate.objects.filter(is_archived=False).order_by("-date_profiled")[:5]

	context = {
		'page_title'	: "Home",
		'active'		: "home",
		"personnels"	: personnels,
		"inmates"		: inmates,
	}
	return render(request, "app/index.html", context)


@login_required
def settings(request):
	defset 	= DEFAULT_SETTINGS.objects.first()
	form	= DEFAULT_SETTINGS_FORM(instance=defset)

	if request.method == "POST":
		form = DEFAULT_SETTINGS_FORM(request.POST, request.FILES, instance=defset)

		if form.is_valid():
			if not request.FILES.get('template_inmate'):
				form.instance.template_inmate = defset.template_inmate

			if not request.FILES.get('template_personnel'):
				form.instance.template_personnel = defset.template_personnel

			if not request.FILES.get('model'):
				form.instance.model = defset.model

			form.save()

			# if request.FILES.get('model'):
			# 	update_image_embeddings()

			return redirect('operate-settings')

	context = {
		'page_title'	: 'Settings',
		'active'		: 'settings',
		'defset'		: defset,
		'form'			: form,
	}
	return render(request, "app/settings.html", context)



def user_login(request):
	login_form = app_forms.LoginForm

	if request.method == "POST":
		form = login_form(request, data=request.POST)

		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('operate-index')
			else:
				form.add_error(None, "Invalid username or password")
	else:
		form = login_form()

	context = {
		'page_title'	: 'User login',
		'title'			: 'User login',
		'form'			: form,
	}
	return render(request, "app/base_public.html", context)





DATABASE_PATH		= DJANGO_SETTINGS.MEDIA_ROOT.joinpath("raw_images")
SEARCH_IMAGE_PATH 	= DJANGO_SETTINGS.MEDIA_ROOT.joinpath("searches")

# @login_required
# def facesearch(request):
# 	default = OPERATE_SETTINGS.objects.first()


# 	context = {
# 		"page_title"	: "Facesearch",
# 		'active'		: 'facesearch',
# 		"form"			: IMAGE_SEARCH_FORM(),
# 		"threshold"		: float(default.threshold),
# 		"camera"		: int(default.camera),
# 		"search_method" : int(default.search_mode),
# 		"profiles"		: [],
# 	}

# 	context['camera'] = int(request.GET.get("camera", context['camera']))

# 	if request.method == "POST":
# 		context['threshold'] = float(request.POST.get("threshold", context['threshold']))

# 		is_option_camera	= int(request.POST.get("option_camera", 0))
# 		is_option_upload	= int(request.POST.get("option_upload", 0))
# 		context['search_method'] = int(request.POST.get("search_method", context['search_method']))
# 		print(f"facesearch(): {is_option_camera = }")
# 		print(f"facesearch(): {is_option_upload = }")
# 		print(f"facesearch(): {context['search_method'] = }")

# 		image_name	= f"{str(timezone.now().strftime("%Y%m%d%H%M%S"))}.png"
# 		input_path	= f"media/searches/{image_name}"
# 		print(f"facesearch(): {image_name = }")
# 		print(f"facesearch() 1: {input_path = }")

# 		if is_option_camera:
# 			context['camera'] = int(request.POST.get("camera", defset.default_camera))

# 			is_image_taken, input_image = take_image(context['camera'], int(defset.crop_camera), int(defset.default_crop_size))

# 			if not is_image_taken:
# 				return render(request, "facesearch/facesearch.html", context)
			
# 			save_image(Path(input_path), input_image)

# 		elif is_option_upload and 'image' in request.FILES: 
# 			context['form'] = UploadedImageForm(request.POST, request.FILES)
			
# 			if context['form'].is_valid():
# 				instance	= context['form'].save()
# 				input_path	= instance.image.path
				

# 		# print(f"facesearch(): input_image: {"Found" if input_image is not None else "Not found."}")
# 		# print(f"facesearch(): {input_image.shape = }")
# 		print(f"facesearch() 2: {input_path = }")
		
# 		# get profiles from images
# 		cand_list	= search(
# 			input_path	= input_path, 
# 			threshold	= context['threshold'], 
# 			by_array	= context['search_method']
# 		)

# 		context['profiles']	= get_profiles(
# 			cand_list	= cand_list,
# 			reverse		= True,							 
# 			by_array	= context['search_method']							 
# 		) if cand_list else None

# 		# Delete the image after use
# 		instance = UploadedImage.objects.filter(image__icontains=str(input_path).split("\\")[-1].split(".")[0]).first()
# 		instance.delete() if instance else Path(input_path).unlink()

# 	return render(request, "facesearch/facesearch.html", context)










