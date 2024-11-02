from django.shortcuts import render, get_object_or_404, redirect

from .models import ArchivePersonnel, ArchiveInmate
from profiles.models import Personnel, Inmate
from home.utils import get_full_name




def personnels(request):
	context = {
		'archived_personnels': ArchivePersonnel.objects.all()
	}
	return render(request, "archives/personnels.html", context)




def inmates(request):
	context = {
		'archived_inmates': ArchiveInmate.objects.all()
	}
	return render(request, "archives/inmates.html", context)


 

def archive_profile_personnel(request, pk):
	context = {
		'archive': get_object_or_404(ArchivePersonnel, pk=pk)
	}
	return render(request, "archives/archive_profile_personnel.html", context)




def archive_profile_inmate(request, pk):
	context = {
		'archive': get_object_or_404(ArchiveInmate, pk=pk)
	}
	return render(request, "archives/archive_profile_inmate.html", context)




def archive_personnel_add(request, pk):
	prev 	= request.GET.get("prev", "")
	profile = get_object_or_404(Personnel, pk=pk)
	user	= request.user

	if request.method == "POST":
		archive = ArchivePersonnel(profile=profile, archive_by=user)

		archive.save()
		return redirect(prev)

	context = {
		'title' 	: "Add archive",
		'action' 	: f"add {get_full_name(profile)} to",
		'profile' 	: profile,
	}
	return render(request, "archives/archives_confirm_template.html", context)




def archive_inmate_add(request, pk):
	prev 	= request.GET.get("prev", "")
	profile = get_object_or_404(Inmate, pk=pk)
	user	= request.user

	if request.method == "POST":
		archive = ArchiveInmate(profile=profile, archive_by=user)

		archive.save()
		return redirect(prev)

	context = {
		'title': "Add archive",
		'action': f"add {get_full_name(profile)} to",
		'profile': profile,
	}
	return render(request, "archives/archives_confirm_template.html", context)




def archive_personnel_remove(request, pk):
	prev	= request.GET.get("prev", "")
	archive = get_object_or_404(ArchivePersonnel, pk=pk)

	if request.method == "POST":
		archive.delete()
		return redirect(prev)

	context = {
		'title' 	: "Remove archive",
		'action' 	: f"remove {get_full_name(archive.profile)} from",
		'archive' 	: archive,
	}
	return render(request, "archives/archives_confirm_template.html", context)




def archive_inmate_remove(request, pk):
	prev	= request.GET.get("prev", "")
	archive = get_object_or_404(ArchiveInmate, pk=pk)

	if request.method == "POST":
		archive.delete()
		return redirect(prev)

	context = {
		'title': "Remove archive",
		'action': f"remove {get_full_name(archive.profile)} from",
		'archive': archive,
	}
	return render(request, "archives/archives_confirm_template.html", context)





