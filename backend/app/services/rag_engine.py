from datetime import datetime, timezone
import math
import re
import time
from typing import Any, Dict, List, Optional
from uuid import UUID
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.models.ai_agent import RetrievalLog
from app.models.auth import User
from app.models.complaint import Complaint
from app.models.document import Document


def clean_and_tokenize(text: str) -> List[str]:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return [w for w in cleaned.split() if len(w) > 2]


class HybridRAGEngine:
    def __init__(
        self,
        bm25_weight: float = settings.HYBRID_BM25_WEIGHT,
        vector_weight: float = settings.HYBRID_VECTOR_WEIGHT
    ):
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self.vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))

    async def retrieve(
        self,
        db: AsyncSession,
        query: str,
        user: User,
        top_k: int = 5,
        bureau_filter: Optional[UUID] = None,
        institution_filter: Optional[UUID] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Fetch authorized candidate records from database
        stmt = (
            select(Complaint)
            .options(
                selectinload(Complaint.institution),
                selectinload(Complaint.bureau),
                selectinload(Complaint.category),
                selectinload(Complaint.documents),
            )
            .order_by(Complaint.created_at.desc())
            .limit(100)
        )

        # Bureau access check if user is not superuser
        if not user.is_superuser:
            user_bureau_ids = [ba.bureau_id for ba in user.bureau_assignments if ba.bureau_id]
            if user_bureau_ids:
                stmt = stmt.where(Complaint.bureau_id.in_(user_bureau_ids))

        if bureau_filter:
            stmt = stmt.where(Complaint.bureau_id == bureau_filter)
        if institution_filter:
            stmt = stmt.where(Complaint.institution_id == institution_filter)

        complaints = (await db.execute(stmt)).scalars().all()
        if not complaints:
            return {"results": [], "query": query, "latency_ms": 0.0, "total_candidates": 0}

        # 2. Build In-Memory Corpus for Query
        corpus_texts = []
        doc_metadata = []
        tokenized_corpus = []

        for c in complaints:
            inst_name = c.institution.name if c.institution else "Unknown Institution"
            perm_id = c.institution.aicte_permanent_id if c.institution else ""
            bureau_name = c.bureau.name if c.bureau else ""
            cat_name = c.category.name if c.category else ""

            full_text = f"{c.complaint_number} {inst_name} {perm_id} {bureau_name} {cat_name} {c.title} {c.description}"
            corpus_texts.append(full_text)
            tokenized_corpus.append(clean_and_tokenize(full_text))

            doc_metadata.append({
                "complaint_id": str(c.id),
                "complaint_number": c.complaint_number,
                "institution_id": str(c.institution_id),
                "institution_name": inst_name,
                "aicte_permanent_id": perm_id,
                "bureau_id": str(c.bureau_id),
                "bureau_name": bureau_name,
                "category": cat_name,
                "status": c.status.value,
                "title": c.title,
                "snippet": c.description[:250] + ("..." if len(c.description) > 250 else ""),
                "received_date": c.received_date.isoformat(),
            })

        # 3. BM25 Scoring
        query_tokens = clean_and_tokenize(query)
        if tokenized_corpus and query_tokens:
            try:
                bm25 = BM25Okapi(tokenized_corpus)
                raw_bm25_scores = bm25.get_scores(query_tokens)
                max_bm25 = max(raw_bm25_scores) if len(raw_bm25_scores) > 0 else 0.0
                if max_bm25 > 0:
                    bm25_scores = [max(0.0, float(s / max_bm25)) for s in raw_bm25_scores]
                else:
                    # Positive token overlap fallback when homogeneous/small corpus causes negative or zero IDF
                    q_set = set(query_tokens)
                    bm25_scores = []
                    for doc_toks in tokenized_corpus:
                        d_set = set(doc_toks)
                        overlap = len(q_set & d_set) / max(len(q_set), 1)
                        bm25_scores.append(float(overlap))
            except Exception:
                q_set = set(query_tokens)
                bm25_scores = [float(len(q_set & set(dt)) / max(len(q_set), 1)) for dt in tokenized_corpus]
        else:
            bm25_scores = [0.0] * len(corpus_texts)

        # 4. Dense Vector Cosine Scoring
        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus_texts + [query])
            query_vec = tfidf_matrix[-1:]
            doc_vecs = tfidf_matrix[:-1]
            cosine_scores = cosine_similarity(query_vec, doc_vecs)[0]
        except Exception:
            cosine_scores = [0.0] * len(corpus_texts)

        # 5. Hybrid Score Fusion & Reranking
        scored_results = []
        for i in range(len(corpus_texts)):
            b_score = float(bm25_scores[i])
            v_score = float(cosine_scores[i])
            hybrid_score = round((self.bm25_weight * b_score) + (self.vector_weight * v_score), 4)

            if hybrid_score > 0.01 or b_score > 0.05 or v_score > 0.05:
                meta = doc_metadata[i].copy()
                meta["bm25_score"] = round(b_score, 4)
                meta["vector_score"] = round(v_score, 4)
                meta["hybrid_score"] = hybrid_score
                scored_results.append(meta)

        # Sort descending by hybrid score
        scored_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        top_results = scored_results[:top_k]

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # 6. Log retrieval to database for observability
        retrieval_log = RetrievalLog(
            query_text=query,
            bm25_matches_count=sum(1 for s in bm25_scores if s > 0),
            vector_matches_count=sum(1 for s in cosine_scores if s > 0),
            hybrid_results=top_results,
            latency_ms=latency_ms
        )
        db.add(retrieval_log)
        await db.commit()

        return {
            "query": query,
            "results": top_results,
            "total_candidates": len(complaints),
            "latency_ms": latency_ms,
        }
