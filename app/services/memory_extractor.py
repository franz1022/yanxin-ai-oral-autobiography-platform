from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Optional


EXTRACTION_METHOD = "Rule-based Memory Extraction Prototype"
REVIEW_WARNING = (
    "Human confirmation is required before the extracted fields are saved "
    "as a life event."
)
REVIEW_WARNING_ZH = "保存为人生事件前，必须由用户逐项确认提取结果。"


@dataclass(frozen=True)
class MemoryExtractionResult:
    """Structured, reviewable fields extracted from one memory passage."""

    source_text: str
    detected_language: str
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


def detect_language(text: str) -> str:
    """Return ``zh`` for Chinese-dominant passages and ``en`` otherwise."""
    source_text = normalise_text(text)
    chinese_count = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", source_text))
    latin_count = len(re.findall(r"[A-Za-z]", source_text))

    if chinese_count >= 2 and chinese_count >= latin_count * 0.15:
        return "zh"

    return "en"


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

    # The prototype treats years parsed from free-form memory text as
    # estimated until the user explicitly confirms them in the review form.
    return start_year, end_year, "Estimated", "medium"


def _clean_extracted_phrase(value: str) -> str:
    """Trim common narrative continuations from an English location phrase."""
    value = normalise_text(value)
    value = re.split(
        r"\b(?:with|while|when|where|who|because|during|and then)\b"
        r"|\band\s+(?:remembered|recalled|celebrated|felt|worked|studied|"
        r"lived|sat|walked)\b",
        value,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    return value.strip(" ,.;:-")


def _clean_chinese_location(value: str) -> str:
    """Keep the place name while removing trailing actions and particles."""
    value = normalise_text(value)
    value = re.split(
        r"(?:举行婚礼|举行|生活|工作|学习|上学|出生|长大|度过|居住|"
        r"结婚|里聊天|聊天|回忆|玩耍|散步|读书|求学|住下)",
        value,
        maxsplit=1,
    )[0]
    value = value.strip(" ，。；！？,:;")
    value = re.sub(r"(院子|房间|屋子)里$", r"\1", value)
    return value


def _extract_location(
    text: str,
    location_hint: Optional[str],
) -> tuple[Optional[str], str]:
    if location_hint and location_hint.strip():
        return normalise_text(location_hint), "high"

    # Migration paths are kept as origin → destination because both places
    # are useful for a reviewed life-event record.
    migration_cn = re.search(
        r"从\s*([^，。；！？]{1,24}?)\s*(?:搬到|迁到|迁往|来到|去了)\s*"
        r"([^，。；！？]{1,30})",
        text,
    )
    if migration_cn:
        origin = _clean_chinese_location(migration_cn.group(1))
        destination = _clean_chinese_location(migration_cn.group(2))
        if origin and destination:
            return f"{origin} → {destination}", "medium"

    migration_en = re.search(
        r"\b(?:moved|relocated|migrated)\s+from\s+"
        r"([^,.!?;]{1,60}?)\s+to\s+([^,.!?;]{1,60}?)"
        r"(?=\s+(?:with|while|when|because|and)\b|[,.!?;]|$)",
        text,
        flags=re.IGNORECASE,
    )
    if migration_en:
        origin = _clean_extracted_phrase(migration_en.group(1))
        destination = _clean_extracted_phrase(migration_en.group(2))
        if origin and destination:
            return f"{origin} → {destination}", "medium"

    destination_cn = re.search(
        r"(?:搬到|迁到|迁往|来到|去了)\s*([^，。；！？]{1,30})",
        text,
    )
    if destination_cn:
        candidate = _clean_chinese_location(destination_cn.group(1))
        if candidate:
            return candidate, "medium"

    # Prefer explicit Chinese place constructions. The look-ahead prevents
    # narrative actions such as “举行婚礼” or “里聊天” entering the value.
    cn_patterns = (
        r"出生在\s*([^，。；！？]{1,30}?)(?=，|。|；|！|？|$)",
        r"(?:坐|站|停留|住)?在\s*([^，。；！？]{1,30}?)"
        r"(?=举行婚礼|生活|工作|学习|上学|出生|长大|度过|居住|"
        r"里聊天|聊天|回忆|，|。|；|！|？|$)",
    )
    excluded_cn = {"一起", "这里", "那里", "当时"}

    for pattern in cn_patterns:
        for match in re.finditer(pattern, text):
            candidate = _clean_chinese_location(match.group(1))
            if candidate and candidate not in excluded_cn:
                return candidate, "medium"

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

    english_candidates: list[tuple[int, int, str]] = []

    for match_index, match in enumerate(
        re.finditer(
            r"\b(in|at|near|beside)\s+([^,.!?;]{2,100})",
            text,
            flags=re.IGNORECASE,
        )
    ):
        preposition = match.group(1).lower()
        candidate = _clean_extracted_phrase(match.group(2))
        lower_candidate = candidate.lower()

        if lower_candidate.startswith(temporal_starts):
            continue

        if re.fullmatch(r"(?:18|19|20)\d{2}", candidate):
            continue

        priority = {
            "in": 5,
            "at": 4,
            "near": 3,
            "beside": 2,
        }[preposition]

        # Phrases such as “a school in Guangzhou” or “a fictional village
        # in Guangdong” contain a more useful nested geographic location.
        nested_matches = list(
            re.finditer(r"\bin\s+(.+)$", candidate, flags=re.IGNORECASE)
        )
        if nested_matches:
            nested_candidate = _clean_extracted_phrase(
                nested_matches[-1].group(1)
            )
            if nested_candidate:
                english_candidates.append(
                    (priority + 10, -match_index, nested_candidate)
                )

        if candidate:
            english_candidates.append((priority, -match_index, candidate))

    if english_candidates:
        english_candidates.sort(reverse=True)
        return english_candidates[0][2], "medium"

    return None, "low"


def _extract_people(
    text: str,
    people_hint: Optional[str],
    language: str,
) -> tuple[Optional[str], str]:
    if people_hint and people_hint.strip():
        return normalise_text(people_hint), "high"

    lower_text = text.lower()

    relation_terms = [
        ("older brother", "older brother", "哥哥"),
        ("younger brother", "younger brother", "弟弟"),
        ("older sister", "older sister", "姐姐"),
        ("younger sister", "younger sister", "妹妹"),
        ("grandmother", "grandmother", "祖母或外祖母"),
        ("grandfather", "grandfather", "祖父或外祖父"),
        ("mother", "mother", "母亲"),
        ("father", "father", "父亲"),
        ("parents", "parents", "父母"),
        ("wife", "wife", "妻子"),
        ("husband", "husband", "丈夫"),
        ("daughter", "daughter", "女儿"),
        ("son", "son", "儿子"),
        ("teacher", "teacher", "老师"),
        ("classmate", "classmate", "同学"),
        ("friend", "friend", "朋友"),
    ]

    chinese_terms = [
        ("哥哥", "older brother", "哥哥"),
        ("弟弟", "younger brother", "弟弟"),
        ("姐姐", "older sister", "姐姐"),
        ("妹妹", "younger sister", "妹妹"),
        ("母亲", "mother", "母亲"),
        ("妈妈", "mother", "母亲"),
        ("父亲", "father", "父亲"),
        ("爸爸", "father", "父亲"),
        ("父母", "parents", "父母"),
        ("奶奶", "grandmother", "奶奶"),
        ("外婆", "grandmother", "外婆"),
        ("爷爷", "grandfather", "爷爷"),
        ("外公", "grandfather", "外公"),
        ("妻子", "wife", "妻子"),
        ("丈夫", "husband", "丈夫"),
        ("女儿", "daughter", "女儿"),
        ("儿子", "son", "儿子"),
        ("老师", "teacher", "老师"),
        ("同学", "classmate", "同学"),
        ("朋友", "friend", "朋友"),
    ]

    detected_en: list[str] = []
    detected_zh: list[str] = []

    for keyword, label_en, label_zh in relation_terms:
        if keyword in lower_text and label_en not in detected_en:
            detected_en.append(label_en)
            detected_zh.append(label_zh)

    for keyword, label_en, label_zh in chinese_terms:
        if keyword in text and label_en not in detected_en:
            detected_en.append(label_en)
            detected_zh.append(label_zh)

    if not detected_en:
        return None, "low"

    if language == "zh":
        if len(detected_zh) == 1:
            return f"讲述者和{detected_zh[0]}", "medium"
        return "讲述者、" + "、".join(detected_zh), "medium"

    if len(detected_en) == 1:
        return f"Storyteller and {detected_en[0]}", "medium"

    return "Storyteller, " + ", ".join(detected_en), "medium"


def _contains_any(text: str, lower_text: str, words: tuple[str, ...]) -> bool:
    return any(word in lower_text or word in text for word in words)


def _extract_emotional_tone(
    text: str,
    emotional_tone_hint: Optional[str],
    language: str,
) -> tuple[str, str]:
    if emotional_tone_hint and emotional_tone_hint.strip():
        return normalise_text(emotional_tone_hint), "high"

    lower_text = text.lower()

    hopeful = ("hope", "hopeful", "new life", "充满希望", "希望", "期待")
    difficult = ("difficult", "hardship", "hard", "struggle", "辛苦", "困难", "艰难")
    warm = ("warm", "fondly", "nostalgic", "remember", "childhood", "温暖", "怀念", "童年", "回忆")
    joyful = ("happy", "joy", "laughed", "celebrated", "开心", "快乐", "高兴", "欢笑")
    sad = ("sad", "loss", "grief", "missed", "难过", "悲伤", "失去", "离别")

    has_hope = _contains_any(text, lower_text, hopeful)
    has_difficulty = _contains_any(text, lower_text, difficult)

    if has_hope and has_difficulty:
        return (
            "艰难但充满希望" if language == "zh" else "Difficult but hopeful",
            "medium",
        )

    if _contains_any(text, lower_text, warm):
        return (
            "温暖而怀念" if language == "zh" else "Warm and nostalgic",
            "medium",
        )

    if _contains_any(text, lower_text, joyful):
        return ("喜悦" if language == "zh" else "Joyful", "medium")

    if _contains_any(text, lower_text, sad):
        return (
            "悲伤而沉思" if language == "zh" else "Sad and reflective",
            "medium",
        )

    if has_hope:
        return ("充满希望" if language == "zh" else "Hopeful", "medium")

    if has_difficulty:
        return (
            "艰难而沉思" if language == "zh" else "Difficult and reflective",
            "medium",
        )

    return ("平静而沉思" if language == "zh" else "Reflective", "low")


def _strip_chinese_time_prefix(text: str) -> str:
    return re.sub(
        r"^(?:大约|大概|约)?\s*(?:在)?\s*(?:18|19|20)\d{2}年?\s*[，,]?\s*",
        "",
        text,
    ).strip()


def _extract_title(
    text: str,
    location: Optional[str],
    language: str,
) -> tuple[str, str]:
    lower_text = text.lower()

    if (
        ("school" in lower_text or "上学" in text or "学校" in text or "小学" in text)
        and ("walk" in lower_text or "走路" in text or "步行" in text or "走着" in text)
    ):
        if language == "zh":
            return (
                "步行去小学" if "primary school" in lower_text or "小学" in text else "步行去学校",
                "high",
            )
        if "primary school" in lower_text or "小学" in text:
            return "Walking to Primary School", "high"
        return "Walking to School", "high"

    if any(word in lower_text for word in ("moved", "move to", "relocated", "migrated")) or any(
        word in text for word in ("搬到", "迁到", "迁往", "来到")
    ):
        if location and "→" in location:
            destination = location.split("→", maxsplit=1)[1].strip()
            return (
                f"搬到{destination}" if language == "zh" else f"Moving to {destination}",
                "high",
            )
        if location:
            return (
                f"搬到{location}" if language == "zh" else f"Moving to {location}",
                "medium",
            )
        return (
            "搬到新家" if language == "zh" else "Moving to a New Home",
            "medium",
        )

    if any(word in lower_text for word in ("started work", "first job", "began working")) or any(
        word in text for word in ("参加工作", "第一份工作", "开始工作")
    ):
        return ("开始工作" if language == "zh" else "Starting Work", "high")

    if any(word in lower_text for word in ("married", "wedding")) or any(
        word in text for word in ("结婚", "婚礼")
    ):
        return ("结婚与家庭" if language == "zh" else "Marriage and Family", "high")

    if any(word in lower_text for word in ("was born", "birth")) or "出生" in text:
        return (
            "出生与早年家庭" if language == "zh" else "Birth and Early Family",
            "high",
        )

    # Common autobiographical event types are normalised to short,
    # review-friendly titles rather than copying the whole first sentence.
    if (
        ("院子" in text and "聊天" in text)
        or ("courtyard" in lower_text and any(
            word in lower_text for word in ("sat", "talked", "conversation")
        ))
    ):
        if language == "zh":
            if "母亲" in text or "妈妈" in text:
                return "在院子里与母亲聊天", "high"
            return "在院子里聊天", "medium"
        return "Conversations in the Family Courtyard", "high"

    if "毕业" in text and any(word in text for word in ("庆祝", "开心", "快乐")):
        return "庆祝毕业", "high"
    if "graduation" in lower_text and any(
        word in lower_text for word in ("celebrated", "celebrating", "happy")
    ):
        return "Celebrating Graduation", "high"

    if any(word in text for word in ("父亲离开了我们", "父亲离世", "父亲去世")):
        return "父亲离世", "high"
    if any(
        phrase in lower_text
        for phrase in ("father's loss", "father passed away", "loss of my father")
    ):
        return "Remembering My Father", "high"

    if "窗边" in text and "回忆" in text:
        return "窗边回忆", "high"
    if "window" in lower_text and any(
        word in lower_text for word in ("remembered", "recalled", "memory")
    ):
        if "kitchen window" in lower_text:
            return "Memories by the Kitchen Window", "high"
        return "Memories by the Window", "medium"

    if any(word in text for word in ("学习", "求学", "上学")) and location:
        return f"在{location}求学", "high"
    if any(word in lower_text for word in ("studied", "studying")) and location:
        return f"Studying in {location}", "high"

    if ("童年" in text or "小时候" in text) and location:
        return f"{location}的童年", "high"
    if "childhood" in lower_text and location:
        return f"Childhood in {location}", "high"

    first_sentence = re.split(r"[.!?。！？]", text, maxsplit=1)[0]

    if language == "zh":
        first_sentence = _strip_chinese_time_prefix(first_sentence)
        first_sentence = normalise_text(first_sentence)
        if not first_sentence:
            return "未命名回忆", "low"
        if len(first_sentence) > 30:
            first_sentence = first_sentence[:27].rstrip() + "..."
        return first_sentence, "low"

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


def _warning_text(language: str, warning_type: str) -> str:
    messages = {
        "en": {
            "review": REVIEW_WARNING,
            "year": "No explicit year was found.",
            "location": "No reliable location was found.",
            "people": "No named person or relationship was found.",
        },
        "zh": {
            "review": REVIEW_WARNING_ZH,
            "year": "未识别到明确年份。",
            "location": "未识别到可靠地点。",
            "people": "未识别到明确人物或亲属关系。",
        },
    }
    return messages[language][warning_type]


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

    language = detect_language(source_text)

    start_year, end_year, date_certainty, year_confidence = _extract_year_range(
        source_text,
        year_hint,
    )
    location, location_confidence = _extract_location(source_text, location_hint)
    people, people_confidence = _extract_people(
        source_text,
        people_hint,
        language,
    )
    emotional_tone, tone_confidence = _extract_emotional_tone(
        source_text,
        emotional_tone_hint,
        language,
    )
    title, title_confidence = _extract_title(source_text, location, language)

    warnings: list[str] = [_warning_text(language, "review")]

    if start_year is None:
        warnings.append(_warning_text(language, "year"))

    if location is None:
        warnings.append(_warning_text(language, "location"))

    if people is None:
        warnings.append(_warning_text(language, "people"))

    return MemoryExtractionResult(
        source_text=source_text,
        detected_language=language,
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
