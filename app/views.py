from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from facesearch.utils import update_image_embeddings

from . import (
    models 	as app_models,
    forms 	as app_forms,
)
from profiles.models import (
    Personnel, 
    Inmate
)

FORM_DEFAULT_SETTINGS 	= app_forms.FormOperateSettings
DEFAULT_SETTINGS 		= app_models.DefaultSettings


@login_required
def index(request):
	# Get five (5) recently created profiles that are not archived
	personnels 	= Personnel.objects.exclude(archivepersonnel__isnull= False).order_by("-date_profiled")[:5]
	inmates 	= Inmate.objects.exclude(archiveinmate__isnull= False).order_by("-date_profiled")[:5]

	context = {
		'page_title'	: "Home",
		'active'		: "home",
		"personnels"	: personnels,
		"inmates"		: inmates,
	}
	return render(request, "app/index.html", context)


@login_required
def settings(request):
	default_settings = DEFAULT_SETTINGS.objects.first()

	if request.method == "POST":
		form = FORM_DEFAULT_SETTINGS(request.POST, request.FILES, instance=default_settings)

		if form.is_valid():
			if not request.FILES.get('inmate_template'):
				form.instance.inmate_template = default_settings.inmate_template

			if not request.FILES.get('personnel_template'):
				form.instance.personnel_template = default_settings.personnel_template

			if not request.FILES.get('model'):
				form.instance.model = default_settings.model

			instance = form.save()

			if request.FILES.get('model'):
				update_image_embeddings()

			return redirect('operate-settings')
	else:
		form = FORM_DEFAULT_SETTINGS(instance = default_settings)

	context = {
		'page_title'	: 'Settings',
		'active'		: 'user settings',
		'settings'		: default_settings,
		'form'			: form,
	}
	return render(request, "settings/settings.html", context)