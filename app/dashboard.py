from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from app.services.database import (  # noqa: E402
    DEFAULT_DB_PATH,
    add_file_material,
    add_text_material,
    create_life_event,
    create_project,
    create_storyteller,
    get_project_summary,
    get_storyteller,
    initialize_database,
    list_generated_contents,
    list_life_events,
    list_materials,
    list_projects,
    list_storytellers,
    save_generated_content,
    update_content_review_status,
)
from app.services.media_manager import save_uploaded_file  # noqa: E402
from app.services.memory_extraction_providers import (  # noqa: E402
    RULE_BASED_PROVIDER_ID,
    extract_memory_with_provider,
    list_memory_extraction_providers,
)
from app.services.story_generator import (  # noqa: E402
    generate_biography,
    generate_event_content_bundle,
)


st.set_page_config(
    page_title="Yanxin AI Oral Autobiography Platform",
    page_icon="📖",
    layout="wide",
)


initialize_database()


def dataframe_from_records(
    records: list[dict[str, Any]],
    columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()

    frame = pd.DataFrame(records)

    if columns:
        existing_columns = [
            column for column in columns if column in frame.columns
        ]
        frame = frame[existing_columns]

    return frame


def year_or_none(enabled: bool, value: int) -> Optional[int]:
    return int(value) if enabled else None


def get_selected_project() -> tuple[Optional[int], Optional[dict[str, Any]]]:
    projects = list_projects()

    if not projects:
        return None, None

    project_map = {
        (
            f"#{project['project_id']} · "
            f"{project['project_title']} · "
            f"{project['storyteller_name']}"
        ): project
        for project in projects
    }

    selected_label = st.sidebar.selectbox(
        "Current autobiography project",
        options=list(project_map.keys()),
    )

    selected_project = project_map[selected_label]
    return int(selected_project["project_id"]), selected_project


def create_fictional_demo_data() -> None:
    existing = list_storytellers()

    if existing:
        st.sidebar.info(
            "Demo data was not added because storyteller records already exist."
        )
        return

    storyteller_id = create_storyteller(
        full_name="Chen Ming",
        preferred_name="Grandpa Chen",
        birth_year=1948,
        hometown="Guangdong",
        biography_language="Chinese",
        profile_notes=(
            "Fictional demonstration profile. "
            "No real personal information is used."
        ),
    )

    project_id = create_project(
        storyteller_id=storyteller_id,
        project_title="Childhood and Family Memories",
        project_description=(
            "A fictional demonstration project for the public prototype."
        ),
        project_status="In Progress",
        created_by_relationship="Grandchild",
    )

    material_id = add_text_material(
        project_id=project_id,
        text_content=(
            "In the summer of 1958, I walked to school with my older "
            "brother and often stopped beside an old banyan tree."
        ),
        material_description="Fictional childhood memory.",
        estimated_year=1958,
        location="A fictional village in Guangdong",
        people_description="Storyteller and older brother",
    )

    create_life_event(
        project_id=project_id,
        source_material_id=material_id,
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

    st.sidebar.success("Fictional demo data created.")
    st.rerun()


st.title("Yanxin AI Oral Autobiography Platform")

st.caption(
    "Privacy-safe portfolio prototype inspired by a 2023 university "
    "team project."
)

st.info(
    "This prototype organises voice, text and historical photographs "
    "into editable life timelines, autobiography drafts and scene "
    "reconstruction descriptions. It does not claim to generate verified "
    "historical footage."
)


with st.sidebar:
    st.header("Project Controls")

    st.write(f"Database: `{DEFAULT_DB_PATH.name}`")

    if st.button(
        "Create Fictional Demo Data",
        width="stretch",
    ):
        create_fictional_demo_data()

    st.divider()


selected_project_id, selected_project = get_selected_project()


tabs = st.tabs(
    [
        "Overview",
        "People & Projects",
        "Source Materials",
        "Life Timeline",
        "Generate Content",
        "Review",
    ]
)


with tabs[0]:
    st.header("Prototype Overview")

    col1, col2, col3 = st.columns(3)

    storyteller_count = len(list_storytellers())
    project_count = len(list_projects())

    col1.metric("Storytellers", storyteller_count)
    col2.metric("Autobiography Projects", project_count)

    if selected_project_id is not None:
        summary = get_project_summary(selected_project_id)

        col3.metric(
            "Generated Contents",
            summary["generated_content_count"],
        )

        st.subheader("Current Project")

        summary_cols = st.columns(4)
        summary_cols[0].metric(
            "Source Materials",
            summary["material_count"],
        )
        summary_cols[1].metric(
            "Life Events",
            summary["event_count"],
        )
        summary_cols[2].metric(
            "Generated Contents",
            summary["generated_content_count"],
        )
        summary_cols[3].metric(
            "Status",
            summary["project_status"],
        )

        st.write(
            f"**Storyteller:** {summary['storyteller_name']}"
        )
        st.write(
            f"**Project:** {summary['project_title']}"
        )
    else:
        col3.metric("Generated Contents", 0)
        st.warning(
            "Create a storyteller and project before adding materials."
        )

    st.subheader("End-to-End Workflow")

    st.code(
        """
Voice / Text / Historical Photos
                ↓
Material Storage and Metadata
                ↓
Structured Life Events
                ↓
Biography Draft and Scene Description
                ↓
Storyboard and Future Video Prompt
                ↓
Human Review and Approval
        """.strip(),
        language="text",
    )

    st.subheader("Portfolio Positioning")

    st.write(
        """
        The original project was completed by a team. The portfolio owner
        worked primarily as a project coordinator and product–technical
        liaison, while contributing to selected frontend workflows and
        basic database implementation. This public prototype reconstructs
        those responsibilities without claiming independent Transformer
        training or production video generation.
        """
    )


with tabs[1]:
    st.header("People and Autobiography Projects")

    left, right = st.columns(2)

    with left:
        st.subheader("Create Storyteller")

        with st.form("create_storyteller_form"):
            full_name = st.text_input(
                "Full name",
                placeholder="Use fictional information for public demos",
            )

            preferred_name = st.text_input(
                "Preferred name",
            )

            birth_year_enabled = st.checkbox(
                "Birth year is known",
                value=True,
            )

            birth_year_value = st.number_input(
                "Birth year",
                min_value=1850,
                max_value=2026,
                value=1950,
                step=1,
                disabled=not birth_year_enabled,
            )

            hometown = st.text_input("Hometown")

            biography_language = st.selectbox(
                "Biography language",
                ["Chinese", "English", "Bilingual"],
            )

            profile_notes = st.text_area(
                "Profile notes",
            )

            create_storyteller_submit = st.form_submit_button(
                "Create Storyteller",
                width="stretch",
            )

        if create_storyteller_submit:
            try:
                storyteller_id = create_storyteller(
                    full_name=full_name,
                    preferred_name=preferred_name or None,
                    birth_year=year_or_none(
                        birth_year_enabled,
                        int(birth_year_value),
                    ),
                    hometown=hometown or None,
                    biography_language=biography_language,
                    profile_notes=profile_notes or None,
                )

                st.success(
                    f"Storyteller created with ID {storyteller_id}."
                )
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    with right:
        st.subheader("Create Project")

        storytellers = list_storytellers()

        if not storytellers:
            st.warning("Create a storyteller first.")
        else:
            storyteller_options = {
                (
                    f"#{item['storyteller_id']} · "
                    f"{item['full_name']}"
                ): int(item["storyteller_id"])
                for item in storytellers
            }

            with st.form("create_project_form"):
                selected_storyteller_label = st.selectbox(
                    "Storyteller",
                    list(storyteller_options.keys()),
                )

                project_title = st.text_input(
                    "Project title",
                )

                project_description = st.text_area(
                    "Project description",
                )

                project_status = st.selectbox(
                    "Project status",
                    [
                        "Draft",
                        "In Progress",
                        "Under Review",
                        "Completed",
                        "Archived",
                    ],
                )

                created_by_relationship = st.text_input(
                    "Creator relationship",
                    placeholder="Self, child, grandchild, editor...",
                )

                create_project_submit = st.form_submit_button(
                    "Create Project",
                    width="stretch",
                )

            if create_project_submit:
                try:
                    project_id = create_project(
                        storyteller_id=storyteller_options[
                            selected_storyteller_label
                        ],
                        project_title=project_title,
                        project_description=project_description or None,
                        project_status=project_status,
                        created_by_relationship=(
                            created_by_relationship or None
                        ),
                    )

                    st.success(
                        f"Project created with ID {project_id}."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    st.divider()

    st.subheader("Existing Storytellers")

    storyteller_frame = dataframe_from_records(
        list_storytellers(),
        [
            "storyteller_id",
            "full_name",
            "preferred_name",
            "birth_year",
            "hometown",
            "biography_language",
            "created_at",
        ],
    )

    if storyteller_frame.empty:
        st.info("No storytellers have been created.")
    else:
        st.dataframe(
            storyteller_frame,
            width="stretch",
            hide_index=True,
        )

    st.subheader("Existing Projects")

    project_frame = dataframe_from_records(
        list_projects(),
        [
            "project_id",
            "project_title",
            "storyteller_name",
            "project_status",
            "created_by_relationship",
            "created_at",
        ],
    )

    if project_frame.empty:
        st.info("No projects have been created.")
    else:
        st.dataframe(
            project_frame,
            width="stretch",
            hide_index=True,
        )


with tabs[2]:
    st.header("Source Materials")

    if selected_project_id is None:
        st.warning("Create and select a project first.")
    else:
        st.write(
            f"Current project: **{selected_project['project_title']}**"
        )

        text_tab, file_tab = st.tabs(
            ["Written Memory", "Photo or Audio Upload"]
        )

        with text_tab:
            with st.form("text_material_form"):
                text_content = st.text_area(
                    "Written memory",
                    height=180,
                )

                text_description = st.text_input(
                    "Material description",
                )

                text_year_enabled = st.checkbox(
                    "Estimated year is available",
                    value=True,
                    key="text_year_enabled",
                )

                text_year = st.number_input(
                    "Estimated year",
                    min_value=1850,
                    max_value=2026,
                    value=1960,
                    step=1,
                    disabled=not text_year_enabled,
                    key="text_year",
                )

                text_location = st.text_input(
                    "Location",
                    key="text_location",
                )

                text_people = st.text_input(
                    "People mentioned",
                    key="text_people",
                )

                save_text_submit = st.form_submit_button(
                    "Save Written Memory",
                    width="stretch",
                )

            if save_text_submit:
                try:
                    material_id = add_text_material(
                        project_id=selected_project_id,
                        text_content=text_content,
                        material_description=text_description or None,
                        estimated_year=year_or_none(
                            text_year_enabled,
                            int(text_year),
                        ),
                        location=text_location or None,
                        people_description=text_people or None,
                    )

                    st.success(
                        f"Written memory saved with material ID "
                        f"{material_id}."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with file_tab:
            uploaded_file = st.file_uploader(
                "Upload a historical photo or voice recording",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                    "mp3",
                    "wav",
                    "m4a",
                    "aac",
                    "ogg",
                ],
            )

            with st.form("file_material_metadata_form"):
                file_description = st.text_input(
                    "Material description",
                    key="file_description",
                )

                file_year_enabled = st.checkbox(
                    "Estimated year is available",
                    value=False,
                    key="file_year_enabled",
                )

                file_year = st.number_input(
                    "Estimated year",
                    min_value=1850,
                    max_value=2026,
                    value=1960,
                    step=1,
                    disabled=not file_year_enabled,
                    key="file_year",
                )

                file_location = st.text_input(
                    "Location",
                    key="file_location",
                )

                file_people = st.text_input(
                    "People in the material",
                    key="file_people",
                )

                save_file_submit = st.form_submit_button(
                    "Save Uploaded Material",
                    width="stretch",
                )

            if save_file_submit:
                if uploaded_file is None:
                    st.error("Select a file before saving.")
                else:
                    try:
                        metadata = save_uploaded_file(
                            file_source=uploaded_file,
                            original_filename=uploaded_file.name,
                            project_id=selected_project_id,
                            mime_type=uploaded_file.type,
                        )

                        material_id = add_file_material(
                            project_id=selected_project_id,
                            material_type=metadata["material_type"],
                            original_filename=metadata[
                                "original_filename"
                            ],
                            stored_filename=metadata[
                                "stored_filename"
                            ],
                            stored_path=metadata["stored_path"],
                            material_description=(
                                file_description or None
                            ),
                            estimated_year=year_or_none(
                                file_year_enabled,
                                int(file_year),
                            ),
                            location=file_location or None,
                            people_description=file_people or None,
                            mime_type=metadata["mime_type"],
                            file_size_bytes=metadata[
                                "file_size_bytes"
                            ],
                        )

                        st.success(
                            f"{metadata['material_type']} saved with "
                            f"material ID {material_id}."
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        st.divider()

        materials = list_materials(selected_project_id)

        st.subheader("Saved Materials")

        material_frame = dataframe_from_records(
            materials,
            [
                "material_id",
                "material_type",
                "original_filename",
                "material_description",
                "estimated_year",
                "location",
                "people_description",
                "file_size_bytes",
                "uploaded_at",
            ],
        )

        if material_frame.empty:
            st.info("No materials have been saved.")
        else:
            st.dataframe(
                material_frame,
                width="stretch",
                hide_index=True,
            )


with tabs[3]:
    st.header("Life Timeline")

    if selected_project_id is None:
        st.warning("Create and select a project first.")
    else:
        materials = list_materials(selected_project_id)

        no_material_label = (
            "不关联原始素材 / No linked source material"
        )
        material_options: dict[str, Optional[int]] = {
            no_material_label: None
        }

        for material in materials:
            description = (
                material.get("material_description")
                or material.get("original_filename")
                or material.get("text_content")
                or "Material"
            )

            description = str(description)[:60]

            label = (
                f"#{material['material_id']} · "
                f"{material['material_type']} · "
                f"{description}"
            )

            material_options[label] = int(material["material_id"])

        st.subheader(
            "从回忆中提取人生事件 / Extract a Life Event from a Memory"
        )

        st.write(
            "粘贴一段回忆文字。系统会生成可审核的结构化草稿；"
            "只有在你逐项确认后，内容才会保存。 "
            "Paste one memory passage. The prototype creates a reviewable "
            "draft and saves nothing until you confirm the fields."
        )

        provider_infos = list_memory_extraction_providers()
        provider_by_label = {
            (
                f"{provider.display_name_zh} / "
                f"{provider.display_name_en}"
            ): provider
            for provider in provider_infos
        }

        default_provider_label = next(
            label
            for label, provider in provider_by_label.items()
            if provider.provider_id == RULE_BASED_PROVIDER_ID
        )

        def clear_memory_extraction_draft_on_provider_change() -> None:
            """Clear stale review state when the extraction provider changes."""
            st.session_state.pop("memory_extraction_draft", None)
            st.session_state.pop("memory_extraction_linked_material", None)

        selected_provider_label = st.selectbox(
            "提取模式 / Extraction mode",
            options=list(provider_by_label.keys()),
            index=list(provider_by_label.keys()).index(
                default_provider_label
            ),
            key="memory_extraction_provider_label",
            on_change=clear_memory_extraction_draft_on_provider_change,
        )
        selected_provider = provider_by_label[selected_provider_label]

        if selected_provider.available:
            st.caption(
                f"{selected_provider.description_zh} "
                f"{selected_provider.description_en}"
            )
        else:
            st.info(
                f"{selected_provider.description_zh} "
                f"{selected_provider.description_en}"
            )

        extraction_source_text = st.text_area(
            "回忆文字 / Memory passage",
            height=170,
            placeholder=(
                "示例：大约在1976年，我和母亲从广州搬到深圳。 "
                "Example: In the summer of 1958, I walked to primary school "
                "with my older brother..."
            ),
            key="memory_extraction_source_text",
        )

        extraction_material_label = st.selectbox(
            "可选关联素材 / Optional linked source material",
            list(material_options.keys()),
            key="memory_extraction_material_label",
        )

        extract_memory_submit = st.button(
            "提取可审核字段 / Extract Reviewable Fields",
            width="stretch",
            key="extract_memory_submit",
            disabled=not selected_provider.available,
        )

        if extract_memory_submit:
            try:
                extraction_result = extract_memory_with_provider(
                    extraction_source_text,
                    provider_id=selected_provider.provider_id,
                )
                extraction_draft_payload = extraction_result.to_dict()
                extraction_draft_payload["provider_id"] = (
                    selected_provider.provider_id
                )
                extraction_draft_payload["provider_name_en"] = (
                    selected_provider.display_name_en
                )
                extraction_draft_payload["provider_name_zh"] = (
                    selected_provider.display_name_zh
                )
                extraction_draft_payload["provider_sends_data_external"] = (
                    selected_provider.sends_data_external
                )
                st.session_state["memory_extraction_draft"] = (
                    extraction_draft_payload
                )
                st.session_state["memory_extraction_linked_material"] = (
                    extraction_material_label
                )
            except Exception as exc:
                st.error(str(exc))

        extraction_draft = st.session_state.get(
            "memory_extraction_draft"
        )

        # Defensive check: never show a draft produced by a different provider.
        if (
            extraction_draft
            and extraction_draft.get("provider_id")
            != selected_provider.provider_id
        ):
            st.session_state.pop("memory_extraction_draft", None)
            st.session_state.pop("memory_extraction_linked_material", None)
            extraction_draft = None

        if extraction_draft:
            draft_language = extraction_draft.get(
                "detected_language",
                "en",
            )
            is_chinese_draft = draft_language == "zh"

            extraction_ui = {
                "review_warning": (
                    "结构化提取结果必须由人工确认。保存前请逐项检查并修改。"
                    if is_chinese_draft
                    else "AI-assisted extraction requires human confirmation. "
                    "Review and edit every field before saving."
                ),
                "title_confidence": (
                    "标题置信度" if is_chinese_draft else "Title confidence"
                ),
                "year_confidence": (
                    "年份置信度" if is_chinese_draft else "Year confidence"
                ),
                "location_confidence": (
                    "地点置信度" if is_chinese_draft else "Location confidence"
                ),
                "people_confidence": (
                    "人物置信度" if is_chinese_draft else "People confidence"
                ),
                "tone_confidence": (
                    "情绪置信度" if is_chinese_draft else "Tone confidence"
                ),
                "review_note": (
                    "审核提示" if is_chinese_draft else "Review note"
                ),
                "event_title": (
                    "确认后的事件标题"
                    if is_chinese_draft
                    else "Reviewed event title"
                ),
                "event_description": (
                    "确认后的事件描述"
                    if is_chinese_draft
                    else "Reviewed event description"
                ),
                "start_year_available": (
                    "可以确认开始年份"
                    if is_chinese_draft
                    else "Reviewed start year is available"
                ),
                "start_year": (
                    "确认后的开始年份"
                    if is_chinese_draft
                    else "Reviewed start year"
                ),
                "end_year_available": (
                    "可以确认结束年份"
                    if is_chinese_draft
                    else "Reviewed end year is available"
                ),
                "end_year": (
                    "确认后的结束年份"
                    if is_chinese_draft
                    else "Reviewed end year"
                ),
                "date_certainty": (
                    "日期确定程度"
                    if is_chinese_draft
                    else "Reviewed date certainty"
                ),
                "location": (
                    "确认后的事件地点"
                    if is_chinese_draft
                    else "Reviewed event location"
                ),
                "people": (
                    "确认后的相关人物"
                    if is_chinese_draft
                    else "Reviewed people involved"
                ),
                "emotional_tone": (
                    "确认后的情绪基调"
                    if is_chinese_draft
                    else "Reviewed emotional tone"
                ),
                "display_order": (
                    "时间线显示顺序"
                    if is_chinese_draft
                    else "Reviewed timeline display order"
                ),
                "source_material": (
                    "关联的原始素材"
                    if is_chinese_draft
                    else "Reviewed linked source material"
                ),
                "save": (
                    "确认并保存人生事件"
                    if is_chinese_draft
                    else "Confirm and Save Life Event"
                ),
                "discard": (
                    "放弃本次提取草稿"
                    if is_chinese_draft
                    else "Discard Extracted Draft"
                ),
                "success": (
                    "已创建审核后的人生事件，事件编号为"
                    if is_chinese_draft
                    else "Reviewed life event created with ID"
                ),
            }

            st.warning(extraction_ui["review_warning"])

            provider_name = (
                extraction_draft.get("provider_name_zh")
                if is_chinese_draft
                else extraction_draft.get("provider_name_en")
            )
            if provider_name:
                if is_chinese_draft:
                    st.caption(f"本次提取模式：{provider_name}")
                else:
                    st.caption(f"Extraction mode: {provider_name}")

            confidence = extraction_draft.get("field_confidence", {})

            def format_confidence(value: object) -> str:
                normalized_value = str(value or "unknown").lower()
                if is_chinese_draft:
                    return {
                        "high": "高",
                        "medium": "中",
                        "low": "低",
                        "unknown": "未知",
                    }.get(normalized_value, normalized_value)
                return normalized_value.title()

            confidence_cols = st.columns(5)
            confidence_cols[0].metric(
                extraction_ui["title_confidence"],
                format_confidence(confidence.get("event_title")),
            )
            confidence_cols[1].metric(
                extraction_ui["year_confidence"],
                format_confidence(confidence.get("year")),
            )
            confidence_cols[2].metric(
                extraction_ui["location_confidence"],
                format_confidence(confidence.get("location")),
            )
            confidence_cols[3].metric(
                extraction_ui["people_confidence"],
                format_confidence(confidence.get("people_involved")),
            )
            confidence_cols[4].metric(
                extraction_ui["tone_confidence"],
                format_confidence(confidence.get("emotional_tone")),
            )

            for warning in extraction_draft.get("warnings", []):
                st.caption(f"{extraction_ui['review_note']}: {warning}")

            draft_start_year = extraction_draft.get("start_year")
            draft_end_year = extraction_draft.get("end_year")
            draft_date_certainty = extraction_draft.get(
                "date_certainty",
                "Estimated",
            )
            certainty_options = ["Confirmed", "Estimated", "Unknown"]
            certainty_index = (
                certainty_options.index(draft_date_certainty)
                if draft_date_certainty in certainty_options
                else 1
            )

            saved_material_label = st.session_state.get(
                "memory_extraction_linked_material",
                no_material_label,
            )
            if saved_material_label == "No linked source material":
                saved_material_label = no_material_label
            material_labels = list(material_options.keys())
            material_index = (
                material_labels.index(saved_material_label)
                if saved_material_label in material_labels
                else 0
            )

            with st.form("memory_extraction_review_form"):
                reviewed_event_title = st.text_input(
                    extraction_ui["event_title"],
                    value=extraction_draft.get("event_title", ""),
                )

                reviewed_event_description = st.text_area(
                    extraction_ui["event_description"],
                    value=extraction_draft.get(
                        "event_description",
                        extraction_draft.get("source_text", ""),
                    ),
                    height=170,
                )

                reviewed_start_year_enabled = st.checkbox(
                    extraction_ui["start_year_available"],
                    value=draft_start_year is not None,
                    key="reviewed_start_year_enabled",
                )

                reviewed_start_year = st.number_input(
                    extraction_ui["start_year"],
                    min_value=1850,
                    max_value=2026,
                    value=int(draft_start_year or 1960),
                    step=1,
                    disabled=not reviewed_start_year_enabled,
                )

                reviewed_end_year_enabled = st.checkbox(
                    extraction_ui["end_year_available"],
                    value=draft_end_year is not None,
                    key="reviewed_end_year_enabled",
                )

                reviewed_end_year = st.number_input(
                    extraction_ui["end_year"],
                    min_value=1850,
                    max_value=2026,
                    value=int(draft_end_year or reviewed_start_year),
                    step=1,
                    disabled=not reviewed_end_year_enabled,
                )

                reviewed_date_certainty = st.selectbox(
                    extraction_ui["date_certainty"],
                    certainty_options,
                    index=certainty_index,
                    format_func=(
                        lambda value: {
                            "Confirmed": "已确认",
                            "Estimated": "估计",
                            "Unknown": "未知",
                        }[value]
                        if is_chinese_draft
                        else value
                    ),
                )

                reviewed_location = st.text_input(
                    extraction_ui["location"],
                    value=extraction_draft.get("location") or "",
                )

                reviewed_people = st.text_input(
                    extraction_ui["people"],
                    value=extraction_draft.get("people_involved") or "",
                )

                reviewed_emotional_tone = st.text_input(
                    extraction_ui["emotional_tone"],
                    value=extraction_draft.get("emotional_tone") or "",
                )

                reviewed_display_order = st.number_input(
                    extraction_ui["display_order"],
                    min_value=0,
                    value=1,
                    step=1,
                )

                reviewed_material_label = st.selectbox(
                    extraction_ui["source_material"],
                    material_labels,
                    index=material_index,
                )

                confirm_extraction_submit = st.form_submit_button(
                    extraction_ui["save"],
                    width="stretch",
                )

            if confirm_extraction_submit:
                try:
                    event_id = create_life_event(
                        project_id=selected_project_id,
                        event_title=reviewed_event_title,
                        event_description=reviewed_event_description,
                        start_year=year_or_none(
                            reviewed_start_year_enabled,
                            int(reviewed_start_year),
                        ),
                        end_year=year_or_none(
                            reviewed_end_year_enabled,
                            int(reviewed_end_year),
                        ),
                        date_certainty=reviewed_date_certainty,
                        location=reviewed_location or None,
                        people_involved=reviewed_people or None,
                        emotional_tone=(
                            reviewed_emotional_tone or None
                        ),
                        display_order=int(reviewed_display_order),
                        source_material_id=material_options[
                            reviewed_material_label
                        ],
                    )

                    st.session_state.pop(
                        "memory_extraction_draft",
                        None,
                    )
                    st.session_state.pop(
                        "memory_extraction_linked_material",
                        None,
                    )
                    if is_chinese_draft:
                        st.success(
                            f"{extraction_ui['success']} {event_id}。"
                        )
                    else:
                        st.success(
                            f"{extraction_ui['success']} {event_id}."
                        )
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

            if st.button(
                extraction_ui["discard"],
                key="discard_memory_extraction_draft",
            ):
                st.session_state.pop(
                    "memory_extraction_draft",
                    None,
                )
                st.session_state.pop(
                    "memory_extraction_linked_material",
                    None,
                )
                st.rerun()

        st.divider()
        st.subheader("Manual Life Event Entry")

        with st.form("life_event_form"):
            event_title = st.text_input("Event title")

            event_description = st.text_area(
                "Event description",
                height=150,
            )

            start_year_enabled = st.checkbox(
                "Start year is available",
                value=True,
                key="event_start_year_enabled",
            )

            start_year = st.number_input(
                "Start year",
                min_value=1850,
                max_value=2026,
                value=1960,
                step=1,
                disabled=not start_year_enabled,
            )

            end_year_enabled = st.checkbox(
                "End year is available",
                value=False,
            )

            end_year = st.number_input(
                "End year",
                min_value=1850,
                max_value=2026,
                value=1960,
                step=1,
                disabled=not end_year_enabled,
            )

            date_certainty = st.selectbox(
                "Date certainty",
                ["Confirmed", "Estimated", "Unknown"],
            )

            event_location = st.text_input("Event location")
            people_involved = st.text_input("People involved")
            emotional_tone = st.text_input(
                "Emotional tone",
                placeholder="Warm, difficult, hopeful, reflective...",
            )

            display_order = st.number_input(
                "Timeline display order",
                min_value=0,
                value=1,
                step=1,
            )

            linked_material_label = st.selectbox(
                "Linked source material",
                list(material_options.keys()),
            )

            save_event_submit = st.form_submit_button(
                "Add Life Event",
                width="stretch",
            )

        if save_event_submit:
            try:
                event_id = create_life_event(
                    project_id=selected_project_id,
                    event_title=event_title,
                    event_description=event_description,
                    start_year=year_or_none(
                        start_year_enabled,
                        int(start_year),
                    ),
                    end_year=year_or_none(
                        end_year_enabled,
                        int(end_year),
                    ),
                    date_certainty=date_certainty,
                    location=event_location or None,
                    people_involved=people_involved or None,
                    emotional_tone=emotional_tone or None,
                    display_order=int(display_order),
                    source_material_id=material_options[
                        linked_material_label
                    ],
                )

                st.success(
                    f"Life event created with ID {event_id}."
                )
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

        st.divider()

        events = list_life_events(selected_project_id)

        st.subheader("Timeline Records")

        event_frame = dataframe_from_records(
            events,
            [
                "event_id",
                "display_order",
                "event_title",
                "start_year",
                "end_year",
                "date_certainty",
                "location",
                "people_involved",
                "emotional_tone",
                "source_material_id",
            ],
        )

        if event_frame.empty:
            st.info("No life events have been created.")
        else:
            st.dataframe(
                event_frame,
                width="stretch",
                hide_index=True,
            )

            for event in events:
                with st.expander(
                    (
                        f"#{event['event_id']} · "
                        f"{event['event_title']}"
                    )
                ):
                    st.write(event["event_description"])


with tabs[4]:
    st.header("Generate Autobiography and Scene Content")

    if selected_project_id is None:
        st.warning("Create and select a project first.")
    else:
        events = list_life_events(selected_project_id)

        if not events:
            st.warning(
                "Add at least one life event before generating content."
            )
        else:
            storyteller = get_storyteller(
                int(selected_project["storyteller_id"])
            )

            st.subheader("Full Biography Draft")

            if st.button(
                "Generate and Save Biography",
                width="stretch",
            ):
                try:
                    biography = generate_biography(
                        storyteller=storyteller or {},
                        project=selected_project,
                        life_events=events,
                    )

                    content_id = save_generated_content(
                        project_id=selected_project_id,
                        content_type=biography["content_type"],
                        content_title=biography["content_title"],
                        content_text=biography["content_text"],
                        generation_method=biography[
                            "generation_method"
                        ],
                        review_status=biography["review_status"],
                    )

                    st.success(
                        f"Biography saved with content ID {content_id}."
                    )
                    st.session_state[
                        "latest_biography"
                    ] = biography["content_text"]
                except Exception as exc:
                    st.error(str(exc))

            latest_biography = st.session_state.get(
                "latest_biography"
            )

            if latest_biography:
                st.markdown(latest_biography)

            st.divider()

            st.subheader("Generate Content for One Event")

            event_map = {
                (
                    f"#{event['event_id']} · "
                    f"{event['event_title']}"
                ): event
                for event in events
            }

            selected_event_label = st.selectbox(
                "Life event",
                list(event_map.keys()),
            )

            selected_event = event_map[selected_event_label]

            if st.button(
                "Generate and Save Event Content Bundle",
                width="stretch",
            ):
                try:
                    storyteller_name = (
                        (storyteller or {}).get("preferred_name")
                        or (storyteller or {}).get("full_name")
                        or "The storyteller"
                    )

                    bundle = generate_event_content_bundle(
                        storyteller_name=storyteller_name,
                        event=selected_event,
                    )

                    saved_ids = []

                    for item in bundle:
                        saved_ids.append(
                            save_generated_content(
                                project_id=selected_project_id,
                                life_event_id=int(
                                    selected_event["event_id"]
                                ),
                                content_type=item["content_type"],
                                content_title=item["content_title"],
                                content_text=item["content_text"],
                                generation_method=item[
                                    "generation_method"
                                ],
                                review_status=item["review_status"],
                            )
                        )

                    st.session_state["latest_bundle"] = bundle

                    st.success(
                        "Generated and saved Chapter, Scene Description, "
                        f"Storyboard and Video Prompt. IDs: {saved_ids}"
                    )
                except Exception as exc:
                    st.error(str(exc))

            latest_bundle = st.session_state.get("latest_bundle", [])

            for item in latest_bundle:
                with st.expander(
                    f"{item['content_type']} · {item['content_title']}",
                    expanded=item["content_type"] == "Chapter",
                ):
                    st.markdown(item["content_text"])


with tabs[5]:
    st.header("Human Review")

    if selected_project_id is None:
        st.warning("Create and select a project first.")
    else:
        generated_contents = list_generated_contents(
            selected_project_id
        )

        if not generated_contents:
            st.info("No generated content is available for review.")
        else:
            content_options = {
                (
                    f"#{item['content_id']} · "
                    f"{item['content_type']} · "
                    f"{item['content_title']} · "
                    f"{item['review_status']}"
                ): item
                for item in generated_contents
            }

            selected_content_label = st.selectbox(
                "Generated content",
                list(content_options.keys()),
            )

            selected_content = content_options[
                selected_content_label
            ]

            st.subheader(selected_content["content_title"])
            st.caption(
                (
                    f"Type: {selected_content['content_type']} | "
                    f"Method: {selected_content['generation_method']} | "
                    f"Current status: {selected_content['review_status']}"
                )
            )

            st.markdown(selected_content["content_text"])

            st.divider()

            with st.form("review_content_form"):
                new_status = st.selectbox(
                    "New review status",
                    ["Draft", "Reviewed", "Approved", "Rejected"],
                )

                reviewed_by = st.text_input(
                    "Reviewed by",
                    placeholder="Demo reviewer name or role",
                )

                review_comment = st.text_area(
                    "Review comment",
                )

                update_review_submit = st.form_submit_button(
                    "Update Review Status",
                    width="stretch",
                )

            if update_review_submit:
                try:
                    update_content_review_status(
                        content_id=int(
                            selected_content["content_id"]
                        ),
                        new_status=new_status,
                        review_comment=review_comment or None,
                        reviewed_by=reviewed_by or None,
                    )

                    st.success("Review status updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

            st.subheader("Generated Content Register")

            content_frame = dataframe_from_records(
                generated_contents,
                [
                    "content_id",
                    "content_type",
                    "content_title",
                    "generation_method",
                    "review_status",
                    "life_event_id",
                    "created_at",
                    "updated_at",
                ],
            )

            st.dataframe(
                content_frame,
                width="stretch",
                hide_index=True,
            )


st.divider()

st.caption(
    "Yanxin AI Oral Autobiography Platform · "
    "Streamlit · SQLite · Privacy-safe local prototype"
)
