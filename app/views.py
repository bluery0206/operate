from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings as DJANGO_SETTINGS

from pathlib import Path
from uuid import uuid4

import logging


from .models import Setting as OPERATE_SETTINGS
from .forms import OperateSettingsForm, LoginForm, PasswordResetForm, SearchImageForm

from profiles.models import Personnel, Inmate

from operate.excepts import *
from operate.facesearch import Facesearch
from operate.embedding_generator import update_embeddings
from operate.camera import Camera 
from operate.model_loader import get_model, ModelType
from operate.image_handler import save_image


logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)



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
		form = OperateSettingsForm(request.POST, request.FILES, instance=defset)

		if form.is_valid():
			if request.FILES.get('model_detection') or request.FILES.get('model_embedding_generator'):
				instance = form.save(commit=False)

				if request.FILES.get('model_detection'): 
					logger.debug("Setting new detection model.")
					instance.model_detection.name = "face_detection.onnx"
					instance.save()
				
				# Update fields with files only if there are files uploaded.
				if request.FILES.get('model_embedding_generator'): 
					logger.debug("Setting new embedding generator model.")
					instance.save()

					try:
						model = get_model(ModelType.EMBEDDING_GENERATOR)
						defset.input_size = model.get_inputs()[0].shape[1]
						defset.save()

						# Different models, different embeddings even if we used the same image
						# and therefore, updating embeddings when new model is uploaded is very important.
						update_embeddings()
					except MissingFaceError as e:
						messages.warning(request, "No face was detected. Please update the profile and reupload the model in the settings.")
						return redirect('profile-update', e.profile_type, e.profile_id)
					except Exception as e:
						messages.error(request, e)
						return redirect('operate-settings')
			else:
				form.save()

			messages.success(request, "Settings updated.")
			return redirect('operate-settings')
	else:
		form = OperateSettingsForm(instance=defset)

	context = {
		'page_title'	: 'Settings',
		'active'		: 'settings',
		'defset'		: defset,
		'form'			: form,
	}
	return render(request, "app/settings.html", context)


@login_required
def settings_update_embeddings(request):
	next = request.GET.get("next", "")

	if request.method == "POST":
		update_embeddings()

		messages.success(request, "Profile image iembeddings successfully updated.")
		return redirect("operate-settings")

	context = {
		'page_title'	: "Update image embeddings",
		'title'			: "Update image embeddings",
		'warning' 		: "Updating all image embeddings will overwrite existing data and may take significant time.",
		'prev'			: next,
		'danger'		: False
	}
	return render(request, "app/base_confirmation.html", context)


# Had to use a custom login view method because of the password eye
def user_login(request):
	login_form = LoginForm

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
	login_form = PasswordResetForm

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
	defset	 		= OPERATE_SETTINGS.objects.first()
	has_inmate 		= Inmate.objects.all().count()
	has_personnel 	= Personnel.objects.all().count()
	can_search		= has_inmate or has_personnel
	curr 			= request.build_absolute_uri()
	form 			= SearchImageForm()
	threshold 		= defset.threshold
	cam_id 			= defset.camera
	search_result 	= []
	instance 		= None
	search_category	= request.POST.get("search_category", "inmate")

	# So that it will auto-select what search categort is available if one search is not available
	if not has_personnel or not has_inmate:
		if not has_personnel:
			search_category = "inmate"
		elif not has_inmate:
			search_category = "personnel"

	if request.method == "POST":
		uuid_name = str(uuid4())
		input_path = DJANGO_SETTINGS.MEDIA_ROOT.joinpath(uuid_name + ".png")

		try:
			# Camera option
			if int(request.POST.get("option_camera", 0)):
				cam_id = int(request.POST.get("camera", defset.camera))
				cam = Camera(cam_id, defset.cam_clipping, defset.clip_size)
				input_image = cam.live_feed()
				save_image(input_path, input_image)

			# Upload option
			elif 'image' in request.FILES: 
				form = SearchImageForm(request.POST, request.FILES)

				if form.is_valid():
					instance = form.save(commit=False)
					instance.image.name = uuid_name
					instance.save()
					input_path = Path(instance.image.path)

			search_result = Facesearch(search_category, input_path, defset.threshold).search()
			messages.success(request, f"Facesearch done. Found {len(search_result)} similar faces.")
		except CameraShutdownException:
			messages.info(request, "Camera shutdown. Search cancelled.")
			return redirect(curr)
		except ImageNotSavedException:
			messages.error(request, "Image save operation failed. Search cancelled.")
			return redirect(curr)
		except MissingFaceError:
			messages.error(request, "No face was detected.")
			messages.info(request, "Ensure the image includes a clear face.")
			return redirect(curr)
		except NoSimilarFaceException:
			messages.success(request, "No matching face detected during the search.")
			return redirect(curr)
		except ProfileNotFoundError:
			messages.error(request, "Search profile does not exist in the system.")
			return redirect(curr)
		except EmptyDatabase as e:
			messages.error(request, e)
			return redirect(curr)
		except TooManyFacesError as e:
			messages.error(request, e)
			messages.info(request, "Ensure there is only one face in the image.")
			return redirect(curr)
		except Exception as e:
			messages.error(request, "An error occured. Search cancelled.")
			messages.error(request, e)
			return redirect(curr)
		finally:
			# Delete the image after use whether if search is successful or not
			logger.debug("Deleting input image...")

			if instance:
				instance.delete()
			elif input_path.exists():
				input_path.unlink()

	context = {
		"page_title"		: "Facesearch",
		'active'			: 'facesearch',
		"form"				: form,
		"threshold"			: threshold,
		"camera"			: cam_id,
		"search_result"		: search_result,
		"search_category"	: search_category,
		"has_inmate"		: has_inmate,
		"has_personnel"		: has_personnel,
		"can_search"		: can_search,
	}
	return render(request, "app/facesearch.html", context)










