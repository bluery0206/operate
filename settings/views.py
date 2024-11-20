from django.shortcuts import render, redirect
from .models import OperateSetting
from .forms import OperateSettingsForm

OPERATE_SETTINGS = OperateSetting.objects.first()
OPERATE_SETTINGS.crop_camera = int(OPERATE_SETTINGS.crop_camera)
# OPERATE_SETTINGS = None

# Create your views here.
def settings(request):
    context = {
        'default_settings': OPERATE_SETTINGS,
        'p_type' : 'personnel',
        'page_title': 'Settings',
        'form': OperateSettingsForm(instance=OPERATE_SETTINGS)
    }

    if request.method == "POST":
        context['form'] = OperateSettingsForm(request.POST, request.FILES, instance=OPERATE_SETTINGS)

        if context['form'].is_valid():
            if not request.FILES.get('inmate_template'):
                context['form'].instance.inmate_template = OPERATE_SETTINGS.inmate_template

            if not request.FILES.get('personnel_template'):
                context['form'].instance.personnel_template = OPERATE_SETTINGS.personnel_template

            context['form'].save()
            return redirect('operate-settings')

    return render(request, "settings/settings.html", context)