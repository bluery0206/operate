from django.db.models import Q
from django.shortcuts import (
	render, 
	redirect, 
	get_object_or_404
)	

from datetime import datetime
from pathlib import Path

from .models import Personnel, Inmate, Template
from home.utils import save_profile_picture, get_full_name, generate_docx, save_docx
from .forms import (
	CreatePersonnel, 
	CreateInmate, 
	UpdatePersonnel, 
	UpdateInmate, 
	TemplateUploadForm
)
from facesearch.utils import take_image, save_image


ORDER_CHOICES = [
	['descending',"Descending"],
	['ascending', "Ascending"],
]

COMMON_SORT_CHOICES = [
	['l_name', "Last Name"],
	['f_name', "First Name"],
	['age', "Age"]
]

PERSONNEL_SORT_CHOICES = COMMON_SORT_CHOICES + [
	['date_profiled',"Date Profiled"],
	['date_assigned',"Date Assigned"],
	['date_relieved',"Date Relieved"],
]

INMATE_SORT_CHOICES = [
	['date_profiled',"Date Profiled"],
	['date_arrested',"Date Arrested"],
	['date_committed',"Date Committed"],
]

CWD_PATH = Path().cwd()
MEDIA_PATH =  CWD_PATH.joinpath("media")


def personnels(request):
	context = {
		'personnels'	: Personnel.objects.exclude(archivepersonnel__isnull=False),
		'ranks'			: [rank[0] for rank in Personnel.RANKS],
		'sort_choices'	: PERSONNEL_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {},
		'page_title'	: "OPERATE | Personnel Profiles"
	}

	if request.method == "GET":
		reset_filter		= request.GET.get("reset_filter", None)
		reset_search		= request.GET.get("reset_search", None)
		search		= request.GET.get("search", "").strip()

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
			if rank: context['personnels'] = context['personnels'].filter(rank=rank)
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

	return render(request, "profiles/personnels.html", context)





def inmates(request):
	context = {
		'inmates'	: Inmate.objects.exclude(archiveinmate__isnull=False),
		'sort_choices'	: INMATE_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {},
		'page_title'	: "OPERATE | Inmate Profiles"
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
	return render(request, "profiles/inmates.html", context)





def profile_template_upload(request):
	if request.method == "POST":
		form = TemplateUploadForm(request.POST, request.FILES)

		if form.is_valid():
			form.save()
	else:
		form= TemplateUploadForm()

	context = {
		'prev'		: request.GET.get("prev", ""),
		'form'		: form,
		'page_title': "OPERATE | Template Upload"
	}
	return render(request, "profiles/profile_update.html", context)





def profile(request, p_type, pk):
	p_class =  Personnel if p_type == "personnel" else Inmate
	profile =  get_object_or_404(p_class, pk=pk)
	context = {
		'profile'		: profile,
		'page_title'	: f"OPERATE | {profile}"
	}
	return render(request, "profiles/profile.html", context)




 
def profile_add(request, p_type):
	create_profile_form = CreatePersonnel if p_type == "personnel" else CreateInmate

	if request.method == "POST":
		form = create_profile_form(request.POST, request.FILES)

		if form.is_valid():
			instance = form.save()

			if 'raw_image' in request.FILES: save_profile_picture(instance)

			return redirect('profile', p_type, instance.pk)
	else:
		form = create_profile_form()

	context = {
		'form'			: form,
		'default_img'	: "../../../media/default.jpg",
		'p_type'		: p_type,
		'page_title'	: f"OPERATE | Add Profile"
	}
	return render(request, "profiles/profile_add.html", context)





def profile_update(request, p_type, pk):
	p_class, update_form = [Personnel, UpdatePersonnel] if p_type == "personnel" else [Inmate, UpdateInmate]
	profile = get_object_or_404(p_class, pk=pk)

	if request.method == "POST":
		form = update_form(request.POST, request.FILES, instance=profile)

		# is_option_camera = request.POST.get("open_camera", 0)

		# if is_option_camera:
		# 	camera			= int(request.POST.get("camera", 0))
		# 	is_image_taken	= take_image(camera)

		# 	context["camera"] =	camera

		# 	if is_image_taken:
		# 		_, frame = is_image_taken
				
		# 		save_image(image_path, frame)	
		# 	else:
		# 		return render(request, "profiles/profile_update.html", context)
			
		if form.is_valid():
			instance = form.save()

			if 'raw_image' in request.FILES: save_profile_picture(instance)

			return redirect('profile', p_type, pk)
	else:
		form = update_form(instance=profile)

	context = {
		'prev'			: request.GET.get("prev", ""),
		'profile'		: profile,
		'form'			: form,
		'page_title'	: f"OPERATE | Update {profile}"
	}
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
		'page_title'	: f"OPERATE | Delete {profile}"
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
		'page_title'	: f"OPERATE | Delete All"
	}
	return render(request, "home/confirmation_page.html", context)





def profile_docx_download(_, p_type, pk):
	p_class = Personnel if p_type == "personnel" else Inmate

	template	= Template.objects.get(template_name__icontains=p_type)
	profile		= p_class.objects.get(pk=pk)

	fields = [field.name for field in profile._meta.get_fields()]
	fields.append("full_name")
	fields = [f"[[{field}]]" for field in fields]
	
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
		template_path	= template.template_file.path, 
		image_path		= profile.raw_image.path, 
		fields 			= fields, 
		data 			= data
	)

	response = save_docx(file_name, save_path)
	
	return response
