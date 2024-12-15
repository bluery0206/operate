from django.db import models

class SearchImage(models.Model):
	image = models.FileField()
      
class Setting(models.Model):
    # Pagination
    profiles_per_page   = models.IntegerField(default = 20)
    thumbnail_size      = models.IntegerField(default = 200)

    # Camera and Cropping
    camera              = models.IntegerField(default = 0)
    crop_size           = models.IntegerField(default = 200)
    crop_camera         = models.CharField(
                                default='1',
                                choices=[
                                    ('0', 'Do not crop'),
                                    ('1', 'Crop'),
                                ],
                                max_length=1,
                            )

    # Search
    threshold   = models.FloatField(default = 1.0)
    search_mode = models.CharField(
        default='1',
        choices=[
            ('1', 'Embedding (Faster)'),
            ('0', 'Image'),
        ],
        max_length=1,
    )

    # Templates
    template_personnel = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "templates"
    )
    template_inmate = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "templates"
    )

    # Model
    model = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "models"
    )

