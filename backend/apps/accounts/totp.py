"""TOTP 二要素認証基盤

pyotp ベースの TOTP (Time-based One-Time Password) 生成・検証。
将来的にQRコード生成・リカバリーコードも追加予定。
"""

from __future__ import annotations

import secrets
import string


def generate_totp_secret() -> str:
    """32文字のBase32 TOTP秘密鍵を生成する。"""
    alphabet = string.ascii_uppercase + "234567"
    return "".join(secrets.choice(alphabet) for _ in range(32))


def verify_totp(secret: str, token: str) -> bool:
    """TOTPトークンを検証する。pyotpが利用可能な場合に使用。"""
    try:
        import pyotp

        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    except ImportError:
        return False


def get_provisioning_uri(secret: str, username: str, issuer: str = "Construction-GRC") -> str:
    """QRコード用のプロビジョニングURIを生成する。"""
    try:
        import pyotp

        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)
    except ImportError:
        return ""
