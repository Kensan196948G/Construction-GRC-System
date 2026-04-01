"""Test settings — SQLite + minimal config."""

from .base import *  # noqa: F401, F403

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# --- ArrayField SQLite 互換パッチ ---
# PostgreSQL の ArrayField は SQLite で動作しないため
# マイグレーション実行時に JSONField として振る舞うようパッチ
import django.contrib.postgres.fields as _pg_fields  # noqa: E402
from django.db import models as _models  # noqa: E402

_OrigArrayField = _pg_fields.ArrayField


class _SQLiteArrayField(_models.JSONField):
    """SQLite用 ArrayField 代替（JSONField ベース）"""

    def __init__(self, base_field=None, size=None, **kwargs):
        self.base_field = base_field
        self.size = size
        kwargs.setdefault("default", list)
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, "django.contrib.postgres.fields.ArrayField", args, kwargs


_pg_fields.ArrayField = _SQLiteArrayField
# ---

# Disable Redis cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery in eager mode for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
