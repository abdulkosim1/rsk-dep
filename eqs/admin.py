from django.contrib import admin
from .models import EQS

class EQSAdmin(admin.ModelAdmin):
    list_display = ['service', 'branch', 'description']
    search_fields = ['service__name', 'branch__name']

admin.site.register(EQS, EQSAdmin)
