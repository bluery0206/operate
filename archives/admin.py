from django.contrib import admin
from .models import (
    ArchivePersonnel,
    ArchiveInmate,
)

admin.site.register(ArchivePersonnel)
admin.site.register(ArchiveInmate)
