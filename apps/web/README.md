# `@bookforge/web`

Next.js web dashboard for BookForge AI.

## Responsibilities

- **Dashboard** — Overview of recent books, pipeline status, system health
- **Book Editor** — Create and edit book specifications
- **Pipeline Monitor** — Real-time progress tracking with stage-level detail
- **Review Interface** — Chapter verdicts, findings, approve/revise actions
- **Project Management** — Collaborator invitations and role management
- **Download Center** — PDF and EPUB download with file sizes

## Architecture Role

The web UI communicates exclusively with the REST API. It holds no business logic, accesses no databases, and makes no LLM calls. It is a pure presentation layer.

## Technology

| Component | Technology |
|---|---|
| Framework | Next.js 14+ |
| Language | TypeScript |
| Styling | Tailwind CSS |
| API Client | Generated OpenAPI client |
| State Management | React Query |
| Real-time Updates | Server-Sent Events for pipeline progress |

## Running

```bash
npm run dev        # Development
npm run build      # Production build
npm run start      # Production serve
```

## Dependencies

- `api` — REST API (required backend)
