from django.contrib import admin

from .models import Risk


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ["risk_id", "title", "category", "risk_level", "status", "risk_owner", "updated_at"]
    list_filter = ["category", "status", "treatment_strategy"]
    search_fields = ["risk_id", "title", "description"]
    ordering = ["-updated_at"]
