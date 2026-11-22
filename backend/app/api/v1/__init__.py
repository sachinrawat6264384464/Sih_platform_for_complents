from fastapi import APIRouter
from app.api.v1.agents import router as agents_router
from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.bureaus import router as bureaus_router
from app.api.v1.cases import router as cases_router
from app.api.v1.complaints import router as complaints_router
from app.api.v1.institutions import router as institutions_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.mcp_admin import router as mcp_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.officers import router as officers_router
from app.api.v1.overlap import router as overlap_router
from app.api.v1.rag import router as rag_router
from app.api.v1.reports import router as reports_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(institutions_router)
api_v1_router.include_router(complaints_router)
api_v1_router.include_router(cases_router)
api_v1_router.include_router(bureaus_router)
api_v1_router.include_router(officers_router)
api_v1_router.include_router(overlap_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(integrations_router)
api_v1_router.include_router(mcp_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(audit_router)
