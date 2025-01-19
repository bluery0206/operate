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
                    template_inmate     = str(list(settings.MEDIA_ROOT.glob("templates/profile_inmate_templa*.docx"))[0])
                    template_personnel  = str(list(settings.MEDIA_ROOT.glob("templates/profile_personnel_templa*.docx"))[0])
                    model_recognition   = str(list(settings.MEDIA_ROOT.glob("models/*emb_gen*.onnx"))[0])
                    model_detection     = str(list(settings.MEDIA_ROOT.glob("models/*face_det*.onnx"))[0])

                    operate_setting.objects.create(
                        template_personnel  = template_personnel if template_personnel else None,
                        template_inmate     = template_inmate if template_inmate else None,
                        model_recognition   = model_recognition if model_recognition else None,
                        model_detection     = model_detection if model_detection else None,
                    )

            except OperationalError:
                pass

        # Connect the signal to `post_migrate`
        post_migrate.connect(create_initial_settings, sender=self)