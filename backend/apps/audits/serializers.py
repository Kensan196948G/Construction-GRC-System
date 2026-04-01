from rest_framework import serializers

from .models import ActivityLog, Audit, AuditFinding


class AuditFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditFinding
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AuditSerializer(serializers.ModelSerializer):
    findings = AuditFindingSerializer(many=True, read_only=True)
    findings_count = serializers.SerializerMethodField()

    class Meta:
        model = Audit
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_findings_count(self, obj):
        return obj.findings.count()


class ActivityLogSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "action",
            "model_name",
            "object_id",
            "object_repr",
            "changes",
            "ip_address",
            "timestamp",
        ]

    def get_user_display(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "システム"
