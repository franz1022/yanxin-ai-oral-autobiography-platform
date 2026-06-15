from pathlib import Path
import sqlite3

base = Path.cwd()

docs = {
    "docs/product_requirements.md": """# Product Requirements Document

## Project Name
Yanxin AI Oral Autobiography Platform

## Background
The platform helps users preserve personal and family memories by organising voice recordings, written narratives and historical photographs into structured life timelines, autobiography drafts and reconstructed scene descriptions.

This public repository is a privacy-safe portfolio prototype inspired by a 2023 university team project. It does not contain private user materials or the original proprietary codebase.

## Target Users
- elderly people recording life stories;
- family members preserving parents' or grandparents' memories;
- oral-history teams and community organisations;
- biography editors and reviewers.

## Product Goals
1. Collect voice, text and photograph materials.
2. Organise fragmented memories into a life timeline.
3. Generate editable autobiography drafts.
4. Produce scene descriptions and storyboard ideas.
5. Keep users in control of factual review.
6. Protect personal information.

## Version 1 Scope
- storyteller profile creation;
- autobiography project creation;
- text input;
- audio and photo upload;
- material metadata management;
- life-event timeline;
- template-based biography generation;
- scene and storyboard description generation;
- review status;
- SQLite storage;
- Streamlit interface.

## Conceptual AI Functions
- speech-to-text;
- text cleaning and segmentation;
- entity and event extraction;
- biography drafting;
- historical-scene description;
- storyboard and video-prompt creation.

## Out of Scope
- production-grade video generation;
- automatic historical fact verification;
- face reconstruction of real people;
- real private user data;
- authentication, payment and cloud deployment.

## Core User Stories
- Create a storyteller profile.
- Add written memories.
- Upload voice recordings.
- Upload old photographs with year, location and people notes.
- Build and correct a chronological life timeline.
- Generate an editable biography draft.
- Generate an AI-assisted historical-scene description.
- Review and approve generated content.

## Functional Requirements
- FR-01: Manage storyteller profiles.
- FR-02: Manage autobiography projects.
- FR-03: Accept text, audio and photo materials.
- FR-04: Store material metadata.
- FR-05: Create and order life events.
- FR-06: Generate structured biography content.
- FR-07: Generate scene descriptions and storyboard suggestions.
- FR-08: Support Draft, Reviewed and Approved statuses.
- FR-09: Store data in SQLite.
- FR-10: Exclude private uploads and databases from Git.

## Non-functional Requirements
- understandable for non-technical users;
- unique filenames for uploads;
- supported-file validation;
- clear AI-assisted labels;
- human factual review;
- local privacy protection;
- foreign-key relationships;
- tolerance for missing dates and incomplete narratives.

## Success Criteria
A user can create a profile and project, submit materials, create life events, generate a draft biography and scene description, review saved records, and restart the application without losing data.

## Privacy and Ethics
A production system would require informed consent, authentication, encryption, access control, deletion and export functions, AI-content labels, and copyright and portrait-right review.
""",

    "docs/role_and_contributions.md": """# Role and Contributions

## Project Context
The original Yanxin Oral Autobiography Platform was a university team project completed in 2023.

## My Role
**Project Coordinator and Product–Technical Liaison**

I was not the main machine-learning or Transformer engineer. My responsibilities combined project coordination, business requirement translation and selected technical participation.

## Business-to-Technical Translation
I helped turn broad ideas into implementation questions, including:
- what information users should enter;
- which file formats should be supported;
- what metadata should be stored for photos;
- how life events should be arranged;
- what pages and buttons were needed;
- what data should be saved;
- where human review was necessary.

## Technical-to-Business Communication
I communicated considerations such as:
- AI-generated stories may contain inaccuracies;
- reconstructed scenes are interpretative, not historical evidence;
- poor audio quality reduces transcription accuracy;
- photos often need user-provided context;
- long content may take more processing time;
- video generation is more complex and costly;
- private data requires careful permission and storage design.

## Cross-functional Coordination
I supported:
- requirement clarification;
- implementation prioritisation;
- feasibility discussions;
- task breakdown;
- checking whether outputs matched user needs;
- resolving differences between business goals and technical constraints.

## Frontend Participation
I participated in selected frontend work and user-flow discussions, including input forms, upload flows, project information layout and generated-result presentation.

## Database Participation
I contributed to database discussions or implementation concerning storyteller profiles, projects, uploaded materials, life events, generated stories and table relationships.

## AI Output Review
Where applicable, I reviewed whether AI-assisted outputs were coherent, complete, understandable and consistent with source materials. I do not describe this as independent model training.

## Accurate Portfolio Positioning
> Coordinated an AI-assisted oral autobiography platform, translating business requirements into technical tasks and communicating technical feasibility back to commercial stakeholders, while contributing to selected frontend workflows and basic database implementation.

## What I Do Not Claim
- independently training Transformer models;
- independently developing the entire platform;
- creating a production video-generation system;
- owning all frontend and backend implementation;
- using private user materials in this public repository.
""",

    "docs/user_journey.md": """# User Journey

## Persona
A family member helping an elderly relative preserve personal memories.

## Journey

### 1. Create Storyteller Profile
Enter name, preferred name, approximate birth year, hometown, relationship and preferred language.

### 2. Create Autobiography Project
Create a project such as Childhood Memories, Family Migration History or Career and Community Contribution.

### 3. Provide Source Materials
- written memories and interview notes;
- voice recordings;
- historical photographs with optional year, location and people descriptions.

### 4. Process Materials
Conceptual processing includes transcription, text cleaning, photo metadata handling, event extraction and uncertainty detection.

### 5. Build Life Timeline
Each event may include title, year range, certainty, location, people, description, source material and display order.

### 6. Generate Autobiography Content
Create editable drafts for introduction, childhood, education, work, family, turning points and reflection.

### 7. Reconstruct Historical Scenes
Generate scene descriptions, atmosphere, people, actions, camera suggestions, storyboard text and future video prompts.

### 8. Review and Correct
The user checks names, dates, places, relationships, tone, missing events and unsupported details.

Status flow: `Draft → Reviewed → Approved`

### 9. Save and Export
Potential outputs include a timeline, autobiography, story chapters, scene descriptions and storyboard documents.

## UX Principles
- plain language;
- simple navigation;
- support incomplete dates;
- preserve user control;
- show privacy reminders;
- clearly label AI-assisted content;
- never present reconstruction as verified historical evidence.
""",

    "docs/technical_constraints.md": """# Technical Constraints and Product Risks

## Speech Recognition
Noise, accents, multiple speakers and low-quality recordings may reduce transcription accuracy.

Mitigation: editable transcripts, preserved audio and manual confirmation.

## Long-form Narrative Processing
Stories may be repetitive, non-chronological and incomplete.

Mitigation: segmentation, structured timelines, source references and manual ordering.

## Historical Photographs
Photos may have low resolution, unknown dates, unidentified people and unclear locations.

Mitigation: user-provided descriptions, estimated-date labels and human review.

## AI Hallucination
Generative AI may add unsupported details.

Mitigation: draft labels, source links, user approval and separation of facts from interpretation.

## Video Reconstruction Complexity
Full video generation requires script, storyboard, image generation, motion, voice, sound and continuity. This prototype therefore generates scene descriptions and prompts rather than claiming full video reconstruction.

## Privacy and Security
The platform may contain names, voices, faces, relationships and private photographs.

A production system would require authentication, encryption, access control, secure deletion, retention policies, audit logs and compliance review.

## Copyright and Consent
The product must consider photo ownership, consent, story permissions and rights relating to generated voices or faces.

## Accessibility
The interface should use readable labels, clear instructions, minimal required fields and understandable errors.

## Cost and Latency
AI services may introduce API charges, processing delays, storage costs and rate limits.

## Public Reconstruction Boundary
This repository:
- does not contain the original private codebase;
- does not contain real user data;
- does not reproduce proprietary assets;
- focuses on coordination, frontend participation and database participation.
""",
}

schema = """PRAGMA foreign_keys = ON;

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
"""

for rel, content in docs.items():
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")

schema_path = base / "sql/schema.sql"
schema_path.parent.mkdir(parents=True, exist_ok=True)
schema_path.write_text(schema.strip() + "\n", encoding="utf-8")

conn = sqlite3.connect(":memory:")
conn.executescript(schema_path.read_text(encoding="utf-8"))
conn.close()

print("Project documents and database schema created successfully.")
for rel in [*docs.keys(), "sql/schema.sql"]:
    p = base / rel
    print(f"{rel}: {p.stat().st_size} bytes")
print("SQLite schema validation successful.")
