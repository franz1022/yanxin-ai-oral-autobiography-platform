from app.services.story_generator import (
    generate_biography,
    generate_event_content_bundle,
)


def main() -> None:
    storyteller = {
        "storyteller_id": 1,
        "full_name": "Chen Ming",
        "preferred_name": "Grandpa Chen",
        "birth_year": 1948,
        "hometown": "Guangdong",
    }

    project = {
        "project_id": 1,
        "project_title": "Childhood and Family Memories",
    }

    event = {
        "event_id": 1,
        "event_title": "Walking to Primary School",
        "start_year": 1958,
        "end_year": None,
        "date_certainty": "Estimated",
        "location": "A fictional village in Guangdong",
        "people_involved": "Grandpa Chen and his older brother",
        "event_description": (
            "They walked along a narrow village road and often stopped "
            "beside an old banyan tree before reaching school."
        ),
        "emotional_tone": "Warm and nostalgic",
        "display_order": 1,
    }

    biography = generate_biography(
        storyteller=storyteller,
        project=project,
        life_events=[event],
    )

    bundle = generate_event_content_bundle(
        storyteller_name="Grandpa Chen",
        event=event,
    )

    print("Story generator test completed successfully.")
    print()
    print("Biography:")
    print(biography["content_text"])
    print()
    print("=" * 70)
    print()

    for item in bundle:
        print(item["content_type"])
        print(item["content_title"])
        print(item["content_text"])
        print()
        print("-" * 70)
        print()

    expected_types = {
        "Chapter",
        "Scene Description",
        "Storyboard",
        "Video Prompt",
    }

    actual_types = {item["content_type"] for item in bundle}

    assert actual_types == expected_types
    assert biography["content_type"] == "Biography"
    assert "AI-assisted" in biography["content_text"]

    print("All story generator assertions passed.")


if __name__ == "__main__":
    main()
