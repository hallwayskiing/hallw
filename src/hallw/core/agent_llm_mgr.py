import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_litellm import ChatLiteLLM, ChatLiteLLMRouter
from litellm import Router


class AgentLLMManager:
    """Factory for LLM"""

    _router_cache: dict[str, Router] = {}

    @classmethod
    def get_gemini_router(cls, model_name: str) -> Router:
        if model_name not in cls._router_cache:
            keys = [os.getenv(k) for k in os.environ if k.startswith("GOOGLE_API_KEY_") and os.getenv(k)]

            model_list = [
                {
                    "model_name": "gemini-pool",
                    "litellm_params": {
                        "model": model_name,
                        "api_key": k,
                    },
                }
                for k in keys
            ]

            cls._router_cache[model_name] = Router(
                model_list=model_list,
                routing_strategy="simple-shuffle",
                num_retries=len(model_list),
                allowed_fails=1,
                cooldown_time=60,
            )

        return cls._router_cache[model_name]

    @classmethod
    def get_llm(cls, model_name: str, **kwargs) -> BaseChatModel:
        if "gemini" in model_name.lower():
            router = cls.get_gemini_router(model_name)
            return ChatLiteLLMRouter(router=router, model_name="gemini-pool", **kwargs)

        return ChatLiteLLM(model=model_name, **kwargs)
