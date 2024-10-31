from django.shortcuts import render

# Create your views here.
def personnel(request):
	return render(request, "profiles/personnels.html")

def inmate(request):
	return render(request, "profiles/inmates.html")

def profile(request, pk):
	return render(request, "profiles/profile.html")