# Workflow

> End-to-end workflows for BookForge AI — from specification to published book.

---

## Table of Contents

- [Workflow Philosophy](#workflow-philosophy)
- [User-Facing Workflows](#user-facing-workflows)
- [System Workflows](#system-workflows)
- [Workflow Orchestration](#workflow-orchestration)
- [Exception Workflows](#exception-workflows)

---

## Workflow Philosophy

Every workflow in BookForge AI follows three principles:

1. **Asynchronous by default** — No user waits synchronously for an LLM to generate content. Every action that takes longer than 1 second executes in the background.
2. **Observable at every step** — Users can see what stage is running, how long it has been running, and what the estimated remaining time is.
3. **Resumable from failure** — No workflow restarts from scratch after a failure. Checkpoints ensure recovery from the last successful step.

---

## User-Facing Workflows

### 1. Create a Book

```mermaid
sequenceDiagram
    actor User
    participant WEB as Web UI
    participant API as REST API
    participant BM as Book Manager
    participant DB as PostgreSQL

    User->>WEB: Fill book creation form
    WEB->>API: POST /books
    API->>BM: create_book(spec)
    BM->>DB: validate topic & fields
    BM->>DB: insert book record
    BM-->>API: book_id + status
    API-->>WEB: 201 Created + book_id
    WEB-->>User: Book created, ready to start pipeline
```

**User sees:** Confirmation with book ID and status "draft". Button to start the pipeline.

---

### 2. Start and Monitor the Pipeline

```mermaid
sequenceDiagram
    actor User
    participant WEB as Web UI
    participant API as REST API
    participant BM as Book Manager
    participant JQ as Job Queue
    participant ORCH as Orchestrator
    participant WRK as Worker

    User->>WEB: Click "Start Generation"
    WEB->>API: POST /books/{id}/pipeline/start
    API->>BM: transition_state(in_progress)
    BM->>BM: validate pipeline not already running
    BM->>JQ: enqueue pipeline.start
    API-->>WEB: 202 Accepted + current stage
    WEB-->>User: Pipeline started, show progress view

    loop Poll status every 5 seconds
        WEB->>API: GET /books/{id}/pipeline/status
        API->>BM: load current stage & progress
        BM-->>API: status payload
        API-->>WEB: current stage, progress %
        WEB-->>User: Update progress bar
    end

    JQ->>ORCH: execute(pipeline.start, book_id)
    ORCH->>WRK: run stages sequentially

    WRK-->>ORCH: pipeline.completed
    ORCH->>BM: transition_state(completed)

    WEB->>API: GET /books/{id}/pipeline/status
    API-->>WEB: status = completed
    WEB-->>User: "Book complete! Download now available"
```

**User sees:** A progress view showing:
- Current stage name with icon
- Overall progress bar (% complete)
- Per-stage status (pending, running, completed, failed)
- Estimated time remaining
- "Cancel" button (only when running)

---

### 3. Review and Revise

```mermaid
sequenceDiagram
    actor User
    participant WEB as Web UI
    participant API as REST API
    participant RV as Review Engine
    participant WE as Writing Engine
    participant DB as PostgreSQL

    User->>WEB: Navigate to review section
    WEB->>API: GET /books/{id}/review
    API->>RV: load_review_reports(book_id)
    RV->>DB: query review reports
    DB-->>RV: reports with findings
    RV-->>API: aggregated review data
    API-->>WEB: review dashboard
    WEB-->>User: See per-chapter verdicts

    User->>WEB: Click "Request Revision" on Chapter 3
    WEB->>API: POST /books/{id}/review/chapters/{ch}/request-revision
    API->>RV: request_revision(chapter_id, comments)
    RV->>DB: store revision request
    RV->>WE: regenerate_chapter(chapter_id, feedback)
    WE->>DB: update chapter content
    WE-->>RV: chapter updated
    RV->>DB: reset review verdicts for chapter
    RV-->>API: revision queued
    API-->>WEB: 202 Accepted
    WEB-->>User: "Revision queued"
```

**User sees:** Review dashboard with:
- Per-chapter verdict cards (pass/fail)
- Expandable findings per review stage
- "Approve" and "Request Revision" buttons
- Revision cycle counter
- Comment box for revision requests

---

### 4. Download Completed Book

```mermaid
sequenceDiagram
    actor User
    participant WEB as Web UI
    participant API as REST API
    participant BM as Book Manager
    participant S3 as Object Storage

    User->>WEB: Click "Download PDF"
    WEB->>API: GET /books/{id}/outputs
    API->>BM: get_output_refs(book_id)
    BM-->>API: output_refs {pdf: ..., epub: ...}
    API-->>WEB: output list with download URLs
    WEB-->>User: Show download buttons

    User->>WEB: Click "PDF" download button
    WEB->>API: GET /books/{id}/outputs/pdf
    API->>API: generate presigned URL
    API-->>WEB: 302 Redirect to S3 URL
    WEB-->>User: File download begins
```

**User sees:** Download buttons for PDF and EPUB formats. File sizes displayed. Cover thumbnail shown.

---

### 5. Manage Projects and Collaborators

```mermaid
sequenceDiagram
    actor Owner as Project Owner
    actor Collab as Collaborator
    participant WEB as Web UI
    participant API as REST API
    participant PM as Project Manager

    Owner->>WEB: Navigate to project settings
    WEB->>API: GET /projects/{id}
    API->>PM: load_project(project_id)
    PM-->>API: project with collaborators
    API-->>WEB: project settings form
    WEB-->>Owner: Project dashboard

    Owner->>WEB: Click "Add Collaborator"
    WEB->>API: POST /projects/{id}/collaborators
    API->>PM: add_collaborator(email, role)
    PM-->>API: collaborator added
    API-->>WEB: confirmation
    WEB-->>Owner: Collaborator invited

    Collab->>WEB: Accept invitation
    WEB->>API: POST /projects/{id}/collaborators/accept
    API->>PM: accept_invitation(token)
    PM-->>API: access granted
    API-->>WEB: redirect to project
```

**User sees (Owner):** Collaborator list with roles, invite form, remove button.
**User sees (Collaborator):** Project in shared projects list, access to books.

---

## System Workflows

### 6. Provider Health Monitoring

```mermaid
sequenceDiagram
    participant PRM as Provider Manager
    participant NIM as NVIDIA NIM
    participant OLL as Ollama
    participant LOG as Logging System
    participant CFG as Config Manager

    loop Every 60 seconds
        PRM->>NIM: health()
        NIM-->>PRM: Healthy (200ms)
        PRM->>OLL: health()
        OLL-->>PRM: Healthy (1500ms)
        PRM->>PRM: cache health status
    end

    Note over PRM: NVIDIA starts failing
    PRM->>NIM: health()
    NIM-->>PRM: Timeout
    PRM->>NIM: health() [retry 1]
    NIM-->>PRM: Timeout
    PRM->>PRM: mark_unhealthy(nvidia)
    PRM->>LOG: log provider degradation
    PRM->>CFG: set_feature_flag(provider.fallback.enabled, true)
```

---

### 7. Pipeline Checkpoint Recovery

```mermaid
sequenceDiagram
    participant ORCH as Orchestrator
    participant DB as PostgreSQL
    participant STAGE as Worker Pool

    Note over ORCH: Worker crashes during Stage 6 (Writing)
    ORCH->>ORCH: detect crash via broker heartbeat timeout

    ORCH->>DB: load_last_checkpoint(book_id)
    DB-->>ORCH: checkpoint at Stage 5 (Knowledge Base) completed

    ORCH->>ORCH: determine resume_from = Stage 6 (Writing)

    ORCH->>STAGE: execute(writing, context)
    STAGE->>DB: load previous output (chapter_1 through chapter_4)
    DB-->>STAGE: chapter content

    Note over STAGE: Continues from chapter_5

    STAGE->>DB: persist chapter_5
    STAGE->>DB: create pipeline_event (stage.started)
    STAGE-->>ORCH: StageResult(success)
```

---

### 8. Configuration Reload

```mermaid
sequenceDiagram
    participant ADMIN as Admin
    participant API as REST API
    participant CFG as Config Manager
    participant SUB as Subsystems

    ADMIN->>API: PATCH /system/config/features/review.style.enabled
    API->>CFG: update_feature_flag(name, value=false)
    CFG->>CFG: validate flag exists
    CFG->>CFG: update config_values table
    CFG->>CFG: invalidate config cache

    Note over CFG,SUB: Next subsystem request

    SUB->>CFG: get_feature_flag(review.style.enabled)
    CFG->>CFG: cache miss, load from DB
    CFG-->>SUB: false

    Note over SUB: Subsystem skips style review stage
```

---

## Workflow Orchestration

```mermaid
stateDiagram-v2
    state "User Workflows" as USER {
        [*] --> Drafting: Create Book
        Drafting --> Validating: Start Pipeline
        Validating --> Monitoring: Pipeline Running
        Monitoring --> Reviewing: Pipeline Paused
        Reviewing --> Revising: Request Changes
        Revising --> Monitoring: Revision Queued
        Monitoring --> Downloading: Pipeline Complete
        Downloading --> [*]
    }

    state "System Workflows" as SYSTEM {
        [*] --> HealthCheck: Every 60s
        HealthCheck --> Degraded: Provider Unhealthy
        Degraded --> Recovery: Provider Restored
        HealthCheck --> [*]
        Recovery --> [*]
    }

    state "Exception Workflows" as EXCEPTION {
        [*] --> Retry: Stage Failed
        Retry --> Fallback: Retries Exhausted
        Retry --> Recovered: Success
        Fallback --> Recovered: Fallback Succeeds
        Fallback --> Failed: All Providers Down
        Failed --> ManualRecovery: Admin Intervention
        ManualRecovery --> [*]
        Recovered --> [*]
    }
```

---

## Exception Workflows

### Provider Failure During Generation

```mermaid
flowchart TB
    REQ[Writing Engine<br/>requests generation] --> TRY[Provider Manager<br/>sends to NVIDIA NIM]
    TRY --> FAIL{Response?}
    FAIL -->|Success| DONE([Content Generated])
    FAIL -->|Error| RETRY{Retries left?}
    RETRY -->|Yes| WAIT[Wait 2^N seconds + jitter]
    WAIT --> TRY
    RETRY -->|No| FALLBACK{Fallback configured?}
    FALLBACK -->|Yes| SWITCH[Switch to Ollama]
    SWITCH --> TRY_OLL[Send to Ollama]
    TRY_OLL --> FAIL2{Response?}
    FAIL2 -->|Success| DONE
    FAIL2 -->|Error| ABORT([Pipeline Aborted])
    FALLBACK -->|No| ABORT
```

### Pipeline Stage Timeout

```mermaid
flowchart TB
    START[Stage Starts] --> TIMER[Start timeout timer]
    TIMER --> RUN{Completes before timeout?}
    RUN -->|Yes| PASS([Stage Passed])
    RUN -->|No| TIMEOUT([Timeout Exceeded])
    TIMEOUT --> CHECK{Retry allowed?}
    CHECK -->|Yes| RETRY[Enqueue retry with backoff]
    RETRY --> RUN
    CHECK -->|No| ABORT([Pipeline Aborted])
```

### Manual Intervention Required

When automatic recovery fails, the pipeline enters a `failed` state and the system:
1. Persists all completed work up to the failure point
2. Logs the full error context with trace ID
3. Sends an alert via the configured webhook
4. Waits for manual intervention (API or dashboard)

An admin can:
- **Retry** the failed stage with modified configuration
- **Skip** the failed stage and continue
- **Roll back** to a previous checkpoint
- **Cancel** the pipeline entirely
