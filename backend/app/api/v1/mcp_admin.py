from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.mcp_servers.runtime import mcp_runtime
from app.models.auth import User
from app.models.mcp import MCPExecutionLog, MCPServer
from app.schemas.mcp import MCPExecutionLogOut, MCPServerOut, MCPToolInvokeRequest

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])


@router.get("/servers")
async def get_mcp_servers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    registered_names = mcp_runtime.list_servers()
    servers = []
    for s_name in registered_names:
        tools = mcp_runtime.list_tools(s_name)
        servers.append({
            "name": s_name,
            "transport": "in-process / stdio",
            "version": "2.0.0",
            "is_active": True,
            "health_status": "HEALTHY",
            "tools_count": len(tools),
            "tools": tools,
        })
    return servers


@router.get("/tools")
async def get_mcp_tools(server: Optional[str] = None, current_user: User = Depends(get_current_user)):
    tools = mcp_runtime.list_tools(server)
    return tools


@router.post("/invoke")
async def invoke_mcp_tool(
    request: MCPToolInvokeRequest,
    server: str = Query(..., description="Target MCP server name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await mcp_runtime.execute_tool(
            db=db,
            server_name=server,
            tool_name=request.tool_name,
            arguments=request.arguments,
            user=current_user,
        )
        return {"status": "SUCCESS", "server": server, "tool": request.tool_name, "output": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/logs", response_model=List[MCPExecutionLogOut])
async def get_execution_logs(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(MCPExecutionLog).order_by(MCPExecutionLog.created_at.desc()).limit(limit)
    logs = (await db.execute(query)).scalars().all()
    return logs
