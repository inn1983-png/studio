"""
文件存储客户端 - 支持 MinIO 和本地存储
MinIO 不可用时自动降级为本地文件存储
"""

import asyncio
import os
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from fastapi import UploadFile

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class StorageError(Exception):
    pass


class LocalStorage:
    """本地文件系统存储"""

    def __init__(self):
        self.base_dir = Path(settings.MINIO_ENDPOINT if False else "storage")
        self.base_dir = Path(os.environ.get("LOCAL_STORAGE_DIR", "storage"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._available = True
        logger.info(f"本地文件存储已初始化, 目录: {self.base_dir.resolve()}")

    def _resolve_path(self, object_key: str) -> Path:
        path = (self.base_dir / object_key).resolve()
        if not str(path).startswith(str(self.base_dir.resolve())):
            raise ValueError("Invalid path: directory traversal detected")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def generate_object_key(self, user_id: str, filename: str, prefix: str = "uploads") -> str:
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{prefix}/{user_id}/{date_str}/{unique_name}"

    async def ensure_bucket_exists(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
            self,
            user_id: str,
            file: UploadFile,
            object_key: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            if not object_key:
                object_key = self.generate_object_key(user_id, file.filename)

            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)

            dest = self._resolve_path(object_key)
            async with aiofiles.open(dest, 'wb') as f:
                while True:
                    chunk = file.file.read(65536)
                    if not chunk:
                        break
                    await f.write(chunk)

            if metadata:
                meta_path = dest.with_suffix(dest.suffix + '.meta')
                async with aiofiles.open(meta_path, 'w', encoding='utf-8') as f:
                    for k, v in metadata.items():
                        await f.write(f"{k}={v}\n")

            logger.info(f"文件上传成功(本地): {object_key}, 大小: {file_size} bytes")

            return {
                "bucket": "local",
                "object_key": object_key,
                "size": file_size,
                "etag": str(uuid.uuid4())[:32],
                "url": self.get_presigned_url(object_key),
            }
        except Exception as e:
            logger.error(f"本地上传失败: {e}")
            raise StorageError(f"文件上传失败: {str(e)}")

    async def upload_file_from_path(
            self,
            user_id: str,
            file_path: str,
            original_filename: str,
            object_key: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            if not object_key:
                object_key = self.generate_object_key(user_id, original_filename)

            file_size = Path(file_path).stat().st_size
            dest = self._resolve_path(object_key)
            shutil.copy2(file_path, dest)

            logger.info(f"文件上传成功(本地): {object_key}, 大小: {file_size} bytes")

            return {
                "bucket": "local",
                "object_key": object_key,
                "size": file_size,
                "etag": str(uuid.uuid4())[:32],
                "url": self.get_presigned_url(object_key),
            }
        except Exception as e:
            logger.error(f"本地上传失败: {e}")
            raise StorageError(f"文件上传失败: {str(e)}")

    def get_presigned_url(self, object_key: str, expires: timedelta = timedelta(hours=1)) -> str:
        return f"/api/v1/files/local/{object_key}"

    async def download_file(self, object_key: str) -> bytes:
        path = self._resolve_path(object_key)
        if not path.exists():
            raise StorageError(f"文件不存在: {object_key}")
        async with aiofiles.open(path, 'rb') as f:
            return await f.read()

    async def download_file_to_path(self, object_key: str, dest_path: str) -> None:
        src = self._resolve_path(object_key)
        if not src.exists():
            raise StorageError(f"文件不存在: {object_key}")
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), dest_path)

    async def delete_file(self, object_key: str) -> bool:
        path = self._resolve_path(object_key)
        meta_path = path.with_suffix(path.suffix + '.meta')
        try:
            if path.exists():
                path.unlink()
            if meta_path.exists():
                meta_path.unlink()
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False

    async def copy_file(self, source_object_key: str, dest_object_key: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        src = self._resolve_path(source_object_key)
        dest = self._resolve_path(dest_object_key)
        if not src.exists():
            return False
        shutil.copy2(str(src), str(dest))
        return True

    async def list_files(self, prefix: str, limit: int = 100) -> List[Dict[str, Any]]:
        search_dir = self.base_dir / prefix
        files = []
        if not search_dir.exists():
            return files
        for path in sorted(search_dir.rglob("*")):
            if path.is_file() and path.suffix != '.meta':
                stat = path.stat()
                object_key = str(path.relative_to(self.base_dir)).replace("\\", "/")
                files.append({
                    "object_key": object_key,
                    "size": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "etag": "",
                    "content_type": "",
                    "url": self.get_presigned_url(object_key),
                })
                if len(files) >= limit:
                    break
        return files

    async def get_file_info(self, object_key: str) -> Optional[Dict[str, Any]]:
        path = self._resolve_path(object_key)
        if not path.exists():
            return None
        stat = path.stat()
        return {
            "object_key": object_key,
            "size": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "etag": "",
            "content_type": "",
            "metadata": {},
            "url": self.get_presigned_url(object_key),
        }

    async def file_exists(self, object_key: str) -> bool:
        return self._resolve_path(object_key).exists()

    def get_file_path(self, object_key: str) -> Optional[str]:
        path = self._resolve_path(object_key)
        return str(path) if path.exists() else None


class MinIOStorage:
    """MinIO对象存储客户端"""

    def __init__(self):
        from minio import Minio
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._bucket_ready = False
        self._available = False
        self._check_available()

    def _check_available(self) -> bool:
        try:
            self.client.bucket_exists(self.bucket_name)
            self._available = True
        except Exception:
            self._available = False
            logger.warning("MinIO 不可用，将使用本地文件存储")
        return self._available

    async def ensure_bucket_exists(self) -> None:
        if self._bucket_ready:
            return
        from minio.error import S3Error
        try:
            if not self._check_available():
                raise StorageError("MinIO 不可用")
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name, location="us-east-1")
                logger.info(f"创建MinIO存储桶: {self.bucket_name}")
            self._bucket_ready = True
        except S3Error as e:
            logger.error(f"创建MinIO存储桶失败: {e}")
            raise StorageError(f"无法创建存储桶: {str(e)}")

    def generate_object_key(self, user_id: str, filename: str, prefix: str = "uploads") -> str:
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{prefix}/{user_id}/{date_str}/{unique_name}"

    async def upload_file(
            self,
            user_id: str,
            file: UploadFile,
            object_key: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            await self.ensure_bucket_exists()

            if not object_key:
                object_key = self.generate_object_key(user_id, file.filename)

            if metadata is None:
                metadata = {}

            import urllib.parse
            encoded_filename = urllib.parse.quote(file.filename or "", safe="") if file.filename else ""

            metadata.update({
                "original_filename": encoded_filename,
                "content_type": file.content_type or "application/octet-stream",
                "upload_time": datetime.now().isoformat(),
                "user_id": user_id,
            })

            file.file.seek(0)

            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)

            import asyncio
            result = await asyncio.to_thread(
                self._upload_file_sync,
                object_key,
                file.file,
                file_size,
                file.content_type,
                metadata,
            )

            logger.info(f"文件上传成功(MinIO): {object_key}, 大小: {file_size} bytes")

            return {
                "bucket": self.bucket_name,
                "object_key": object_key,
                "size": file_size,
                "etag": result.etag,
                "url": self.get_presigned_url(object_key),
            }

        except Exception as e:
            logger.error(f"MinIO上传失败: {e}")
            raise StorageError(f"文件上传失败: {str(e)}")

    def _upload_file_sync(self, object_key, data, length, content_type, metadata):
        return self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_key,
            data=data,
            length=length,
            content_type=content_type,
            metadata=metadata,
        )

    async def upload_file_from_path(
            self,
            user_id: str,
            file_path: str,
            original_filename: str,
            object_key: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            if not object_key:
                object_key = self.generate_object_key(user_id, original_filename)

            if metadata is None:
                metadata = {}

            file_size = Path(file_path).stat().st_size

            import urllib.parse
            encoded_filename = urllib.parse.quote(original_filename or "", safe="")

            metadata.update({
                "original_filename": encoded_filename,
                "content_type": "application/octet-stream",
                "upload_time": datetime.now().isoformat(),
                "user_id": user_id,
                "file_path": file_path,
            })

            import asyncio
            result = await asyncio.to_thread(
                self._upload_file_from_path_sync,
                object_key,
                file_path,
                file_size,
                metadata,
            )

            logger.info(f"文件上传成功(MinIO): {object_key}, 大小: {file_size} bytes")

            return {
                "bucket": self.bucket_name,
                "object_key": object_key,
                "size": file_size,
                "etag": result.etag,
                "url": self.get_presigned_url(object_key),
            }

        except Exception as e:
            logger.error(f"MinIO上传失败: {e}")
            raise StorageError(f"文件上传失败: {str(e)}")

    def _upload_file_from_path_sync(self, object_key, file_path, file_size, metadata):
        with open(file_path, 'rb') as file_data:
            return self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_key,
                data=file_data,
                length=file_size,
                metadata=metadata,
            )

    def get_presigned_url(
            self,
            object_key: str,
            expires: timedelta = timedelta(hours=1)
    ) -> str:
        try:
            from minio.error import S3Error
            signing_client = self.client

            if settings.MINIO_PUBLIC_URL:
                from minio import Minio
                public_url = settings.MINIO_PUBLIC_URL
                clean_endpoint = public_url.replace("http://", "").replace("https://", "").rstrip('/')
                is_secure = public_url.startswith("https://") or settings.MINIO_SECURE

                try:
                    signing_client = Minio(
                        endpoint=clean_endpoint,
                        access_key=settings.MINIO_ACCESS_KEY,
                        secret_key=settings.MINIO_SECRET_KEY,
                        secure=is_secure,
                        region=settings.MINIO_REGION,
                    )

                    return signing_client.presigned_get_object(
                        bucket_name=self.bucket_name,
                        object_name=object_key,
                        expires=expires,
                    )
                except Exception as e:
                    logger.warning(f"使用公开域名签名失败，尝试字符串替换回退: {e}")
                    url = self.client.presigned_get_object(
                        bucket_name=self.bucket_name,
                        object_name=object_key,
                        expires=expires,
                    )
                    return url.replace(settings.MINIO_ENDPOINT, clean_endpoint)

            return self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_key,
                expires=expires,
            )
        except S3Error as e:
            logger.error(f"获取预签名URL失败: {e}")
            raise StorageError(f"获取预签名URL失败: {str(e)}")

    async def download_file(self, object_key: str) -> bytes:
        try:
            def _download():
                response = self.client.get_object(self.bucket_name, object_key)
                data = response.read()
                response.close()
                response.release_conn()
                return data
            return await asyncio.to_thread(_download)
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            raise StorageError(f"下载文件失败: {str(e)}")

    async def download_file_to_path(self, object_key: str, dest_path: str) -> None:
        try:
            def _download_to_path():
                response = self.client.get_object(self.bucket_name, object_key)
                Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, 'wb') as f:
                    for chunk in response.stream(8192):
                        f.write(chunk)
                response.close()
                response.release_conn()
            await asyncio.to_thread(_download_to_path)
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            raise StorageError(f"下载文件失败: {str(e)}")

    async def delete_file(self, object_key: str) -> bool:
        try:
            await asyncio.to_thread(self.client.remove_object, self.bucket_name, object_key)
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False

    async def copy_file(self, source_object_key: str, dest_object_key: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        try:
            self.client.copy_object(
                bucket_name=self.bucket_name,
                object_name=dest_object_key,
                source=f"{self.bucket_name}/{source_object_key}",
                metadata=metadata,
            )
            return True
        except Exception as e:
            logger.error(f"复制文件失败: {e}")
            return False

    async def list_files(self, prefix: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            def _list():
                objects = self.client.list_objects(
                    bucket_name=self.bucket_name,
                    prefix=prefix,
                    recursive=True
                )
                files = []
                for i, obj in enumerate(objects):
                    if i >= limit:
                        break
                    if obj.object_name.endswith('/'):
                        continue
                    files.append({
                        "object_key": obj.object_name,
                        "size": obj.size,
                        "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                        "etag": obj.etag,
                        "content_type": obj.content_type,
                        "url": self.get_presigned_url(obj.object_name),
                    })
                return files
            return await asyncio.to_thread(_list)
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            raise StorageError(f"列出文件失败: {str(e)}")

    async def get_file_info(self, object_key: str) -> Optional[Dict[str, Any]]:
        try:
            def _stat():
                stat = self.client.stat_object(self.bucket_name, object_key)
                return {
                    "object_key": object_key,
                    "size": stat.size,
                    "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                    "etag": stat.etag,
                    "content_type": stat.content_type,
                    "metadata": stat.metadata,
                    "url": self.get_presigned_url(object_key),
                }
            return await asyncio.to_thread(_stat)
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return None

    async def file_exists(self, object_key: str) -> bool:
        try:
            await asyncio.to_thread(self.client.stat_object, self.bucket_name, object_key)
            return True
        except Exception:
            return False


_storage_client = None
_storage_type = None


def _detect_storage():
    global _storage_client, _storage_type
    import socket
    host, _, port = settings.MINIO_ENDPOINT.partition(":")
    try:
        with socket.create_connection((host, int(port or 9000)), timeout=2):
            pass
        from minio import Minio
        client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION,
        )
        client.bucket_exists(settings.MINIO_BUCKET_NAME)
        _storage_client = MinIOStorage()
        _storage_type = "minio"
        logger.info(f"存储后端: MinIO ({settings.MINIO_ENDPOINT})")
    except Exception as e:
        logger.warning(f"MinIO 不可用 ({e})，切换到本地文件存储")
        _storage_client = LocalStorage()
        _storage_type = "local"
    return _storage_client


async def get_storage_client():
    global _storage_client, _storage_type
    if _storage_client is None:
        _detect_storage()
    return _storage_client


def get_storage_type() -> str:
    global _storage_type
    if _storage_type is None:
        _detect_storage()
    return _storage_type


storage_client = None


def _init_storage():
    global storage_client
    if storage_client is None:
        _detect_storage()
        storage_client = _storage_client


_init_storage()

__all__ = [
    "LocalStorage",
    "MinIOStorage",
    "StorageError",
    "storage_client",
    "get_storage_client",
    "get_storage_type",
]
