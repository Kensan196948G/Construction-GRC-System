from rest_framework import serializers

from .models import Framework


class FrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Framework
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class FrameworkSummarySerializer(serializers.ModelSerializer):
    """一覧表示用の軽量シリアライザ"""

    class Meta:
        model = Framework
        fields = ["id", "code", "name", "name_ja", "version", "category", "is_active"]
