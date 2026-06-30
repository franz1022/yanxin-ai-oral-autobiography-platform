from __future__ import annotations

from app.services.memory_extraction_providers import (
    LLM_PROVIDER_ID,
    RULE_BASED_PROVIDER_ID,
    ProviderUnavailableError,
    extract_memory_with_provider,
    get_memory_extraction_provider,
    list_memory_extraction_providers,
)


def main() -> None:
    provider_infos = list_memory_extraction_providers()
    provider_ids = [provider.provider_id for provider in provider_infos]

    assert provider_ids == [RULE_BASED_PROVIDER_ID, LLM_PROVIDER_ID]

    rule_info = get_memory_extraction_provider(
        RULE_BASED_PROVIDER_ID
    ).info
    assert rule_info.available is True
    assert rule_info.sends_data_external is False

    llm_info = get_memory_extraction_provider(LLM_PROVIDER_ID).info
    assert llm_info.available is False
    assert llm_info.sends_data_external is True

    chinese_result = extract_memory_with_provider(
        "大约在1976年，我和母亲从广州搬到深圳。"
        "虽然生活辛苦，但我们对新生活充满希望。",
        provider_id=RULE_BASED_PROVIDER_ID,
    )

    assert chinese_result.detected_language == "zh"
    assert chinese_result.event_title == "搬到深圳"
    assert chinese_result.location == "广州 → 深圳"
    assert chinese_result.people_involved == "讲述者和母亲"
    assert chinese_result.review_required is True

    english_result = extract_memory_with_provider(
        "In the summer of 1958, I walked to primary school with my "
        "older brother in a fictional village in Guangdong.",
        provider_id=RULE_BASED_PROVIDER_ID,
    )

    assert english_result.detected_language == "en"
    assert english_result.event_title == "Walking to Primary School"
    assert english_result.review_required is True

    try:
        extract_memory_with_provider(
            "A fictional memory.",
            provider_id=LLM_PROVIDER_ID,
        )
    except ProviderUnavailableError as exc:
        assert "unavailable" in str(exc).lower()
    else:
        raise AssertionError("Disabled LLM provider should not run.")

    try:
        get_memory_extraction_provider("unknown-provider")
    except ValueError as exc:
        assert "Unknown memory extraction provider" in str(exc)
    else:
        raise AssertionError("Unknown provider should raise ValueError.")

    print("Memory extraction provider test completed successfully.")
    print("Rule-based provider: available and local-only.")
    print("LLM provider: registered but safely disabled.")
    print("All provider architecture assertions passed.")


if __name__ == "__main__":
    main()
