from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp_servers.runtime import MCPToolDefinition, mcp_runtime
from app.models.auth import User
from app.services.report_service import get_dashboard_metrics

REPORTING_SERVER_NAME = "reporting_mcp_server"
mcp_runtime.register_server(REPORTING_SERVER_NAME)


async def generate_bureau_report(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    metrics = await get_dashboard_metrics(db)
    return {
        "bureau_workloads": metrics["bureau_workload"],
        "total_complaints": metrics["total_complaints"],
        "pending_complaints": metrics["pending_complaints"],
    }


async def generate_sla_report(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    metrics = await get_dashboard_metrics(db)
    return {
        "sla_compliance_rate": metrics["sla_compliance_rate"],
        "overdue_complaints": metrics["overdue_complaints"],
        "pending_complaints": metrics["pending_complaints"],
    }


mcp_runtime.register_tool(
    REPORTING_SERVER_NAME,
    MCPToolDefinition(
        name="generate_bureau_report",
        description="Aggregate real-time complaint workloads, pending queues, and disposal counts across all AICTE bureaus.",
        input_schema={"type": "object", "properties": {}},
        handler=generate_bureau_report,
        is_read_only=True,
    ),
)

mcp_runtime.register_tool(
    REPORTING_SERVER_NAME,
    MCPToolDefinition(
        name="generate_sla_report",
        description="Calculate SLA adherence statistics, overdue breaches, and impending deadlines.",
        input_schema={"type": "object", "properties": {}},
        handler=generate_sla_report,
        is_read_only=True,
    ),
)

