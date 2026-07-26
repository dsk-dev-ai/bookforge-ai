# `@bookforge/images`

Image Engine subsystem — cover and illustration image generation.

## Responsibilities

- Generates book cover images from metadata via image-capable providers
- Generates illustrations for chapter content
- Processes and optimises images (resize, crop, format conversion)
- Manages image resolution and placement in content
- Stores image assets in object storage
- Supports multiple image generation backends
- Part of the **Creation** phase of the pipeline (Stage 9)

## Pipeline Stages

| Stage | Role |
|---|---|
| Stage 9: Cover | Generate book cover image |

## Dependencies

- `llm` — Image generation via Provider Manager
- `shared` — Types, configuration

## Referenced In

- `docs/PIPELINE.md` — Stage 9
- `docs/ARCHITECTURE.md` — Image Engine subsystem
