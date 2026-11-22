# AICTE NEXUS - ARCHITECTURAL & TECHNICAL DECISIONS

## 1. Storage & Disk Space Strategy
- **Context**: The developer host machine's `C:` drive was critically constrained (~150MB free), while `D:` drive provides >53GB free space.
- **Decision**:
  - All temporary builds, pip caches, npm caches are redirected to `D:\temp`, `D:\.pip-cache`, `D:\.npm-cache`.
  - Python virtual environment is anchored at `D:\sih_problm1.0\backend\venv`.
  - PostgreSQL database `aicte_nexus` was created on the local PostgreSQL 13 instance running on port 5433 with native extensions.

## 2. PostgreSQL 13 Compatibility & Hybrid RAG Vector Strategy
- **Context**: The local PostgreSQL version is 13.22. `pgvector` requires compilation and admin DLL installation not natively shipped in Postgres 13 on this machine.
- **Decision**:
  - We verified and enabled native extensions: `pg_trgm` (trigram text similarity), `fuzzystrmatch` (Levenshtein, Soundex, Metaphone for institution and address matching), and `uuid-ossp` (standard UUID generation).
  - For Hybrid RAG and Overlap Vector Similarity: We implement a high-performance vector representation layer using dense embeddings with persistent JSONB array storage in PostgreSQL and Cosine similarity computation accelerated via NumPy/Scikit-Learn/FAISS-compatible search, combined with `rank-bm25` and trigram filtering. This provides government-grade retrieval without requiring external unverified C++ binaries.

## 3. Modular Monolith over Unnecessary Microservices
- **Decision**: In strict accordance with the master project specification, AICTE Nexus is structured as a modular monolith with clean domain boundaries:
  - Domain modules: Institutions, Complaints, Bureaus, Cases, Integrations, MCP Servers, AI Intelligence, Notifications, Audit.
  - Allows single-command local deployment, atomic transactional guarantees across complaints and audit logs, and simplified debugging while preserving clean separation of concerns.

## 4. MCP (Model Context Protocol) Implementation
- **Decision**: Use the official `mcp` Python SDK (v1.x/2.x).
  - 7 specialized MCP servers: PGRC, Regulation Bureau, Institution, Complaint, Reporting, Document, and Notification.
  - Strict read-only defaults, human-in-the-loop permission checks for any mutating action, and execution audit logging.
