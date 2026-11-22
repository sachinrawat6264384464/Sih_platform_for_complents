---
name: aicte-nexus-agentic-ai
description: Multi-agent AI workflow design, LangGraph state machine, role separation, and human-in-the-loop controls
---

# Agentic AI Skill - AICTE Nexus

## Agent Architecture
AICTE Nexus uses 7 dedicated agents coordinated by a centralized Supervisor:
1. **Complaint Classification Agent**: Categorizes grievances (ragging, capitation fee, faculty shortage, infrastructure, fake documents) and extracts named entities.
2. **Institution Resolution Agent**: Matches reported names/aliases to verified AICTE permanent IDs using trigram, fuzzy, and contextual address signals.
3. **Duplicate Detection Agent**: Identifies exact and semantic duplicates across time and reporting channels.
4. **Bureau Coordination Agent**: Analyzes cross-bureau overlap (e.g., simultaneous complaints in PGRC and Regulation Bureau) and suggests coordinating lead.
5. **SLA Monitoring Agent**: Tracks deadlines, identifies bottlenecks, computes escalation paths.
6. **Report Generation Agent**: Synthesizes verified case records into executive briefings.
7. **Supervisor Agent**: Stateful router directing incoming complaints through classification, resolution, overlap detection, and human approval queues.

## Non-Negotiable Constraint
- AI agents NEVER finalize regulatory decisions, merge distinct complaints, or alter official institutional statuses automatically.
- All AI suggestions generate an `approval_request` for authorized human review.

