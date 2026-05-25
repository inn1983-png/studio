from .base import BaseLLMProvider, BaseVideoProvider, get_registered_providers
from .openai_provider import OpenAIProvider
from .deepseek_provider import DeepSeekProvider
from .volcengine_provider import VolcengineProvider
from .siliconflow_provider import SiliconFlowProvider
from .custom_provider import CustomProvider
from .vector_engine_provider import VectorEngineProvider


class ProviderFactory:

    @staticmethod
    def create(provider: str, api_key: str, **kwargs) -> BaseLLMProvider | BaseVideoProvider:
        provider = provider.lower()

        match provider:
            case "openai":
                return OpenAIProvider(api_key, kwargs.get("max_concurrency", 5))
            case "deepseek":
                return DeepSeekProvider(api_key, kwargs.get("max_concurrency", 5))
            case "volcengine":
                return VolcengineProvider(api_key, kwargs.get("max_concurrency", 5))
            case "siliconflow":
                return SiliconFlowProvider(api_key, kwargs.get("max_concurrency", 5))
            case "custom":
                return CustomProvider(api_key, kwargs.get("max_concurrency", 5),
                                      kwargs.get("base_url", "https://api.aiconapi.me/v1"))
            case "local":
                return CustomProvider(api_key, kwargs.get("max_concurrency", 5),
                                      kwargs.get("base_url", "http://localhost:8081/v1"))
            case "vectorengine":
                return VectorEngineProvider(api_key, kwargs.get("base_url", "https://api.vectorengine.ai/v1"))
            case _:
                registry = get_registered_providers()
                if provider in registry:
                    cls = registry[provider]
                    return cls(api_key, **kwargs)
                raise ValueError(f"未知 provider: {provider}")

    @staticmethod
    def get_supported_providers() -> list:
        return [
            {"id": "openai", "name": "OpenAI", "type": "llm", "capabilities": ["llm", "image", "tts"]},
            {"id": "deepseek", "name": "DeepSeek", "type": "llm", "capabilities": ["llm", "image"]},
            {"id": "volcengine", "name": "火山引擎", "type": "llm", "capabilities": ["llm", "image", "tts"]},
            {"id": "siliconflow", "name": "SiliconFlow", "type": "llm", "capabilities": ["llm", "image", "tts"]},
            {"id": "custom", "name": "自定义 (OpenAI兼容)", "type": "llm", "capabilities": ["llm", "image", "tts"]},
            {"id": "local", "name": "本地模型", "type": "llm", "capabilities": ["llm"]},
            {"id": "vectorengine", "name": "Vector Engine", "type": "video", "capabilities": ["video"]},
        ]
