# AICTE NEXUS — Model Context Protocol (MCP) Runtime

AICTE NEXUS integrates **7 dedicated Model Context Protocol (MCP) servers** following the official Python MCP SDK standards. These servers expose standardized tools for autonomous AI agents, regional desks, and bureau portals.

---

## Registered MCP Servers

### 1. `aicte-pgrc-mcp` — Public Grievance Redressal Cell Server
- **Server ID**: `aicte-pgrc-mcp`
- **Focus**: Ingestion, status queries, and citizen grievance lookups.
- **Tools**:
  - `query_pgrc_complaints`: Query active PGRC cases with filters for status, date ranges, and priority.
  - `get_pgrc_case_details`: Retrieve full citizen grievance dossier by complaint number.

### 2. `aicte-rb-mcp` — Regulation Bureau Server
- **Server ID**: `aicte-rb-mcp`
- **Focus**: Regulatory notices, inspection orders, and show-cause proceedings.
- **Tools**:
  - `list_regulatory_actions`: Fetch active regulatory enforcement actions for an institution.
  - `issue_regulatory_notice`: Issue a formal regulatory notice or inspection directive.

### 3. `aicte-institution-mcp` — Technical Institution Registry Server
- **Server ID**: `aicte-institution-mcp`
- **Focus**: Institution lookup, alias resolution, and approval status verification.
- **Tools**:
  - `lookup_institution`: Search technical institutions by AICTE permanent ID or fuzzy name.
  - `get_institution_profile`: Fetch comprehensive institutional dossier including approval history.

### 4. `aicte-complaint-mcp` — Complaint Lifecycle & State Machine Server
- **Server ID**: `aicte-complaint-mcp`
- **Focus**: State transitions, officer assignments, and chronological history.
- **Tools**:
  - `get_complaint_lifecycle`: Query the 12-state workflow status and transition history of a complaint.
  - `transition_complaint_status`: Execute an authorized state transition with mandatory statutory remarks.

### 5. `aicte-reporting-mcp` — Analytics & Telemetry Server
- **Server ID**: `aicte-reporting-mcp`
- **Focus**: Real-time caseload aggregation, SLA compliance metrics, and bureau workload.
- **Tools**:
  - `get_dashboard_telemetry`: Retrieve real-time computed database metrics.
  - `get_bureau_workload_breakdown`: Retrieve caseload distribution across PGRC, Regulation Bureau, and Regional Desks.

### 6. `aicte-document-mcp` — Supporting Evidence & Document Server
- **Server ID**: `aicte-document-mcp`
- **Focus**: Document metadata, file validation, and audit logging.
- **Tools**:
  - `list_complaint_documents`: List supporting PDF/evidence documents attached to a grievance.

### 7. `aicte-notification-mcp` — Multi-Channel Notification Server
- **Server ID**: `aicte-notification-mcp`
- **Focus**: Officer assignment alerts, SLA warnings, and cross-bureau overlap notices.
- **Tools**:
  - `send_officer_notification`: Dispatch in-app notification to assigned bureau officer.

---

## MCP Tool Invocation Interface

AI agents and external callers invoke tools through the unified runtime API:
```http
POST /api/v1/mcp/servers/{server_id}/call
Authorization: Bearer <token>
Content-Type: application/json

{
  "tool_name": "lookup_institution",
  "arguments": {
    "identifier": "1-43289012"
  }
}
```

The runtime verifies authorization, executes the tool implementation via async database session, logs execution latency, and returns standardized output:
```json
{
  "success": true,
  "data": { ... },
  "latency_ms": 14.2
}
```

