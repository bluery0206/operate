from django.apps import AppConfig
from django.db.utils import OperationalError
from django.db.models.signals import post_migrate
from pathlib import Path


class SettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings'

    # Creates initial settings after install or if init settings doesnt exists just yet.
    def ready(self):
        from .models import OperateSetting
        operate_setting = OperateSetting

        # Connect the signal to run after migrations are complete
        def create_initial_settings(sender, **kwargs):
            try:
                if not operate_setting.objects.exists():
                    
                    # Load default templates and models
                    inmate_template     = list(Path.cwd().glob("media/templates/profile_inmate_templa*.docx"))
                    personnel_template  = list(Path.cwd().glob("media/templates/profile_personnel_templa*.docx"))
                    model               = list(Path.cwd().glob("media/models/*.onnx"))

                    operate_setting.objects.create(
                        personnel_template=str(personnel_template[0]) if personnel_template else None,
                        inmate_template=str(inmate_template[0]) if inmate_template else None,
                        model=str(model[0]) if model else None,
                    )
                    print("Default settings created successfully.")
            except OperationalError:
                print("Database is not ready. Skipping default settings creation.")

        # Connect the signal to `post_migrate`
        post_migrate.connect(create_initial_settings, sender=self)