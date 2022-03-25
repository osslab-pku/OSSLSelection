from django.apps import AppConfig
from django.contrib import admin


class HomepageConfig(AppConfig):
    name = 'homepage'
    admin.site.site_header = 'OSS License Selection'