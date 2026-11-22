# AICTE NEXUS — REST API Specification

**Platform**: AICTE NEXUS (SIH26264)  
**Standard**: OpenAPI 3.1 / JSON REST  
**Authentication**: HTTP Bearer JWT (Access Token in `Authorization: Bearer <token>`)

---

## 1. Authentication Endpoints (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Authenticate officer with username/email and password | No |
| `POST` | `/api/v1/auth/refresh` | Refresh expired access token using valid refresh token | No |
| `GET` | `/api/v1/auth/me` | Fetch active officer profile, designations, and bureau scopes | Yes |

---

## 2. Institution Endpoints (`/api/v1/institutions`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/institutions` | Paginated listing of technical institutions with trigram search & state filter | Yes |
| `POST` | `/api/v1/institutions` | Register new institution with official AICTE Permanent ID | Yes (Super Admin / Bureau Lead) |
| `GET` | `/api/v1/institutions/{id}` | Retrieve institution profile, alternate names, and complaint loads | Yes |
| `GET` | `/api/v1/institutions/permanent-id/{perm_id}` | Look up institution by exact AICTE Permanent ID (`1-XXXXXXX`) | Yes |
| `PUT` | `/api/v1/institutions/{id}` | Update institution address, approval status, or contact details | Yes |

---

## 3. Complaint & Lifecycle Endpoints (`/api/v1/complaints`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/complaints` | Filterable complaints directory (status, priority, bureau, overdue) | Yes |
| `POST` | `/api/v1/complaints` | Ingest and register a citizen/student complaint into the system | Yes |
| `GET` | `/api/v1/complaints/categories` | Retrieve list of authorized grievance categories | Yes |
| `GET` | `/api/v1/complaints/{id}` | Retrieve complaint dossier with attachments and audit timeline | Yes |
| `POST` | `/api/v1/complaints/{id}/transition` | Execute state transition under 12-state state machine rules | Yes |
| `POST` | `/api/v1/complaints/{id}/triage` | Trigger LangGraph multi-agent triage (Severity, Routing, Sieve, Plan) | Yes |

---

## 4. Overlap & Coordination Endpoints (`/api/v1/overlap`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/overlap/candidates` | List overlap candidate pairs with 8-stage sieve scores | Yes |
| `POST` | `/api/v1/overlap/scan` | Execute 8-stage sieve scan across active complaints | Yes |
| `POST` | `/api/v1/overlap/candidates/{id}/review` | Officer review: `Confirmed` (Link cases) or `Rejected` (False Positive) | Yes |

---

## 5. Model Context Protocol (MCP) Endpoints (`/api/v1/mcp`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/mcp/servers` | Inspect all 7 registered MCP servers, statuses, and tool manifests | Yes |
| `GET` | `/api/v1/mcp/servers/{server_id}/tools` | Retrieve tool schemas and parameter definitions for an MCP server | Yes |
| `POST` | `/api/v1/mcp/servers/{server_id}/call` | Execute a tool call against the server runtime and return result | Yes |

---

## 6. Hybrid RAG Endpoints (`/api/v1/rag`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/rag/query` | Hybrid BM25 + dense vector cosine retrieval with bureau access checks | Yes |

---

## 7. Integration Endpoints (`/api/v1/integrations`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/integrations/connectors` | List integration connectors (PGRC, RB, CSV/SFTP) and sync health | Yes |
| `POST` | `/api/v1/integrations/connectors/{type}/test` | Health ping / connectivity test against external gateway | Yes |
| `POST` | `/api/v1/integrations/connectors/{type}/sync` | Execute batch sync run from connector into local DB | Yes |
| `POST` | `/api/v1/integrations/connectors/csv-sftp/upload-dossier` | Ingest raw CSV complaint dossier for offline/regional desks | Yes |

---

## 8. Reports & Analytics (`/api/v1/reports`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/reports/dashboard` | Real-time database metrics, bureau workload, regional spread, SLA trends | Yes |
| `GET` | `/api/v1/reports/export/complaints` | Download complaints dataset in CSV format | Yes |
| `GET` | `/api/v1/reports/export/institutions` | Download institutions dataset in CSV format | Yes |

---

## 9. Immutable Audit Trail (`/api/v1/audit`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/audit/logs` | Query chronological audit logs with entity, action, and user filters | Yes |
| `GET` | `/api/v1/audit/security-events` | Retrieve security-critical events (failed logins, privilege changes) | Yes |

