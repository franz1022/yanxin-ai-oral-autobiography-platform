PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS storytellers (
    storyteller_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    preferred_name TEXT,
    birth_year INTEGER,
    hometown TEXT,
    biography_language TEXT NOT NULL DEFAULT 'Chinese',
    profile_notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS autobiography_projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    storyteller_id INTEGER NOT NULL,
    project_title TEXT NOT NULL,
    project_description TEXT,
    project_status TEXT NOT NULL DEFAULT 'Draft'
        CHECK (project_status IN ('Draft','In Progress','Under Review','Completed','Archived')),
    created_by_relationship TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (storyteller_id)
        REFERENCES storytellers(storyteller_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS source_materials (
    material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    material_type TEXT NOT NULL
        CHECK (material_type IN ('Text','Audio','Photo')),
    original_filename TEXT,
    stored_filename TEXT,
    stored_path TEXT,
    text_content TEXT,
    material_description TEXT,
    estimated_year INTEGER,
    location TEXT,
    people_description TEXT,
    mime_type TEXT,
    file_size_bytes INTEGER,
    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id)
        REFERENCES autobiography_projects(project_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS life_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    source_material_id INTEGER,
    event_title TEXT NOT NULL,
    start_year INTEGER,
    end_year INTEGER,
    date_certainty TEXT NOT NULL DEFAULT 'Estimated'
        CHECK (date_certainty IN ('Confirmed','Estimated','Unknown')),
    location TEXT,
    people_involved TEXT,
    event_description TEXT NOT NULL,
    emotional_tone TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id)
        REFERENCES autobiography_projects(project_id)
        ON DELETE CASCADE,
    FOREIGN KEY (source_material_id)
        REFERENCES source_materials(material_id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS generated_contents (
    content_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    life_event_id INTEGER,
    content_type TEXT NOT NULL
        CHECK (content_type IN ('Biography','Chapter','Scene Description','Storyboard','Video Prompt')),
    content_title TEXT NOT NULL,
    content_text TEXT NOT NULL,
    generation_method TEXT NOT NULL DEFAULT 'Template Prototype',
    review_status TEXT NOT NULL DEFAULT 'Draft'
        CHECK (review_status IN ('Draft','Reviewed','Approved','Rejected')),
    reviewer_notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id)
        REFERENCES autobiography_projects(project_id)
        ON DELETE CASCADE,
    FOREIGN KEY (life_event_id)
        REFERENCES life_events(event_id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS content_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    review_comment TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id)
        REFERENCES generated_contents(content_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_projects_storyteller
ON autobiography_projects(storyteller_id);

CREATE INDEX IF NOT EXISTS idx_materials_project
ON source_materials(project_id);

CREATE INDEX IF NOT EXISTS idx_events_project
ON life_events(project_id);

CREATE INDEX IF NOT EXISTS idx_events_order
ON life_events(project_id, display_order);

CREATE INDEX IF NOT EXISTS idx_generated_project
ON generated_contents(project_id);

CREATE INDEX IF NOT EXISTS idx_generated_event
ON generated_contents(life_event_id);

CREATE INDEX IF NOT EXISTS idx_reviews_content
ON content_reviews(content_id);
