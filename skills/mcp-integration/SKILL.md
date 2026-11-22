---
name: aicte-nexus-mcp-integration
description: Model Context Protocol (MCP) server architecture, tool safety, authorization, and discovery for AICTE Nexus
---

# MCP Integration Skill - AICTE Nexus

## MCP Architectural Overview
AICTE Nexus implements 7 core Model Context Protocol (MCP) servers using the official Python MCP SDK:
1. **PGRC MCP Server**: Public Grievance queries, complaint history, grievance categories.
2. **Regulation Bureau MCP Server**: Regulatory cases, penal actions, show cause notices, compliance statuses.
3. **Institution MCP Server**: Institution profiles, AICTE permanent ID lookups, affiliated colleges, regional office mappings.
4. **Complaint MCP Server**: Cross-bureau complaint search, case timelines, status details.
5. **Reporting MCP Server**: Bureau workload aggregations, SLA compliance statistics, disposal rates.
6. **Document MCP Server**: Authorized document metadata, verification status, attachment retrieval.
7. **Notification MCP Server**: Pending coordination alerts, escalation triggers, approval notifications.

## Safety & Governance
- **Default Read-Only**: Every exposed MCP tool is read-only by default.
- **Human-in-the-Loop**: Mutating or sensitive actions (transfers, escalations, overlap confirmation) require explicit human approval via the Admin/Coordination UI.
- **Strict Auditing**: Every tool call is logged in `mcp_execution_logs` with caller context, parameters (sanitized), latency, and status.
