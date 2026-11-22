import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth import User
from app.models.bureau import Bureau
from app.models.complaint import Complaint
from app.models.institution import Institution
from app.models.mcp import MCPExecutionLog, MCPServer, MCPTool


class MCPToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable,
        is_read_only: bool = True,
        required_permission: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler
        self.is_read_only = is_read_only
        self.required_permission = required_permission


class MCPRuntime:
    """
    Model Context Protocol (MCP) Client Runtime for AICTE Nexus.
    Manages in-process and stdio/HTTP MCP tools, permissions, and audit trails.
    """

    def __init__(self):
        self._registry: Dict[str, Dict[str, MCPToolDefinition]] = {}

    def register_server(self, server_name: str):
        if server_name not in self._registry:
            self._registry[server_name] = {}

    def register_tool(self, server_name: str, tool_def: MCPToolDefinition):
        if server_name not in self._registry:
            self.register_server(server_name)
        self._registry[server_name][tool_def.name] = tool_def

    def list_servers(self) -> List[str]:
        return list(self._registry.keys())

    def list_tools(self, server_name: Optional[str] = None) -> List[Dict[str, Any]]:
        tools = []
        servers = [server_name] if server_name else self._registry.keys()
        for s_name in servers:
            for t_name, t_def in self._registry.get(s_name, {}).items():
                tools.append({
                    "server": s_name,
                    "name": t_def.name,
                    "description": t_def.description,
                    "input_schema": t_def.input_schema,
                    "is_read_only": t_def.is_read_only,
                })
        return tools

    async def execute_tool(
        self,
        db: AsyncSession,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        server_tools = self._registry.get(server_name)
        if not server_tools or tool_name not in server_tools:
            raise ValueError(f"MCP Tool '{tool_name}' on server '{server_name}' not found.")

        tool_def = server_tools[tool_name]

        # Check permissions for non-read-only tools
        if not tool_def.is_read_only:
            if not user or not user.is_superuser:
                raise PermissionError(f"Mutating tool '{tool_name}' requires human approval or Super Admin privilege.")

        # Execute handler
        status = "SUCCESS"
        output = None
        try:
            output = await tool_def.handler(db, arguments, user)
        except Exception as e:
            status = "ERROR"
            output = {"error": str(e)}
            raise e
        finally:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            # Log execution to database
            server_rec = (await db.execute(select(MCPServer).where(MCPServer.name == server_name))).scalar_one_or_none()
            if server_rec:
                log = MCPExecutionLog(
                    mcp_server_id=server_rec.id,
                    tool_name=tool_name,
                    invoked_by_id=user.id if user else None,
                    input_arguments=arguments,
                    output_payload=output if isinstance(output, dict) else {"result": str(output)},
                    status=status,
                    duration_ms=duration_ms
                )
                db.add(log)
                await db.commit()

        return output


mcp_runtime = MCPRuntime()
