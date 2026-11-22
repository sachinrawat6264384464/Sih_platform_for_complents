from fastapi import APIRouter, Depends, Response
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_optional_current_user, require_permission
from app.core.database import get_db
from app.models.auth import User
from app.schemas.reports import DashboardMetricsOut
from app.services.report_service import generate_complaints_csv, generate_complaints_excel, get_dashboard_metrics

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


@router.get("/dashboard", response_model=DashboardMetricsOut)
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    metrics = await get_dashboard_metrics(db)
    return metrics


@router.get("/export/csv")
async def export_csv(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("REPORT_GENERATE")),
):
    csv_data = await generate_complaints_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="aicte_nexus_complaints.csv"'},
    )


@router.get("/export/excel")
async def export_excel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("REPORT_GENERATE")),
):
    excel_data = await generate_complaints_excel(db)
    return Response(
        content=excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="aicte_nexus_complaints.xlsx"'},
    )

