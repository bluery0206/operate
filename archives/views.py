from django.shortcuts import render, get_object_or_404, redirect
from .models import Personnel, Inmate
from profiles import models as profiles
from home.utils import get_full_name

context = {}

# Create your views here.
def personnel(request):
	return render(request, "archives/personnels.html", context)

def inmate(request):
	return render(request, "archives/inmates.html")

def profile(request, pk):
	return render(request, "archives/profile.html", context)

def archive(request, pk):
	return render(request, "archives/archive_confirm.html", context)

def remove(request, pk):
	return render(request, "archives/archive_confirm.html", context)



# 	from django.shortcuts import render, get_object_or_404, redirect
# from .models import Personnel, Inmate
# from profiles import models as profiles
# from home.utils import get_full_name
# context = {}

# # Create your views here.
# def personnel(request):
# 	personnels = Personnel.objects.all()

# 	context['personnels'] = personnels
# 	return render(request, "archives/personnels.html", context)

# def inmate(request):
# 	return render(request, "archives/inmates.html")

# def profile(request, pk):
# 	profile = get_object_or_404(Personnel, pk=pk)
	
# 	context["profile"] 	= profile
# 	return render(request, "archives/profile.html", context)

# def archive(request, pk):
# 	prev_page 	= request.GET.get("next", "")

# 	profile = get_object_or_404(profiles.Personnel, pk=pk)
# 	user	= request.user

# 	if request.method == "POST":
# 		archive = Personnel(profile=profile, archive_by=user)
# 		archive.save()
# 		return redirect(prev_page)

# 	context['action'] = f"add {get_full_name(profile)} to"
# 	context['profile'] = profile
# 	return render(request, "archives/archive_confirm.html", context)

# def remove(request, pk):
# 	prev_page 	= request.GET.get("next", "")

# 	profile = get_object_or_404(Personnel, pk=pk)
# 	user	= request.user

# 	if request.method == "POST":
# 		archive = Personnel(profile=profile, archive_by=user)
# 		archive.delete()
# 		return redirect(prev_page)

# 	context['action'] = f"remove {get_full_name(profile)} from"
# 	context['profile'] = profile
# 	return render(request, "archives/archive_confirm.html", context)