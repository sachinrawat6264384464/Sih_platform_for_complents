from abc import ABC, abstractmethod
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class NormalizedIngestRecord(BaseModel):
    source_case_id: str
    aicte_permanent_id: str
    institution_name: str
    category_code: str
    title: str
    description: str
    complainant_type: str = "Citizen"
    complainant_name: Optional[str] = None
    priority: str = "Medium"
    received_date: datetime
    raw_payload: Dict[str, Any]


class SyncResult(BaseModel):
    status: str  # SUCCESS, PARTIAL, FAILED
    records_fetched: int
    records_imported: int
    records_failed: int
    details: Dict[str, Any] = {}
    error_message: Optional[str] = None


class BaseConnector(ABC):
    def __init__(self, config_id: UUID, name: str, base_url: Optional[str] = None, credentials: Optional[Dict[str, Any]] = None):
        self.config_id = config_id
        self.name = name
        self.base_url = base_url
        self.credentials = credentials or {}

    @abstractmethod
    async def test_connectivity(self) -> Dict[str, Any]:
        """Verify network connectivity and credentials with external bureau/system."""
        pass

    @abstractmethod
    async def fetch_records(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch raw external records since last sync checkpoint."""
        pass

    @abstractmethod
    def normalize_record(self, raw_record: Dict[str, Any]) -> NormalizedIngestRecord:
        """Map and normalize vendor/bureau specific schema into standard AICTE schema."""
        pass

    def compute_payload_hash(self, raw_payload: Dict[str, Any]) -> str:
        serialized = json.dumps(raw_payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
