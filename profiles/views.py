from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreatePersonnel, CreateInmate, UpdatePersonnel, UpdateInmate
from .models import Personnel, Inmate
from home.utils import save_profile_picture


def personnels(request):
	context = {
		'personnels': Personnel.objects.all(),
	}
	return render(request, "profiles/personnels.html", context)


def inmates(request):
	context = {
		'inmates': Inmate.objects.all(),
	}
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