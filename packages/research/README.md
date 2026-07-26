# `@bookforge/research`

Research engine for BookForge AI — gathers, organizes, validates, and prepares technical knowledge before book writing. Operates independently of any specific LLM provider.

## Usage

```python
from bookforge.research import ResearchEngine

engine = ResearchEngine()
result = engine.research("Kubernetes networking")

print(result.summary)
print(f"Found {len(result.key_concepts)} key concepts")
print(f"Found {len(result.references)} references")
```

With pre-collected sources:

```python
from bookforge.research import ResearchEngine, ResearchSource
from bookforge.research.enums import SourceType

engine = ResearchEngine()
sources = [
    ResearchSource(
        id="s1",
        title="Kubernetes Docs",
        source_type=SourceType.DOCUMENTATION,
        content="Kubernetes networking enables pod-to-pod communication...",
    ),
]
result = engine.research_with_sources("Kubernetes", sources)
```

## Pipeline

```text
Topic
  │
  ▼
Planning ─────────── ResearchPlanner generates objectives and queries
  │
  ▼
Normalization ────── ResearchNormalizer extracts sections and cleans content
  │
  ▼
Deduplication ────── ResearchDeduplicator removes duplicate sources
  │
  ▼
Ranking ──────────── ResearchRanker scores by authority, freshness, relevance, completeness
  │
  ▼
Validation ───────── ResearchValidator checks metadata, URLs, empty content
  │
  ▼
Export ───────────── ResearchExporter produces the final ResearchResult
```

## Models

| Model | Description |
|---|---|
| `ResearchSource` | Raw source of information (doc, blog, RFC, paper, etc.) |
| `ResearchDocument` | Normalized document extracted from a source |
| `ResearchSection` | A section within a document with optional subsections |
| `ResearchPlan` | Structured plan with objectives, queries, and target sources |
| `ResearchResult` | Final structured output: summary, concepts, terminology, APIs, code, architecture, references |
| `ResearchJob` | Job tracking a research lifecycle |
| `ResearchTask` | Individual task within a research job |
| `ResearchStatistics` | Counters for sources, duplicates, errors, elapsed time |
| `KeyConcept` | Named concept with definition and relevance score |
| `Terminology` | Technical term with definition and context |
| `CodeReference` | Code snippet with language, description, and source |
| `ArchitectureNote` | Architecture insight with title and content |
| `Reference` | Bibliographic reference with authors, year, URL |

## Enums

| Enum | Values |
|---|---|
| `SourceType` | `DOCUMENTATION`, `GITHUB`, `RFC`, `PAPER`, `BLOG`, `BOOK`, `SPECIFICATION`, `API` |
| `ResearchStatus` | `PENDING`, `PLANNING`, `COLLECTING`, `NORMALIZING`, `DEDUPLICATING`, `RANKING`, `VALIDATING`, `EXPORTING`, `COMPLETED`, `FAILED` |
| `RankCriterion` | `AUTHORITY`, `FRESHNESS`, `RELEVANCE`, `COMPLETENESS` |
| `SupportedInput` | `TECHNICAL_TOPIC`, `PROGRAMMING_LANGUAGE`, `FRAMEWORK`, `TECHNOLOGY`, `SOFTWARE_LIBRARY`, `API`, `RFC`, `ARCHITECTURE` |

## Components

| Component | Responsibility |
|---|---|
| `ResearchEngine` | Top-level entry point. Calls `research(topic)` or `research_with_sources(topic, sources)`. |
| `ResearchManager` | Manages job lifecycle: create, start, cancel, list, track status. |
| `ResearchPipeline` | Orchestrates the 6-stage pipeline (plan → normalize → dedupe → rank → validate → export). |
| `ResearchPlanner` | Generates a structured plan from a topic — objectives, search queries, target sources. |
| `ResearchNormalizer` | Extracts sections from raw content and produces normalized documents. |
| `ResearchDeduplicator` | Content-fingerprint deduplication via SHA-256 hashes. |
| `ResearchRanker` | Rule-based scoring by authority, freshness, relevance, completeness. |
| `ResearchValidator` | Checks duplicate sources, invalid URLs, missing metadata, empty summaries. |
| `ResearchExporter` | Exports results to dict, JSON, summary statistics. |
| `MemoryCache` | In-memory cache with configurable TTL. |
| `DiskCache` | File-system cache with SHA-256 key hashing and JSON serialization. |

## Cache

Two implementations of `ResearchCache`:

```python
from bookforge.research.cache import MemoryCache, DiskCache

memory = MemoryCache(default_ttl=3600)
memory.set("key", value)

disk = DiskCache("/tmp/research-cache", default_ttl=3600)
disk.set("key", value)
```

## Ranking

Ranking is rule-based with no external LLM calls:

| Criterion | Weight | Method |
|---|---|---|
| Authority | 0.35 | Source type hierarchy (Specification > RFC > Book > Paper > Doc > API > GitHub > Blog) |
| Freshness | 0.20 | Source type decay rate |
| Relevance | 0.30 | Title and content keyword matching |
| Completeness | 0.15 | Title presence, content length, URL presence |
