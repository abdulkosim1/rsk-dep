from django.contrib import admin
from . models import Document, Service, Terminal, DayOff, LanguageName


class LanguageAdmin(admin.ModelAdmin):
    list_display = ['lang','text']
    

admin.site.register(LanguageName, LanguageAdmin)

class LanguageDocumentInline(admin.TabularInline):
    model = LanguageName.documents.through
    extra = 1

class LanguageServiceInline(admin.TabularInline):
    model = LanguageName.service.through
    extra = 1


class DocumentInline(admin.TabularInline):
    model = Document.service.through
    extra = 0


class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file']
    
    exclude = ['lang_name']
    inlines = [LanguageDocumentInline]

admin.site.register(Document, DocumentAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id','name','auto_transport','service_to_auto_transport']

    exclude = ['documents','lang_name']
    inlines = [DocumentInline,LanguageServiceInline]

admin.site.register(Service, ServiceAdmin)


class TerminalAdmin(admin.ModelAdmin):
    list_display = ['organization','pin','pc_name']
    search_fields = ['pc_name']

admin.site.register(Terminal, TerminalAdmin)


class DayOffAdmin(admin.ModelAdmin):
    list_display = ['day']

admin.site.register(DayOff, DayOffAdmin)