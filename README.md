# AICTE NEXUS
### Intelligent Institution Complaint Monitoring & Coordination Platform
**Smart India Hackathon (SIH) Problem Statement**: SIH26264  
**Organization**: All India Council for Technical Education (AICTE)  
**Departments**: Regulation Bureau (RB) & Public Grievance Redressal Cell (PGRC)

---

## 🏛️ Executive Summary
AICTE Nexus is a centralized, government-grade intelligence and case coordination platform designed to eliminate duplicate investigations, conflicting regulatory actions, and unmonitored complaint backlogs across disparate AICTE bureaus and regional offices.

### Core Problems Solved
1. **Siloed Redressal**: Eliminates conflicting actions where PGRC and Regulation Bureau independently investigate the same educational institution without visibility.
2. **Duplicate Ingestion**: Detects exact, near, and semantic duplicate complaints across multiple ingress channels (online portal, email, regional offices, manual CSV/SFTP).
3. **Multi-Stage Overlap Detection**: Uses an 8-stage hybrid matching engine (Permanent ID, fuzzy alias matching, regional geographic proximity, category alignment, BM25 keyword matching, dense vector similarity, cross-bureau correlation, and human review).
4. **Governed Interoperability**: Exposes 7 official Model Context Protocol (MCP) servers allowing authorized AI assistants to query complaints, institutions, and SLA metrics under strict least-privilege RBAC.

---

## 🚀 Key Features
- **Enterprise Multi-Bureau Dashboard**: Dynamic, real-time database-driven metrics (zero hardcoded numbers) showing workload, ageing, SLA breaches, and overlapping cases.
- **Institution Management**: Full lifecycle directory with AICTE Permanent IDs, alternate names, approved programs, connected complaint histories, and regional jurisdiction.
- **Complaint & Case Coordination Workspace**: 12-state validated complaint lifecycle with chronological audit trails, evidence attachments, and multi-bureau transfer protocols.
- **MCP Ecosystem**: 7 official Python SDK MCP servers (PGRC, RB, Institution, Complaint, Reporting, Document, Notification) with fine-grained tool permissions.
- **Hybrid RAG & Intelligence**: Dual-index retrieval combining BM25 keyword indexing with dense vector embeddings and role-based document access segregation.
- **Bilingual & Multilingual Support**: Processes complaints in English and Hindi with phonetic and trigram matching.
- **National Government UI**: High-contrast dark and light themes, subtle animated cloud backdrop, interactive water ripple cursor, and accessible keyboard-first command palette (`Ctrl+K`).

---

## 💻 Tech Stack
- **Frontend**: Next.js 16+ (App Router), React 19, TypeScript, Tailwind CSS 4, Lucide React, TanStack Query & Table, Recharts.
- **Backend**: Python 3.12+, FastAPI (Async), SQLAlchemy 2.0 Async, Pydantic 2.x, Alembic.
- **Database & Cache**: PostgreSQL 13+ (with `pg_trgm`, `fuzzystrmatch`, `uuid-ossp`), Redis 8.
- **AI & Retrieval**: Rank-BM25, Scikit-Learn vector similarity, LangGraph multi-agent supervisor, official Python MCP SDK.

---

## 🛠️ Local Quick Start
See [LOCAL_SETUP.md](file:///D:/sih_problm1.0/LOCAL_SETUP.md) for full instructions.

```bash
# 1. Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python bootstrap_admin.py
uvicorn app.main:app --reload --port 8000

# 2. Frontend Setup
cd frontend
npm install
npm run dev
```
Access Frontend at: `http://localhost:3000`  
Access API Documentation at: `http://localhost:8000/docs`

# Sih_platform_for_complents
