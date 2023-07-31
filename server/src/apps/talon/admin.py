from django.contrib import admin
from . models import Talon



class TalonAdmin(admin.ModelAdmin):
    list_display = ['token', 'status', 'client_type', 'is_pensioner', 'client_comment', 'branch', 'appointment_date', 'service_start', 'service_end', 'employee_comment', 'registered_at', 'updated_at']
    search_fields = ['token', 'client_comment']
    list_filter = ['branch', 'status']
    readonly_fields = ['registered_at', 'updated_at']

admin.site.register(Talon, TalonAdmin)

