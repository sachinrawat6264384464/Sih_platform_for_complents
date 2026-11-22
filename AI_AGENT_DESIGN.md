# AICTE NEXUS — LangGraph Multi-Agent Architecture

## 1. Multi-Agent Triage Paradigm

In AICTE NEXUS, incoming complaints pass through a coordinated multi-agent graph powered by **LangGraph**. The workflow replaces disconnected manual triage with structured, evidence-backed evaluation:

```
                  +-------------------------+
                  |     Ingestion Agent     |
                  +-------------------------+
                               |
                               v
                  +-------------------------+
                  |  Classification Agent   |
                  +-------------------------+
                               |
                               v
                  +-------------------------+
                  |      Routing Agent      |
                  +-------------------------+
                               |
                               v
                  +-------------------------+
                  | Duplicate Detection Agt |
                  +-------------------------+
                               |
                               v
                  +-------------------------+
                  | Action Formulation Agt  |
                  +-------------------------+
                               |
                               v
                         [Triage State]
```

---

## 2. Agent Node Roles

### A. Ingestion Agent (`ingest_node`)
- Validates the incoming complaint payload.
- Verifies target institution exists in the AICTE directory or initiates entity resolution.
- Normalizes free-form text, strips illegal formatting, and assigns ingestion metadata.

### B. Classification Agent (`classify_node`)
- Performs rule-based and semantic classification of violations:
  - Severity assessment: `Low`, `Medium`, `High`, `Critical`.
  - Regulatory violation category: `Fee Violations`, `Faculty Shortage`, `Infrastructure Deficit`, `Capitation Fee`, `Certificate Withholding`.

### C. Bureau Routing Agent (`route_node`)
- Evaluates statutory jurisdiction:
  - Individual student/parent fee issues -> **Public Grievance Redressal Cell (PGRC)**.
  - Institutional approval non-compliance, land/building norm violations -> **Regulation Bureau (RB)**.
  - Local inspection requirements -> **Regional Offices (CRO, NRO, WRO, etc.)**.
- Computes target statutory SLA window (e.g. 15, 30, or 60 days).

### D. Duplicate Detection Agent (`duplicate_check_node`)
- Invokes the **8-Stage Sieve Engine** (`OverlapEngine`).
- Cross-matches against active complaints across ALL bureaus.
- Extracts overlap confidence score and flags related cases.

### E. Action Formulation Agent (`summarize_node`)
- Generates an actionable executive summary for the bureau officer.
- Proposes immediate next steps (e.g., "Request fee receipts from college", "Issue notice under Section 10(p)").
- Records an immutable trace log in `ai_agent_traces` for transparency.

---

## 3. Human-in-the-Loop Safety Rule

AICTE NEXUS strictly adheres to the **Human-in-the-Loop Principle**:
- Agents **advise and triage**; they **NEVER** automatically close, reject, or dispose of complaints without human officer authorization.
- Overlap matches must be explicitly reviewed and confirmed by an authorized officer in the Coordination Workspace.

