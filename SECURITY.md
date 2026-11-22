# AICTE NEXUS — Government-Grade Security Architecture

## 1. Authentication & Session Management

- **Password Hashing**: Direct native `bcrypt` with 12 rounds of work factor. Passwords are never stored in plaintext or reversible formats.
- **Token Mechanism**: Standard JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`).
- **Token Expiration**:
  - Access Token: 60 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES=60`).
  - Refresh Token: 7 days (`REFRESH_TOKEN_EXPIRE_DAYS=7`).
- **Automatic Session Expiry**: The frontend interceptor detects HTTP 401, clears tokens from storage, and redirects to `/login?expired=1`.

---

## 2. Role-Based Access Control (RBAC)

The platform enforces a multi-tier permission matrix:

| Permission Code | Description | Roles |
|---|---|---|
| `COMPLAINTS_VIEW` | Read complaints in officer's assigned bureau | Officer, Bureau Lead, Super Admin |
| `COMPLAINTS_CREATE` | Ingest new grievances | Officer, Bureau Lead, Super Admin |
| `COMPLAINTS_TRANSITION` | Transition complaint state machine | Bureau Lead, Super Admin |
| `OVERLAP_REVIEW` | Confirm or reject overlap candidates | Bureau Lead, Super Admin |
| `INTEGRATIONS_MANAGE` | Trigger syncs, configure connectors | Bureau Lead, Super Admin |
| `MCP_EXECUTE` | Invoke MCP server tools | All Authorized Roles |
| `ADMIN_FULL` | Superuser management across all bureaus | Super Admin (`admin`) |

---

## 3. Immutable Security & Audit Trail

All sensitive operations write to the `audit_logs` table via `AuditService.log_action`:
- `USER_LOGIN`
- `CREATE_INSTITUTION`
- `CREATE_COMPLAINT`
- `STATUS_TRANSITION`
- `OVERLAP_SCAN`
- `CONFIRM_LINK`
- `MCP_CALL`

Each audit entry captures:
- Timestamp (UTC)
- Actor User ID & Username
- Action Type
- Target Entity Type & ID
- Client IP Address & User Agent
- Detailed JSON before/after state diff

---

## 4. Injection & Database Protection

- **SQL Injection Defense**: 100% parameterization via SQLAlchemy 2.0 ORM and Core expressions. No raw SQL string concatenation.
- **Input Validation**: Pydantic v2 schemas strictly validate every request body and query parameter.
- **CORS Protection**: Explicit allowed origin whitelist (`http://localhost:3000`, `http://127.0.0.1:3000`).
