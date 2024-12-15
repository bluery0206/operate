from django.apps import AppConfig
from django.db.utils import OperationalError
from django.db.models.signals import post_migrate
from django.conf import settings


class AppConfig(AppConfig):
    default_auto_field  = 'django.db.models.BigAutoField'
    name                = 'app'

    # Creates initial settings after install or if init settings doesnt exists just yet.
    def ready(self):
        from .models import Setting as operate_setting

        # Connect the signal to run after migrations are complete
        def create_initial_settings(sender, **kwargs):
            try:
                if not operate_setting.objects.exists():
                    
                    # Load default templates and models
                    inmate_template     = str(list(settings.MEDIA_ROOT.glob("templates/profile_inmate_templa*.docx"))[0])
                    personnel_template  = str(list(settings.MEDIA_ROOT.glob("templates/profile_personnel_templa*.docx"))[0])
                    model               = str(list(settings.MEDIA_ROOT.glob("models/*.onnx"))[0])

                    operate_setting.objects.create(
                        personnel_template  = personnel_template if personnel_template else None,
                        inmate_template     = inmate_template if inmate_template else None,
                        model               = model if model else None,
                    )

            except OperationalError:
                pass

        # Connect the signal to `post_migrate`
        post_migrate.connect(create_initial_settings, sender=self)