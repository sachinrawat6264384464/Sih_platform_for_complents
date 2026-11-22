# AICTE NEXUS - EXTERNAL INTEGRATION STATUS

In strict compliance with Master Project Non-Negotiable Rules:
- No invented external API endpoints.
- No fabricated AICTE integration credentials.
- No unsupported claims about live connectivity.
- Provide a clear `NOT CONFIGURED` or `MOCK / SIMULATED READY` state with exact access requirements documented.

---

## Connector Catalog

### 1. PGRC (Public Grievance Redressal Cell) Connector
- **Type**: REST / OAuth2 API & Webhooks
- **Protocol**: HTTP/JSON
- **Configured State**: `MOCK_AVAILABLE / PENDING_CREDENTIALS`
- **Required Production Credentials**:
  - `PGRC_PORTAL_BASE_URL` (e.g., `https://pgrc.aicte-india.org/api/v1`)
  - `PGRC_CLIENT_ID`
  - `PGRC_CLIENT_SECRET`
  - `PGRC_WEBHOOK_SECRET`
- **Capabilities**: Ingest grievance records, sync complaint updates, push coordination notes.

### 2. Regulation Bureau (RB) Connector
- **Type**: REST API & Database View
- **Protocol**: HTTP / Read-Only Postgres Replica
- **Configured State**: `MOCK_AVAILABLE / PENDING_CREDENTIALS`
- **Required Production Credentials**:
  - `RB_PORTAL_BASE_URL` (e.g., `https://approval.aicte-india.org/rb/api`)
  - `RB_API_KEY`
- **Capabilities**: Fetch ongoing inquiries, disciplinary notices, penal actions, show-cause notices.

### 3. Regional Office Connector
- **Type**: Multi-region REST / SFTP Sync
- **Protocol**: SFTP / Batch CSV
- **Configured State**: `MOCK_AVAILABLE / PENDING_CREDENTIALS`
- **Regions Supported**: Northern (Kanpur), Western (Mumbai), Southern (Chennai), Eastern (Kolkata), South-Western (Bangalore), Central (Bhopal), North-Western (Chandigarh).
- **Required Production Credentials**:
  - `REGIONAL_SFTP_HOST`
  - `REGIONAL_SFTP_PORT`
  - `REGIONAL_SFTP_USER`
  - `REGIONAL_SSH_KEY`

### 4. Approved Email Complaints Ingestion
- **Type**: IMAP / POP3 / Microsoft Graph / Google Workspace Mail
- **Protocol**: IMAP/TLS or OAuth2 REST
- **Configured State**: `MOCK_AVAILABLE / PENDING_CREDENTIALS`
- **Required Production Credentials**:
  - `MAIL_IMAP_SERVER`
  - `MAIL_USERNAME`
  - `MAIL_PASSWORD` or `MAIL_OAUTH_TOKEN`

### 5. CSV / Excel Manual & SFTP Batch Ingestion
- **Type**: File Upload & Local / Remote SFTP Ingestion
- **Protocol**: Multipart HTTP Upload & Local Batch Import
- **Configured State**: `FULLY_OPERATIONAL`
- **Capabilities**: Standard AICTE CSV schema import, idempotency validation, duplicate filtering, dead-letter logging.

