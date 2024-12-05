from django.db.models import Q
from django.shortcuts import (
	render, 
	redirect, 
	get_object_or_404
)	

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.utils import timezone
from datetime import datetime
from pathlib import Path

from .models import Personnel, Inmate
from home.utils import get_full_name, generate_docx, save_docx

from .forms import (
	CreatePersonnel, 
	CreateInmate, 
	UpdatePersonnel, 
	UpdateInmate
)
from facesearch.utils import *



from settings.views import OperateSetting

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

CWD_PATH = Path().cwd()

FS_PATH		= CWD_PATH.joinpath("facesearch")
MED_PATH 	= CWD_PATH.joinpath("media")

SNN_PATH	= FS_PATH.joinpath(f"snn_models")

EMB_PATH	= MED_PATH.joinpath(f"embeddings")
RAW_PATH	= MED_PATH.joinpath(f"raw_images")
EMB_PATH	= MED_PATH.joinpath(f"embeddings")



def personnels(request):
	context = {
		'personnels'	: Personnel.objects.exclude(archivepersonnel__isnull=False).order_by("-date_profiled"),
		'ranks'			: [rank[0] for rank in Personnel.RANKS],
		'sort_choices'	: PERSONNEL_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {},
		'page_title'	: "Personnel Profiles",
		'p_type'		: 'personnel',
		'active'		: 'profiles personnels'
	}


	if request.method == "GET":
		reset_filter		= request.GET.get("reset_filter", None)
		reset_search		= request.GET.get("reset_search", None)
		search				= request.GET.get("search", "").strip()

		if not reset_search and search:
			context['personnels'] = Personnel.objects.filter(
		        Q(f_name__icontains=search) |
		        Q(l_name__icontains=search) |
		        Q(m_name__icontains=search)
	        )
		else:
			search = ""

		if reset_filter:
			designation, rank, sort_by, sort_order	= None, None, None, None
		else:
			designation	= request.GET.get("designation", "")
			rank		= request.GET.get("rank", "")
			sort_by		= request.GET.get("sort_by", "")
			sort_order	= request.GET.get("sort_order", "descending")

			designation = designation.strip()

			if designation: context['personnels'] = context['personnels'].filter(designation__icontains=designation)
			if rank: 		context['personnels'] = context['personnels'].filter(rank=rank)
			if sort_by:
				sort = "-" + sort_by if sort_order == "descending" else sort_by
				context['personnels'] = context['personnels'].order_by(sort)

			context['filters'] = {
				'designation': designation,
				'rank': rank,
				'sort_by': sort_by,
				'sort_order': sort_order,
			}

		context['filters'].update({"search": search})
	
	page		= request.GET.get('page', 1)  # Get the current page number
	paginator	= Paginator(context['personnels'], OperateSetting.objects.first().default_profiles_per_page)

	try:
		context['personnels'] = paginator.page(page)
	except PageNotAnInteger:
		context['personnels'] = paginator.page(1)  # If page is not an integer, show the first page
	except EmptyPage:
		context['personnels'] = paginator.page(paginator.num_pages)  # If page is out of range, show the last page

	context["is_paginated"] = paginator.num_pages > 1

	return render(request, "profiles/personnels.html", context)





def inmates(request):
	context = {
		'inmates'	: Inmate.objects.exclude(archiveinmate__isnull=False).order_by("-date_profiled"),
		'sort_choices'	: INMATE_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {},
		'page_title'	: "Inmate Profiles",
		'p_type'		: 'inmate',
		'active'		: 'profiles inmates'
	}

	if request.method == "GET":
		reset_filter		= request.GET.get("reset_filter", "")
		reset_search		= request.GET.get("reset_search", "")
		search		= request.GET.get("search", "").strip()

		if not reset_search and search:
			context['inmates'] = Inmate.objects.filter(
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

			crime_violated = crime_violated.strip()

			if crime_violated: context['inmates'] = context['inmates'].filter(crime_violated__icontains=crime_violated)
			if sort_by:
				sort = "-" + sort_by if sort_order == "descending" else sort_by
				context['inmates'] = context['inmates'].order_by(sort)

			context['filters'] = {
				'crime_violated': crime_violated,
				'sort_by': sort_by,
				'sort_order': sort_order,
			}

		context['filters'].update({"search": search})

	page		= request.GET.get('page', 1)  # Get the current page number
	paginator	= Paginator(context['inmates'], OperateSetting.objects.first().default_profiles_per_page)

	try:
		context['inmates'] = paginator.page(page)
	except PageNotAnInteger:
		context['inmates'] = paginator.page(1)  # If page is not an integer, show the first page
	except EmptyPage:
		context['inmates'] = paginator.page(paginator.num_pages)  # If page is out of range, show the last page

	context["is_paginated"] = paginator.num_pages > 1

	return render(request, "profiles/inmates.html", context)






def profile(request, p_type, pk):
	p_class =  Personnel if p_type == "personnel" else Inmate
	profile =  get_object_or_404(p_class, pk=pk)
	context = {
		'profile'		: profile,
		'page_title'	: profile,
		'p_type'		: p_type
	}
	return render(request, "profiles/profile.html", context)




 
def profile_add(request, p_type):
	create_profile_form = CreatePersonnel if p_type == "personnel" else CreateInmate
	defset				= OperateSetting.objects.first()

	context = {
		'form'			: create_profile_form(),
		'default_img'	: "../../../media/default.png",
		'p_type'		: p_type,
		'page_title'	: "Add Profile",
		'camera'		: defset.default_camera,
		'p_type'		: p_type,
		'active'		: 'add ' + p_type
	}

	if request.method == "POST":
		context["form"] = create_profile_form(request.POST, request.FILES)

		if context["form"].is_valid():
			is_option_camera = request.POST.get("option_camera", 0)
			is_option_upload = request.POST.get("option_upload", 0)

			if not is_option_camera and 'raw_image' not in request.FILES:
				context['missing_image'] = True
				return render(request, "profiles/profile_add.html", context)
			
			instance = context["form"].save()

			curr_time 	= str(timezone.now().strftime("%Y%m%d%H%M%S"))
			image_name = f"{curr_time}.png"

			raw_image_save_path = f"media/raw_images/{image_name}"
			thumbnail_save_path	= f"media/thumbnails/{image_name}"

			if is_option_camera:
				# Get camera
				context["camera"] = int(request.POST.get("camera", 0))

				# Take picture
				is_image_taken, raw_image = take_image(context["camera"], defset.crop_camera, defset.default_crop_size)

				# If not then, return
				if not is_image_taken:
					instance.delete()
					return render(request, "profiles/profile_add.html", context)
				
			elif is_option_upload and 'raw_image' in request.FILES: 
				instance_raw_image_path = instance.raw_image.path

				raw_image = open_image(instance_raw_image_path)

			# Save raw image first so that we can use it to create the thumbnail
			is_image_saved = save_image(raw_image_save_path, raw_image)	
			
			# Create thumbnail
			resized_image	= create_thumbnail(
				raw_image_path	= CWD_PATH.joinpath(raw_image_save_path),
				new_size		= defset.default_thumbnail_size
			)

			is_image_saved = save_image(thumbnail_save_path, resized_image)	

			is_image_saved, emb_name, inp_emb = save_embedding(raw_image_save_path)

			if not is_image_saved:
				instance.delete()
				return render(request, "profiles/profile_add.html", context)
			
			instance.embedding = f"embeddings/{emb_name}"
			instance.raw_image = f"raw_images/{image_name}"
			instance.thumbnail = f"thumbnails/{image_name}"

			instance.save()

			return redirect('profile', p_type, instance.pk)

	return render(request, "profiles/profile_add.html", context)





def profile_update(request, p_type, pk):
	p_class, update_form = [Personnel, UpdatePersonnel] if p_type == "personnel" else [Inmate, UpdateInmate]
	defset				= OperateSetting.objects.first()
	profile = get_object_or_404(p_class, pk=pk)

	context = {
		'form'			: update_form(instance=profile),
		'p_type'		: p_type,
		'page_title'	: f"Update {profile}",
		'camera'		: defset.default_camera,
		'profile'		: profile
	}

	if request.method == "POST":
		context['form'] = update_form(request.POST, request.FILES, instance=context['profile'])

		if context['form'].is_valid():
			instance = context['form'].save()

			is_option_camera = request.POST.get("option_camera", 0)
			is_option_upload = request.POST.get("option_upload", 0)

			if is_option_camera or 'raw_image' in request.FILES:
				image_name = f"{str(timezone.now().strftime("%Y%m%d%H%M%S"))}.png"

				raw_image_save_path = f"media/raw_images/{image_name}"
				thumbnail_save_path	= f"media/thumbnails/{image_name}"

				raw_image = None

				if is_option_camera:
					# Get camera
					camera = int(request.POST.get("camera", defset.default_camera))

					# Take picture
					is_image_taken, raw_image = take_image(camera, defset.crop_camera, defset.default_crop_size)

					# If not then, return
					if not is_image_taken:
						return render(request, "profiles/profile_update.html", context)
					
				elif is_option_upload and 'raw_image' in request.FILES: 
					instance_raw_image_path = instance.raw_image.path

					raw_image = open_image(instance_raw_image_path)
				
				# Save raw image taken
				is_image_saved  = save_image(raw_image_save_path, raw_image)	

				# Create thumbnail
				resized_image	= create_thumbnail(
					raw_image_path	= CWD_PATH.joinpath(raw_image_save_path),
					new_size		= defset.default_thumbnail_size
				)

				# Save thumbnail
				is_image_saved	= save_image(thumbnail_save_path, resized_image)	

				is_image_saved, emb_name, inp_emb = save_embedding(raw_image_save_path)

				if not is_image_saved:
					instance.delete()
					return render(request, "profiles/profile_update.html", context)
				
				instance.embedding = f"embeddings/{emb_name}"
				instance.raw_image = f"raw_images/{image_name}"
				instance.thumbnail = f"thumbnails/{image_name}"

			instance.save()

			return redirect('profile', p_type, instance.pk)
		
	return render(request, "profiles/profile_update.html", context)





def profile_delete(request, p_type, pk):
	prev = request.GET.get("prev", "")

	p_class = Personnel if p_type == "personnel" else Inmate
	profile = get_object_or_404(p_class, pk=pk)

	if request.method == "POST":
		profile.delete()

		return redirect(prev) if prev else redirect(f"profiles-{p_type}s")

	context = {
		'title' 		: f"Delete {get_full_name(profile)}'s Profile",
		'warning' 		: f"You can't retrieve this profile once its deleted. Why not archive it first if you're not sure and haven't done it yet?",
		'page_title'	: f"Delete {profile}",
		'prev'			: prev,
		'p_type'		: p_type,
		'danger'		: True
	}
	return render(request, "home/confirmation_page.html", context)





def profile_delete_all(request, p_type):
	prev 	= request.GET.get("prev", "")

	if request.method == "POST":
		if p_type == "personnel":
			Personnel.objects.exclude(archivepersonnel__isnull=False).delete() 
		else:
			Inmate.objects.exclude(archiveinmate__isnull=False).delete() 

		return redirect(prev)

	context = {
		'title' 		: f"Delete All Profile",
		'warning' 		: f"You can't retrieve all profiles once they're deleted. Why not archive them first if you're not sure and haven't done it yet?",
		'page_title'	: f"Delete All",
		'p_type'		: p_type,
		'danger'		: True
	}
	return render(request, "home/confirmation_page.html", context)





def profile_docx_download(_, p_type, pk):
	p_class, template = [Personnel, OperateSetting.objects.first().personnel_template] if p_type == "personnel" else [Inmate, OperateSetting.objects.first().inmate_template]

	profile		= p_class.objects.get(pk=pk)

	fields = [field.name for field in profile._meta.get_fields()]
	fields.append("full_name")
	fields = [f"[[{field}]]" for field in fields]

	print(fields)
	
	data = {field.name: getattr(profile, field.name, None) for field in profile._meta.get_fields()}
	data["full_name"] = get_full_name(profile)

	time_format = "%B %d, %Y"

	for key, value in data.items():
		if "date" in key and value:
			data[key] = datetime.fromisoformat(str(data[key])).strftime(time_format).upper()
		elif type(value) == str:
			data[key] = value.upper()

	data = [value for key, value in data.items()]
	print(f"{data=}")

	file_name, save_path = generate_docx(
		template_path	= template.path, 
		image_path		= profile.raw_image.path, 
		fields 			= fields, 
		data 			= data
	)

	response = save_docx(file_name, save_path)
	
	return response
