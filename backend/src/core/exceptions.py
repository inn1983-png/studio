from typing import Any, Optional

class TxtovideoException(Exception):
    """Txtovideo Studio 基础异常类"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)

class NotFoundError(TxtovideoException):
    """资源不存在异常"""
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )

class BusinessLogicError(TxtovideoException):
    """业务逻辑异常"""
    def __init__(self, message: str, code: str = "BUSINESS_ERROR"):
        super().__init__(
            message=message,
            status_code=400,
            error_code=code
        )

class PermissionDeniedError(TxtovideoException):
    """权限不足异常"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="PERMISSION_DENIED"
        )

class AuthenticationError(TxtovideoException):
    """认证失败异常"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_FAILED"
        )

class ValidationError(TxtovideoException):
    """数据验证异常"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR"
        )

class FileUploadError(TxtovideoException):
    """文件上传异常"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR"
        )
