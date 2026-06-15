from app.services.database import initialize_database
from app.services.media_manager import validate_upload
from app.services.story_generator import generate_scene_description


def main() -> None:
    initialize_database()

    assert validate_upload(
        filename="example.png",
        file_size_bytes=100,
        mime_type="image/png",
    ) == "Photo"

    result = generate_scene_description(
        {
            "event_title": "Demo Event",
            "event_description": "A fictional event.",
            "start_year": 1960,
            "date_certainty": "Estimated",
            "location": "A fictional location",
            "people_involved": "A fictional family",
            "emotional_tone": "Reflective",
        }
    )

    assert result["content_type"] == "Scene Description"

    print("Dashboard dependency test completed successfully.")


if __name__ == "__main__":
    main()
