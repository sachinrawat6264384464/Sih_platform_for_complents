# AICTE NEXUS - REPOSITORY CODING INSTRUCTIONS & CONVENTIONS

## Core Principles
1. **Government-Grade Rigor**: Everything built here must reflect real-world enterprise standards suitable for AICTE (Ministry of Education, Govt. of India).
2. **Zero Fictional Data in Production**: No hardcoded dashboard statistics or dummy claims. All metrics must query real database tables.
3. **Deterministic Over Heuristic**: Deterministic logic handles business rules, state machines, and SLA transitions. AI agents provide classification, entity resolution, similarity scoring, and drafting assistance—they never merge cases or close complaints automatically.
4. **Least Privilege & Centralized RBAC**: Permissions are evaluated at database, service, and API layer. Frontend hiding is visual only, never security.
5. **Robust Local Environment**: Python 3.12+ (Async FastAPI), PostgreSQL 13 on port 5433 with D: drive cache & data resilience, Redis 8 on port 6379, Next.js 16+ App Router with React 19 and Tailwind CSS.
6. **No Mockup Buttons**: Every button, modal, form, and action must connect to an actual working backend endpoint.

## Architecture Guidelines
- **Backend**:
  - FastAPI modular monolith with clear domain separation: `models`, `schemas`, `services`, `api/v1`, `integrations`, `mcp_servers`, `ai`.
  - Database access via SQLAlchemy 2.x async session (`postgresql+asyncpg`), with sync session available for Alembic migrations and CLI scripts.
  - Strict Pydantic 2.x models with field validation and documentation.
  - All timestamps stored in UTC (`datetime.now(timezone.utc)`).
- **Frontend**:
  - Next.js App Router (`src/app`), strict TypeScript, React 19.
  - Tailwind CSS 4 with custom dark/light government color palettes.
  - Interactive water ripple cursor and subtle ambient effects respecting accessibility settings (`prefers-reduced-motion`).
  - TanStack Query for cache invalidation and async data flow.
- **MCP Servers**:
  - Official Python MCP SDK standard.
  - Read-only tools by default; write tools require explicit authorization and human-in-the-loop review.
  - Stdio & Streamable HTTP support for enterprise connectivity.
- **AI & RAG**:
  - Hybrid RAG combining BM25 keyword search with dense vector similarity.
  - Trigram (`pg_trgm`) and phonetic (`fuzzystrmatch`) matching for institution names and aliases.
  - LangGraph stateful multi-agent workflow for complaint triage and coordination.

## Directory Structure
- `backend/app/`: FastAPI application code
- `backend/alembic/`: Database migrations
- `backend/tests/`: Pytest suite (unit, integration, and MCP contract tests)
- `frontend/src/`: Next.js client application
- `docs/`: Comprehensive architecture, database, integration, and security specifications
- `skills/`: Modular engineering skills

