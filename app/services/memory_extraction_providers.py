from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from app.services.memory_extractor import (
    MemoryExtractionResult,
    extract_memory,
)


RULE_BASED_PROVIDER_ID = "rule_based"
LLM_PROVIDER_ID = "llm"


class ProviderUnavailableError(RuntimeError):
    """Raised when a selected extraction provider cannot currently run."""


@dataclass(frozen=True)
class MemoryExtractionProviderInfo:
    """User-facing metadata for one extraction provider."""

    provider_id: str
    display_name_en: str
    display_name_zh: str
    description_en: str
    description_zh: str
    available: bool
    sends_data_external: bool

    def display_name(self, language: str = "en") -> str:
        if language == "zh":
            return self.display_name_zh
        return self.display_name_en

    def description(self, language: str = "en") -> str:
        if language == "zh":
            return self.description_zh
        return self.description_en


class MemoryExtractionProvider(Protocol):
    """Common interface implemented by every memory extraction provider."""

    info: MemoryExtractionProviderInfo

    def extract(
        self,
        text: str,
        *,
        year_hint: Optional[int] = None,
        location_hint: Optional[str] = None,
        people_hint: Optional[str] = None,
        emotional_tone_hint: Optional[str] = None,
    ) -> MemoryExtractionResult:
        """Return a reviewable structured memory extraction result."""


class RuleBasedMemoryExtractionProvider:
    """Deterministic local provider used by the public portfolio demo."""

    info = MemoryExtractionProviderInfo(
        provider_id=RULE_BASED_PROVIDER_ID,
        display_name_en="Rule-based demo mode",
        display_name_zh="规则演示模式",
        description_en=(
            "Runs locally with deterministic rules. No memory text is sent "
            "to an external service."
        ),
        description_zh=(
            "使用本地确定性规则运行，不会把回忆文字发送到外部服务。"
        ),
        available=True,
        sends_data_external=False,
    )

    def extract(
        self,
        text: str,
        *,
        year_hint: Optional[int] = None,
        location_hint: Optional[str] = None,
        people_hint: Optional[str] = None,
        emotional_tone_hint: Optional[str] = None,
    ) -> MemoryExtractionResult:
        return extract_memory(
            text,
            year_hint=year_hint,
            location_hint=location_hint,
            people_hint=people_hint,
            emotional_tone_hint=emotional_tone_hint,
        )


class LLMMemoryExtractionProvider:
    """
    Reserved provider boundary for a future optional LLM integration.

    The public portfolio version intentionally does not call an external API.
    This keeps the demo runnable without credentials and prevents accidental
    disclosure of sensitive memory text.
    """

    info = MemoryExtractionProviderInfo(
        provider_id=LLM_PROVIDER_ID,
        display_name_en="LLM enhanced mode (not configured)",
        display_name_zh="LLM增强模式（尚未配置）",
        description_en=(
            "Provider interface reserved for a future opt-in LLM integration. "
            "It is disabled in the public demo."
        ),
        description_zh=(
            "已预留未来可选LLM接口；公开演示版本中默认禁用。"
        ),
        available=False,
        sends_data_external=True,
    )

    def extract(
        self,
        text: str,
        *,
        year_hint: Optional[int] = None,
        location_hint: Optional[str] = None,
        people_hint: Optional[str] = None,
        emotional_tone_hint: Optional[str] = None,
    ) -> MemoryExtractionResult:
        del text
        del year_hint
        del location_hint
        del people_hint
        del emotional_tone_hint

        raise ProviderUnavailableError(
            "LLM enhanced mode is not configured in the public demo. "
            "Select rule-based demo mode instead."
        )


_PROVIDER_REGISTRY: dict[str, MemoryExtractionProvider] = {
    RULE_BASED_PROVIDER_ID: RuleBasedMemoryExtractionProvider(),
    LLM_PROVIDER_ID: LLMMemoryExtractionProvider(),
}


def list_memory_extraction_providers() -> tuple[MemoryExtractionProviderInfo, ...]:
    """Return provider metadata in a stable UI order."""
    return tuple(provider.info for provider in _PROVIDER_REGISTRY.values())


def get_memory_extraction_provider(
    provider_id: str,
) -> MemoryExtractionProvider:
    """Resolve one provider by ID and fail clearly for unknown values."""
    try:
        return _PROVIDER_REGISTRY[provider_id]
    except KeyError as exc:
        available_ids = ", ".join(_PROVIDER_REGISTRY)
        raise ValueError(
            f"Unknown memory extraction provider: {provider_id!r}. "
            f"Available providers: {available_ids}."
        ) from exc


def extract_memory_with_provider(
    text: str,
    *,
    provider_id: str = RULE_BASED_PROVIDER_ID,
    year_hint: Optional[int] = None,
    location_hint: Optional[str] = None,
    people_hint: Optional[str] = None,
    emotional_tone_hint: Optional[str] = None,
) -> MemoryExtractionResult:
    """Extract a reviewable memory draft through the selected provider."""
    provider = get_memory_extraction_provider(provider_id)

    if not provider.info.available:
        raise ProviderUnavailableError(
            f"{provider.info.display_name_en} is currently unavailable."
        )

    return provider.extract(
        text,
        year_hint=year_hint,
        location_hint=location_hint,
        people_hint=people_hint,
        emotional_tone_hint=emotional_tone_hint,
    )
