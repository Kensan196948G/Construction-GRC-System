from django.contrib import admin

from .models import Framework


@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    list_display = ["code", "name_ja", "version", "category", "is_active", "updated_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["code", "name", "name_ja", "description"]
    ordering = ["code"]
