from django.contrib import admin

from .models import Evidence, ISO27001Control, NistCSFCategory


@admin.register(ISO27001Control)
class ISO27001ControlAdmin(admin.ModelAdmin):
    list_display = ["control_id", "domain", "title", "implementation_status", "is_applicable", "owner"]
    list_filter = ["domain", "implementation_status", "is_applicable"]
    search_fields = ["control_id", "title"]
    ordering = ["control_id"]


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ["title", "control", "file_name", "file_size", "uploaded_by", "created_at"]
    list_filter = ["control__domain", "file_type", "created_at"]
    search_fields = ["title", "description", "file_name"]
    readonly_fields = ["id", "file_size", "file_type", "created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(NistCSFCategory)
class NistCSFCategoryAdmin(admin.ModelAdmin):
    list_display = ["category_id", "category_name_ja", "function_id", "function_name_ja"]
    list_filter = ["function_id", "function_name_ja"]
    search_fields = ["category_id", "category_name", "category_name_ja", "function_name", "function_name_ja"]
    ordering = ["category_id"]
