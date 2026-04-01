"""カスタムページネーション

大量データ向けの最適化されたページネーションクラス。
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """標準ページネーション (20件/ページ)"""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """大量データ用ページネーション (100件/ページ)"""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


class SmallPagination(PageNumberPagination):
    """軽量データ用ページネーション (10件/ページ)"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
