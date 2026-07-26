# `@bookforge/core`

Domain entities, value objects, enums, and serialization for BookForge AI.

## Overview

The core package defines the business domain that every subsystem depends on. It follows Clean Architecture, Domain-Driven Design, and SOLID principles.

No provider integrations, no API calls, no database, no business workflows — only the domain model.

## Package

```
packages/core/src/bookforge/core/
├── __init__.py          # Public API exports
├── enums.py             # All enumerations
├── value_objects.py     # Immutable value objects
├── author.py            # Author entity
├── book.py              # Project, Book, Chapter, Section entities
├── content.py           # Paragraph, CodeExample, Diagram, ImageAsset, Table
├── reference.py         # Reference, Citation, Bibliography
├── prompt.py            # PromptTemplate entity
├── publishing.py        # PublishingInfo, ReviewInfo, ExportInfo
├── taxonomy.py          # Category, Tag, LearningObjective
└── serialization.py     # JSON, dict, YAML helpers
```

## Modules

### Enums

| Enum | Values |
|---|---|
| `Difficulty` | beginner, intermediate, advanced, expert |
| `Audience` | developers, data_scientists, devops, architects, students, hobbyists, professionals, managers |
| `Language` | 20 language codes (en, es, fr, de, zh, ja, ...) |
| `BookStatus` | draft, planning, researching, writing, reviewing, editing, formatting, published, archived |
| `GenerationStage` | created → outlining → outlined → researching → researched → writing → written → reviewing → reviewed → formatting → formatted → exporting → exported → failed |
| `ExportFormat` | pdf, epub, mobi, docx, html, markdown, latex, asciidoc, plain_text |
| `DiagramType` | flowchart, sequence, class, erd, architecture, component, deployment, state, timing, gantt, mindmap, custom |
| `ReferenceType` | book, article, conference, thesis, technical_report, website, documentation, standard, patent, software, video, podcast, blog, other |
| `AssetType` | image, diagram, code_snippet, table, chart, screenshot, logo, icon, attachment, other |
| `CodeLanguage` | 30+ languages (python, javascript, typescript, rust, go, java, ...) |
| `BloomLevel` | remember, understand, apply, analyze, evaluate, create |

### Value Objects (Immutable)

| Object | Fields | Validation |
|---|---|---|
| `PersonName` | first, last | Non-empty |
| `EmailAddress` | address | RFC-like regex |
| `URL` | url | http/https regex |
| `ISBN` | value | ISBN-10/13 format + checksum |
| `PageRange` | start, end | Positive, end >= start |
| `Version` | major, minor, patch | Non-negative |
| `Color` | hex | `#RRGGBB` format |
| `ImageDimension` | width, height | Positive, ≤ 100000 |

### Domain Entities

| Entity | Description |
|---|---|
| `Project` | Top-level container with books, versioning, duplicate ID validation |
| `Book` | Book with metadata, specification, settings, chapters, references, glossary |
| `BookMetadata` | Title, subtitle, description, language, cover, tags, edition |
| `BookSpecification` | Audience, difficulty, page/chapter counts, prerequisites, learning objectives |
| `BookSettings` | Temperature, top_p, tone, verbosity, code style |
| `BookConfiguration` | Status, stage, lock flag, timestamps, version, model assignments |
| `Chapter` | Numbered chapter with sections, introduction, summary |
| `Section` | Heading with paragraphs, code, diagrams, images, tables; supports nesting |
| `Paragraph` | Text with optional style, list type, indent |
| `CodeExample` | Code snippet with language, title, explanation, highlights, output |
| `Diagram` | Diagram with type, Mermaid/PlantUML source, caption, alt text |
| `ImageAsset` | Image URL with alt text, caption, dimensions |
| `Table` | Headers, rows with column-count validation, caption |
| `Reference` | Publication reference with full bibliographic metadata |
| `Citation` | In-text citation pointing to a reference with context and locators |
| `Bibliography` | Ordered collection of references with citation style (apa, mla, ieee, ...) |
| `PromptTemplate` | Versioned prompt template with variables, category, tags, model config |
| `Author` | Author profile with name, contact, social links, specialties, expertise |
| `Category` | Hierarchical category (e.g., "Programming" → "Python") |
| `Tag` | Tag optionally scoped to a category |
| `LearningObjective` | Objective with Bloom level, difficulty, chapter/section binding |
| `PublishingInfo` | ISBN, publisher, edition, format, pricing, rights |
| `ReviewInfo` | Review status, reviewer, rating, revision notes, timestamps |
| `ExportInfo` | Export job tracking: format, file path, status, size, version |

## Validation

All domain entities include Pydantic validators:

- **Empty strings** — title, name, text, heading, id fields reject empty/whitespace-only values
- **Unique constraints** — duplicate chapter numbers, duplicate book IDs, duplicate reference IDs
- **Range checks** — page counts ≥ 1, temperature 0–2, rating 1–5, indent 0–10
- **Format checks** — ISBN checksum, email regex, URL regex, hex color pattern
- **Structural checks** — table row columns match header count, list_type matches pattern

## Serialization

All domain entities support three serialization formats:

```python
from bookforge.core.serialization import to_dict, to_json, to_yaml
from bookforge.core import Book, BookMetadata

book = Book(id="b1", metadata=BookMetadata(title="Python Deep Dive"))

d = to_dict(book)          # → dict
j = to_json(book)          # → JSON string
y = to_yaml(book)          # → YAML string

restored = Book.model_validate(d)   # dict → entity
restored = Book.model_validate_json(j)  # JSON → entity
```

## Requirements

```
pydantic>=2.0
pyyaml>=6.0
```
