from rest_framework import serializers

from .models import ISO27001Control


class ISO27001ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ISO27001Control
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class SoASerializer(serializers.ModelSerializer):
    """適用宣言書（Statement of Applicability）用シリアライザ"""

    class Meta:
        model = ISO27001Control
        fields = [
            "control_id",
            "domain",
            "title",
            "is_applicable",
            "exclusion_reason",
            "implementation_status",
            "owner",
            "evidence_required",
            "nist_csf_mapping",
        ]
