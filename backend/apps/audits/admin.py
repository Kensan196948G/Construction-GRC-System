from django.contrib import admin

from .models import Audit, AuditFinding


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ["audit_id", "title", "audit_type", "target_department", "status", "planned_start"]
    list_filter = ["status", "audit_type"]
    search_fields = ["audit_id", "title"]


@admin.register(AuditFinding)
class AuditFindingAdmin(admin.ModelAdmin):
    list_display = ["finding_id", "audit", "finding_type", "title", "cap_status"]
    list_filter = ["finding_type", "cap_status"]
    search_fields = ["finding_id", "title"]
