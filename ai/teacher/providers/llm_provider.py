"""Provider-neutral LLM contract shared by Teacher Brain modules."""
from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMProviderError(RuntimeError):
    """A provider could not produce the requested response."""

class LLMProvider(ABC):
    @abstractmethod
    def generate_structured(self, prompt: str, response_model: Type[T]) -> T:
        raise NotImplementedError

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError
