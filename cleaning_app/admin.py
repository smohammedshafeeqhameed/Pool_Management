from django.contrib import admin
from .models import Villa

@admin.register(Villa)
class VillaAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'latitude', 'longitude', 'added_by', 'created_at')
    search_fields = ('name', 'phone_number')
    list_filter = ('added_by', 'created_at')
