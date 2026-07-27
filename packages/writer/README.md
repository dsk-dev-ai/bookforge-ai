# `@bookforge/writer`

Writing engine for BookForge AI.

Converts a `BookBlueprint` and `ResearchResult` into structured Markdown drafts
using provider-independent LLM generation.

## Usage

```python
from bookforge.writer import WriterEngine, WritingConfig
from bookforge.writer.models import DraftBook, DraftChapter, WritingContext

engine = WriterEngine()

# Create a draft from a blueprint
draft = DraftBook(
    title="Kubernetes Networking",
    topic="Kubernetes",
    chapters=[DraftChapter(title="Introduction to Networking")],
)

# Provide a generator (wraps ProviderManager)
class MyGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        from bookforge.llm import ProviderManager
        mgr = ProviderManager.from_env()
        from bookforge.llm.models import Message, MessageRole
        response = await mgr.chat([
            Message(role=MessageRole.SYSTEM, content=prompt),
        ])
        return response.content

# Write
result = await engine.write(draft, MyGenerator())
print(result.markdown)
```

## Pipeline

```
Blueprint / DraftBook
  ↓
ChapterWriter  → writes each chapter
IntroductionWriter → prepends intro
SectionWriter  → writes section content
ConclusionWriter → appends conclusion
GlossaryWriter → generates glossary
ReferenceWriter → generates references
ContentValidator → validates output
MarkdownAssembler → assembles full Markdown
  ↓
DraftBook + Markdown
```

## Models

| Model | Description |
|---|---|
| `DraftBook` | Top-level book draft with chapters, front/back matter, glossary, references |
| `DraftChapter` | Single chapter with content, sections, metadata |
| `DraftSection` | Section with heading, content, nested subsections |
| `WritingContext` | Immutable context from blueprint + research |
| `WritingSession` | Tracks a writing session with context and draft |
| `WritingStatistics` | Stats: chapters/sections written, word counts, validation |
| `WritingMetrics` | LLM metrics: token counts, latency, retries |
| `WritingJob` | Job tracked by WriterManager |

## Validation

- Empty chapters / sections
- Duplicate sections
- H1 headings inside chapters
- Word count thresholds
- Invalid code fence language specifiers
- Unclosed code fences
- Orphaned table separators
- Missing references section when content references external resources

## Export

- `to_markdown()` — full Markdown string
- `to_dict()` — metadata summary
- `to_json()` — JSON string
- `to_file()` — write to file

## Writers

| Writer | Purpose |
|---|---|
| `ChapterWriter` | Full chapter content |
| `SectionWriter` | Individual section content |
| `IntroductionWriter` | Chapter introductions |
| `ConclusionWriter` | Chapter conclusions |
| `GlossaryWriter` | Glossary definitions |
| `ReferenceWriter` | Reference documentation |
| `CodeExampleWriter` | Standalone code examples |
| `TableWriter` | Markdown tables |
