from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreatePersonnel, CreateInmate, UpdatePersonnel, UpdateInmate
from .models import Personnel, Inmate
from home.utils import save_profile_picture
from django.db.models import Q

def personnels(request):
	sort_choices = [
		['l_name', "Last Name"],
		['f_name', "First Name"],
		['age', "Age"],
		['date_profiled',"Date Profiled"],
		['date_assigned',"Date Assigned"],
		['date_relieved',"Date Relieved"],
	]

	order_choices = [
		['descending',"Descending"],
		['ascending', "Ascending"],
	]

	context = {
		'personnels'	: Personnel.objects.exclude(archivepersonnel__isnull=False),
		'ranks'			: [rank[0] for rank in Personnel.RANKS],
		'sort_choices'	: sort_choices,
		'order_choices'	: order_choices,
		'filters'		: {}
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
			designation	= None
			rank		= None
			sort_by		= None
			sort_order	= None
		else:
			designation	= request.GET.get("designation", "")
			rank		= request.GET.get("rank", "")
			sort_by		= request.GET.get("sort_by", "")
			sort_order	= request.GET.get("sort_order", "descending")

			designation = designation.strip()

			if designation:
				context['personnels'] = context['personnels'].filter(designation__icontains=designation)

			if rank:
				context['personnels'] = context['personnels'].filter(rank=rank)

			if sort_by:
				if sort_order == "descending":
					sort_by = "-" + sort_by
				context['personnels'] = context['personnels'].order_by(sort_by)

			context['filters'] = {
				'designation': designation,
				'rank': rank,
				'sort_by': sort_by,
				'sort_order': sort_order,
				'sort_order': sort_order,
			}

		context['filters'].update({"search": search})

	return render(request, "profiles/personnels.html", context)


def inmates(request):
	sort_choices = [
		['l_name', "Last Name"],
		['f_name', "First Name"],
		['age', "Age"],
		['date_profiled',"Date Profiled"],
		['date_arresetd',"Date Arrested"],
		['date_committed',"Date Committed"],
	]

	order_choices = [
		['descending',"Descending"],
		['ascending', "Ascending"],
	]

	context = {
		'inmates'	: Inmate.objects.exclude(archiveinmate__isnull=False),
		'sort_choices'	: sort_choices,
		'order_choices'	: order_choices,
		'filters'		: {}
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
			crime_violated	= None
			sort_by		= None
			sort_order	= None
		else:
			crime_violated	= request.GET.get("crime_violated", "")
			sort_by		= request.GET.get("sort_by", "")
			sort_order	= request.GET.get("sort_order", "descending")

			crime_violated = crime_violated.strip()

			if crime_violated:
				context['inmates'] = context['inmates'].filter(crime_violated__icontains=crime_violated)

			if sort_by:
				if sort_order == "descending":
					sort_by = "-" + sort_by
				context['inmates'] = context['inmates'].order_by(sort_by)

			context['filters'] = {
				'crime_violated': crime_violated,
				'sort_by': sort_by,
				'sort_order': sort_order,
			}

		context['filters'].update({"search": search})
	return render(request, "profiles/inmates.html", context)

 
def profile_personnel(request, pk):
	context = {
		'profile': get_object_or_404(Personnel, pk=pk),
	}
	return render(request, "profiles/profile_personnel.html", context)
 

def profile_inmate(request, pk):
	context = {
		'profile': get_object_or_404(Inmate, pk=pk),
	}
	return render(request, "profiles/profile_inmate.html", context)


def profile_personnel_update(request, pk):
	profile = get_object_or_404(Personnel, pk=pk)

	if request.method == "POST":
		form = UpdatePersonnel(request.POST, request.FILES, instance=profile)

		if form.is_valid():
			instance = form.save()

			# For updating profile picture
			if 'raw_image' in request.FILES:
				save_profile_picture(instance)

			return redirect('profile-personnel', pk)
	else:
		form = UpdatePersonnel(instance=profile)

	context = {
		'prev'		: request.GET.get("prev", ""),
		'profile'	: profile,
		'form'		: form,
	}
	return render(request, "profiles/profile_update.html", context)


def profile_inmate_update(request, pk):
	profile = get_object_or_404(Inmate, pk=pk)

	if request.method == "POST":
		form = UpdateInmate(request.POST, request.FILES, instance=profile)

		if form.is_valid():
			instance = form.save()

			# For updating profile picture
			if 'raw_image' in request.FILES:
				save_profile_picture(instance)

			return redirect('profile-inmate', pk)
	else:
		form = UpdateInmate(instance=profile)

	context = {
		'prev'		: request.GET.get("prev", ""),
		'profile'	: profile,
		'form'		: form,
	}
	return render(request, "profiles/profile_update.html", context)


def profile_inmate_add(request):
	prev = request.GET.get("prev", "")

	if request.method == "POST":
		form = CreateInmate(request.POST, request.FILES)

		if form.is_valid():
			instance = form.save()
			# saveProfilePicture(instance.image_model, instance.id)
			return redirect(prev)
	else:
		form = CreateInmate()

	context = {
		'form' : form,
	}
	return render(request, "profiles/profile_add.html", context)


def profile_personnel_add(request):
	prev = request.GET.get("prev", "")

	if request.method == "POST":
		form = CreatePersonnel(request.POST, request.FILES)

		if form.is_valid():
			instance = form.save()
			# saveProfilePicture(instance.image_model, instance.id)
			return redirect(prev)
	else:
		form = CreatePersonnel()

	context = {
		'form' : form,
	}
	return render(request, "profiles/profile_add.html", context)


def profile_personnel_delete(request, pk):
	prev	= request.GET.get("prev", "")
	profile = get_object_or_404(Personnel, pk=pk)

	if request.method == "POST":
		profile.delete()

		if prev:
			return redirect(prev)
		else:
			return redirect('profiles-personnels')

	context = {
		'profile' : profile,
	}
	return render(request, "profiles/profile_delete_confirm.html", context)


def profile_inmate_delete(request, pk):
	prev	= request.GET.get("prev", "")
	profile = get_object_or_404(Inmate, pk=pk)

	if request.method == "POST":
		profile.delete()

		if prev:
			return redirect(prev)
		else:
			return redirect('profiles-inmates')

	context = {
		'profile' : profile,
	}
	return render(request, "profiles/profile_delete_confirm.html", context)













# def personnels(request):
# 	personnels = Personnel.objects.filter(archive__isnull=True)

# 	context["personnels"] 	= personnels
# 	return render(request, "profiles/personnels.html", context)

# def inmates(request):
# 	return render(request, "profiles/inmates.html", context)

# def profile(request, profile_type, pk):
# 	profile = get_object_or_404(Personnel, pk=pk)
	
# 	context["prev"] 	= request.GET.get("prev", "")
# 	context["profile"] 	= profile
# 	return render(request, "profiles/profile.html", context)

# def profile_update(request, pk):
# 	# profile = get_object_or_404(Personnel, pk=pk)

# 	# if request.method == "POST":
# 	# 	form = UpdatePersonnel(request.POST, request.FILES, instance=profile)

# 	# 	if form.is_valid():
# 	# 		instance = form.save()

# 	# 		# For updating profile picture
# 	# 		# if 'image_model' in request.FILES:
# 	# 		# 	saveProfilePicture(instance.image_model, instance.id)

# 	# 		return redirect('profile', pk)
# 	# else:
# 	# 	form = UpdatePersonnel(instance=profile)

# 	# context["profile"] 	= profile
# 	# context["prev"] 	= request.GET.get("prev", "")
# 	# context["form"] 	= form
# 	return render(request, "profiles/profile_update.html", context)