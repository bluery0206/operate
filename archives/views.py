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



def unarchive_all_inmate(request):
	prev 	= request.GET.get("prev", "")
	

	if request.method == "POST":

		ArchiveInmate.objects.all().delete()
		return redirect(prev)

	return render(request, "archives/profile_unarchive_all.html")


def unarchive_all_personnel(request):
	prev 	= request.GET.get("prev", "")

	if request.method == "POST":

		ArchivePersonnel.objects.all().delete()
		return redirect(prev)

	return render(request, "archives/profile_unarchive_all.html")


def archive_all_personnel(request):
	prev 	= request.GET.get("prev", "")
	# archive_by	
	# profile
	if request.method == "POST":
		profiles = Personnel.objects.all()
		user = request.user

		for profile in profiles:
			archive = ArchivePersonnel.objects.create(archive_by=user, profile=profile)
			archive.save()

		return redirect(prev)

	return render(request, "archives/profile_archive_all.html")





def archive_all_inmate(request):
	prev 	= request.GET.get("prev", "")

	if request.method == "POST":
		profiles = Inmate.objects.all()
		user = request.user

		for profile in profiles:
			archive = ArchiveInmate.objects.create(archive_by=user, profile=profile)
			archive.save()

		return redirect(prev)

	return render(request, "archives/profile_archive_all.html")


def archive_add(request, p_type, pk):
	prev 	= request.GET.get("prev", "")

	p_class, archive_form = [Personnel, ArchivePersonnel] if p_type == "personnel" else [Inmate, ArchiveInmate]

	profile = get_object_or_404(p_class, pk=pk)
	user	= request.user

	if request.method == "POST":
		archive = archive_form(profile=profile, archive_by=user)
		archive.save()

		return redirect(prev)

	context = {
		'title' 	: f"Add {get_full_name(profile)} to archives?",
		'warning' 	: f"You will not be able to see this profile in the \"Profile\" Page anymore.",
		'profile' 	: profile,
	}
	return render(request, "home/confirmation_page.html", context)