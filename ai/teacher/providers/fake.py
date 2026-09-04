"""Deterministic test double for LLMProvider."""
from typing import Callable, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from ai.teacher.providers.llm_provider import LLMProvider, LLMProviderError

T = TypeVar("T", bound=BaseModel)

class FakeLLMProvider(LLMProvider):
    def __init__(self, structured_response: Optional[Union[BaseModel, Callable[[str, type], BaseModel]]] = None,
                 text_response: Union[str, Callable[[str], str]] = "", raise_error: bool = False):
        self._structured_response = structured_response
        self._text_response = text_response
        self._raise_error = raise_error
        self.calls = []

    def generate_structured(self, prompt: str, response_model: Type[T]) -> T:
        self.calls.append(("structured", prompt, response_model))
        if self._raise_error:
            raise LLMProviderError("simulated provider failure")
        if self._structured_response is None:
            raise LLMProviderError("FakeLLMProvider has no structured_response configured")
        response = self._structured_response(prompt, response_model) if callable(self._structured_response) else self._structured_response
        return response if isinstance(response, response_model) else response_model.model_validate(response)

    def generate_text(self, prompt: str) -> str:
        self.calls.append(("text", prompt, None))
        if self._raise_error:
            raise LLMProviderError("simulated provider failure")
        return self._text_response(prompt) if callable(self._text_response) else self._text_response
