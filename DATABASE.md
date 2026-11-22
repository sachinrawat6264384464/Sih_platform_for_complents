# AICTE NEXUS - DATABASE SCHEMA SPECIFICATION

Database Name: `aicte_nexus`  
Database Engine: PostgreSQL 13.22  
Port: 5433  
Key Extensions: `uuid-ossp`, `pg_trgm`, `fuzzystrmatch`

---

## Complete Entity Catalog

### 1. Identity & RBAC
- `users`: Core user accounts (officers, administrators, auditors).
- `roles`: Role definitions with hierarchical levels.
- `permissions`: Atomic capabilities (`COMPLAINT_CREATE`, `CASE_TRANSFER`, `OVERLAP_CONFIRM`, etc.).
- `user_roles`: Many-to-many user to role bindings.
- `role_permissions`: Many-to-many role to permission mappings.
- `user_bureau_assignments`: Bureau and region jurisdiction assignments.

### 2. Organizational Hierarchy
- `bureaus`: AICTE Bureaus (PGRC, Regulation Bureau, Approval Bureau, Finance, etc.).
- `regional_offices`: AICTE Regional Offices (Northern, Western, Southern, etc.).

### 3. Institutions & Identifiers
- `institutions`: Verified educational institutions with AICTE Permanent ID.
- `institution_aliases`: Alternate names, acronyms, and historical names.
- `institution_identifiers`: AISHE code, State code, University affiliation.

### 4. Complaints, Sources & Ingestion
- `source_systems`: Ingress channels (PGRC Portal, Regulation Bureau, Email, CSV Import).
- `source_records`: Raw immutable ingested records with hash and payload.
- `complaint_categories`: Standardized AICTE grievance taxonomy.
- `complaints`: Normalized complaint records with status, subject, description, priority.

### 5. Cases & Workflows
- `cases`: Coordination case records tracking multi-bureau response.
- `case_assignments`: Specific officer assignments with active duration.
- `case_status_history`: Chronological 12-state audit trail.
- `case_actions`: Regulatory notices, inspections, hearings, notes.
- `case_transfers`: Bureau-to-bureau transfer proposals with approval status.
- `case_escalations`: SLA breach escalations and seniority routing.
- `case_relationships`: Direct and indirect linkages between cases.

### 6. Overlap Detection & Graph Intelligence
- `overlap_candidates`: Computed overlap pairs with stage scores and confidence.
- `overlap_reviews`: Human officer verdicts (Confirmed, False Positive, Linked).

### 7. Documents, Notifications, SLAs & System
- `documents`: Uploaded evidence, notices, investigation reports.
- `document_versions`: Revision history and SHA-256 integrity checksums.
- `notifications`: User notifications with read status and delivery channels.
- `notification_preferences`: Per-officer alert settings.
- `sla_policies`: Bureau-specific deadline rules and grace periods.
- `sla_events`: SLA deadline breaches and warning milestones.
- `integration_configs`: Connector settings and credential vaults (encrypted).
- `integration_field_mappings`: Source field to canonical column transformations.
- `integration_sync_runs`: Scheduled and manual synchronization runs.
- `integration_failures`: Dead-letter queue for failed ingestions.
- `mcp_servers`: Registered Model Context Protocol endpoints.
- `mcp_tools`: Tool definitions, schemas, and approval requirements.
- `mcp_execution_logs`: Audit trail of all MCP tool invocations.
- `agent_runs`: LangGraph agent workflow runs.
- `agent_steps`: Granular agent reasoning traces and tool outputs.
- `retrieval_logs`: RAG retrieval performance and context evaluations.
- `audit_logs`: Immutable, append-only security and activity ledger.
- `security_events`: Failed logins, rate limits, unauthorized attempts.
- `system_settings`: Platform-wide configurations and feature flags.
- `approval_requests`: Human-in-the-loop pending approval queues.

