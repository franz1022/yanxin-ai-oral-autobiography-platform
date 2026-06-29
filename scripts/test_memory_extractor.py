from app.services.memory_extractor import (
    EXTRACTION_METHOD,
    create_life_event_payload,
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

    assert english_result.event_title == "Walking to Primary School"
    assert english_result.start_year == 1958
    assert english_result.date_certainty == "Estimated"
    assert english_result.location is not None
    assert "Guangdong" in english_result.location
    assert english_result.people_involved == "Storyteller and older brother"
    assert english_result.emotional_tone == "Warm and nostalgic"
    assert english_result.extraction_method == EXTRACTION_METHOD
    assert english_result.review_required is True

    chinese_memory = (
        "大约在1976年，我和母亲从广州搬到深圳。"
        "虽然生活辛苦，但我们对新生活充满希望。"
    )

    chinese_result = extract_memory(chinese_memory)

    print("Chinese extraction:")
    print(chinese_result.to_dict())
    print()

    assert chinese_result.event_title == "Moving to 深圳"
    assert chinese_result.start_year == 1976
    assert chinese_result.date_certainty == "Estimated"
    assert chinese_result.location == "广州 → 深圳"
    assert chinese_result.people_involved == "Storyteller and mother"
    assert chinese_result.emotional_tone == "Difficult but hopeful"

    unknown_year_result = extract_memory(
        "I remember sitting beside the kitchen window with my mother.",
        location_hint="Family home",
    )

    assert unknown_year_result.start_year is None
    assert unknown_year_result.date_certainty == "Unknown"
    assert "No explicit year was found." in unknown_year_result.warnings

    payload = create_life_event_payload(
        english_result,
        project_id=7,
        source_material_id=3,
        display_order=2,
    )

    assert payload["project_id"] == 7
    assert payload["source_material_id"] == 3
    assert payload["event_title"] == "Walking to Primary School"
    assert payload["display_order"] == 2

    try:
        extract_memory("   ")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("Empty memory text should raise ValueError.")

    print("Memory extractor test completed successfully.")
    print("All memory extractor assertions passed.")


if __name__ == "__main__":
    main()
