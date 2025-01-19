from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings as DJANGO_SETTINGS

from pathlib import Path
from uuid import uuid4

from . import (
    models 	as app_models,
    forms 	as app_forms,
	utils	as app_utils
)
from profiles.models import (
    Personnel, 
    Inmate
)

import logging

from operate.excepts import *
from operate.facesearch import Facesearch
from operate.embedding_generator import update_embeddings
from operate import (
	camera,
	model_loader as mload,
	image_handler as imhand,
)

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

OPERATE_SETTINGS_FORM 	= app_forms.OperateSettingsForm
OPERATE_SETTINGS 		= app_models.Setting



@login_required
def index(request):
	# Get five (5) recently created profiles that are not archived
	personnels = Personnel.objects.filter(is_archived=False).order_by("-date_profiled")[:5]
	inmates = Inmate.objects.filter(is_archived=False).order_by("-date_profiled")[:5]
	context = {
		'page_title'	: "Home",
		'active'		: "home",
		"personnels"	: personnels,
		"inmates"		: inmates,
	}
	return render(request, "app/index.html", context)


@login_required
def settings(request):
	defset 	= OPERATE_SETTINGS.objects.first()

	if request.method == "POST":
		form = OPERATE_SETTINGS_FORM(request.POST, request.FILES, instance=defset)

		if form.is_valid():
			if request.FILES.get('model_detection') or request.FILES.get('model_embedding_generator'):
				instance = form.save(commit=False)

				if request.FILES.get('model_detection'): 
					logger.debug("Setting new detection model.")
					instance.model_detection.name = "face_detection.onnx"
					instance.save()

					try:
						model = mload.get_model(mload.ModelType.DETECTION_AS_ONNX)
					except (UnrecognizedModelError, FileNotFoundError) as e:
						messages.error(request, e)
						return redirect('operate-settings')
					defset.input_size = model.get_inputs()[0].shape[1]
					defset.save()
				
				# Update fields with files only if there are files uploaded.
				if request.FILES.get('model_embedding_generator'): 
					logger.debug("Setting new embedding generator model.")
					instance.save()

					try:
						model = mload.get_model(mload.ModelType.EMBEDDING_GENERATOR)
						defset.input_size = model.get_inputs()[0].shape[1]
						defset.save()
						update_embeddings()
					except MissingFaceError as e:
						messages.warning(request, "No face was detected. Please update the profile and reupload the model in the settings.")
						return redirect('profile-update', e.profile_type, e.profile_id)
					except (UnrecognizedModelError, FileNotFoundError, EmbeddingNotSavedException) as e:
						messages.error(request, e)
						return redirect('operate-settings')
			else:
				form.save()

			messages.success(request, "Settings updated.")
			return redirect('operate-settings')
	else:
		form = OPERATE_SETTINGS_FORM(instance=defset)

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
	defset = OPERATE_SETTINGS.objects.first()
	curr = request.build_absolute_uri()
	form = app_forms.SearchImageForm()
	threshold = defset.threshold
	cam_id = defset.camera
	search_result = []
	instance = None

	if request.method == "POST":
		uuid_name = str(uuid4())
		input_path	= DJANGO_SETTINGS.MEDIA_ROOT.joinpath(uuid_name)

		# Camera option
		if int(request.POST.get("option_camera", 0)):
			try:
				cam_id = int(request.POST.get("camera", defset.camera))
				cam = camera.Camera(cam_id, defset.cam_clipping, defset.clip_size)
				input_image = cam.live_feed()
				imhand.save_image(input_path, input_image)
			except CameraShutdownException:
				messages.info(request, "Camera shutdown. Search cancelled.")
				return redirect(curr)
			except ImageNotSavedException:
				messages.error(request, "Image save operation failed. Search cancelled.")
				return redirect(curr)
			except Exception as e:
				messages.error(request, "An error occured. Search cancelled.")
				return redirect(curr)

		# Upload option
		elif 'image' in request.FILES: 
			form = app_forms.SearchImageForm(request.POST, request.FILES)
			
			if form.is_valid():
				instance = form.save(commit=False)
				instance.image.name = uuid_name
				instance.save()
				input_path = Path(instance.image.path)

		try:
			fsearch = Facesearch(input_path, defset.threshold)
			search_result = fsearch.search()
			messages.success(request, f"Facesearch done. Found {len(search_result)} similar faces.")
		except MissingFaceError:
			messages.error(request, "No face was detected. Ensure the image includes a clear face.")
			return redirect(curr)
		except NoSimilarFaceException:
			messages.success(request, "No matching face detected during the search.")
			return redirect(curr)
		except ProfileNotFoundError:
			messages.success(request, "Search profile does not exist in the system.")
			return redirect(curr)
		except (UnrecognizedModelError, FileNotFoundError, ModelNotFoundError) as e:
			messages.error(request, e)
			return redirect(curr)
		except Exception as e:
			messages.error(request, "An error occured. Search cancelled.")
			return redirect(curr)
		finally:
			# Delete the image after use
			logger.debug("Deleting input image...")
			instance.delete() if instance else Path(input_path).unlink()
	
	context = {
		"page_title"	: "Facesearch",
		'active'		: 'facesearch',
		"form"			: form,
		"threshold"		: threshold,
		"camera"		: cam_id,
		"search_result"	: search_result,
	}
	return render(request, "app/facesearch.html", context)










