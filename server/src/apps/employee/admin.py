from django.contrib import admin
from django.contrib.auth.hashers import make_password

from apps.base.models import Service
from .models import User


class ServiceInline(admin.TabularInline):
    model = Service.employee.through
    extra = 0


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'window', 'position', 'shift', 'branch', 'comment', 'status', 'auto_call', 'max_transport', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    fieldsets = [
        (None, {'fields': ['username', 'email', 'password']}),
        ('Personal Info', {'fields': ['window', 'position', 'shift', 'branch']}),
        ('Additional Info', {'fields': ['comment', 'status', 'auto_call', 'max_transport']}),
        ('Permissions', {'fields': ['is_staff', 'is_active']}),
    ]
    exclude = ['service']

    inlines = [ServiceInline]

    def save_model(self, request, obj, form, change):
        if not change or form.cleaned_data['password']:
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)
