from django.contrib import admin
from .models import (
    Personnel,
    Inmate,
    Template,
)

admin.site.register(Personnel)
admin.site.register(Inmate)
admin.site.register(Template)
