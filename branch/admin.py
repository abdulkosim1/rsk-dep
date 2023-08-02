from django.contrib import admin

from .models import Branch, Window
from apps.talon.models import Monitor
from apps.base.models import Service, LanguageName

class ServiceInline(admin.TabularInline):
    model = Service.branch.through
    extra = 0

class LanguageServiceInline(admin.TabularInline):
    model = LanguageName.branch.through
    extra = 1


class BranchAdmin(admin.ModelAdmin):
    list_display = ['city', 'address', 'terminal', 'work_time_start','work_time_end']
    search_fields = ['city', 'address']
    list_filter = ['city','address']

    exclude = ['service','lang_name']

    inlines = [ServiceInline,LanguageServiceInline]


admin.site.register(Branch, BranchAdmin)
admin.site.register(Window)
admin.site.register(Monitor)


