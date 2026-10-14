from __future__ import annotations

from typing import Any

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import (
    _construct_responses_api_payload,
    _get_last_messages,
)
from langchain_openai.chat_models.base import (
    _convert_message_to_dict as _lc_convert_message_to_dict,
)


class ChatDeepSeek(ChatOpenAI):
    """ChatOpenAI wrapper that preserves DeepSeek reasoning_content when present."""

    @property
    def _llm_type(self) -> str:
        return "deepseek-chat"

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        messages = self._convert_input(input_).to_messages()
        if stop is not None:
            kwargs["stop"] = stop

        payload = {**self._default_params, **kwargs}
        if self._use_responses_api(payload):
            if self.use_previous_response_id:
                last_messages, previous_response_id = _get_last_messages(messages)
                payload_to_use = last_messages if previous_response_id else messages
                if previous_response_id:
                    payload["previous_response_id"] = previous_response_id
                payload = _construct_responses_api_payload(payload_to_use, payload)
            else:
                payload = _construct_responses_api_payload(messages, payload)
            return payload

        payload["messages"] = [_lc_convert_message_to_dict(m) for m in messages]
        last_human_index = -1
        for index, message in enumerate(messages):
            if isinstance(message, HumanMessage):
                last_human_index = index

        for index, (message, message_dict) in enumerate(
            zip(messages, payload["messages"])
        ):
            if not isinstance(message, AIMessage):
                continue
            reasoning_content = message.additional_kwargs.get("reasoning_content")
            if reasoning_content is None:
                continue
            if index <= last_human_index:
                continue
            message_dict["reasoning_content"] = reasoning_content
        return payload

    def _create_chat_result(
        self, response: Any, generation_info: dict | None = None
    ) -> ChatResult:
        chat_result = super()._create_chat_result(response, generation_info)
        response_dict = (
            response if isinstance(response, dict) else response.model_dump()
        )
        choices = response_dict.get("choices") or []
        for index, choice in enumerate(choices):
            message_dict = (choice or {}).get("message") or {}
            reasoning_content = None
            if isinstance(message_dict, dict):
                if "reasoning_content" in message_dict:
                    reasoning_content = message_dict["reasoning_content"]
                elif "model_extra" in message_dict and isinstance(
                    message_dict["model_extra"], dict
                ):
                    reasoning_content = message_dict["model_extra"].get(
                        "reasoning_content"
                    )
            if reasoning_content is None:
                continue
            if index >= len(chat_result.generations):
                continue
            message = chat_result.generations[index].message
            if isinstance(message, AIMessage):
                message.additional_kwargs["reasoning_content"] = reasoning_content
        return chat_result

    def _convert_chunk_to_generation_chunk(
        self, chunk: dict, default_chunk_class: type, base_generation_info: dict | None
    ) -> ChatGenerationChunk | None:
        generation_chunk = super()._convert_chunk_to_generation_chunk(
            chunk, default_chunk_class, base_generation_info
        )
        if generation_chunk is None:
            return None
        choices = chunk.get("choices", []) or chunk.get("chunk", {}).get("choices", [])
        if not choices:
            return generation_chunk
        delta = choices[0].get("delta") or {}
        reasoning_content = delta.get("reasoning_content")
        if reasoning_content is None:
            reasoning_content = delta.get("reasoning")
        if reasoning_content is not None and isinstance(
            generation_chunk.message, AIMessageChunk
        ):
            generation_chunk.message.additional_kwargs["reasoning_content"] = (
                reasoning_content
            )
        return generation_chunk
