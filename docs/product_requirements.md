# Product Requirements Document

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
