import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OPERATIONAL"
        assert data["database"] == "HEALTHY"


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "AICTE" in data["platform"]
        assert data["status"] == "ONLINE"


@pytest.mark.asyncio
async def test_admin_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username_or_email": "admin",
                "password": "AicteNexus@2026SecureAdmin"
            }
        )
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        # Verify /me endpoint
        token = token_data["access_token"]
        me_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["username"] == "admin"
        assert me_data["is_superuser"] is True
        assert "SUPER_ADMIN" in me_data["roles"]


@pytest.mark.asyncio
async def test_dashboard_metrics():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First login
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": "admin", "password": "AicteNexus@2026SecureAdmin"}
        )
        token = login_res.json()["access_token"]

        res = await client.get(
            "/api/v1/reports/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert "total_institutions" in data
        assert "total_complaints" in data
        assert "bureau_workload" in data
        assert len(data["bureau_workload"]) >= 4  # PGRC, RB, AB, PB


@pytest.mark.asyncio
async def test_mcp_servers_and_tools():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": "admin", "password": "AicteNexus@2026SecureAdmin"}
        )
        token = login_res.json()["access_token"]

        # List MCP servers
        servers_res = await client.get("/api/v1/mcp/servers", headers={"Authorization": f"Bearer {token}"})
        assert servers_res.status_code == 200
        servers = servers_res.json()
        assert len(servers) >= 7

        # List MCP tools
        tools_res = await client.get("/api/v1/mcp/tools", headers={"Authorization": f"Bearer {token}"})
        assert tools_res.status_code == 200
        tools = tools_res.json()
        tool_names = [t["name"] for t in tools]
        assert "get_pgrc_complaints" in tool_names
        assert "get_rb_cases" in tool_names
        assert "search_institution" in tool_names
        assert "generate_bureau_report" in tool_names


@pytest.mark.asyncio
async def test_institution_and_complaint_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": "admin", "password": "AicteNexus@2026SecureAdmin"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Institution
        perm_id = "TEST-1-9876543210"
        inst_res = await client.post(
            "/api/v1/institutions",
            headers=headers,
            json={
                "aicte_permanent_id": perm_id,
                "name": "TEST AICTE National College of Engineering",
                "alternate_names": ["TANCE", "AICTE Tech College"],
                "institution_type": "Autonomous",
                "address": "Nelson Mandela Marg, Vasant Kunj",
                "city": "New Delhi",
                "district": "New Delhi",
                "state": "Delhi",
                "pincode": "110070",
                "approval_status": "Approved"
            }
        )
        assert inst_res.status_code in [201, 400]
        if inst_res.status_code == 201:
            inst_data = inst_res.json()
            inst_id = inst_data["id"]
        else:
            get_inst = await client.get(f"/api/v1/institutions/permanent-id/{perm_id}", headers=headers)
            inst_id = get_inst.json()["id"]

        # 2. Get Bureau & Category
        bureaus_res = await client.get("/api/v1/bureaus", headers=headers)
        bureau_id = bureaus_res.json()[0]["id"]

        cats_res = await client.get("/api/v1/complaints/categories", headers=headers)
        cat_id = cats_res.json()[0]["id"]

        # 3. Create Complaint
        comp_res = await client.post(
            "/api/v1/complaints",
            headers=headers,
            json={
                "institution_id": inst_id,
                "bureau_id": bureau_id,
                "category_id": cat_id,
                "title": "TEST Overcharging of examination fee and capitation",
                "description": "College is demanding additional 25,000 INR mandatory charge before releasing hall ticket.",
                "priority": "High"
            }
        )
        assert comp_res.status_code == 201
        comp_data = comp_res.json()
        assert comp_data["status"] == "Received"
        complaint_id = comp_data["id"]

        # 4. Status Transition: Received -> Acknowledged
        trans_res = await client.post(
            f"/api/v1/complaints/{complaint_id}/transition",
            headers=headers,
            json={
                "new_status": "Acknowledged",
                "remarks": "Complaint verified and assigned to grievance cell officer."
            }
        )
        assert trans_res.status_code == 200
        assert trans_res.json()["status"] == "Acknowledged"

        # 5. Invalid Transition: Acknowledged -> Disposed (Should Fail 400)
        invalid_res = await client.post(
            f"/api/v1/complaints/{complaint_id}/transition",
            headers=headers,
            json={
                "new_status": "Disposed",
                "remarks": "Premature disposal without investigation."
            }
        )
        assert invalid_res.status_code == 400

        # 6. Run AI Triage Workflow
        triage_res = await client.post(f"/api/v1/complaints/{complaint_id}/triage", headers=headers)
        assert triage_res.status_code == 200
        triage_data = triage_res.json()
        assert triage_data["status"] == "COMPLETED"
        assert len(triage_data["state"]["trace"]) >= 4


@pytest.mark.asyncio
async def test_hybrid_rag_query():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": "admin", "password": "AicteNexus@2026SecureAdmin"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = await client.post(
            "/api/v1/rag/query",
            headers=headers,
            json={"query": "capitation fee hall ticket extra charges", "top_k": 3}
        )
        assert res.status_code == 200
        data = res.json()
        assert "results" in data
        assert "latency_ms" in data
        assert len(data["results"]) > 0
        top_match = data["results"][0]
        assert "hybrid_score" in top_match
        assert "bm25_score" in top_match
        assert "vector_score" in top_match
