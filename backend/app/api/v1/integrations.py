from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.integrations.csv_sftp_connector import CSVSFTPConnector
from app.integrations.registry import execute_sync_run, get_connector_instance
from app.models.auth import User
from app.models.bureau import Bureau
from app.models.complaint import Complaint, ComplaintCategory, ComplaintStatus, SourceRecord, SourceSystem
from app.models.institution import Institution
from app.models.integration import IntegrationConfig, IntegrationFailure, IntegrationSyncRun
from app.schemas.integration import (
    IntegrationConfigCreate,
    IntegrationConfigOut,
    IntegrationConfigUpdate,
    IntegrationSyncRunOut,
)
from app.services.audit_service import record_audit_log
from app.services.overlap_engine import scan_complaint_for_overlaps

router = APIRouter(prefix="/integrations", tags=["Integrations & Connectors"])


@router.get("", response_model=List[IntegrationConfigOut])
async def get_integrations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    configs = (await db.execute(select(IntegrationConfig).order_by(IntegrationConfig.name))).scalars().all()
    return configs


@router.post("", response_model=IntegrationConfigOut, status_code=status.HTTP_201_CREATED)
async def create_integration(
    data: IntegrationConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("INTEGRATION_MANAGE")),
):
    config = IntegrationConfig(
        name=data.name,
        connector_type=data.connector_type,
        base_url=data.base_url,
        auth_type=data.auth_type,
        encrypted_credentials=data.credentials,
        sync_frequency_minutes=data.sync_frequency_minutes,
        webhook_secret=data.webhook_secret,
    )
    db.add(config)
    await record_audit_log(
        db,
        action="CREATE_INTEGRATION",
        entity_type="INTEGRATION_CONFIG",
        entity_id=config.id,
        user_id=current_user.id,
        changes={"name": data.name, "connector_type": data.connector_type}
    )
    await db.commit()
    await db.refresh(config)
    return config


@router.post("/{config_id}/test")
async def test_integration_connectivity(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("INTEGRATION_MANAGE")),
):
    config = (await db.execute(select(IntegrationConfig).where(IntegrationConfig.id == config_id))).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration config not found.")

    connector = get_connector_instance(config)
    test_result = await connector.test_connectivity()
    return test_result


@router.post("/{config_id}/sync")
async def trigger_sync(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("INTEGRATION_MANAGE")),
):
    result = await execute_sync_run(db, config_id)
    return result


@router.get("/runs", response_model=List[IntegrationSyncRunOut])
async def get_sync_runs(
    config_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(IntegrationSyncRun).order_by(IntegrationSyncRun.started_at.desc()).limit(50)
    if config_id:
        query = query.where(IntegrationSyncRun.integration_config_id == config_id)
    runs = (await db.execute(query)).scalars().all()
    return runs


@router.post("/upload-csv")
async def upload_batch_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("INTEGRATION_MANAGE")),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only standard CSV files are accepted.")

    content = await file.read()
    csv_text = content.decode("utf-8", errors="ignore")

    csv_connector = CSVSFTPConnector(config_id=current_user.id, name="CSV Upload")
    records = csv_connector.parse_csv_stream(csv_text)

    source_sys = (await db.execute(select(SourceSystem).where(SourceSystem.code == "MANUAL_CSV"))).scalar_one()
    default_bureau = (await db.execute(select(Bureau).where(Bureau.code == "PGRC"))).scalar_one()
    default_cat = (await db.execute(select(ComplaintCategory).where(ComplaintCategory.code == "INFRASTRUCTURE"))).scalar_one()

    imported_count = 0
    for r in records:
        inst = (await db.execute(select(Institution).where(Institution.aicte_permanent_id == r.aicte_permanent_id))).scalar_one_or_none()
        if not inst:
            inst = Institution(
                aicte_permanent_id=r.aicte_permanent_id,
                name=r.institution_name,
                address="Uploaded from CSV",
                city="New Delhi",
                district="New Delhi",
                state="Delhi",
                approval_status="Approved",
                is_verified=False,
            )
            db.add(inst)
            await db.flush()

        complaint = Complaint(
            complaint_number=f"AICTE-CSV-{int(datetime.now().timestamp())}-{imported_count+1}",
            institution_id=inst.id,
            bureau_id=default_bureau.id,
            source_system_id=source_sys.id,
            category_id=default_cat.id,
            title=r.title,
            description=r.description,
            complainant_type=r.complainant_type,
            complainant_name=r.complainant_name,
            status=ComplaintStatus.RECEIVED,
            received_date=r.received_date,
            is_overlapping=False,
        )
        db.add(complaint)
        await db.flush()
        await scan_complaint_for_overlaps(db, complaint.id)
        imported_count += 1

    await db.commit()
    return {"message": f"Successfully parsed and ingested {imported_count} complaints from CSV.", "count": imported_count}
