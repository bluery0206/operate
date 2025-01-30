from django.db import models


class SearchImage(models.Model):
	image = models.FileField()

      
class Setting(models.Model):
    # Pagination
    profiles_per_page   = models.IntegerField(default = 20)
    thumbnail_size      = models.IntegerField(default = 200)

    # Camera and Cropping
    camera              = models.IntegerField(default = 0)
    cam_clipping        = models.BooleanField(default = True)
    clip_size           = models.IntegerField(default = 200)

    # Search
    threshold           = models.FloatField(default = 1.0)
    input_size          = models.IntegerField(default = 105)
    bbox_size           = models.IntegerField(default = 300)

    # Templates
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

    # Model
    model_detection = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "models"
    )
    model_embedding_generator = models.FileField(
        blank       = True,
        null        = True,
        upload_to   = "models"
    )

