from rest_framework import serializers

from .models import Evidence, ISO27001Control, NistCSFCategory


class ISO27001ControlSerializer(serializers.ModelSerializer):
    # ArrayField(CharField) は DRF が内部フィールドの .model を参照してエラーになるため明示宣言
    evidence_required = serializers.ListField(child=serializers.CharField(), required=False)
    nist_csf_mapping = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = ISO27001Control
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class NistCSFCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NistCSFCategory
        fields = "__all__"


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = "__all__"
        read_only_fields = [
            "id",
            "file_name",
            "file_size",
            "file_type",
            "uploaded_by",
            "created_at",
            "updated_at",
        ]


class SoASerializer(serializers.ModelSerializer):
    """適用宣言書（Statement of Applicability）用シリアライザ"""

    # ArrayField(CharField) は DRF が内部フィールドの .model を参照してエラーになるため明示宣言
    evidence_required = serializers.ListField(child=serializers.CharField(), read_only=True)
    nist_csf_mapping = serializers.ListField(child=serializers.CharField(), read_only=True)

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
