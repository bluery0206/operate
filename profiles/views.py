from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreatePersonnel, CreateInmate, UpdatePersonnel, UpdateInmate
from .models import Personnel, Inmate

context = {}

def personnels(request):
	personnels = Personnel.objects.filter(archive__isnull=True)

	context["personnels"] 	= personnels
	return render(request, "profiles/personnels.html", context)

def inmates(request):
	return render(request, "profiles/inmates.html", context)

def profile(request, pk):
	profile = get_object_or_404(
		Personnel, 
		pk = pk
	)
	context["profile"] 	= profile
	return render(request, "profiles/profile.html", context)

def profile_update(request, pk):
	profile = get_object_or_404(
		Personnel, 
		pk = pk
	)

	if request.method == "POST":
		form = UpdatePersonnel(
			request.POST, 
			request.FILES, 
			instance = profile
		)

		if form.is_valid():
			instance = form.save()

			# For updating profile picture
			# if 'image_model' in request.FILES:
			# 	saveProfilePicture(instance.image_model, instance.id)

			return redirect('profile', pk)
	else:
		form = UpdatePersonnel(instance=profile)

	context["form"] 	= form
	context["profile"] 	= profile
	return render(request, "profiles/profile_update.html", context)
