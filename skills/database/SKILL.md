---
name: aicte-nexus-database
description: Database conventions, PostgreSQL configuration, Alembic migrations, and indexing strategies for AICTE Nexus
---

# Database Skill - AICTE Nexus

## Database Design Guidelines
1. **Primary Keys**: Always use UUID v4 (`UUID(as_uuid=True)` in SQLAlchemy, `DEFAULT gen_random_uuid()` or `uuid_generate_v4()`).
2. **Timestamps**: All tables must include `created_at` and `updated_at` with UTC default timestamps (`server_default=func.now()`).
3. **Foreign Keys**: Enforce referential integrity with explicit `ondelete` clauses (`RESTRICT`, `CASCADE`, `SET NULL`).
4. **Indexes**:
   - B-tree indexes on foreign keys, status columns, dates, and lookups.
   - GIN trigram indexes (`gin_trgm_ops`) on institution names, aliases, complaint summaries for lightning-fast fuzzy search.
5. **JSONB Columns**: Store structured metadata, raw source payloads, and vector embeddings in JSONB for schema flexibility and auditability.
6. **Transactions**: Use `async with session.begin():` to guarantee atomic multi-table updates.
