from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp_servers.runtime import MCPToolDefinition, mcp_runtime
from app.models.auth import User
from app.models.document import Document

DOCUMENT_SERVER_NAME = "document_mcp_server"
mcp_runtime.register_server(DOCUMENT_SERVER_NAME)


async def search_documents(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    file_name = args.get("file_name", "").strip()
    query = select(Document).where(Document.file_name.ilike(f"%{file_name}%")).limit(10)
    docs = (await db.execute(query)).scalars().all()
    return {
        "documents": [
            {
                "id": str(d.id),
                "file_name": d.file_name,
                "document_type": d.document_type,
                "size_kb": round(d.file_size_bytes / 1024, 1),
                "is_confidential": d.is_confidential,
            }
            for d in docs
        ]
    }


mcp_runtime.register_tool(
    DOCUMENT_SERVER_NAME,
    MCPToolDefinition(
        name="search_documents",
        description="Search authorized uploaded evidence, regulatory notices, and inspection reports.",
        input_schema={"type": "object", "properties": {"file_name": {"type": "string"}}, "required": ["file_name"]},
        handler=search_documents,
        is_read_only=True,
    ),
)

