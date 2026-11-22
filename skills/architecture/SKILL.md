---
name: aicte-nexus-architecture
description: Architecture standards and module boundaries for AICTE Nexus government-grade platform
---

# Architecture Skill - AICTE Nexus

## Monolith Modular Design
AICTE Nexus is structured as a robust modular monolith:
- `backend/app/core/`: Configuration, database engines, security, logging
- `backend/app/models/`: Declarative SQLAlchemy 2.0 async models
- `backend/app/schemas/`: Pydantic 2.0 schemas for request/response serialization
- `backend/app/services/`: Pure business logic, transaction boundaries, audit hooks
- `backend/app/api/v1/`: Thin API routers delegating to services with dependency injection
- `backend/app/integrations/`: Connector framework for external AICTE bureaus and cells
- `backend/app/mcp_servers/`: Model Context Protocol servers for AI tool interoperability
- `backend/app/ai/`: LangGraph orchestration, Hybrid RAG, 8-stage Overlap Detection engine

## Key Rules
1. Never bypass the service layer from API endpoints.
2. Every mutation must emit an entry to `audit_logs`.
3. Never expose internal database IDs directly if UUIDs or canonical identifiers exist.
4. Keep models strictly typed and validate all inputs with Pydantic.
