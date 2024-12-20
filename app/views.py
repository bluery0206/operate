from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings as DJANGO_SETTINGS

from pathlib import Path

from . import (
    models 	as app_models,
    forms 	as app_forms,
	utils	as app_utils
)
from profiles.models import (
    Personnel, 
    Inmate
)



OPERATE_SETTINGS = app_models.Setting

DEFAULT_SETTINGS_FORM 	= app_forms.DefaultSettingsForm
DEFAULT_SETTINGS 		= app_models.Setting


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
	return render(request, "app/user/login.html", context)



def password_reset_confirm(request, uidb64, token):
	login_form = app_forms.PasswordResetForm

	try:
		uid = urlsafe_base64_decode(uidb64).decode()
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	# Check if the token is valid for the user
	if user is None or not default_token_generator.check_token(user, token):
		return render(request, "app/user/password_reset_invalid.html")

	if request.method == "POST":
		form = login_form(user, request.POST)

		if form.is_valid():
			form.save()

			return redirect('password_reset_complete')
	else:
		form = login_form(user)

	context = {
		'page_title'	: 'User login',
		'title'			: 'User login',
		'form'			: form,
	}
	return render(request, "app/user/password_reset_confirm.html", context)



@login_required
def facesearch(request):
	prev_page 	= request.GET.get("prev", "/")
	curr_page	= request.build_absolute_uri()

	defset = OPERATE_SETTINGS.objects.first()

	form_class	= app_forms.SearchImageForm
	form_model	= app_models.SearchImage
	form 		= form_class()
	threshold	= defset.threshold
	search_mode = defset.search_mode
	camera		= defset.camera
	profiles	= []

	if request.method == "POST":
		is_option_camera	= int(request.POST.get("option_camera", 0))
		is_option_upload	= int(request.POST.get("option_upload", 0))

		curr_time	= str(timezone.now().strftime("%Y%m%d%H%M%S"))
		image_name	= curr_time + ".png"

		input_path	= DJANGO_SETTINGS.MEDIA_ROOT.joinpath(image_name)

		if is_option_camera:
			camera = int(request.POST.get("camera", defset.camera))

			is_image_taken, input_image = app_utils.take_image(
				camera		= camera, 
				clip_camera = defset.clip_camera, 
				clip_size	= defset.clip_size
			)

			if not is_image_taken:
				return render(curr_page)
			
			app_utils.save_image(Path(input_path), input_image)

		elif is_option_upload and 'image' in request.FILES: 
			form = form_class(request.POST, request.FILES)
			
			if form.is_valid():
				instance	= form.save()
				input_path	= instance.image.path

		# get profiles from images
		cand_list	= app_utils.search(
			input_path	= input_path, 
			threshold	= threshold, 
			search_mode	= search_mode
		)
		# search_mode			
		profiles = app_utils.get_profiles(
			cand_list	= cand_list,
			reverse		= True,							 
			search_mode	= search_mode					 
		) if cand_list else None

		# Delete the image after use
		instance = form_model.objects.filter(image__icontains=Path(input_path).stem).first()
		instance.delete() if instance else Path(input_path).unlink()
	
	context = {
		"page_title"	: "Facesearch",
		'active'		: 'facesearch',
		"form"			: form,
		"threshold"		: threshold,
		"camera"		: camera,
		"profiles"		: profiles,
	}
	return render(request, "app/facesearch.html", context)










