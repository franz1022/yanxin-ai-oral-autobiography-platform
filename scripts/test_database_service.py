from pathlib import Path

from app.services.database import (
    add_text_material,
    create_life_event,
    create_project,
    create_storyteller,
    get_project_summary,
    initialize_database,
    list_generated_contents,
    list_life_events,
    list_materials,
    list_projects,
    list_storytellers,
    save_generated_content,
    update_content_review_status,
)


BASE_DIR = Path(__file__).resolve().parents[1]
TEST_DB_PATH = BASE_DIR / "data" / "yanxin_autobiography_test.db"


def main() -> None:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    initialize_database(TEST_DB_PATH)

    storyteller_id = create_storyteller(
        full_name="Chen Ming",
        preferred_name="Grandpa Chen",
        birth_year=1948,
        hometown="Guangdong",
        biography_language="Chinese",
        profile_notes="Fictional demonstration profile.",
        db_path=TEST_DB_PATH,
    )

    project_id = create_project(
        storyteller_id=storyteller_id,
        project_title="Childhood and Family Memories",
        project_description=(
            "A privacy-safe fictional project used to test the prototype."
        ),
        project_status="In Progress",
        created_by_relationship="Grandchild",
        db_path=TEST_DB_PATH,
    )

    material_id = add_text_material(
        project_id=project_id,
        text_content=(
            "In the summer of 1958, I walked to school with my older "
            "brother and often stopped beside the old banyan tree."
        ),
        material_description="Fictional childhood memory.",
        estimated_year=1958,
        location="A fictional village in Guangdong",
        people_description="Storyteller and older brother",
        db_path=TEST_DB_PATH,
    )

    event_id = create_life_event(
        project_id=project_id,
        source_material_id=material_id,
        event_title="Walking to Primary School",
        event_description=(
            "A childhood memory about walking to school with an older "
            "brother and resting near an old banyan tree."
        ),
        start_year=1958,
        date_certainty="Estimated",
        location="A fictional village in Guangdong",
        people_involved="Storyteller and older brother",
        emotional_tone="Warm and nostalgic",
        display_order=1,
        db_path=TEST_DB_PATH,
    )

    content_id = save_generated_content(
        project_id=project_id,
        life_event_id=event_id,
        content_type="Chapter",
        content_title="The Road to School",
        content_text=(
            "Every morning, the two brothers followed the narrow road "
            "toward the village school. The banyan tree became a quiet "
            "landmark in their shared childhood memories."
        ),
        generation_method="Template Prototype",
        review_status="Draft",
        db_path=TEST_DB_PATH,
    )

    update_content_review_status(
        content_id=content_id,
        new_status="Reviewed",
        review_comment=(
            "The fictional story is coherent and ready for revision."
        ),
        reviewed_by="Demo Reviewer",
        db_path=TEST_DB_PATH,
    )

    print("Database service test completed successfully.")
    print(f"Test database: {TEST_DB_PATH}")
    print()
    print("Storytellers:")
    print(list_storytellers(TEST_DB_PATH))
    print()
    print("Projects:")
    print(list_projects(db_path=TEST_DB_PATH))
    print()
    print("Materials:")
    print(list_materials(project_id, TEST_DB_PATH))
    print()
    print("Life events:")
    print(list_life_events(project_id, TEST_DB_PATH))
    print()
    print("Generated contents:")
    print(list_generated_contents(project_id, db_path=TEST_DB_PATH))
    print()
    print("Project summary:")
    print(get_project_summary(project_id, TEST_DB_PATH))


if __name__ == "__main__":
    main()
