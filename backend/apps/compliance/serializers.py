from rest_framework import serializers

from .models import ComplianceRequirement


class ComplianceRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceRequirement
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
