from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Used Django's default login and logout view so they're not here but on the urls.py

@login_required
def home(request):
	return render(request, "user/index.html")

@login_required
def user(request):
	return render(request, "user/index.html")