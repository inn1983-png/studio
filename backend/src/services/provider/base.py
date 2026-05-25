from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from functools import wraps
import json
import time
from src.core.logging import get_logger

logger = get_logger(__name__)


def log_provider_call(method_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()
            base_url = getattr(self, 'base_url', 'unknown')
            provider_name = self.__class__.__name__

            request_info = {
                "provider": provider_name,
                "method": method_name,
                "args": _sanitize_for_log(args),
                "kwargs": _sanitize_for_log(kwargs),
                "base_url": base_url
            }

            logger.info(f"[{provider_name}] {method_name} 请求开始")
            logger.info(f"[{provider_name}] {method_name} 请求参数: {json.dumps(request_info, ensure_ascii=False, indent=2)}")

            try:
                result = await func(self, *args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"[{provider_name}] {method_name} 请求成功 (耗时: {elapsed:.2f}s)")
                logger.info(f"[{provider_name}] {method_name} 响应摘要: {_get_response_summary(result)}")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"[{provider_name}] {method_name} 请求失败 (耗时: {elapsed:.2f}s): {e}")
                raise

        return wrapper
    return decorator


def _sanitize_for_log(data: Any, max_length: int = 200) -> Any:
    if isinstance(data, dict):
        return {k: _sanitize_for_log(v, max_length) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [_sanitize_for_log(item, max_length) for item in data]
    elif isinstance(data, str):
        if len(data) > max_length:
            return data[:max_length] + f"... (truncated, total {len(data)} chars)"
        return data
    else:
        return data


def _get_response_summary(response: Any) -> str:
    try:
        if hasattr(response, '__dict__'):
            attrs = {k: v for k, v in response.__dict__.items() if not k.startswith('_')}
            return f"Object({type(response).__name__}) with {len(attrs)} attributes"
        elif isinstance(response, dict):
            return f"Dict with {len(response)} keys: {list(response.keys())[:5]}"
        elif isinstance(response, (list, tuple)):
            return f"{type(response).__name__} with {len(response)} items"
        else:
            return f"{type(response).__name__}"
    except:
        return "Unknown response type"


class BaseLLMProvider(ABC):
    provider_type: str = "llm"

    @abstractmethod
    async def completions(
            self,
            model: str,
            messages: List[Dict[str, Any]],
            **kwargs: Any
    ) -> Any:
        pass

    async def generate_image(
            self,
            prompt: str,
            model: str = None,
            **kwargs: Any
    ) -> Any:
        raise NotImplementedError(f"{self.__class__.__name__} 不支持图像生成")

    async def generate_audio(
            self,
            input_text: str,
            voice: str = "alloy",
            model: str = "tts-1",
            **kwargs: Any
    ) -> Any:
        raise NotImplementedError(f"{self.__class__.__name__} 不支持音频生成")


class BaseVideoProvider(ABC):
    provider_type: str = "video"

    @abstractmethod
    async def create_video(
            self,
            prompt: str,
            images: Optional[List[str]] = None,
            model: str = None,
            **kwargs: Any
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_video_content(self, task_id: str) -> Dict[str, Any]:
        pass


class BaseTTSProvider(ABC):
    provider_type: str = "tts"

    @abstractmethod
    async def generate_audio(
            self,
            input_text: str,
            voice: str = "alloy",
            model: str = "tts-1",
            **kwargs: Any
    ) -> Any:
        pass


class BaseImageProvider(ABC):
    provider_type: str = "image"

    @abstractmethod
    async def generate_image(
            self,
            prompt: str,
            model: str = None,
            **kwargs: Any
    ) -> Any:
        pass


_PROVIDER_REGISTRY: Dict[str, type] = {}


def register_provider(name: str):
    def decorator(cls):
        _PROVIDER_REGISTRY[name.lower()] = cls
        return cls
    return decorator


def get_registered_providers() -> Dict[str, type]:
    return dict(_PROVIDER_REGISTRY)
