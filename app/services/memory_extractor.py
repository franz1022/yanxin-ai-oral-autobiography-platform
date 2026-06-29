from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Optional


EXTRACTION_METHOD = "Rule-based Memory Extraction Prototype"
REVIEW_WARNING = (
    "Human confirmation is required before the extracted fields are saved "
    "as a life event."
)


@dataclass(frozen=True)
class MemoryExtractionResult:
    """Structured, reviewable fields extracted from one memory passage."""

    source_text: str
    event_title: str
    start_year: Optional[int]
    end_year: Optional[int]
    date_certainty: str
    location: Optional[str]
    people_involved: Optional[str]
    event_description: str
    emotional_tone: str
    extraction_method: str
    review_required: bool
    field_confidence: dict[str, str]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalise_text(text: str) -> str:
    """Collapse repeated whitespace while preserving readable punctuation."""
    return re.sub(r"\s+", " ", text or "").strip()


def _first_years(text: str) -> list[int]:
    values = re.findall(r"(?<!\d)(?:18|19|20)\d{2}(?!\d)", text)
    years: list[int] = []

    for value in values:
        year = int(value)
        if year not in years:
            years.append(year)

    return years


def _extract_year_range(
    text: str,
    year_hint: Optional[int],
) -> tuple[Optional[int], Optional[int], str, str]:
    if year_hint is not None:
        return int(year_hint), None, "Estimated", "high"

    years = _first_years(text)

    if not years:
        return None, None, "Unknown", "low"

    start_year = years[0]
    end_year = years[1] if len(years) > 1 else None

    estimated_keywords = (
        "around",
        "about",
        "approximately",
        "roughly",
        "circa",
        "大约",
        "大概",
        "约",
        "前后",
        "左右",
    )

    certainty = (
        "Estimated"
        if any(keyword in text.lower() for keyword in estimated_keywords)
        else "Estimated"
    )

    return start_year, end_year, certainty, "medium"


def _clean_extracted_phrase(value: str) -> str:
    value = normalise_text(value)
    value = re.split(
        r"\b(?:with|while|when|where|who|because|and then)\b",
        value,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    return value.strip(" ,.;:-")


def _extract_location(
    text: str,
    location_hint: Optional[str],
) -> tuple[Optional[str], str]:
    if location_hint and location_hint.strip():
        return normalise_text(location_hint), "high"

    migration_cn = re.search(
        r"从\s*([^，。；！？]{1,20}?)\s*(?:搬到|迁到|来到|去了)\s*"
        r"([^，。；！？]{1,20})",
        text,
    )
    if migration_cn:
        origin = normalise_text(migration_cn.group(1))
        destination = normalise_text(migration_cn.group(2))
        return f"{origin} → {destination}", "medium"

    destination_cn = re.search(
        r"(?:搬到|迁到|来到|去了)\s*([^，。；！？]{1,24})",
        text,
    )
    if destination_cn:
        return normalise_text(destination_cn.group(1)), "medium"

    cn_matches = re.findall(
        r"在\s*([^，。；！？]{2,30}?)"
        r"(?:生活|工作|学习|上学|出生|长大|度过|，|。)",
        text,
    )
    if cn_matches:
        return normalise_text(cn_matches[-1]), "medium"

    temporal_starts = (
        "the summer",
        "summer",
        "the spring",
        "spring",
        "the winter",
        "winter",
        "the autumn",
        "autumn",
        "the fall",
        "fall",
        "19",
        "20",
    )

    english_candidates: list[tuple[int, str]] = []

    for match in re.finditer(
        r"\b(in|at|near|beside)\s+([^,.!?;]{2,80})",
        text,
        flags=re.IGNORECASE,
    ):
        preposition = match.group(1).lower()
        candidate = _clean_extracted_phrase(match.group(2))
        lower_candidate = candidate.lower()

        if lower_candidate.startswith(temporal_starts):
            continue

        if re.fullmatch(r"(?:18|19|20)\d{2}", candidate):
            continue

        priority = {
            "in": 3,
            "at": 2,
            "near": 1,
            "beside": 0,
        }[preposition]
        english_candidates.append((priority, candidate))

        nested_in = re.search(
            r"\bin\s+(.+)$",
            candidate,
            flags=re.IGNORECASE,
        )
        if nested_in:
            nested_candidate = _clean_extracted_phrase(
                nested_in.group(1)
            )
            if nested_candidate:
                english_candidates.append((3, nested_candidate))

    if english_candidates:
        english_candidates.sort(key=lambda item: item[0], reverse=True)
        return english_candidates[0][1], "medium"

    return None, "low"


def _extract_people(
    text: str,
    people_hint: Optional[str],
) -> tuple[Optional[str], str]:
    if people_hint and people_hint.strip():
        return normalise_text(people_hint), "high"

    lower_text = text.lower()

    relation_terms = [
        ("older brother", "older brother"),
        ("younger brother", "younger brother"),
        ("older sister", "older sister"),
        ("younger sister", "younger sister"),
        ("grandmother", "grandmother"),
        ("grandfather", "grandfather"),
        ("mother", "mother"),
        ("father", "father"),
        ("parents", "parents"),
        ("wife", "wife"),
        ("husband", "husband"),
        ("daughter", "daughter"),
        ("son", "son"),
        ("teacher", "teacher"),
        ("classmate", "classmate"),
        ("friend", "friend"),
    ]

    chinese_terms = [
        ("哥哥", "older brother"),
        ("弟弟", "younger brother"),
        ("姐姐", "older sister"),
        ("妹妹", "younger sister"),
        ("母亲", "mother"),
        ("妈妈", "mother"),
        ("父亲", "father"),
        ("爸爸", "father"),
        ("奶奶", "grandmother"),
        ("外婆", "grandmother"),
        ("爷爷", "grandfather"),
        ("外公", "grandfather"),
        ("妻子", "wife"),
        ("丈夫", "husband"),
        ("女儿", "daughter"),
        ("儿子", "son"),
        ("老师", "teacher"),
        ("同学", "classmate"),
        ("朋友", "friend"),
    ]

    detected: list[str] = []

    for keyword, label in relation_terms:
        if keyword in lower_text and label not in detected:
            detected.append(label)

    for keyword, label in chinese_terms:
        if keyword in text and label not in detected:
            detected.append(label)

    if not detected:
        return None, "low"

    if len(detected) == 1:
        people = f"Storyteller and {detected[0]}"
    else:
        people = "Storyteller, " + ", ".join(detected)

    return people, "medium"


def _extract_emotional_tone(
    text: str,
    emotional_tone_hint: Optional[str],
) -> tuple[str, str]:
    if emotional_tone_hint and emotional_tone_hint.strip():
        return normalise_text(emotional_tone_hint), "high"

    lower_text = text.lower()

    hopeful = (
        "hope",
        "hopeful",
        "new life",
        "充满希望",
        "希望",
        "期待",
    )
    difficult = (
        "difficult",
        "hardship",
        "hard",
        "struggle",
        "辛苦",
        "困难",
        "艰难",
    )
    warm = (
        "warm",
        "fondly",
        "nostalgic",
        "remember",
        "childhood",
        "温暖",
        "怀念",
        "童年",
        "回忆",
    )
    joyful = (
        "happy",
        "joy",
        "laughed",
        "celebrated",
        "开心",
        "快乐",
        "高兴",
        "欢笑",
    )
    sad = (
        "sad",
        "loss",
        "grief",
        "missed",
        "难过",
        "悲伤",
        "失去",
        "离别",
    )

    has_hope = any(word in lower_text or word in text for word in hopeful)
    has_difficulty = any(
        word in lower_text or word in text
        for word in difficult
    )

    if has_hope and has_difficulty:
        return "Difficult but hopeful", "medium"

    if any(word in lower_text or word in text for word in warm):
        return "Warm and nostalgic", "medium"

    if any(word in lower_text or word in text for word in joyful):
        return "Joyful", "medium"

    if any(word in lower_text or word in text for word in sad):
        return "Sad and reflective", "medium"

    if has_hope:
        return "Hopeful", "medium"

    if has_difficulty:
        return "Difficult and reflective", "medium"

    return "Reflective", "low"


def _extract_title(text: str, location: Optional[str]) -> tuple[str, str]:
    lower_text = text.lower()

    if (
        ("school" in lower_text or "上学" in text or "学校" in text)
        and ("walk" in lower_text or "走路" in text or "步行" in text)
    ):
        if "primary school" in lower_text or "小学" in text:
            return "Walking to Primary School", "high"
        return "Walking to School", "high"

    if any(word in lower_text for word in ("moved", "move to", "relocated")) or any(
        word in text for word in ("搬到", "迁到", "来到")
    ):
        if location and "→" in location:
            destination = location.split("→", maxsplit=1)[1].strip()
            return f"Moving to {destination}", "high"
        if location:
            return f"Moving to {location}", "medium"
        return "Moving to a New Home", "medium"

    if any(word in lower_text for word in ("started work", "first job", "began working")) or any(
        word in text for word in ("参加工作", "第一份工作", "开始工作")
    ):
        return "Starting Work", "high"

    if any(word in lower_text for word in ("married", "wedding")) or any(
        word in text for word in ("结婚", "婚礼")
    ):
        return "Marriage and Family", "high"

    if any(word in lower_text for word in ("was born", "birth")) or "出生" in text:
        return "Birth and Early Family", "high"

    first_sentence = re.split(r"[.!?。！？]", text, maxsplit=1)[0]
    first_sentence = re.sub(
        r"^(?:in|around|about|approximately)\s+(?:the\s+)?",
        "",
        first_sentence,
        flags=re.IGNORECASE,
    )
    first_sentence = normalise_text(first_sentence)

    if not first_sentence:
        return "Untitled Memory", "low"

    if len(first_sentence) > 60:
        first_sentence = first_sentence[:57].rstrip() + "..."

    if re.search(r"[A-Za-z]", first_sentence):
        first_sentence = first_sentence[0].upper() + first_sentence[1:]

    return first_sentence, "low"


def extract_memory(
    text: str,
    *,
    year_hint: Optional[int] = None,
    location_hint: Optional[str] = None,
    people_hint: Optional[str] = None,
    emotional_tone_hint: Optional[str] = None,
) -> MemoryExtractionResult:
    """
    Extract one reviewable life-event candidate from a memory passage.

    The function is deterministic and does not call an external AI model.
    Hints are treated as user-provided metadata and override text inference.
    """
    source_text = normalise_text(text)

    if not source_text:
        raise ValueError("Memory text cannot be empty.")

    start_year, end_year, date_certainty, year_confidence = (
        _extract_year_range(source_text, year_hint)
    )
    location, location_confidence = _extract_location(
        source_text,
        location_hint,
    )
    people, people_confidence = _extract_people(
        source_text,
        people_hint,
    )
    emotional_tone, tone_confidence = _extract_emotional_tone(
        source_text,
        emotional_tone_hint,
    )
    title, title_confidence = _extract_title(source_text, location)

    warnings: list[str] = [REVIEW_WARNING]

    if start_year is None:
        warnings.append("No explicit year was found.")

    if location is None:
        warnings.append("No reliable location was found.")

    if people is None:
        warnings.append("No named person or relationship was found.")

    return MemoryExtractionResult(
        source_text=source_text,
        event_title=title,
        start_year=start_year,
        end_year=end_year,
        date_certainty=date_certainty,
        location=location,
        people_involved=people,
        event_description=source_text,
        emotional_tone=emotional_tone,
        extraction_method=EXTRACTION_METHOD,
        review_required=True,
        field_confidence={
            "event_title": title_confidence,
            "year": year_confidence,
            "location": location_confidence,
            "people_involved": people_confidence,
            "emotional_tone": tone_confidence,
        },
        warnings=tuple(warnings),
    )


def create_life_event_payload(
    result: MemoryExtractionResult,
    *,
    project_id: int,
    source_material_id: Optional[int] = None,
    display_order: int = 0,
) -> dict[str, Any]:
    """Convert a reviewed extraction result into database function inputs."""
    return {
        "project_id": int(project_id),
        "source_material_id": source_material_id,
        "event_title": result.event_title,
        "event_description": result.event_description,
        "start_year": result.start_year,
        "end_year": result.end_year,
        "date_certainty": result.date_certainty,
        "location": result.location,
        "people_involved": result.people_involved,
        "emotional_tone": result.emotional_tone,
        "display_order": int(display_order),
    }
