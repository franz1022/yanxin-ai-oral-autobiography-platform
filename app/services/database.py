from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "data" / "yanxin_autobiography.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def _dict_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


@contextmanager
def get_connection(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> Iterator[sqlite3.Connection]:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database(
    db_path: Path | str = DEFAULT_DB_PATH,
    schema_path: Path | str = SCHEMA_PATH,
) -> Path:
    schema_file = Path(schema_path)

    if not schema_file.exists():
        raise FileNotFoundError(
            f"Database schema was not found: {schema_file}"
        )

    schema_sql = schema_file.read_text(encoding="utf-8")

    with get_connection(db_path) as connection:
        connection.executescript(schema_sql)

    return Path(db_path)


def create_storyteller(
    full_name: str,
    preferred_name: Optional[str] = None,
    birth_year: Optional[int] = None,
    hometown: Optional[str] = None,
    biography_language: str = "Chinese",
    profile_notes: Optional[str] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    if not full_name.strip():
        raise ValueError("full_name cannot be empty.")

    sql = '''
        INSERT INTO storytellers (
            full_name,
            preferred_name,
            birth_year,
            hometown,
            biography_language,
            profile_notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
    '''

    values = (
        full_name.strip(),
        preferred_name.strip() if preferred_name else None,
        birth_year,
        hometown.strip() if hometown else None,
        biography_language.strip() or "Chinese",
        profile_notes.strip() if profile_notes else None,
    )

    with get_connection(db_path) as connection:
        cursor = connection.execute(sql, values)
        return int(cursor.lastrowid)


def list_storytellers(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    sql = '''
        SELECT *
        FROM storytellers
        ORDER BY created_at DESC, storyteller_id DESC
    '''

    with get_connection(db_path) as connection:
        rows = connection.execute(sql).fetchall()

    return [_dict_from_row(row) for row in rows]


def get_storyteller(
    storyteller_id: int,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> Optional[dict[str, Any]]:
    sql = '''
        SELECT *
        FROM storytellers
        WHERE storyteller_id = ?
    '''

    with get_connection(db_path) as connection:
        row = connection.execute(sql, (storyteller_id,)).fetchone()

    return _dict_from_row(row) if row else None


def create_project(
    storyteller_id: int,
    project_title: str,
    project_description: Optional[str] = None,
    project_status: str = "Draft",
    created_by_relationship: Optional[str] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    if not project_title.strip():
        raise ValueError("project_title cannot be empty.")

    sql = '''
        INSERT INTO autobiography_projects (
            storyteller_id,
            project_title,
            project_description,
            project_status,
            created_by_relationship
        )
        VALUES (?, ?, ?, ?, ?)
    '''

    values = (
        storyteller_id,
        project_title.strip(),
        project_description.strip() if project_description else None,
        project_status,
        (
            created_by_relationship.strip()
            if created_by_relationship
            else None
        ),
    )

    with get_connection(db_path) as connection:
        cursor = connection.execute(sql, values)
        return int(cursor.lastrowid)


def list_projects(
    storyteller_id: Optional[int] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    if storyteller_id is None:
        sql = '''
            SELECT
                p.*,
                s.full_name AS storyteller_name
            FROM autobiography_projects AS p
            JOIN storytellers AS s
              ON s.storyteller_id = p.storyteller_id
            ORDER BY p.created_at DESC, p.project_id DESC
        '''
        params: tuple[Any, ...] = ()
    else:
        sql = '''
            SELECT
                p.*,
                s.full_name AS storyteller_name
            FROM autobiography_projects AS p
            JOIN storytellers AS s
              ON s.storyteller_id = p.storyteller_id
            WHERE p.storyteller_id = ?
            ORDER BY p.created_at DESC, p.project_id DESC
        '''
        params = (storyteller_id,)

    with get_connection(db_path) as connection:
        rows = connection.execute(sql, params).fetchall()

    return [_dict_from_row(row) for row in rows]


def add_text_material(
    project_id: int,
    text_content: str,
    material_description: Optional[str] = None,
    estimated_year: Optional[int] = None,
    location: Optional[str] = None,
    people_description: Optional[str] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    if not text_content.strip():
        raise ValueError("text_content cannot be empty.")

    sql = '''
        INSERT INTO source_materials (
            project_id,
            material_type,
            text_content,
            material_description,
            estimated_year,
            location,
            people_description
        )
        VALUES (?, 'Text', ?, ?, ?, ?, ?)
    '''

    values = (
        project_id,
        text_content.strip(),
        material_description.strip() if material_description else None,
        estimated_year,
        location.strip() if location else None,
        people_description.strip() if people_description else None,
    )

    with get_connection(db_path) as connection:
        cursor = connection.execute(sql, values)
        return int(cursor.lastrowid)


def add_file_material(
    project_id: int,
    material_type: str,
    original_filename: str,
    stored_filename: str,
    stored_path: str,
    material_description: Optional[str] = None,
    estimated_year: Optional[int] = None,
    location: Optional[str] = None,
    people_description: Optional[str] = None,
    mime_type: Optional[str] = None,
    file_size_bytes: Optional[int] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    if material_type not in {"Audio", "Photo"}:
        raise ValueError(
            "material_type must be either 'Audio' or 'Photo'."
        )

    sql = '''
        INSERT INTO source_materials (
            project_id,
            material_type,
            original_filename,
            stored_filename,
            stored_path,
            material_description,
            estimated_year,
            location,
            people_description,
            mime_type,
            file_size_bytes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    values = (
        project_id,
        material_type,
        original_filename,
        stored_filename,
        stored_path,
        material_description.strip() if material_description else None,
        estimated_year,
        location.strip() if location else None,
        people_description.strip() if people_description else None,
        mime_type,
        file_size_bytes,
    )

    with get_connection(db_path) as connection:
        cursor = connection.execute(sql, values)
        return int(cursor.lastrowid)


def list_materials(
    project_id: int,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    sql = '''
        SELECT *
        FROM source_materials
        WHERE project_id = ?
        ORDER BY uploaded_at DESC, material_id DESC
    '''

    with get_connection(db_path) as connection:
        rows = connection.execute(sql, (project_id,)).fetchall()

    return [_dict_from_row(row) for row in rows]


def create_life_event(
    project_id: int,
    event_title: str,
    event_description: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    date_certainty: str = "Estimated",
    location: Optional[str] = None,
    people_involved: Optional[str] = None,
    emotional_tone: Optional[str] = None,
    display_order: int = 0,
    source_material_id: Optional[int] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    if not event_title.strip():
        raise ValueError("event_title cannot be empty.")

    if not event_description.strip():
        raise ValueError("event_description cannot be empty.")

    sql = '''
        INSERT INTO life_events (
            project_id,
            source_material_id,
            event_title,
            start_year,
            end_year,
            date_certainty,
            location,
            people_involved,
            event_description,
            emotional_tone,
            display_order
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    values = (
        project_id,
        source_material_id,
        event_title.strip(),
        start_year,
        end_year,
        date_certainty,
        location.strip() if location else None,
        people_involved.strip() if people_involved else None,
        event_description.strip(),
        emotional_tone.strip() if emotional_tone else None,
        display_order,
    )

    with get_connection(db_path) as connection:
        cursor = connection.execute(sql, values)
        return int(cursor.lastrowid)


def list_life_events(
    project_id: int,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    sql = '''
        SELECT *
        FROM life_events
        WHERE project_id = ?
        ORDER BY
            display_order ASC,
            CASE WHEN start_year IS NULL THEN 1 ELSE 0 END,
            start_year ASC,
            event_id ASC
    '''

    with get_connection(db_path) as connection:
        rows = connection.execute(sql, (project_id,)).fetchall()

    return [_dict_from_row(row) for row in rows]


def save_generated_content(
    project_id: int,
    content_type: str,
    content_title: str,
    content_text: str,
    life_event_id: Optional[int] = None,
    generation_method: str = "Template Prototype",
    review_status: str = "Draft",
    reviewer_notes: Optional[str] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    if not content_title.strip():
        raise ValueError("content_title cannot be empty.")

    if not content_text.strip():
        raise ValueError("content_text cannot be empty.")

    sql = '''
        INSERT INTO generated_contents (
            project_id,
            life_event_id,
            content_type,
            content_title,
            content_text,
            generation_method,
            review_status,
            reviewer_notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''

    values = (
        project_id,
        life_event_id,
        content_type,
        content_title.strip(),
        content_text.strip(),
        generation_method,
        review_status,
        reviewer_notes.strip() if reviewer_notes else None,
    )

    with get_connection(db_path) as connection:
        cursor = connection.execute(sql, values)
        return int(cursor.lastrowid)


def list_generated_contents(
    project_id: int,
    content_type: Optional[str] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    if content_type is None:
        sql = '''
            SELECT *
            FROM generated_contents
            WHERE project_id = ?
            ORDER BY created_at DESC, content_id DESC
        '''
        params: tuple[Any, ...] = (project_id,)
    else:
        sql = '''
            SELECT *
            FROM generated_contents
            WHERE project_id = ?
              AND content_type = ?
            ORDER BY created_at DESC, content_id DESC
        '''
        params = (project_id, content_type)

    with get_connection(db_path) as connection:
        rows = connection.execute(sql, params).fetchall()

    return [_dict_from_row(row) for row in rows]


def update_content_review_status(
    content_id: int,
    new_status: str,
    review_comment: Optional[str] = None,
    reviewed_by: Optional[str] = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> None:
    allowed_statuses = {"Draft", "Reviewed", "Approved", "Rejected"}

    if new_status not in allowed_statuses:
        raise ValueError(
            f"new_status must be one of: {sorted(allowed_statuses)}"
        )

    with get_connection(db_path) as connection:
        row = connection.execute(
            '''
            SELECT review_status
            FROM generated_contents
            WHERE content_id = ?
            ''',
            (content_id,),
        ).fetchone()

        if row is None:
            raise ValueError(
                f"Generated content ID {content_id} does not exist."
            )

        previous_status = row["review_status"]

        connection.execute(
            '''
            UPDATE generated_contents
            SET
                review_status = ?,
                reviewer_notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE content_id = ?
            ''',
            (
                new_status,
                review_comment.strip() if review_comment else None,
                content_id,
            ),
        )

        connection.execute(
            '''
            INSERT INTO content_reviews (
                content_id,
                previous_status,
                new_status,
                review_comment,
                reviewed_by
            )
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                content_id,
                previous_status,
                new_status,
                review_comment.strip() if review_comment else None,
                reviewed_by.strip() if reviewed_by else None,
            ),
        )


def get_project_summary(
    project_id: int,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    sql = '''
        SELECT
            p.project_id,
            p.project_title,
            p.project_status,
            s.storyteller_id,
            s.full_name AS storyteller_name,
            (
                SELECT COUNT(*)
                FROM source_materials AS m
                WHERE m.project_id = p.project_id
            ) AS material_count,
            (
                SELECT COUNT(*)
                FROM life_events AS e
                WHERE e.project_id = p.project_id
            ) AS event_count,
            (
                SELECT COUNT(*)
                FROM generated_contents AS g
                WHERE g.project_id = p.project_id
            ) AS generated_content_count
        FROM autobiography_projects AS p
        JOIN storytellers AS s
          ON s.storyteller_id = p.storyteller_id
        WHERE p.project_id = ?
    '''

    with get_connection(db_path) as connection:
        row = connection.execute(sql, (project_id,)).fetchone()

    if row is None:
        raise ValueError(f"Project ID {project_id} does not exist.")

    return _dict_from_row(row)
