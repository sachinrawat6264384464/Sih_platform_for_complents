# AICTE NEXUS - KNOWN ISSUES & ENVIRONMENT CONSTRAINTS

1. **Host Disk Space Constraint on C:**:
   - Host `C:` drive has minimal free space (~100-200MB).
   - *Mitigation*: All heavy directories (pip cache, npm cache, temp files, Python virtualenv) are explicitly redirected to `D:` drive (>53GB available).
2. **PostgreSQL 13 Port & Extensions**:
   - The developer machine runs PostgreSQL 13 on port `5433` (service `postgresql-x64-13`).
   - `pgvector` native C extension is not compiled into Postgres 13 on this machine.
   - *Mitigation*: Enabled native `pg_trgm`, `fuzzystrmatch`, `uuid-ossp`. Hybrid RAG and similarity calculations use dense embedding vectors persisted in JSONB columns, indexed and queried via Scikit-Learn/NumPy/BM25 in-process and trigram indexes in PostgreSQL.
3. **External AICTE Portal Access**:
   - Live external AICTE bureau portals (PGRC and Regulation Bureau production endpoints) require official institutional VPN / network whitelisting and credentials.
   - *Mitigation*: Comprehensive connector architecture with simulated mock environments for automated testing, coupled with rigorous validation against production schemas when credentials are provided.

