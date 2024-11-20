from django.db import models


# Create your models here.
class OperateSetting(models.Model):
    default_threshold = models.FloatField(
        default = 1.0,
        blank   = True,
        null    = True
    )

    default_camera = models.IntegerField(
        default = 1,
        blank   = True,
        null    = True
    )

    default_profiles_per_page = models.IntegerField(
        default = 20,
        blank   = True,
        null    = True
    )

    default_thumbnail_size = models.IntegerField(
        default = 200,
        blank   = True,
        null    = True
    )

    crop_camera = models.CharField(
        default='0',
        choices=[
            (0, 'Do not crop'),
            (1, 'Crop'),
        ],
        max_length=1,
    )

    default_crop_size = models.IntegerField(
        default = 200,
        blank   = True,
        null    = True
    )

    default_search_method = models.CharField(
        default='1',
        choices=[
            (1, 'Embedding (Faster)'),
            (0, 'Image'),
        ],
        max_length=1,
    )

    personnel_template = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "templates"
    )

    inmate_template = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "templates"
    )

    model = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "model"
    )









