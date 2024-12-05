from django.shortcuts import render, redirect

from facesearch.utils import update_image_embeddings
from settings.models import OperateSetting
from .forms import OperateSettingsForm

# Create your views here.
def settings(request):
    defset  = OperateSetting.objects.first()
    form    = OperateSettingsForm(instance=defset)

    if request.method == "POST":
        form = OperateSettingsForm(request.POST, request.FILES, instance=defset)

        if form.is_valid():
            if not request.FILES.get('inmate_template'):
                form.instance.inmate_template = defset.inmate_template

            if not request.FILES.get('personnel_template'):
                form.instance.personnel_template = defset.personnel_template

            if not request.FILES.get('model'):
                form.instance.model = defset.model

            instance = form.save()
            
            if request.FILES.get('model'):
                update_image_embeddings()

            return redirect('operate-settings')

    context = {
        'p_type'            : 'personnel',
        'page_title'        : 'Settings',
        'default_settings'  : defset,
        'form'              : form,
        'active'            : 'user settings'
    }
    return render(request, "settings/settings.html", context)