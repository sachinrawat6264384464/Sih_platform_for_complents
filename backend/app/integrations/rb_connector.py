from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.integrations.base import BaseConnector, NormalizedIngestRecord


class RegulationBureauConnector(BaseConnector):
    """
    Regulation Bureau (RB) Connector
    Ingests official regulatory show-cause proceedings, expert visit findings, and penal actions.
    """

    async def test_connectivity(self) -> Dict[str, Any]:
        api_key = self.credentials.get("api_key")
        if not self.base_url or not api_key:
            return {
                "connected": False,
                "status": "NOT_CONFIGURED",
                "message": "Regulation Bureau internal URL or API key missing in integration vault.",
                "latency_ms": 0.0,
            }
        return {"connected": False, "status": "PENDING_CREDENTIALS", "simulated_mock_available": True}

    async def fetch_records(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        return [
            {
                "rb_case_ref": "RB-INQ-2026-0044",
                "institution_aicte_id": "1-1097234511",
                "institute_title": "Delhi Institute of Technology & Engineering",
                "inquiry_type": "FACULTY_SHORTAGE",
                "notice_title": "Show Cause Notice regarding AICTE-Faculty Ratio Non-Compliance",
                "details": "Inspection committee noted 60% deficiency in required cadre ratio for Computer Engineering.",
                "referral_date": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def normalize_record(self, raw_record: Dict[str, Any]) -> NormalizedIngestRecord:
        ref_str = raw_record.get("referral_date")
        ref_dt = datetime.fromisoformat(ref_str) if ref_str else datetime.now(timezone.utc)

        return NormalizedIngestRecord(
            source_case_id=raw_record.get("rb_case_ref", "UNKNOWN"),
            aicte_permanent_id=raw_record.get("institution_aicte_id", "UNKNOWN"),
            institution_name=raw_record.get("institute_title", "Unknown"),
            category_code=raw_record.get("inquiry_type", "FACULTY_SHORTAGE"),
            title=raw_record.get("notice_title", "Regulation Bureau Inquiry"),
            description=raw_record.get("details", ""),
            complainant_type="Regulatory Committee",
            priority="Critical",
            received_date=ref_dt,
            raw_payload=raw_record,
        )
