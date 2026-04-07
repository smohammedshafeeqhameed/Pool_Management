from django.contrib import admin
from .models import Villa, CleaningRecord

@admin.register(Villa)
class VillaAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'pool_size', 'added_by', 'created_at')
    search_fields = ('name', 'address')
    list_filter = ('added_by', 'created_at')

@admin.register(CleaningRecord)
class CleaningRecordAdmin(admin.ModelAdmin):
    list_display = ('villa', 'date', 'cleaner', 'ph_level', 'chlorine_level')
    list_filter = ('date', 'cleaner', 'villa')
    search_fields = ('villa__name', 'notes')
