"""
安全相关功能模块 - 简化版，只保留核心功能
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from src.core.config import settings


class SecurityError(Exception):
    """安全相关异常基类"""
    pass


class TokenError(SecurityError):
    """Token相关异常"""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        import bcrypt
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        raise SecurityError(f"密码哈希生成失败: {str(e)}")


def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": now})

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        raise TokenError("令牌创建失败")


def verify_token(token: str) -> Dict[str, Any]:
    """验证令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        exp = payload.get("exp")
        if exp is None:
            raise TokenError("无效令牌")

        return payload

    except JWTError as e:
        raise TokenError("无效令牌")
    except Exception as e:
        raise TokenError("令牌验证失败")


def verify_websocket_token(token: str) -> Dict[str, Any]:
    """验证WebSocket令牌"""
    return verify_token(token)


__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "verify_token",
    "verify_websocket_token",
    "SecurityError",
    "TokenError",
]
