from django.contrib import admin

from .models import ComplianceRequirement


@admin.register(ComplianceRequirement)
class ComplianceRequirementAdmin(admin.ModelAdmin):
    list_display = ["req_id", "framework", "title", "compliance_status", "is_mandatory", "owner"]
    list_filter = ["framework", "compliance_status", "is_mandatory"]
    search_fields = ["req_id", "title"]
