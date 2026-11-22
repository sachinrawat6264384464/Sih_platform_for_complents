# AICTE NEXUS - SYSTEM ARCHITECTURE

## 1. High-Level Architectural Diagram

```
                     ┌──────────────────────────────────────────┐
                     │          Next.js 16+ Frontend            │
                     │  (App Router, React 19, Tailwind CSS 4)  │
                     └─────────────────────┬────────────────────┘
                                           │ HTTPS / WSS
                                           ▼
                     ┌──────────────────────────────────────────┐
                     │          FastAPI Async Backend           │
                     │      (Python 3.12+, Pydantic 2.x)        │
                     └──────┬────────────────────────────┬──────┘
                            │                            │
          ┌─────────────────┴─────────────┐    ┌─────────┴─────────────────────┐
          ▼                               ▼    ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│  Authentication  │            │ Integration GW   │            │ MCP Client       │
│  & Granular RBAC │            │ (Connectors:     │            │ Runtime          │
│  (Roles/Bureaus) │            │  PGRC, RB, Reg,  │            │ (7 Core Managed  │
└──────────────────┘            │  Email, CSV/SFTP)│            │  MCP Servers)    │
                                └──────────────────┘            └──────────────────┘
                                          │                               │
                                          ▼                               ▼
                                ┌──────────────────────────────────────────────┐
                                │             AI & Analytics Core              │
                                │ ┌───────────────────┐  ┌───────────────────┐ │
                                │ │ Hybrid RAG        │  │ 8-Stage Overlap   │ │
                                │ │ (BM25 + Vectors)  │  │ Detection Engine  │ │
                                │ └───────────────────┘  └───────────────────┘ │
                                │ ┌───────────────────┐  ┌───────────────────┐ │
                                │ │ LangGraph Agents  │  │ Graph Traversal   │ │
                                │ │ (7 Specialist Ags)│  │ & Entity Network  │ │
                                │ └───────────────────┘  └───────────────────┘ │
                                └──────────────────────┬───────────────────────┘
                                                       │
                                                       ▼
                            ┌──────────────────────────────────────────┐
                            │        PostgreSQL 13 Database            │
                            │      (`pg_trgm`, `fuzzystrmatch`,        │
                            │       `uuid-ossp`, JSONB vectors)        │
                            └──────────────────────────────────────────┘
```

## 2. Core Subsystems

### A. Authentication & RBAC Engine
- Hierarchical roles: Super Admin, AICTE Administrator, Senior Officer, Bureau Head, Regional Officer, Case Officer, PGRC Officer, Regulation Bureau Officer, Auditor, Read-Only Viewer.
- Dual-layer access checks: Role Permission AND Bureau Ownership.

### B. Integration Gateway & Connector Framework
- Standardized `BaseConnector` lifecycle: `validate_credentials()`, `sync()`, `normalize()`, `retry()`, `dead_letter()`.
- Guaranteed idempotency via deterministic source hashing (`hash(source_system_id + original_record_id)`).

### C. Overlap & Entity Resolution Engine
- Multi-stage progressive sieve:
  1. Exact AICTE Permanent ID match.
  2. Trigram & Levenshtein institution name matching.
  3. Regional Office & Geographic District proximity.
  4. Grievance taxonomy and category alignment.
  5. BM25 keyword overlap on complaint summary.
  6. Dense vector cosine semantic similarity.
  7. Cross-bureau open case correlation.
  8. Human verification queue with explanatory provenance.
