from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import (
	render, 
	redirect, 
	get_object_or_404
)	
from django.utils import timezone
from django.conf import settings

from datetime import datetime
from pathlib import Path
from docx2pdf import convert

from app import (
    utils as app_utils,
    models as app_model,
)

from . import (
    models as profiles_models,
	forms as profiles_forms
)



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
	context = {
		'page_title'	: "Personnel Profiles",
		'active'		: 'profiles personnel',
		'p_type'		: 'personnel',
		'personnels'	: profiles_models.Personnel.objects.all().order_by("-date_profiled"),
		'ranks'			: [rank[0] for rank in profiles_models.RANKS],
		'sort_choices'	: PERSONNEL_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {},
	}

	if request.method == "GET":
		reset_filter		= request.GET.get("reset_filter", None)
		reset_search		= request.GET.get("reset_search", None)
		search				= request.GET.get("search", "").strip()

		if not reset_search and search:
			context['personnels'] = profiles_models.Personnel.objects.filter(
		        Q(f_name__icontains=search) |
		        Q(l_name__icontains=search) |
		        Q(m_name__icontains=search)
	        )
		else:
			search = ""

		if reset_filter:
			designation, rank, sort_by, sort_order= None, None, None, None
		else:
			designation	= request.GET.get("designation", "")
			rank		= request.GET.get("rank", "")
			sort_by		= request.GET.get("sort_by", "")
			sort_order	= request.GET.get("sort_order", "descending")
			state		= request.GET.get("state", "open")

			designation = designation.strip()

			if state:
				context['personnels'] = context['personnels'].filter(
					is_archived = True if state == "archived" else False
				)

			if designation:
				context['personnels'] = context['personnels'].filter(designation__icontains=designation)

			if rank: 		
				context['personnels'] = context['personnels'].filter(rank=rank)

			if sort_by:
				sort = "-" + sort_by if sort_order == "descending" else sort_by
				context['personnels'] = context['personnels'].order_by(sort)

			context['filters'] = {
				'state'			: state,
				'designation'	: designation,
				'rank'			: rank,
				'sort_by'		: sort_by,
				'sort_order'	: sort_order,
			}

		context['filters'].update({"search": search})
	
	page		= request.GET.get('page', 1)
	paginator	= Paginator(context['personnels'], OPERATE_SETTINGS.objects.first().profiles_per_page)

	try:
		context['personnels'] = paginator.page(page)
	except PageNotAnInteger:
		context['personnels'] = paginator.page(1)  # If page is not an integer, show the first page
	except EmptyPage:
		context['personnels'] = paginator.page(paginator.num_pages)  # If page is out of range, show the last page

	context["is_paginated"] = paginator.num_pages > 1

	return render(request, "profiles/all_personnel.html", context)


@login_required
def all_inmate(request):
	context = {
		'page_title'	: "Inmate Profiles",
		'active'		: 'profiles inmate',
		'p_type'		: 'inmate',
		'inmates'		: profiles_models.Inmate.objects.all().order_by("-date_profiled"),
		'sort_choices'	: INMATE_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {},
	}

	if request.method == "GET":
		reset_filter		= request.GET.get("reset_filter", "")
		reset_search		= request.GET.get("reset_search", "")
		search				= request.GET.get("search", "").strip()

		if not reset_search and search:
			context['inmates'] = profiles_models.Inmate.objects.filter(
		        Q(f_name__icontains=search) |
		        Q(l_name__icontains=search) |
		        Q(m_name__icontains=search)
	        )
		else:
			search = ""

		if reset_filter:
			crime_violated, sort_by, sort_order	= None, None, None
		else:
			crime_violated	= request.GET.get("crime_violated", "")
			sort_by			= request.GET.get("sort_by", "")
			sort_order		= request.GET.get("sort_order", "descending")
			state			= request.GET.get("state", "open")

			crime_violated = crime_violated.strip()

			if state:
				context['inmates'] = context['inmates'].filter(
					is_archived = True if state == "archived" else False
				)

			if crime_violated: 
				context['inmates'] = context['inmates'].filter(crime_violated__icontains=crime_violated)
			if sort_by:
				sort = "-" + sort_by if sort_order == "descending" else sort_by
				context['inmates'] = context['inmates'].order_by(sort)

			context['filters'] = {
				'state'			: state,
				'crime_violated': crime_violated,
				'sort_by'		: sort_by,
				'sort_order'	: sort_order,
			}

		context['filters'].update({"search": search})

	page		= request.GET.get('page', 1)  # Get the current page number
	paginator	= Paginator(context['inmates'], OPERATE_SETTINGS.objects.first().profiles_per_page)

	try:
		context['inmates'] = paginator.page(page)
	except PageNotAnInteger:
		context['inmates'] = paginator.page(1)  # If page is not an integer, show the first page
	except EmptyPage:
		context['inmates'] = paginator.page(paginator.num_pages)  # If page is out of range, show the last page

	context["is_paginated"] = paginator.num_pages > 1

	return render(request, "profiles/all_inmate.html", context)



@login_required
def profile(request, p_type, pk):
	prev 	= request.GET.get("prev", "")

	p_class =  profiles_models.Personnel if p_type == "personnel" else profiles_models.Inmate
	profile =  get_object_or_404(p_class, pk=pk)
	context = {
		'page_title'	: profile,
		'profile'		: profile,
		'p_type'		: p_type,
		'prev'			: prev,
	}
	return render(request, "profiles/profile.html", context)



@login_required
def profile_add(request, p_type):
	defset		= OPERATE_SETTINGS.objects.first()
	camera		= defset.camera

	personnel_form	= profiles_forms.PersonnelForm
	inmate_form		= profiles_forms.InmateForm

	form_class 	= personnel_form if p_type == "personnel" else inmate_form
	form 		= form_class()

	if request.method == "POST":
		prev = request.GET.get("prev", "/")
		form = form_class(request.POST, request.FILES)

		if form.is_valid():
			is_option_camera = request.POST.get("option_camera", 0)
			is_option_upload = request.POST.get("option_upload", 0)
			
			print(is_option_camera)

			if not is_option_camera and 'raw_image' not in request.FILES:
				form.add_error(
					field = "raw_image",
					error = "No profile picture found. Please upload one to complete your profile"
				)

			instance = form.save()

			curr_time 	= timezone.now().strftime("%Y%m%d%H%M%S")
			image_name 	= curr_time + ".png"

			raw_image_save_path = DJANGO_SETTINGS.RAW_IMG_ROOT.joinpath(image_name)
			thumbnail_save_path	= DJANGO_SETTINGS.THUMBNAIL_ROOT.joinpath(image_name)

			if is_option_camera:
				camera = int(request.POST.get("camera", camera))

				is_image_taken, raw_image = app_utils.take_image(
					camera		= camera, 
					clip_camera = defset.clip_camera, 
					clip_size	= defset.clip_size
				)

				if not is_image_taken:
					instance.delete()
					return redirect(prev)
				
			elif is_option_upload and 'raw_image' in request.FILES: 
				instance_raw_image_path = instance.raw_image.path

				raw_image = app_utils.open_image(instance_raw_image_path)

			# Save raw image first so that we can use it to create the thumbnail
			is_image_saved = app_utils.save_image(raw_image_save_path, raw_image)	

			if not is_image_saved:
				instance.delete()
				return redirect(prev)
			
			resized_image = app_utils.create_thumbnail(
				raw_image_path	= raw_image_save_path,
				thumbnail_size	= defset.thumbnail_size
			)

			is_image_saved = app_utils.save_image(
				image_path 	= thumbnail_save_path, 
				image		= resized_image
			)	

			if not is_image_saved:
				instance.delete()
				return redirect(prev)

			is_image_saved, emb_name, _ = app_utils.save_embedding(raw_image_save_path)

			if not is_image_saved:
				instance.delete()
				return redirect(prev)
			
			if is_image_saved:
				instance.embedding = "embeddings/" + emb_name
				instance.raw_image = "raw_images/" + image_name
				instance.thumbnail = "thumbnails/" + image_name

				instance.save()

				return redirect('profile', p_type, instance.pk)

	context = {
		'page_title'	: "Add " + p_type.title() + " Profile",
		'active'		: "add " + p_type,
		'p_type'		: p_type,
		'form'			: form,
		'camera'		: camera,
	}
	return render(request, "profiles/profile_add.html", context)



@login_required
def profile_update(request, p_type, pk):
	prev_page 	= request.GET.get("prev", "/")
	curr_page	= request.build_absolute_uri()
	defset		= OPERATE_SETTINGS.objects.first()
	camera		= defset.camera

	personnel	= [profiles_models.Personnel, profiles_forms.PersonnelForm]
	inmate		= [profiles_models.Inmate, profiles_forms.InmateForm]

	p_class, form_class = personnel if p_type == "personnel" else inmate
	profile = get_object_or_404(p_class, pk=pk)
	form  	= form_class(instance=profile)

	if request.method == "POST":
		form = form_class(request.POST, request.FILES, instance=profile)

		if form.is_valid():
			instance = form.save()

			is_option_camera = request.POST.get("option_camera", 0)
			is_option_upload = request.POST.get("option_upload", 0)

			if is_option_camera or 'raw_image' in request.FILES:
				curr_time	= str(timezone.now().strftime("%Y%m%d%H%M%S"))
				image_name	= curr_time + ".png"

				raw_image_save_path = DJANGO_SETTINGS.RAW_IMG_ROOT.joinpath(image_name)
				thumbnail_save_path	= DJANGO_SETTINGS.THUMBNAIL_ROOT.joinpath(image_name)

				raw_image = None

				if is_option_camera:
					camera = int(request.POST.get("camera", camera))

					is_image_taken, raw_image = app_utils.take_image(
						camera		= camera, 
						clip_camera	= defset.clip_camera, 
						clip_size	= defset.clip_size
					)

					if not is_image_taken:
						# Add message info for reminder that it needs profile picture to create

						return redirect(curr_page)
					
				elif is_option_upload and 'raw_image' in request.FILES: 
					instance_raw_image_path = instance.raw_image.path

					raw_image = app_utils.open_image(instance_raw_image_path)
				
				is_image_saved = app_utils.save_image(raw_image_save_path, raw_image)	

				if not is_image_saved:
					instance.delete()
					return redirect(curr_page)
				
				resized_image = app_utils.create_thumbnail(
					raw_image_path	= raw_image_save_path,
					thumbnail_size	= defset.thumbnail_size
				)
				
				is_image_saved	= app_utils.save_image(
					image_path	= thumbnail_save_path, 
					image		= resized_image
				)	
				
				if not is_image_saved:
					instance.delete()
					return redirect(curr_page)

				is_image_saved, emb_name, _ = app_utils.save_embedding(raw_image_save_path)

				if not is_image_saved:
					instance.delete()
					return redirect(curr_page)
				
				instance.embedding = f"embeddings/{emb_name}"
				instance.raw_image = f"raw_images/{image_name}"
				instance.thumbnail = f"thumbnails/{image_name}"

			instance.save()

			return redirect('profile', p_type, instance.pk)

	context = {
		'page_title'	: "Update " + str(profile),
		'p_type'		: p_type,
		'form'			: form,
		'camera'		: camera,
		'profile'		: profile
	}
	return render(request, "profiles/profile_update.html", context)



@login_required
def profile_delete(request, p_type, pk):
	prev = request.GET.get("prev", "")

	p_class = profiles_models.Personnel if p_type == "personnel" else profiles_models.Inmate
	profile = get_object_or_404(p_class, pk=pk)

	if request.method == "POST":
		profile.delete()

		print(f"{prev=}")

		return redirect(prev) if prev else redirect(f"profiles-all-{p_type}")

	context = {
		'page_title'	: "Delete " + str(profile),
		'title'			: "Delete Profile: " + app_utils.get_full_name(profile),
		'warning' 		: "You can't retrieve this profile once its deleted. Why not archive it first if you're not sure and haven't done it yet?",
		'prev'			: prev,
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

		return redirect(prev)

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
	prev 	= request.GET.get("prev", "")

	personnel	= profiles_models.Personnel
	inmate		= profiles_models.Inmate

	p_class = personnel if p_type == "personnel" else inmate
	profile = get_object_or_404(p_class, pk=pk)

	if request.method == "POST":
		profile.is_archived = True
		profile.save()

		return redirect(prev) if prev else redirect('profile', p_type, profile.pk)

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
	prev 	= request.GET.get("prev", "")

	personnel	= profiles_models.Personnel
	inmate		= profiles_models.Inmate

	p_class = personnel if p_type == "personnel" else inmate
	profile = get_object_or_404(p_class, pk=pk)

	if request.method == "POST":
		profile.is_archived = False
		profile.save()

		return redirect(prev) if prev else redirect('profile', p_type, profile.pk)

	context = {
		'page_title'	: "Unarchive: " + str(profile),
		'title' 		: "Archive: " + str(profile),
		'p_type'		: p_type,
		'active'		: p_type,
	}
	return render(request, "app/base_confirmation.html", context)



@login_required
def archive_add_all(request, p_type):
	prev = request.GET.get("prev", "")

	if request.method == "POST":
		if p_type == "personnel":
			profiles = profiles_models.Personnel.objects.filter(is_archived=False).all() 
		else:
			profiles = profiles_models.Inmate.objects.filter(is_archived=False).all() 

		for profile in profiles:
			profile.is_archived = True
			profile.save()

		return redirect(prev) if prev else redirect(f'profiles-all-{p_type}')

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
	prev 	= request.GET.get("prev", "")

	if request.method == "POST":
		if p_type == "personnel":
			profiles = profiles_models.Personnel.objects.filter(is_archived=True).all() 
		else:
			profiles = profiles_models.Inmate.objects.filter(is_archived=True).all() 

		for profile in profiles:
			profile.is_archived = False
			profile.save()

		return redirect(prev) if prev else redirect(f'profiles-all-{p_type}')

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

	for field in fields:
		print(field)
	
	data = {field.name: getattr(profile, field.name, None) for field in profile._meta.get_fields()}
	data["full_name"] = app_utils.get_full_name(profile)

	time_format = "%B %d, %Y"

	for key, value in data.items():
		if "date" in key and value:
			data[key] = datetime.fromisoformat(str(data[key])).strftime(time_format).upper()
		elif type(value) == str:
			data[key] = value.upper()

	data = [value for key, value in data.items()]

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







