from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.shortcuts import (
	render, 
	redirect, 
	get_object_or_404
)	
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import ArchivePersonnel, ArchiveInmate
from profiles.models import Personnel, Inmate
from settings.models import OperateSetting
from home.utils import get_full_name


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
		'filters'		: {},
		'page_title'	: "Archived Personnel Profiles",
		'p_type'		: 'personnel',
		'active'		: 'archives personnels'
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
				'designation'	: designation,
				'rank'			: rank,
				'sort_by'		: sort_by,
				'sort_order'	: sort_order,
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

	return render(request, "archives/personnels.html", context)





def inmates(request):
	context = {
		'inmates'		: ArchiveInmate.objects.all(),
		'sort_choices'	: INMATE_SORT_CHOICES,
		'order_choices'	: ORDER_CHOICES,
		'filters'		: {},
		'page_title'	: "Archived Inmate Profiles",
		'p_type'		: 'inmate',
		'active'		: 'archives inmates'
	}

	if request.method == "GET":
		reset_filter		= request.GET.get("reset_filter", "")
		reset_search		= request.GET.get("reset_search", "")
		search				= request.GET.get("search", "").strip()

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
				'sort_by'		: sort_by,
				'sort_order'	: sort_order,
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
		'title' 		: f"Add {get_full_name(profile)}'s profile to archives?",
		'warning' 		: f"You will not be able to see this profile in the \"Profile\" Page anymore.",
		'page_title'	: f"Archiving {get_full_name(profile)}'s Profile",
		'p_type'		: p_type,
		'active'		: 'archive ' + p_type
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
		'title' 	: f"Remove {get_full_name(archive.profile)}'s profile from archives",
		'p_type'	: p_type,
		'active'	: 'archive ' + p_type
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
		'title' 		: f"Add all {p_type} profiles to archives",
		'warning' 		: f"You will not be able to see all profiles in the \"Profile\" Page anymore. You can still view them in the \"Archives section\"",
		'page_title'	: f"Archiving All Profiles",
		'p_type'		: p_type,
		'active'		: 'archive ' + p_type
	}
	return render(request, "home/confirmation_page.html", context)





def archive_remove_all(request, p_type):
	prev 	= request.GET.get("prev", "")
	a_class = ArchivePersonnel if p_type == "personnel" else ArchiveInmate

	if request.method == "POST":
		a_class.objects.all().delete()

		return redirect(prev) if prev else redirect(f'profiles-{p_type}s')

	context = {
		'title' 		: f"Remove all {p_type} profiles from archives",
		'page_title'	: f"Unachiving All Profiles",
		'p_type'		: p_type,
		'active'		: 'archive ' + p_type
	}
	return render(request, "home/confirmation_page.html", context)




