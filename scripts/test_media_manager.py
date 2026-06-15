from __future__ import annotations

import io
import wave
from pathlib import Path

from PIL import Image

from app.services.media_manager import (
    clear_project_uploads,
    delete_uploaded_file,
    save_uploaded_file,
    sanitize_filename,
)


BASE_DIR = Path(__file__).resolve().parents[1]
TEST_UPLOAD_DIR = BASE_DIR / "data" / "uploads"


def create_test_png() -> bytes:
    buffer = io.BytesIO()

    image = Image.new(
        mode="RGB",
        size=(80, 60),
        color=(220, 220, 220),
    )
    image.save(buffer, format="PNG")

    return buffer.getvalue()


def create_test_wav() -> bytes:
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        wav_file.writeframes(b"\x00\x00" * 800)

    return buffer.getvalue()


def main() -> None:
    project_id = 999
    clear_project_uploads(project_id, TEST_UPLOAD_DIR)

    print("Sanitised filename:")
    print(
        sanitize_filename(
            "Grandpa Chen - old family photo (1958).png"
        )
    )
    print()

    photo_metadata = save_uploaded_file(
        file_source=create_test_png(),
        original_filename="fictional_family_photo_1958.png",
        project_id=project_id,
        mime_type="image/png",
        upload_dir=TEST_UPLOAD_DIR,
    )

    audio_metadata = save_uploaded_file(
        file_source=create_test_wav(),
        original_filename="fictional_oral_memory.wav",
        project_id=project_id,
        mime_type="audio/wav",
        upload_dir=TEST_UPLOAD_DIR,
    )

    print("Photo metadata:")
    print(photo_metadata)
    print()

    print("Audio metadata:")
    print(audio_metadata)
    print()

    photo_exists = Path(photo_metadata["absolute_path"]).exists()
    audio_exists = Path(audio_metadata["absolute_path"]).exists()

    print(f"Photo saved successfully: {photo_exists}")
    print(f"Audio saved successfully: {audio_exists}")

    deleted = delete_uploaded_file(
        audio_metadata["stored_path"],
        BASE_DIR,
    )
    print(f"Audio deletion test: {deleted}")

    cleaned = clear_project_uploads(
        project_id,
        TEST_UPLOAD_DIR,
    )
    print(f"Project upload cleanup test: {cleaned}")

    print()
    print("Media manager test completed successfully.")


if __name__ == "__main__":
    main()
