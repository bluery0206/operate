from django.shortcuts import render

# Create your views here.
def personnels(request):
	return render(request, "profiles/personnels.html")

def inmates(request):
	return render(request, "profiles/inmates.html")

def profile(request, pk):
	return render(request, "profiles/profile.html")