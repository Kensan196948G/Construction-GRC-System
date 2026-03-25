from django.contrib import admin

from .models import ISO27001Control


@admin.register(ISO27001Control)
class ISO27001ControlAdmin(admin.ModelAdmin):
    list_display = ["control_id", "domain", "title", "implementation_status", "is_applicable", "owner"]
    list_filter = ["domain", "implementation_status", "is_applicable"]
    search_fields = ["control_id", "title"]
    ordering = ["control_id"]
