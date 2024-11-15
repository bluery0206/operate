from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.shortcuts import (
	render, 
	redirect, 
	get_object_or_404
)	
from datetime import datetime

from .models import ArchivePersonnel, ArchiveInmate
from profiles.models import Personnel, Inmate
from home.utils import save_profile_picture, get_full_name, generate_docx, save_docx
from profiles.models import Personnel, Inmate, Template


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





def personnels(request):
	context = {
		'personnels'	: ArchivePersonnel.objects.all(),
		'ranks'			: [rank[0] for rank in Personnel.RANKS],
		'sort_choices'	: PERSONNEL_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {}
	}

	if request.method == "GET":
		reset_filter		= request.GET.get("reset_filter", None)
		reset_search		= request.GET.get("reset_search", None)
		search				= request.GET.get("search", "").strip()

		if not reset_search and search:
			context['personnels'] = ArchivePersonnel.objects.filter(
		        Q(profile__f_name__icontains=search) |
		        Q(profile__l_name__icontains=search) |
		        Q(profile__m_name__icontains=search)
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

			if designation: 
				context['personnels'] = context['personnels'].filter(profile__designation__icontains=designation)

			if rank: 
				context['personnels'] = context['personnels'].filter(profile__rank=rank)

			if sort_by:
				sort = "-profile__" + sort_by if sort_order == "descending" else "profile__" + sort_by
				context['personnels'] = context['personnels'].order_by(sort)

			context['filters'] = {
				'designation': designation,
				'rank': rank,
				'sort_by': sort_by,
				'sort_order': sort_order,
			}

		context['filters'].update({"search": search})

	return render(request, "archives/personnels.html", context)





def inmates(request):
	context = {
		'inmates'		: ArchiveInmate.objects.all(),
		'sort_choices'	: INMATE_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {}
	}

	if request.method == "GET":
		reset_filter		= request.GET.get("reset_filter", "")
		reset_search		= request.GET.get("reset_search", "")
		search		= request.GET.get("search", "").strip()

		if not reset_search and search:
			context['inmates'] = ArchiveInmate.objects.filter(
		        Q(profile__f_name__icontains=search) |
		        Q(profile__l_name__icontains=search) |
		        Q(profile__m_name__icontains=search)
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

			if crime_violated: 
				context['inmates'] = context['inmates'].filter(profile__crime_violated__icontains=crime_violated)

			if sort_by:
				sort = "-profile__" + sort_by if sort_order == "descending" else "profile__" + sort_by
				context['inmates'] = context['inmates'].order_by(sort)

			context['filters'] = {
				'crime_violated': crime_violated,
				'sort_by': sort_by,
				'sort_order': sort_order,
			}

		context['filters'].update({"search": search})
	return render(request, "archives/inmates.html", context)





def archive_add(request, p_type, pk):
	prev 	= request.GET.get("prev", "")

	p_class, archive_form = [Personnel, ArchivePersonnel] if p_type == "personnel" else [Inmate, ArchiveInmate]

	profile = get_object_or_404(p_class, pk=pk)
	user	= request.user

	if request.method == "POST":
		archive = archive_form(profile=profile, archive_by=user)
		archive.save()

		return redirect(prev) if prev else redirect('profile', p_type, profile.pk)

	context = {
		'title' 	: f"Add {get_full_name(profile)}'s profile to archives?",
		'warning' 	: f"You will not be able to see this profile in the \"Profile\" Page anymore.",
	}
	return render(request, "home/confirmation_page.html", context)





def archive_remove(request, p_type, pk):
	prev 	= request.GET.get("prev", "")

	a_class = ArchivePersonnel if p_type == "personnel" else ArchiveInmate

	archive = get_object_or_404(a_class, pk=pk)

	if request.method == "POST":
		archive.delete()

		return redirect(prev) if prev else redirect('profile', p_type, archive.profile.pk)

	context = {
		'title' : f"Remove {get_full_name(archive.profile)}'s profile from archives",
	}
	return render(request, "home/confirmation_page.html", context)





def archive_add_all(request, p_type):
	prev 	= request.GET.get("prev", "")

	if request.method == "POST":
		if p_type == "personnel":
			profiles = Personnel.objects.exclude(archivepersonnel__isnull=False).all() 
			a_class = ArchivePersonnel
		else:
			profiles = Inmate.objects.exclude(archiveinmate__isnull=False).all() 
			a_class = ArchiveInmate

		user = request.user

		for profile in profiles:
			archive = a_class.objects.create(archive_by=user, profile=profile)
			archive.save()

		return redirect(prev) if prev else redirect(f'archives-{p_type}s')

	context = {
		'title' 	: f"Add all profiles to archives",
		'warning' 	: f"You will not be able to see all profiles in the \"Profile\" Page anymore.",
	}
	return render(request, "home/confirmation_page.html", context)





def archive_remove_all(request, p_type):
	prev 	= request.GET.get("prev", "")
	a_class = ArchivePersonnel if p_type == "personnel" else ArchiveInmate

	if request.method == "POST":
		a_class.objects.all().delete()

		return redirect(prev) if prev else redirect(f'profiles-{p_type}s')

	context = {
		'title' 	: f"Remove all profiles from archives",
	}
	return render(request, "home/confirmation_page.html", context)




