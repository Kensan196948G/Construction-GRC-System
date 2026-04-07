from rest_framework import serializers

from .models import ComplianceRequirement


class ComplianceRequirementSerializer(serializers.ModelSerializer):
    # ArrayField(UUIDField) は DRF が内部フィールドの .model を参照してエラーになるため明示宣言
    evidence_ids = serializers.ListField(child=serializers.UUIDField(), required=False)

    class Meta:
        model = ComplianceRequirement
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
