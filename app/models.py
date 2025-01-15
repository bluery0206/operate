from django.db import models



# Pagination
# Camera and Cropping
# Search
# Templates
# Model



class SearchImage(models.Model):
	image = models.FileField()


      
class Setting(models.Model):
    profiles_per_page   = models.IntegerField(default = 20)
    thumbnail_size      = models.IntegerField(default = 200)

    camera              = models.IntegerField(default = 0)
    clip_camera         = models.BooleanField(default = True)
    clip_size           = models.IntegerField(default = 200)

    threshold           = models.FloatField(default = 1.0)
    input_size          = models.IntegerField(default = 105)
    search_mode         = models.CharField(
        default='embedding',
        choices=[
            ('embedding', 'Embedding (Faster)'),
            ('image', 'Image'),
        ],
        max_length=9,
    )

    template_personnel  = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "templates"
    )
    template_inmate     = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "templates"
    )

    model_recognition = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "models"
    )

    model_detection = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "models"
    )

