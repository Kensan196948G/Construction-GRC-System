from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from grc.cache import CACHE_TTL

from .models import Framework
from .serializers import FrameworkSerializer, FrameworkSummarySerializer


class FrameworkViewSet(viewsets.ReadOnlyModelViewSet):
    """フレームワーク定義 API ViewSet"""

    queryset = Framework.objects.filter(is_active=True)
    serializer_class = FrameworkSerializer
    filterset_fields = ["category", "is_active"]
    search_fields = ["code", "name", "name_ja"]

    @method_decorator(cache_page(CACHE_TTL["framework_list"]))
    def list(self, request, *args, **kwargs):
        """フレームワーク一覧（24時間キャッシュ）"""
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """一覧表示用の軽量データ"""
        frameworks = self.filter_queryset(self.get_queryset())
        serializer = FrameworkSummarySerializer(frameworks, many=True)
        return Response(serializer.data)
