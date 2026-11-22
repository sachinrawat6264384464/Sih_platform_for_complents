# AICTE NEXUS — External System Integration Guide

## 1. Overview

AICTE Bureaus and regional offices may operate different systems, legacy databases, or disconnected offline workflows. AICTE NEXUS solves this through a **connector-based integration architecture**:

```
+-----------------------------------------------------------------+
|                       AICTE NEXUS CORE                          |
|             (Consolidated Monitoring & Overlap Sieve)           |
+-----------------------------------------------------------------+
                                ^
                                |
             +------------------+------------------+
             |                                     |
   [REST / Webhook Gateway]              [Batch Ingestion Gateway]
             |                                     |
    +--------+--------+                            |
    |                 |                            v
 [PGRC API]   [Regulation Bureau]         [CSV / SFTP Dossiers]
  Connector        Connector                    Connector
```

---

## 2. Connector Types

### A. PGRC Connector (`PGRCConnector`)
- **Mode**: REST API polling and webhook listener.
- **Target**: Public Grievance Redressal Cell portal.
- **Synchronization**: Pulls citizen complaints with fields: citizen details, institution permanent ID, category, priority, and date.
- **Deduplication**: Maps to `Complaint` model; triggers 8-stage sieve scan upon ingestion.

### B. Regulation Bureau Connector (`RegulationBureauConnector`)
- **Mode**: Direct database sync / secure REST gateway.
- **Target**: Regulation Bureau show-cause & approval records.
- **Synchronization**: Syncs regulatory notices, pending compliance audits, and inspection recommendations.

### C. CSV / SFTP Batch Ingestion Connector (`CSVSFTPConnector`)
- **Mode**: Automated folder monitoring / manual multipart web upload.
- **Target**: Air-gapped regional offices or offline cells.
- **CSV Format Specification**:
  ```csv
  complaint_number,aicte_permanent_id,institution_name,category,title,description,priority
  PGRC-2026-9011,1-43289012,Delhi Tech College,Fee Violation,Demanding Capitation,Mandatory capitation fee demanded,High
  ```
- **Validation**:
  1. Header conformity check
  2. Non-empty required columns
  3. AICTE permanent ID format check (`1-[0-9]+`)
  4. Automatic institution resolution or creation

---

## 3. Webhook Integration for Future Bureau Systems

External bureaus can push real-time grievances to AICTE NEXUS via:
```http
POST /api/v1/integrations/webhook/{connector_key}
X-AICTE-Signature: <hmac-sha256>
Content-Type: application/json

{
  "event": "complaint.created",
  "complaint_number": "RB-2026-0045",
  "aicte_permanent_id": "1-98765432",
  "category": "Faculty Shortage",
  "title": "Severe faculty shortage in Mechanical Engineering",
  "description": "50% faculty positions vacant during inspection",
  "priority": "High"
}
```
