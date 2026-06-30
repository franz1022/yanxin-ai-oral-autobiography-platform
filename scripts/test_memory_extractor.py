from app.services.memory_extractor import (
    EXTRACTION_METHOD,
    REVIEW_WARNING,
    REVIEW_WARNING_ZH,
    create_life_event_payload,
    detect_language,
    extract_memory,
)


def main() -> None:
    english_memory = (
        "In the summer of 1958, I walked to primary school with my "
        "older brother and often stopped beside an old banyan tree "
        "in a fictional village in Guangdong. I still remember it warmly."
    )

    english_result = extract_memory(english_memory)

    print("English extraction:")
    print(english_result.to_dict())
    print()

    assert detect_language(english_memory) == "en"
    assert english_result.detected_language == "en"
    assert english_result.event_title == "Walking to Primary School"
    assert english_result.start_year == 1958
    assert english_result.date_certainty == "Estimated"
    assert english_result.location is not None
    assert "Guangdong" in english_result.location
    assert english_result.people_involved == "Storyteller and older brother"
    assert english_result.emotional_tone == "Warm and nostalgic"
    assert english_result.extraction_method == EXTRACTION_METHOD
    assert english_result.review_required is True
    assert REVIEW_WARNING in english_result.warnings

    chinese_memory = (
        "大约在1976年，我和母亲从广州搬到深圳。"
        "虽然生活辛苦，但我们对新生活充满希望。"
    )

    chinese_result = extract_memory(chinese_memory)

    print("Chinese extraction:")
    print(chinese_result.to_dict())
    print()

    assert detect_language(chinese_memory) == "zh"
    assert chinese_result.detected_language == "zh"
    assert chinese_result.event_title == "搬到深圳"
    assert chinese_result.start_year == 1976
    assert chinese_result.date_certainty == "Estimated"
    assert chinese_result.location == "广州 → 深圳"
    assert chinese_result.people_involved == "讲述者和母亲"
    assert chinese_result.emotional_tone == "艰难但充满希望"
    assert REVIEW_WARNING_ZH in chinese_result.warnings

    chinese_school_result = extract_memory(
        "1958年，我和哥哥每天走路去小学，那是一段温暖的童年回忆。"
    )
    assert chinese_school_result.event_title == "步行去小学"
    assert chinese_school_result.people_involved == "讲述者和哥哥"
    assert chinese_school_result.emotional_tone == "温暖而怀念"

    unknown_year_result = extract_memory(
        "I remember sitting beside the kitchen window with my mother.",
        location_hint="Family home",
    )

    assert unknown_year_result.start_year is None
    assert unknown_year_result.date_certainty == "Unknown"
    assert "No explicit year was found." in unknown_year_result.warnings

    chinese_unknown_result = extract_memory(
        "我常常和母亲坐在院子里聊天。",
        location_hint="老家的院子",
    )
    assert chinese_unknown_result.detected_language == "zh"
    assert "未识别到明确年份。" in chinese_unknown_result.warnings
    assert chinese_unknown_result.people_involved == "讲述者和母亲"

    payload = create_life_event_payload(
        chinese_result,
        project_id=7,
        source_material_id=3,
        display_order=2,
    )

    assert payload["project_id"] == 7
    assert payload["source_material_id"] == 3
    assert payload["event_title"] == "搬到深圳"
    assert payload["display_order"] == 2

    try:
        extract_memory("   ")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("Empty memory text should raise ValueError.")

    print("Language-aware memory extractor test completed successfully.")
    print("All language consistency assertions passed.")


if __name__ == "__main__":
    main()
