from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from profiles.models import Personnel, Inmate

context = {
	
}

@login_required
def home(request):
	personnels = Personnel.objects.exclude(archivepersonnel__isnull=False).order_by("-date_profiled")[:5]
	inmates = Inmate.objects.exclude(archiveinmate__isnull=False).order_by("-date_profiled")[:5]

	context["personnels"] = personnels
	context["inmates"] = inmates
	
	return render(request, "home/index.html", context)