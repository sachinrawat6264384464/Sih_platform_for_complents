# AICTE NEXUS — Testing & Quality Assurance Guide

## 1. Test Architecture

The testing suite validates:
1. **Health & Readiness Endpoints**: Database and Redis connection checks.
2. **Authentication & JWT Issuance**: Bcrypt password verification, access token issuance.
3. **Real Database Metrics**: Aggregations across institutions, complaints, SLA overdue counts.
4. **MCP Server & Tool Manifest**: Schema validation for all 7 registered servers.
5. **12-State Complaint Lifecycle**: Status transitions, invalid transition rejections (`400 Bad Request`).
6. **LangGraph AI Triage**: Verification of 5-node workflow execution and trace generation.
7. **Hybrid RAG Retrieval**: BM25 lexical + dense vector cosine scoring and ranking.

---

## 2. Executing Pytest Suite

From `backend/`:
```powershell
cd D:\sih_problm1.0\backend
.\venv\Scripts\Activate.ps1
pytest tests\test_api.py -v
```

### Expected Output:
```
tests/test_api.py::test_health_check PASSED                              [ 14%]
tests/test_api.py::test_root PASSED                                      [ 28%]
tests/test_api.py::test_admin_login PASSED                               [ 42%]
tests/test_api.py::test_dashboard_metrics PASSED                         [ 57%]
tests/test_api.py::test_mcp_servers_and_tools PASSED                     [ 71%]
tests/test_api.py::test_institution_and_complaint_lifecycle PASSED       [ 85%]
tests/test_api.py::test_hybrid_rag_query PASSED                          [100%]

============================== 7 passed in 7.24s ==============================
```

---

## 3. Frontend Verification

From `frontend/`:
```powershell
cd D:\sih_problm1.0\frontend
npm run build
```

Build succeeds with 14/14 static and dynamic routes compiled, typechecked, and prerendered.
