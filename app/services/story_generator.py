from __future__ import annotations

import re
from typing import Any, Iterable, Optional


AI_ASSISTED_NOTICE = (
    "AI-assisted draft for human review. "
    "This content is based on user-provided materials and may contain "
    "interpretative language that requires factual verification."
)


def clean_text(text: Optional[str]) -> str:
    """Normalise whitespace in user-provided text."""
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def lower_initial_article(text: str) -> str:
    """
    Lowercase an initial English article when the text appears inside
    a sentence, for example:
    'A fictional village' -> 'a fictional village'.
    """
    replacements = {
        "A ": "a ",
        "An ": "an ",
        "The ": "the ",
    }

    for prefix, replacement in replacements.items():
        if text.startswith(prefix):
            return replacement + text[len(prefix):]

    return text


def format_year_range(
    start_year: Optional[int],
    end_year: Optional[int],
    date_certainty: str = "Estimated",
) -> str:
    """Create a readable year label for one life event."""
    if start_year is None and end_year is None:
        return "Year unknown"

    if start_year is not None and end_year is not None:
        if start_year == end_year:
            label = str(start_year)
        else:
            label = f"{start_year}–{end_year}"
    elif start_year is not None:
        label = str(start_year)
    else:
        label = f"before or around {end_year}"

    if date_certainty == "Estimated":
        return f"Around {label}"

    if date_certainty == "Unknown":
        return f"Date uncertain: {label}"

    return label


def _event_sort_key(event: dict[str, Any]) -> tuple[int, int, int]:
    display_order = int(event.get("display_order") or 0)
    start_year = event.get("start_year")
    event_id = int(event.get("event_id") or 0)

    year_value = int(start_year) if start_year is not None else 9999
    return display_order, year_value, event_id


def generate_event_chapter(
    storyteller_name: str,
    event: dict[str, Any],
) -> dict[str, str]:
    """Generate one editable biography chapter from a life event."""
    event_title = clean_text(event.get("event_title")) or "Untitled Memory"
    event_description = clean_text(event.get("event_description"))
    location = clean_text(event.get("location"))
    people = clean_text(event.get("people_involved"))
    emotional_tone = clean_text(event.get("emotional_tone"))
    year_label = format_year_range(
        event.get("start_year"),
        event.get("end_year"),
        event.get("date_certainty") or "Estimated",
    )

    if location:
        sentence_location = lower_initial_article(location)
        opening = (
            f"{year_label}, {storyteller_name} experienced an important "
            f"moment in {sentence_location}."
        )
    else:
        opening = (
            f"{year_label}, {storyteller_name} experienced an important "
            "moment."
        )

    detail_sentences: list[str] = []

    if event_description:
        detail_sentences.append(event_description.rstrip(".") + ".")

    if people:
        detail_sentences.append(
            f"People connected with this memory include {people}."
        )

    if emotional_tone:
        detail_sentences.append(
            f"The memory carries a {emotional_tone.lower()} tone."
        )

    detail_sentences.append(
        "The wording should be checked against the original voice, text "
        "or photograph materials before approval."
    )

    content = "\n\n".join(
        [
            opening,
            " ".join(detail_sentences),
            AI_ASSISTED_NOTICE,
        ]
    )

    return {
        "content_type": "Chapter",
        "content_title": event_title,
        "content_text": content,
        "generation_method": "Template Prototype",
        "review_status": "Draft",
    }


def generate_biography(
    storyteller: dict[str, Any],
    project: dict[str, Any],
    life_events: Iterable[dict[str, Any]],
) -> dict[str, str]:
    """Generate a structured autobiography draft from timeline events."""
    full_name = clean_text(storyteller.get("full_name")) or "The storyteller"
    preferred_name = clean_text(storyteller.get("preferred_name"))
    hometown = clean_text(storyteller.get("hometown"))
    birth_year = storyteller.get("birth_year")
    project_title = (
        clean_text(project.get("project_title"))
        or f"{full_name}'s Life Story"
    )

    display_name = preferred_name or full_name

    intro_parts = [
        f"This autobiography draft brings together selected memories from "
        f"{display_name}'s life."
    ]

    if birth_year:
        intro_parts.append(
            f"{display_name} was born around {birth_year}."
        )

    if hometown:
        intro_parts.append(
            f"The storyteller's background is connected with {hometown}."
        )

    events = sorted(list(life_events), key=_event_sort_key)

    sections = [
        f"# {project_title}",
        "",
        "## Introduction",
        " ".join(intro_parts),
    ]

    if not events:
        sections.extend(
            [
                "",
                "## Timeline",
                "No life events have been added yet.",
            ]
        )
    else:
        for index, event in enumerate(events, start=1):
            chapter = generate_event_chapter(display_name, event)

            sections.extend(
                [
                    "",
                    f"## Chapter {index}: {chapter['content_title']}",
                    chapter["content_text"],
                ]
            )

    sections.extend(
        [
            "",
            "## Review Notice",
            AI_ASSISTED_NOTICE,
        ]
    )

    return {
        "content_type": "Biography",
        "content_title": project_title,
        "content_text": "\n".join(sections),
        "generation_method": "Template Prototype",
        "review_status": "Draft",
    }


def generate_scene_description(
    event: dict[str, Any],
) -> dict[str, str]:
    """Generate an interpretative historical-scene description."""
    title = clean_text(event.get("event_title")) or "Historical Memory"
    description = clean_text(event.get("event_description"))
    location = clean_text(event.get("location")) or "An unspecified location"
    people = clean_text(event.get("people_involved")) or "People described in the memory"
    tone = clean_text(event.get("emotional_tone")) or "Reflective"
    year_label = format_year_range(
        event.get("start_year"),
        event.get("end_year"),
        event.get("date_certainty") or "Estimated",
    )

    sentence_location = lower_initial_article(location)

    content = f"""### Scene details

- **Time setting:** {year_label}
- **Location:** {location}
- **People:** {people}
- **Emotional atmosphere:** {tone}

### Scene reconstruction

The scene opens in {sentence_location}. Its surroundings should suggest the
period indicated by **{year_label.lower()}**, while avoiding unsupported
historical details.

The central action is based on this user-provided memory:

> {description or "No detailed event description was provided."}

### Visual guidance

- Use period-appropriate but non-specific clothing and surroundings.
- Avoid inventing identifiable faces, exact dialogue or unverified events.
- Maintain a {tone.lower()} visual tone.
- Treat the result as an interpretative reconstruction, not historical evidence.

### Review notice

{AI_ASSISTED_NOTICE}
"""

    return {
        "content_type": "Scene Description",
        "content_title": f"Scene Reconstruction: {title}",
        "content_text": content.strip(),
        "generation_method": "Template Prototype",
        "review_status": "Draft",
    }


def generate_storyboard(
    event: dict[str, Any],
) -> dict[str, str]:
    """Generate a simple five-shot storyboard for one life event."""
    title = clean_text(event.get("event_title")) or "Historical Memory"
    location = clean_text(event.get("location")) or "the setting"
    people = clean_text(event.get("people_involved")) or "the storyteller"
    description = clean_text(event.get("event_description"))
    tone = clean_text(event.get("emotional_tone")) or "Reflective"

    shots = [
        (
            "Shot 1 – Establishing view",
            f"A wide view of {lower_initial_article(location)}, introducing "
            "the time and environment.",
        ),
        (
            "Shot 2 – Character introduction",
            f"A medium shot showing {people}, without inventing exact "
            "facial details.",
        ),
        (
            "Shot 3 – Main action",
            description
            or "The central memory is represented through restrained action.",
        ),
        (
            "Shot 4 – Emotional detail",
            f"A close-up of an object, gesture or environmental detail that "
            f"conveys a {tone.lower()} mood.",
        ),
        (
            "Shot 5 – Closing image",
            "A quiet final image that links the memory to the storyteller's "
            "later reflection.",
        ),
    ]

    lines = [
        f"# Storyboard: {title}",
        "",
    ]

    for shot_title, shot_text in shots:
        lines.extend(
            [
                f"## {shot_title}",
                shot_text,
                "",
            ]
        )

    lines.extend(
        [
            "## Review Notice",
            AI_ASSISTED_NOTICE,
        ]
    )

    return {
        "content_type": "Storyboard",
        "content_title": f"Storyboard: {title}",
        "content_text": "\n".join(lines).strip(),
        "generation_method": "Template Prototype",
        "review_status": "Draft",
    }


def generate_video_prompt(
    event: dict[str, Any],
) -> dict[str, str]:
    """Create a future video-generation prompt without generating video."""
    title = clean_text(event.get("event_title")) or "Historical Memory"
    location = clean_text(event.get("location")) or "An unspecified location"
    description = clean_text(event.get("event_description"))
    people = clean_text(event.get("people_involved")) or "The storyteller"
    tone = clean_text(event.get("emotional_tone")) or "Reflective"
    year_label = format_year_range(
        event.get("start_year"),
        event.get("end_year"),
        event.get("date_certainty") or "Estimated",
    )

    prompt = f"""### Video concept

Create a short, respectful, documentary-style reconstruction of the memory
titled **"{title}"**.

- **Time:** {year_label}
- **Location:** {location}
- **People:** {people}
- **Mood:** {tone}
- **Source memory:** {description or "No detailed source description provided."}

### Requirements

- Do not claim that the result is authentic historical footage.
- Do not invent exact faces, dialogue, names or political details.
- Use restrained camera movement and natural lighting.
- Emphasise atmosphere, environment and memory rather than spectacle.
- Present the final output as an AI-assisted interpretation requiring human review.
"""

    return {
        "content_type": "Video Prompt",
        "content_title": f"Video Prompt: {title}",
        "content_text": prompt.strip(),
        "generation_method": "Template Prototype",
        "review_status": "Draft",
    }


def generate_event_content_bundle(
    storyteller_name: str,
    event: dict[str, Any],
) -> list[dict[str, str]]:
    """Generate all supported content types for one event."""
    return [
        generate_event_chapter(storyteller_name, event),
        generate_scene_description(event),
        generate_storyboard(event),
        generate_video_prompt(event),
    ]
