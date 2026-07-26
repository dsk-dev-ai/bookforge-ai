# `@bookforge/planner`

Book planning engine for BookForge AI.

Converts structured research into a complete technical book blueprint with
chapter outlines, dependency graphs, learning paths, and page/time estimates.
Does **not** write chapter text or call LLMs.

## Usage

```python
from bookforge.planner import PlannerEngine

engine = PlannerEngine()
blueprint = engine.plan_book(
    topic="Kubernetes Networking",
    chapter_titles=["Introduction", "Pods", "Services", "Ingress", "DNS"],
    title="Kubernetes Networking Deep Dive",
)

# Inspect the blueprint
print(blueprint.estimated_chapters)     # 5
print(blueprint.estimated_pages)        # ~42
print(blueprint.estimated_reading_minutes)

# Validate
errors = engine.validate_blueprint(blueprint)
for e in errors:
    print(f"[{e.severity}] {e.message}")

# Export
json_str = engine.export_blueprint(blueprint, format="json")
yaml_str = engine.export_blueprint(blueprint, format="yaml")
```

## Pipeline

```
Research Result → BookPlanner → DAG building → Strategy application
    ↓                                              ↓
  BookBlueprint ← Learning Path ← Sequence Optimizer ← Validation
    ↓
  Exporter (dict / JSON / YAML)
```

## Models

| Model | Description |
|---|---|
| `BookBlueprint` | Complete book design: outline, graphs, estimates |
| `BookOutline` | Ordered chapters with front/back matter |
| `ChapterPlan` | Single chapter: title, goals, sections, estimates |
| `SectionPlan` | Nested section with page/time estimates |
| `DependencyGraph` | Directed graph of chapter dependencies |
| `PrerequisiteGraph` | Multi-level prerequisite tree |
| `ConceptGraph` | Concept-relationship map |
| `LearningPath` | Optimized step-by-step learning sequence |
| `TopicCluster` | Group of related topics |

## Strategies

| Strategy | Behaviour |
|---|---|
| `ProgressiveLearningStrategy` | Sort by prerequisites; build learning path |
| `DependencyOrderedStrategy` | Topological sort via dependency graph |
| `DifficultyProgressionStrategy` | Easy → Hard chapter ordering |
| `TopicClusteringStrategy` | Group chapters by topic area |

## Validation

- Duplicate chapters / sections
- Missing prerequisites
- Circular dependencies
- Empty outlines
- Zero page/chapter counts

## Export

- `to_dict()` — plain Python dict
- `to_json()` — JSON string
- `to_yaml()` — YAML string
