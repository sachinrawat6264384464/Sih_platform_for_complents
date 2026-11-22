from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.integrations.base import BaseConnector, NormalizedIngestRecord, SyncResult
from app.integrations.csv_sftp_connector import CSVSFTPConnector
from app.integrations.pgrc_connector import PGRCConnector
from app.integrations.rb_connector import RegulationBureauConnector
from app.models.bureau import Bureau
from app.models.complaint import Complaint, ComplaintCategory, ComplaintStatus, SourceRecord, SourceSystem
from app.models.institution import Institution
from app.models.integration import IntegrationConfig, IntegrationFailure, IntegrationSyncRun
from app.services.complaint_service import create_complaint
from app.services.overlap_engine import scan_complaint_for_overlaps

CONNECTOR_MAP: Dict[str, Type[BaseConnector]] = {
    "PGRC": PGRCConnector,
    "RB": RegulationBureauConnector,
    "CSV_SFTP": CSVSFTPConnector,
}


def get_connector_instance(config: IntegrationConfig) -> BaseConnector:
    connector_cls = CONNECTOR_MAP.get(config.connector_type, CSVSFTPConnector)
    return connector_cls(
        config_id=config.id,
        name=config.name,
        base_url=config.base_url,
        credentials=config.encrypted_credentials,
    )


async def execute_sync_run(db: AsyncSession, config_id: UUID) -> SyncResult:
    config = (await db.execute(select(IntegrationConfig).where(IntegrationConfig.id == config_id))).scalar_one_or_none()
    if not config:
        return SyncResult(status="FAILED", records_fetched=0, records_imported=0, records_failed=0, error_message="Integration configuration not found.")

    if config.is_paused or not config.is_active:
        return SyncResult(status="FAILED", records_fetched=0, records_imported=0, records_failed=0, error_message="Integration is currently disabled or paused.")

    sync_run = IntegrationSyncRun(
        integration_config_id=config.id,
        started_at=datetime.now(timezone.utc),
        status="Running"
    )
    db.add(sync_run)
    await db.flush()

    connector = get_connector_instance(config)
    records_fetched = 0
    records_imported = 0
    records_failed = 0

    try:
        raw_records = await connector.fetch_records(since=config.last_sync_at)
        records_fetched = len(raw_records)

        # Resolve Source System
        source_sys = (await db.execute(select(SourceSystem).where(SourceSystem.code == config.connector_type))).scalar_one_or_none()
        if not source_sys:
            source_sys = (await db.execute(select(SourceSystem).where(SourceSystem.code == "PGRC_PORTAL"))).scalar_one()

        # Resolve Bureau
        bureau = (await db.execute(select(Bureau).where(Bureau.code == config.connector_type))).scalar_one_or_none()
        if not bureau:
            bureau = (await db.execute(select(Bureau).where(Bureau.code == "PGRC"))).scalar_one()

        for raw in raw_records:
            try:
                norm: NormalizedIngestRecord = connector.normalize_record(raw)
                p_hash = connector.compute_payload_hash(norm.raw_payload)

                # 1. Idempotency Check: Skip duplicate raw hashes from same source
                existing_rec = (await db.execute(
                    select(SourceRecord).where(
                        SourceRecord.source_system_id == source_sys.id,
                        SourceRecord.payload_hash == p_hash
                    )
                )).scalar_one_or_none()

                if existing_rec:
                    continue  # Idempotently skip already processed identical payload

                source_record = SourceRecord(
                    source_system_id=source_sys.id,
                    original_case_id=norm.source_case_id,
                    payload_hash=p_hash,
                    raw_payload=norm.raw_payload,
                    sync_timestamp=datetime.now(timezone.utc),
                )
                db.add(source_record)
                await db.flush()

                # 2. Match or Create Institution
                inst = (await db.execute(select(Institution).where(Institution.aicte_permanent_id == norm.aicte_permanent_id))).scalar_one_or_none()
                if not inst:
                    inst = Institution(
                        aicte_permanent_id=norm.aicte_permanent_id,
                        name=norm.institution_name,
                        address="Imported from " + config.name,
                        city="New Delhi",
                        district="New Delhi",
                        state="Delhi",
                        approval_status="Approved",
                        is_verified=False,
                    )
                    db.add(inst)
                    await db.flush()

                # 3. Match Category
                cat = (await db.execute(select(ComplaintCategory).where(ComplaintCategory.code == norm.category_code))).scalar_one_or_none()
                if not cat:
                    cat = (await db.execute(select(ComplaintCategory).where(ComplaintCategory.code == "INFRASTRUCTURE"))).scalar_one()

                # 4. Ingest Complaint
                complaint = Complaint(
                    complaint_number=f"AICTE-SYNC-{datetime.now().strftime('%y%m')}-{norm.source_case_id[-6:]}",
                    institution_id=inst.id,
                    bureau_id=bureau.id,
                    source_system_id=source_sys.id,
                    source_record_id=source_record.id,
                    category_id=cat.id,
                    title=norm.title,
                    description=norm.description,
                    complainant_type=norm.complainant_type,
                    complainant_name=norm.complainant_name,
                    status=ComplaintStatus.RECEIVED,
                    received_date=norm.received_date,
                    is_overlapping=False,
                )
                db.add(complaint)
                await db.flush()

                # Scan for overlaps
                await scan_complaint_for_overlaps(db, complaint.id)

                records_imported += 1

            except Exception as rec_err:
                records_failed += 1
                failure = IntegrationFailure(
                    integration_config_id=config.id,
                    sync_run_id=sync_run.id,
                    original_identifier=str(raw.get("case_id") or raw.get("pgrc_ticket_id") or "UNKNOWN"),
                    raw_record=raw,
                    error_reason=str(rec_err),
                    retry_count=0,
                    is_resolved=False
                )
                db.add(failure)

        sync_run.status = "Success" if records_failed == 0 else "Partial"
        sync_run.completed_at = datetime.now(timezone.utc)
        sync_run.records_fetched = records_fetched
        sync_run.records_imported = records_imported
        sync_run.records_failed = records_failed

        config.last_sync_at = datetime.now(timezone.utc)
        config.last_sync_status = sync_run.status
        config.error_message = None

        await db.commit()
        return SyncResult(
            status=sync_run.status,
            records_fetched=records_fetched,
            records_imported=records_imported,
            records_failed=records_failed,
        )

    except Exception as exc:
        records_failed = records_fetched
        sync_run.status = "Failed"
        sync_run.completed_at = datetime.now(timezone.utc)
        sync_run.records_failed = records_failed

        config.last_sync_status = "FAILED"
        config.error_message = str(exc)

        await db.commit()
        return SyncResult(
            status="FAILED",
            records_fetched=records_fetched,
            records_imported=0,
            records_failed=records_failed,
            error_message=str(exc),
        )
