---
name: aicte-nexus-security
description: Security guidelines, credential protection, token handling, and data segregation for AICTE Nexus
---

# Security Skill - AICTE Nexus

## Security Standards
1. **Password Storage**: Passwords hashed with Bcrypt (cost factor 12).
2. **Token Security**:
   - Short-lived Access Tokens (60 min) signed with HS256/RS256.
   - Long-lived Refresh Tokens (7 days) with rotation and invalidation on logout.
3. **Role & Bureau Scoping**:
   - Access control checks both global role permissions (e.g. `COMPLAINT_READ`) and Bureau ownership (e.g. PGRC officer accessing PGRC cases only, unless explicit coordination granted).
4. **Data Protection**:
   - Sensitive applicant/complainant identification is protected.
   - File uploads validated for extension, MIME type, and size limits (max 25MB).
5. **No Credential Leakage**:
   - API keys and database connection passwords strictly in `.env`.
   - Never echo credentials in error messages or logs.

