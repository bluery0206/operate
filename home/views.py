from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from profiles.models import Personnel, Inmate

context = {
	
}

@login_required
def home(request):
	personnels = Personnel.objects.all()[:5]
	inmates = Inmate.objects.all()[:5]

	context["personnels"] = personnels
	context["inmates"] = inmates
	
	return render(request, "home/index.html", context)