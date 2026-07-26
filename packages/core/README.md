# `@bookforge/core`

Domain entities, pipeline orchestration, and subsystem coordination.

## Responsibilities

- Defines domain entities: `Book`, `Chapter`, `Section`, `Project`, `BookSpec`
- Implements the pipeline state machine with checkpoint recovery
- Orchestrates pipeline stage execution across all subsystems
- Manages book CRUD and lifecycle transitions
- Coordinates the Pipeline Orchestrator — determines stage order, dispatches work, handles completion and failure events
- Provides the `Stage` and `StageResult` abstractions for composable processing

## Subsystem Interfaces

The core package defines the interface that every subsystem implements:

```python
class Stage(ABC):
    async def execute(self, context: PipelineContext) -> StageResult: ...
    async def validate(self, output: StageOutput) -> bool: ...
    async def rollback(self, context: PipelineContext) -> None: ...
```

## Dependencies

- `shared` — Types, configuration, error types
- `llm` — Provider access for subsystem orchestration
- `prompts` — Template rendering for pipeline context
- Every domain subsystem (research, writing, review, etc.)

## Referenced In

- `docs/ARCHITECTURE.md` — Pipeline Orchestrator
- `docs/PIPELINE.md` — Pipeline orchestration sequence
