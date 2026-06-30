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


    # Regression checks added after benchmark error analysis.
    chinese_wedding = extract_memory(
        "1990年，我和妻子在深圳举行婚礼。家人和朋友都很开心。"
    )
    assert chinese_wedding.location == "深圳"
    assert chinese_wedding.event_title == "结婚与家庭"

    chinese_birth = extract_memory(
        "1948年，我出生在广东，和父母住在一起。那段早年生活很平静。"
    )
    assert chinese_birth.location == "广东"

    chinese_courtyard = extract_memory(
        "我常常和母亲坐在老家的院子里聊天，那是一段温暖的回忆。"
    )
    assert chinese_courtyard.location == "老家的院子"
    assert chinese_courtyard.event_title == "在院子里与母亲聊天"

    chinese_graduation = extract_memory(
        "2001年，我在北京生活，和朋友一起庆祝毕业，我们非常开心。"
    )
    assert chinese_graduation.event_title == "庆祝毕业"

    chinese_loss = extract_memory(
        "1998年，我在上海工作，父亲离开了我们，我感到非常悲伤。"
    )
    assert chinese_loss.event_title == "父亲离世"

    chinese_study = extract_memory(
        "从1966年到1968年，我在广州学习，和同学一起度过了艰难的日子。"
    )
    assert chinese_study.location == "广州"
    assert chinese_study.event_title == "在广州求学"

    chinese_window = extract_memory(
        "1995年，我和母亲坐在厨房窗边，安静地回忆童年。"
    )
    assert chinese_window.location == "厨房窗边"
    assert chinese_window.event_title == "窗边回忆"

    english_migration = extract_memory(
        "Around 1976, I moved from Guangzhou to Shenzhen with my mother. "
        "Life was difficult, but we were hopeful about the new beginning."
    )
    assert english_migration.location == "Guangzhou → Shenzhen"
    assert english_migration.event_title == "Moving to Shenzhen"

    english_nested_location = extract_memory(
        "In 1990, I married my wife at a fictional community hall in "
        "Shenzhen. Our friends celebrated happily."
    )
    assert english_nested_location.location == "Shenzhen"

    english_courtyard = extract_memory(
        "I often sat with my mother in the family courtyard and remembered "
        "our childhood warmly."
    )
    assert english_courtyard.location == "the family courtyard"
    assert (
        english_courtyard.event_title
        == "Conversations in the Family Courtyard"
    )

    english_graduation = extract_memory(
        "In 2001, I lived in Beijing with my friends and celebrated "
        "graduation happily."
    )
    assert english_graduation.event_title == "Celebrating Graduation"

    english_study = extract_memory(
        "Between 1966 and 1968, I studied at a school in Guangzhou with "
        "my classmates during a difficult period."
    )
    assert english_study.location == "Guangzhou"
    assert english_study.event_title == "Studying in Guangzhou"

    english_window = extract_memory(
        "In 1995, I sat near the kitchen window with my mother and "
        "remembered childhood."
    )
    assert english_window.location == "the kitchen window"
    assert english_window.event_title == "Memories by the Kitchen Window"

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
