---
name: aicte-nexus-testing
description: Comprehensive testing guidelines for backend, frontend, MCP servers, and integration connectors
---

# Testing Skill - AICTE Nexus

## Test Organization
- `backend/tests/test_auth.py`: JWT token generation, expiration, role and bureau permission boundaries.
- `backend/tests/test_crud.py`: Institutions, complaints, bureaus, cases lifecycle CRUD.
- `backend/tests/test_workflow.py`: 12-state machine transitions, invalid status rejection, transition remarks.
- `backend/tests/test_overlap.py`: 8-stage duplicate and overlap detection scoring with synthetic test benchmarks.
- `backend/tests/test_mcp.py`: MCP tool contract tests verifying schema compliance and authorized invocation.
- `backend/tests/test_rag.py`: BM25 and vector retrieval accuracy and access filtering.

## Rules
1. Test fixtures must be explicitly marked with `TEST_DATA_` or `SYNTHETIC_`.
2. Never rely on production database records for test assertions.
3. Tests must run self-contained and clean up generated records.

