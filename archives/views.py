from django.shortcuts import render
from .models import Personnel, Inmate
import profiles
from home.utils import get_full_name
context = {}

# Create your views here.
def personnel(request):
	personnels = Personnel.objects.all()

	context['personnels'] = personnels
	return render(request, "archives/personnels.html", context)

def inmate(request):
	return render(request, "archives/inmates.html")

def profile(request, pk):
	return render(request, "profiles/profile.html")

def archive(request, profile):
	# p_type	= profiles.Personnel if p_type=="personnel" else profiles.Inmate
	# profile = get_object_or_404(p_type, pk=pk)
	# user	= request.user

	# if request.method == "POST":
	# 	archive = Archives(profile=profile, archive_by=user)
	# 	archive.save()
	# 	return redirect(prev_page)

	context['profile'] = profile
	return render(request, "archives/archive_confirm.html", context)