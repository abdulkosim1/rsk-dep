from django.contrib import admin
from . models import Client




class ClientAdmin(admin.ModelAdmin):
    list_display = ['phone','id']
    

admin.site.register(Client, ClientAdmin)