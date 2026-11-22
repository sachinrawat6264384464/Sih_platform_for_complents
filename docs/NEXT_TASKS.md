# AICTE NEXUS - NEXT TASKS ROADMAP

1. **Phase 2 Completion**:
   - Create Alembic configuration (`backend/alembic.ini`, `backend/alembic/env.py`).
   - Define complete SQLAlchemy 2.0 async models matching all 40+ master database entities.
   - Run Alembic migration to generate schema in PostgreSQL (`aicte_nexus`).
   - Implement `backend/bootstrap_admin.py` with secure interactive and non-interactive administrative account provisioning.
2. **Phase 3 Completion**:
   - Complete core security: password hashing (bcrypt), JWT access and refresh token rotation, centralized RBAC dependencies (`require_permission`, `require_role`, bureau/regional scope checks).
   - Core Auth endpoints: `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/me`, `/api/v1/auth/logout`.
3. **Phase 4 & 5 Completion**:
   - Institution, Bureau, Officer, Complaint CRUD and lifecycle engine.
   - 12-state case workflow with chronological transition validation and immutable audit logging.
4. **Phase 6 & 7 Completion**:
   - Integration connectors (PGRC, Regulation Bureau, Regional Office, Email, CSV/SFTP).
   - MCP Server Suite with official Python MCP SDK.
5. **Phase 8, 9 & 10 Completion**:
   - Hybrid RAG (BM25 + Dense vector cosine retrieval) & Overlap Detection engine (8-stage matching).
   - Multi-agent coordination with LangGraph supervisor.
6. **Phase 11, 12 & 13 Completion**:
   - Next.js 16+ frontend with theme switching, water ripple cursor, cloud effects, command palette, dashboard analytics.
   - Automated tests (Pytest, HTTPX, contract tests).
