from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LicenseList,AboutLicense

admin.site.register(LicenseList)
admin.site.register(AboutLicense)
