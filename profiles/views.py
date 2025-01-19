from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import (
	render, 
	redirect, 
	get_object_or_404
)	
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

from datetime import datetime
from pathlib import Path
from docx2pdf import convert

import logging

from app import (
    utils as app_utils,
    models as app_model,
)

from uuid import uuid4

from . import (
    models as profiles_models,
	forms as profiles_forms
)

from operate.camera import Camera
from operate.excepts import *
from operate import (
	embedding_generator as emb_gen,
	facesearch as fsearch,
	model_loader as mload,
	image_handler as imhand,
	face_detector as facedet,
)

logger = logging.getLogger(__name__)

DJANGO_SETTINGS		= settings
OPERATE_SETTINGS 	= app_model.Setting

ORDER_CHOICES = [
	['descending',"Descending"],
	['ascending', "Ascending"],
]
COMMON_SORT_CHOICES = [
	['date_profiled',"Date Profiled"],
	['l_name', "Last Name"],
	['f_name', "First Name"],
	['age', "Age"],
]
PERSONNEL_SORT_CHOICES = COMMON_SORT_CHOICES + [
	['date_assigned',"Date Assigned"],
	['date_relieved',"Date Relieved"],
]
INMATE_SORT_CHOICES = COMMON_SORT_CHOICES + [
	['date_arrested',"Date Arrested"],
	['date_committed',"Date Committed"],
]



@login_required
def all_personnel(request):
	personnels		= profiles_models.Personnel.objects.all().order_by("-date_profiled")
	ranks			= [rank[0] for rank in profiles_models.RANKS]
	sort_choices	= PERSONNEL_SORT_CHOICES
	order_choices	= ORDER_CHOICES

	reset_filter	= bool(request.GET.get("reset_filter", 0))
	reset_search	= bool(request.GET.get("reset_search", 0))
	search			= request.GET.get("search", "").strip()

	if not reset_search and search:
		# Looks for `f_name`, `m_name`, or `l_name` that contains the `search`
		personnels = profiles_models.Personnel.objects.filter(
			Q(f_name__icontains=search) |
			Q(l_name__icontains=search) |
			Q(m_name__icontains=search)
		)
	else:
		search = ""

	if reset_filter:
		designation, rank, sort_by, sort_order, state = "", "", "", "descending", "open"
	else:
		designation	= request.GET.get("designation", "")
		rank		= request.GET.get("rank", "")
		sort_by		= request.GET.get("sort_by", "")
		sort_order	= request.GET.get("sort_order", "descending")
		state		= request.GET.get("state", "open")

		designation = designation.strip()

	match state:
		case "open":
			personnels = personnels.filter(is_archived=False)
		case "archived":
			personnels = personnels.filter(is_archived=True)

	if designation:
		personnels = personnels.filter(designation__icontains=designation)

	if rank: 		
		personnels = personnels.filter(rank=rank)

	if sort_by:
		sort		= "-" + sort_by if sort_order == "descending" else sort_by
		personnels 	= personnels.order_by(sort)

	filters = {
		'designation'	: designation,
		'rank'			: rank,
		'sort_by'		: sort_by,
		'sort_order'	: sort_order,
		'state'			: state,
		"search"		: search
	}
	
	page		= request.GET.get('page', 1)
	paginator	= Paginator(personnels, OPERATE_SETTINGS.objects.first().profiles_per_page)

	try:
		personnels = paginator.page(page)
	except PageNotAnInteger:
		personnels = paginator.page(1)
	except EmptyPage:
		personnels = paginator.page(paginator.num_pages)

	# Used for showing the page numbers only when there profiles exceeded the set profiles per page number.
	is_paginated = paginator.num_pages > 1 
	
	context = {
		'page_title'	: "Personnel Profiles",
		'active'		: 'profiles personnel',
		'p_type'		: 'personnel',
		'personnels'	: personnels,
		'ranks'			: ranks,
		'sort_choices'	: sort_choices,
		'order_choices'	: order_choices,
		'filters'		: filters,
		'is_paginated'	: is_paginated,
		'query_params'	: f"search={search}&state={state}&designation={designation}&rank={rank}&sort_by={sort_by}&sort_order={sort_order}"
	}
	return render(request, "profiles/all_personnel.html", context)


@login_required
def all_inmate(request):
	inmates			= profiles_models.Inmate.objects.all().order_by("-date_profiled")
	sort_choices	= INMATE_SORT_CHOICES
	order_choices	= ORDER_CHOICES
	filters			= {}

	reset_filter		= bool(request.GET.get("reset_filter", 0))
	reset_search		= bool(request.GET.get("reset_search", 0))
	search				= request.GET.get("search", "").strip()

	# The initialized variable, `personnels`, fetches all personnel objects from the database.
	# The following filters removes data from the `personnel` variable that doesn't fit the filter criteria.

	if not reset_search and search:
		# Looks for `f_name`, `m_name`, or `l_name` that contains the `search`
		inmates = profiles_models.Inmate.objects.filter(
			Q(f_name__icontains=search) |
			Q(l_name__icontains=search) |
			Q(m_name__icontains=search)
		)
	else:
		search = ""

	if reset_filter:
		crime_violated, sort_by, sort_order, state	= "", "", "", "open"
	else:
		crime_violated	= request.GET.get("crime_violated", "")
		sort_by			= request.GET.get("sort_by", "")
		sort_order		= request.GET.get("sort_order", "descending")
		state			= request.GET.get("state", "open")

		crime_violated = crime_violated.strip()

	match state:
		case "open":
			inmates = inmates.filter(is_archived=False)
		case "archived":
			inmates = inmates.filter(is_archived=True)

	if crime_violated: 
		inmates = inmates.filter(crime_violated__icontains=crime_violated)

	if sort_by:
		sort 	= "-" + sort_by if sort_order == "descending" else sort_by
		inmates = inmates.order_by(sort)

	filters = {
		'state'			: state,
		'crime_violated': crime_violated,
		'sort_by'		: sort_by,
		'sort_order'	: sort_order,
		"search"		: search
	}

	page		= request.GET.get('page', 1)
	paginator	= Paginator(inmates, OPERATE_SETTINGS.objects.first().profiles_per_page)

	try:
		inmates = paginator.page(page)
	except PageNotAnInteger:
		inmates = paginator.page(1)
	except EmptyPage:
		inmates = paginator.page(paginator.num_pages)

	# Used for showing the page numbers only when there profiles exceeded the set profiles per page number.
	is_paginated = paginator.num_pages > 1

	context = {
		'page_title'	: "Inmate Profiles",
		'active'		: 'profiles inmate',
		'p_type'		: 'inmate',
		'inmates'		: inmates,
		'sort_choices'	: sort_choices,
		'order_choices'	: order_choices,
		'filters'		: filters,
		'is_paginated'	: is_paginated,
		'query_params'	: f"search={search}&state={state}&sort_by={sort_by}&sort_order={sort_order}&crime_violated={crime_violated}"
	}
	return render(request, "profiles/all_inmate.html", context)


@login_required
def profile(request, p_type, pk):
	prev = request.GET.get("prev", None)

	p_class = profiles_models.Personnel if p_type == "personnel" else profiles_models.Inmate
	profile = get_object_or_404(p_class, pk=pk)

	context = {
		'page_title'	: profile,
		'profile'		: profile,
		'p_type'		: p_type,
		'prev'			: prev,
	}
	return render(request, "profiles/profile.html", context)


@login_required
def profile_add(request, p_type):
	def this_page():
		context = {
			'page_title'	: "Add " + p_type.title() + " Profile",
			'active'		: "add " + p_type,
			'p_type'		: p_type,
			'form'			: form,
			'camera'		: cam_id,
		}
		return render(request, "profiles/profile_add.html", context)
	
	next 	= request.GET.get("next", None)
	defset	= OPERATE_SETTINGS.objects.first()
	cam_id	= defset.camera
	f_class	= profiles_forms.PersonnelForm if p_type == "personnel" else  profiles_forms.InmateForm
	form	= f_class()

	if request.method == "POST":
		form = f_class(request.POST, request.FILES)

		if form.is_valid():
			is_option_camera = bool(request.POST.get("option_camera", 0))
			is_option_upload = 'raw_image' in request.FILES

			if is_option_camera or is_option_upload:
				uuid_name = str(uuid4())
				image_name = uuid_name + ".png"
				
				# We saving the image_names first to hopefully counter opencv errors when
				# 	dealing with spaces or symbols in image names then changing their names
				#	so when we access the image, it will be opened properly by opencv assuming
				#	it was in fact because of that.
				instance = form.save(commit=False)
				instance.raw_image.name = "raw_images/" + image_name if is_option_camera else image_name

				# These fields below somehow needed their save folders to be specified
				# 	assuming that if we didn't use the django fields for these... fields,
				# 	then django just saves these in the `MEDIA_ROOT` (as observed as well).
				instance.embedding.name = "embeddings/" + uuid_name + ".npy"
				instance.thumbnail.name = "thumbnails/" + image_name
				instance.save()
	
				raw_image_path = DJANGO_SETTINGS.RAW_IMG_ROOT.joinpath(image_name)
				thumbnail_path = DJANGO_SETTINGS.THUMBNAIL_ROOT.joinpath(image_name)

				if is_option_camera:
					try:
						cam_id = int(request.POST.get("camera", defset.camera))
						cam = Camera(cam_id, defset.cam_clipping, defset.clip_size)
						raw_image = cam.live_feed()
						imhand.save_image(raw_image_path, raw_image)
					except CameraShutdownException:
						messages.warning(request, "Camera shutdown.")
						messages.warning(request, "Reminder: You need a profile picture to create profile.")
						instance.delete()
						return this_page()
					except ImageNotSavedException:
						messages.error(request, "Image save operation failed.")
						instance.delete()
						return this_page()
					# except Exception as e:
					# 	messages.error(request, f"An error occured: {e}")
					# 	instance.delete()
					# 	return this_page()
				
				try:
					# Thumbnail create and save
					thumbnail = imhand.create_thumbnail(str(raw_image_path))
					imhand.save_image(thumbnail_path, thumbnail)

					# Embedding create and save
					embedding = emb_gen.get_image_embedding(raw_image_path)
					emb_gen.save_embedding(embedding, uuid_name)
				except ImageNotSavedException:
					messages.error(request, "Image save operation failed.")
					instance.delete()
					return this_page()
				except EmbeddingNotSavedException as e:
					messages.error(request, e)
					instance.delete()
					return this_page()
				except MissingFaceError as e:
					messages.error(request, "No face was detected")
					messages.info(request, "Ensure the image includes a clear face.")
					instance.delete()
					return this_page()
				# except Exception as e:
				# 	messages.error(request, f"An error occured: {e}")
				# 	instance.delete()
				# 	return this_page()

			if not is_option_camera and not is_option_upload:
				messages.error(request, "No profile picture found.")
				messages.warning(request, "Reminder: You need a profile picture to create profile.")
				return this_page()
			else:
				message = f"Profile successfully created: {instance}."
				messages.success(request, message)

				return redirect(next) if next else redirect('profile', p_type, instance.pk)
	return this_page()



@login_required
def profile_update(request, p_type, pk):
	def this_page():
		context = {
			'page_title'	: "Update " + str(profile),
			'p_type'		: p_type,
			'form'			: form,
			'camera'		: cam_id,
			'profile'		: profile
		}
		return render(request, "profiles/profile_update.html", context)
	
	next 	= request.GET.get("next", None)
	defset	= OPERATE_SETTINGS.objects.first()
	cam_id	= defset.camera

	if p_type == "personnel":
		p_class 	= profiles_models.Personnel
		f_class 	= profiles_forms.PersonnelForm
	elif p_type == "inmate":
		p_class 	= profiles_models.Inmate
		f_class 	= profiles_forms.InmateForm

	profile = get_object_or_404(p_class, pk=pk)
	form  	= f_class(instance=profile)

	if request.method == "POST":
		form = f_class(request.POST, request.FILES, instance=profile)

		existing_profile = p_class.objects.filter(
			f_name=request.POST.get("f_name"), 
			m_name=request.POST.get("m_name"), 
			l_name=request.POST.get("l_name"),
			suffix=request.POST.get("suffix"),
		).exclude(pk=request.POST.get("pk")).first()

		# Check if profile already exists
		if existing_profile and existing_profile.pk != profile.pk:
			error_message = "A record with the same first, middle, and last name already exists."
			messages.error(request, error_message)
			return this_page()

		if form.is_valid():
			is_option_camera = bool(request.POST.get("option_camera", 0))
			is_option_upload = 'raw_image' in request.FILES


			if is_option_camera or is_option_upload:
				uuid_name = str(uuid4())
				image_name = uuid_name + ".png"

				instance = form.save(commit=False)
				# instance.new_profile.name = "raw_images/" + image_name if is_option_camera else image_name
				instance.raw_image.name = "raw_images/" + image_name if is_option_camera else image_name
				instance.embedding.name = "embeddings/" + uuid_name + ".npy"
				instance.thumbnail.name = "thumbnails/" + image_name
				instance.save()
	
				raw_image_path = DJANGO_SETTINGS.RAW_IMG_ROOT.joinpath(image_name)
				thumbnail_path = DJANGO_SETTINGS.THUMBNAIL_ROOT.joinpath(image_name)

				if is_option_camera:
					try:
						cam_id = int(request.POST.get("camera", defset.camera))
						cam = Camera(cam_id, defset.cam_clipping, defset.clip_size)
						raw_image = cam.live_feed()
						imhand.save_image(raw_image_path, raw_image)
					except CameraShutdownException:
						messages.warning(request, "Camera shutdown.")
						messages.warning(request, "Reminder: You need a profile picture to create profile.")
						return this_page()
					except Exception as e:
						messages.error(request, f"An error occured: {e}")
						return this_page()
				
				try:
					# Thumbnail create and save
					thumbnail = imhand.create_thumbnail(str(raw_image_path))
					imhand.save_image(thumbnail_path, thumbnail)

					# Embedding create and save
					embedding = emb_gen.get_image_embedding(raw_image_path)
					emb_gen.save_embedding(embedding, uuid_name)
				except MissingFaceError as e:
					messages.error(request, "No face was detected")
					messages.info(request, "Ensure the image includes a clear face.")
					# instance.new_profile = profile.new_profile
					# instance.save()
					return this_page()
				except Exception as e:
					messages.error(request, f"An error occured: {e}")
					return this_page()
				# else:
				# 	instance.raw_image = profile.new_profile
				# 	instance.save()
			else:
				instance = form.save()
				
			message = f"Profile successfully updated: {instance}"
			messages.success(request, message)
			logger.debug(message)

			return redirect(next) if next else redirect('profile', p_type, instance.pk)

	return this_page()



@login_required
def profile_delete(request, p_type, pk):
	next = request.GET.get("next", "")

	p_class = profiles_models.Personnel if p_type == "personnel" else profiles_models.Inmate
	profile = get_object_or_404(p_class, pk=pk)

	if request.method == "POST":
		profile.delete()

		messages.success(request, f"Profile successfully deleted: {profile}.")

		print(f"Profile successfully deleted: {profile}.")

		return redirect(next) if next else redirect(f"profiles-all-{p_type}")

	context = {
		'page_title'	: "Delete " + str(profile),
		'title'			: "Delete Profile: " + app_utils.get_full_name(profile),
		'warning' 		: "You can't retrieve this profile once its deleted. Why not archive it first if you're not sure and haven't done it yet?",
		'prev'			: next,
		'p_type'		: p_type,
		'danger'		: True
	}
	return render(request, "app/base_confirmation.html", context)



@login_required
def profile_delete_all(request, p_type):
	prev	= request.GET.get("prev", "")
	state	= request.GET.get("state", "open")

	if request.method == "POST":
		if state:
			is_archived = True if state == "archived" else False

			if p_type == "personnel":
				profiles_models.Personnel.objects.filter(is_archived=is_archived).delete() 
			else:
				profiles_models.Inmate.objects.filter(is_archived=is_archived).delete() 
		else:
			if p_type == "personnel":
				profiles_models.Personnel.objects.all().delete() 
			else:
				profiles_models.Inmate.objects.all().delete() 

		messages.error(request, f"Profiles successfully deleted.")

		print(f"Profiles successfully deleted.")

		return redirect(prev) if prev else redirect(f"profiles-all-{p_type}")

	context = {
		'title' 		: "Delete All Profile",
		'page_title'	: "Delete All Profile",
		'warning' 		: "You can't retrieve all profiles once they're deleted. Why not archive them first if you're not sure and haven't done it yet?",
		'p_type'		: p_type,
		'danger'		: True
	}
	return render(request, "app/base_confirmation.html", context)



@login_required
def archive_add(request, p_type, pk):
	next 	= request.GET.get("next", "")

	personnel	= profiles_models.Personnel
	inmate		= profiles_models.Inmate

	p_class = personnel if p_type == "personnel" else inmate
	profile = get_object_or_404(p_class, pk=pk)

	if request.method == "POST":
		profile.is_archived = True
		profile.save()

		messages.success(request, f"Profile successfully archived: {profile}.")

		print(f"rofile successfully archived: {profile}.")

		return redirect(next) if next else redirect('profile', p_type, profile.pk)

	context = {
		'page_title'	: "Archive: " + str(profile),
		'title' 		: "Archive: " + str(profile),
		'warning' 		: "You will not be able to see this profile in the \"Profile\" Page anymore.",
		'p_type'		: p_type,
		'active'		: p_type
	}
	return render(request, "app/base_confirmation.html", context)



@login_required
def archive_remove(request, p_type, pk):
	next = request.GET.get("next", "")

	personnel	= profiles_models.Personnel
	inmate		= profiles_models.Inmate

	p_class = personnel if p_type == "personnel" else inmate
	profile = get_object_or_404(p_class, pk=pk)

	if request.method == "POST":
		profile.is_archived = False
		profile.save()

		messages.success(request, f"Profile successfully unarchived: {profile}.")

		print(f"rofile successfully unarchived: {profile}.")

		return redirect(next) if next else redirect('profile', p_type, profile.pk)

	context = {
		'page_title'	: "Unarchive: " + str(profile),
		'title' 		: "Unarchive: " + str(profile),
		'p_type'		: p_type,
		'active'		: p_type,
	}
	return render(request, "app/base_confirmation.html", context)



@login_required
def archive_add_all(request, p_type):
	if request.method == "POST":
		if p_type == "personnel":
			profiles = profiles_models.Personnel.objects.filter(is_archived=False).all() 
		else:
			profiles = profiles_models.Inmate.objects.filter(is_archived=False).all() 

		for profile in profiles:
			profile.is_archived = True
			profile.save()

		messages.success(request, f"Profiles successfully archived.")

		print(f"rofile successfully archived.")

		return redirect(f'profiles-all-{p_type}')

	context = {
		'page_title'	: f"Archive all {p_type}s",
		'title'			: f"Archive all {p_type}s",
		'warning' 		: f"You will not be able to see all profiles in the \"Profile\" Page anymore. You can still view them in the \"Archives section\"",
		'p_type'		: p_type,
		'active'		: p_type,
	}
	return render(request, "app/base_confirmation.html", context)



@login_required
def archive_remove_all(request, p_type):
	if request.method == "POST":
		if p_type == "personnel":
			profiles = profiles_models.Personnel.objects.filter(is_archived=True).all() 
		else:
			profiles = profiles_models.Inmate.objects.filter(is_archived=True).all() 

		for profile in profiles:
			profile.is_archived = False
			profile.save()

		messages.success(request, f"Profiles successfully unarchived.")

		print(f"rofile successfully unarchived.")

		return redirect(f'profiles-all-{p_type}')

	context = {
		'page_title'	: f"Unarchive all {p_type}s",
		'title'			: f"Unarchive all {p_type}s",
		'p_type'		: p_type,
		'active'		: p_type,
	}
	return render(request, "app/base_confirmation.html", context)



@login_required
def profile_download(_, p_type, pk, d_type):
	personnel	= [profiles_models.Personnel, OPERATE_SETTINGS.objects.first().template_personnel]
	inmate		= [profiles_models.Inmate, OPERATE_SETTINGS.objects.first().template_inmate]

	p_class, template = personnel if p_type == "personnel" else inmate

	profile = p_class.objects.get(pk=pk)

	fields = [field.name for field in profile._meta.get_fields()]
	fields.append("full_name")
	fields = [f"[[{field.strip()}]]" for field in fields]

	data = {field.name: getattr(profile, field.name, None) for field in profile._meta.get_fields()}
	data["full_name"] = app_utils.get_full_name(profile)

	time_format = "%B %d, %Y"

	for key, value in data.items():
		if "date" in key and value:
			data[key] = datetime.fromisoformat(str(data[key])).strftime(time_format).upper()
		elif type(value) == str:
			data[key] = value.upper()

	data = [value for value in data.values()]

	file_name, docx_path = app_utils.generate_docx(
		template_path	= template.path, 
		image_path		= profile.raw_image.path, 
		fields 			= fields, 
		data 			= data
	)

	if d_type == "pdf":
		pdf_path = Path(str(docx_path).split(".")[-2] + ".pdf")
		pdf_name = pdf_path.name
		
		convert(docx_path, pdf_path)
		
		Path(docx_path).unlink()

		response = app_utils.save_file(pdf_name, pdf_path)
	else:
		response = app_utils.save_file(file_name, docx_path)

	return response







