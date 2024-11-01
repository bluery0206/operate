from django.contrib import admin
from .models import (
    Personnel,
    Inmate,
)

admin.site.register(Personnel)
admin.site.register(Inmate)
