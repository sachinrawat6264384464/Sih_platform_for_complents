from typing import Any, Dict, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.auth import User
from app.services.rag_engine import HybridRAGEngine

router = APIRouter(prefix="/rag", tags=["Hybrid RAG Intelligence"])

rag_engine = HybridRAGEngine()


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language grievance or institution inquiry")
    bureau_filter: Optional[UUID] = None
    institution_filter: Optional[UUID] = None
    top_k: int = Field(5, ge=1, le=20)


@router.post("/query")
async def execute_hybrid_query(
    request: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = await rag_engine.retrieve(
        db=db,
        query=request.query,
        user=current_user,
        top_k=request.top_k,
        bureau_filter=request.bureau_filter,
        institution_filter=request.institution_filter,
    )
    return results
