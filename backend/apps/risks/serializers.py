from rest_framework import serializers

from .models import Risk


class RiskSerializer(serializers.ModelSerializer):
    risk_score_inherent = serializers.ReadOnlyField()
    risk_score_residual = serializers.ReadOnlyField()
    risk_level = serializers.ReadOnlyField()

    class Meta:
        model = Risk
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class RiskHeatmapSerializer(serializers.Serializer):
    likelihood = serializers.IntegerField()
    impact = serializers.IntegerField()
    count = serializers.IntegerField()
    risks = RiskSerializer(many=True)
