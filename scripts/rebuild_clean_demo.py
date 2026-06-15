from __future__ import annotations

import io
import shutil
import wave
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from app.services.database import (
    DEFAULT_DB_PATH,
    add_file_material,
    add_text_material,
    create_life_event,
    create_project,
    create_storyteller,
    get_project_summary,
    initialize_database,
    save_generated_content,
    update_content_review_status,
)
from app.services.media_manager import DEFAULT_UPLOAD_DIR, save_uploaded_file
from app.services.story_generator import (
    generate_biography,
    generate_event_content_bundle,
)


BASE_DIR = Path(__file__).resolve().parents[1]
BACKUP_ROOT = BASE_DIR / "outputs" / "backups"


def create_demo_photo_bytes() -> bytes:
    image = Image.new("RGB", (1000, 650), (220, 205, 170))
    draw = ImageDraw.Draw(image)

    draw.rectangle([0, 420, 1000, 650], fill=(170, 145, 105))
    draw.rectangle([610, 240, 900, 470], fill=(155, 132, 98))
    draw.polygon(
        [(580, 250), (755, 120), (930, 250)],
        fill=(120, 100, 75),
    )
    draw.rectangle([720, 350, 790, 470], fill=(90, 70, 50))

    draw.rectangle([220, 210, 275, 500], fill=(95, 75, 50))
    for box in [
        (110, 95, 310, 280),
        (210, 60, 430, 260),
        (320, 110, 520, 300),
    ]:
        draw.ellipse(box, fill=(100, 110, 70))

    for x, height in [(430, 155), (500, 135), (565, 125)]:
        top = 455 - height
        draw.ellipse([x - 18, top, x + 18, top + 36], fill=(70, 60, 50))
        draw.rectangle([x - 14, top + 32, x + 14, 455], fill=(80, 68, 55))

    draw.rectangle([0, 575, 1000, 650], fill=(85, 70, 50))
    draw.text((28, 595), "FICTIONAL DEMO PHOTO - 1965", fill=(245, 230, 195))

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def create_demo_audio_bytes() -> bytes:
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        wav_file.writeframes(b"\x00\x00" * 16000)

    return buffer.getvalue()


def backup_existing_data() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_ROOT / f"before_clean_demo_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    if DEFAULT_DB_PATH.exists():
        shutil.copy2(
            DEFAULT_DB_PATH,
            backup_dir / DEFAULT_DB_PATH.name,
        )

    if DEFAULT_UPLOAD_DIR.exists():
        shutil.copytree(
            DEFAULT_UPLOAD_DIR,
            backup_dir / "uploads",
            dirs_exist_ok=True,
        )

    return backup_dir


def reset_main_data() -> None:
    if DEFAULT_DB_PATH.exists():
        DEFAULT_DB_PATH.unlink()

    if DEFAULT_UPLOAD_DIR.exists():
        shutil.rmtree(DEFAULT_UPLOAD_DIR)

    DEFAULT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("Backing up the current local demo data...")
    backup_dir = backup_existing_data()
    print(f"Backup created: {backup_dir}")

    print("Resetting the main database and uploads...")
    reset_main_data()
    initialize_database()

    storyteller_id = create_storyteller(
        full_name="Chen Ming",
        preferred_name="Grandpa Chen",
        birth_year=1948,
        hometown="Guangdong",
        biography_language="English",
        profile_notes=(
            "Fictional demonstration profile created for the public portfolio."
        ),
    )

    project_id = create_project(
        storyteller_id=storyteller_id,
        project_title="Childhood and Family Memories",
        project_description=(
            "A privacy-safe demonstration of an AI-assisted oral "
            "autobiography workflow."
        ),
        project_status="In Progress",
        created_by_relationship="Grandchild",
    )

    text_material_1 = add_text_material(
        project_id=project_id,
        text_content=(
            "In the summer of 1958, I walked to school with my older "
            "brother and often stopped beside the old banyan tree."
        ),
        material_description="Fictional childhood school memory",
        estimated_year=1958,
        location="A fictional village in Guangdong",
        people_description="Grandpa Chen and his older brother",
    )

    text_material_2 = add_text_material(
        project_id=project_id,
        text_content=(
            "In 1965, the family gathered near the old house during the "
            "Spring Festival and shared stories about earlier village life."
        ),
        material_description="Fictional family gathering memory",
        estimated_year=1965,
        location="A fictional village in Guangdong",
        people_description="Grandpa Chen and fictional family members",
    )

    photo_metadata = save_uploaded_file(
        file_source=create_demo_photo_bytes(),
        original_filename="fictional_old_photo_1965.png",
        project_id=project_id,
        mime_type="image/png",
    )

    add_file_material(
        project_id=project_id,
        material_type=photo_metadata["material_type"],
        original_filename=photo_metadata["original_filename"],
        stored_filename=photo_metadata["stored_filename"],
        stored_path=photo_metadata["stored_path"],
        material_description="Fictional historical family photograph",
        estimated_year=1965,
        location="A fictional village in Guangdong",
        people_description="Grandpa Chen and fictional family members",
        mime_type=photo_metadata["mime_type"],
        file_size_bytes=photo_metadata["file_size_bytes"],
    )

    audio_metadata = save_uploaded_file(
        file_source=create_demo_audio_bytes(),
        original_filename="fictional_voice_recording.wav",
        project_id=project_id,
        mime_type="audio/wav",
    )

    add_file_material(
        project_id=project_id,
        material_type=audio_metadata["material_type"],
        original_filename=audio_metadata["original_filename"],
        stored_filename=audio_metadata["stored_filename"],
        stored_path=audio_metadata["stored_path"],
        material_description=(
            "Fictional silent oral-history recording for prototype testing"
        ),
        estimated_year=None,
        location="Prototype testing environment",
        people_description="Fictional storyteller",
        mime_type=audio_metadata["mime_type"],
        file_size_bytes=audio_metadata["file_size_bytes"],
    )

    event_1 = create_life_event(
        project_id=project_id,
        source_material_id=text_material_1,
        event_title="Walking to Primary School",
        event_description=(
            "The brothers followed a narrow village road to school and "
            "often rested beside an old banyan tree."
        ),
        start_year=1958,
        date_certainty="Estimated",
        location="A fictional village in Guangdong",
        people_involved="Grandpa Chen and his older brother",
        emotional_tone="Warm and nostalgic",
        display_order=1,
    )

    event_2 = create_life_event(
        project_id=project_id,
        source_material_id=text_material_2,
        event_title="Spring Festival Family Gathering",
        event_description=(
            "The family gathered near the old house during the Spring "
            "Festival and shared stories about earlier village life."
        ),
        start_year=1965,
        date_certainty="Estimated",
        location="A fictional village in Guangdong",
        people_involved="Grandpa Chen and fictional family members",
        emotional_tone="Warm and reflective",
        display_order=2,
    )

    storyteller = {
        "storyteller_id": storyteller_id,
        "full_name": "Chen Ming",
        "preferred_name": "Grandpa Chen",
        "birth_year": 1948,
        "hometown": "Guangdong",
    }

    project = {
        "project_id": project_id,
        "storyteller_id": storyteller_id,
        "project_title": "Childhood and Family Memories",
        "project_status": "In Progress",
    }

    life_events = [
        {
            "event_id": event_1,
            "event_title": "Walking to Primary School",
            "start_year": 1958,
            "end_year": None,
            "date_certainty": "Estimated",
            "location": "A fictional village in Guangdong",
            "people_involved": "Grandpa Chen and his older brother",
            "event_description": (
                "The brothers followed a narrow village road to school and "
                "often rested beside an old banyan tree."
            ),
            "emotional_tone": "Warm and nostalgic",
            "display_order": 1,
        },
        {
            "event_id": event_2,
            "event_title": "Spring Festival Family Gathering",
            "start_year": 1965,
            "end_year": None,
            "date_certainty": "Estimated",
            "location": "A fictional village in Guangdong",
            "people_involved": "Grandpa Chen and fictional family members",
            "event_description": (
                "The family gathered near the old house during the Spring "
                "Festival and shared stories about earlier village life."
            ),
            "emotional_tone": "Warm and reflective",
            "display_order": 2,
        },
    ]

    biography = generate_biography(
        storyteller=storyteller,
        project=project,
        life_events=life_events,
    )

    biography_id = save_generated_content(
        project_id=project_id,
        content_type=biography["content_type"],
        content_title=biography["content_title"],
        content_text=biography["content_text"],
        generation_method=biography["generation_method"],
        review_status=biography["review_status"],
    )

    update_content_review_status(
        content_id=biography_id,
        new_status="Approved",
        review_comment=(
            "The two-chapter biography was checked against the fictional "
            "timeline and approved for prototype demonstration."
        ),
        reviewed_by="Demo Reviewer",
    )

    bundle = generate_event_content_bundle(
        storyteller_name="Grandpa Chen",
        event=life_events[1],
    )

    saved_bundle_ids: list[int] = []

    for item in bundle:
        content_id = save_generated_content(
            project_id=project_id,
            life_event_id=event_2,
            content_type=item["content_type"],
            content_title=item["content_title"],
            content_text=item["content_text"],
            generation_method=item["generation_method"],
            review_status=item["review_status"],
        )
        saved_bundle_ids.append(content_id)

        if item["content_type"] == "Scene Description":
            update_content_review_status(
                content_id=content_id,
                new_status="Reviewed",
                review_comment=(
                    "Scene description checked as an interpretative "
                    "reconstruction."
                ),
                reviewed_by="Demo Reviewer",
            )

    summary = get_project_summary(project_id)

    print()
    print("Clean demo database created successfully.")
    print(f"Main database: {DEFAULT_DB_PATH}")
    print(f"Backup folder: {backup_dir}")
    print(f"Storyteller ID: {storyteller_id}")
    print(f"Project ID: {project_id}")
    print(f"Biography ID: {biography_id}")
    print(f"Event bundle IDs: {saved_bundle_ids}")
    print()
    print("Clean project summary:")
    print(summary)
    print()
    print("Expected clean counts:")
    print("  Storytellers: 1")
    print("  Projects: 1")
    print("  Source materials: 4")
    print("  Life events: 2")
    print("  Generated contents: 5")


if __name__ == "__main__":
    main()
