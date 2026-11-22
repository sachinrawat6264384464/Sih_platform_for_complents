from datetime import datetime, timezone
import difflib
import math
import re
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.models.case import Case, CaseRelationship
from app.models.complaint import Complaint
from app.models.institution import Institution, InstitutionAlias
from app.models.overlap import OverlapCandidate, OverlapReview


def tokenize_text(text: str) -> List[str]:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return [w for w in cleaned.split() if len(w) > 2]


class OverlapDetectionEngine:
    def __init__(
        self,
        potential_threshold: float = settings.OVERLAP_SIMILARITY_THRESHOLD,
        confirmed_threshold: float = settings.CONFIRMED_OVERLAP_THRESHOLD
    ):
        self.potential_threshold = potential_threshold
        self.confirmed_threshold = confirmed_threshold
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))

    def compute_stage1_exact_id(self, comp_a: Complaint, comp_b: Complaint) -> Tuple[float, Optional[str]]:
        if comp_a.institution_id == comp_b.institution_id:
            return 1.0, f"Identical Institution: AICTE Permanent ID match verified."
        return 0.0, None

    def compute_stage2_name_fuzzy(self, inst_a: Optional[Institution], inst_b: Optional[Institution]) -> Tuple[float, Optional[str]]:
        if not inst_a or not inst_b:
            return 0.0, None
        if inst_a.id == inst_b.id:
            return 1.0, f"Institution name exact match: '{inst_a.name}'"

        name_sim = difflib.SequenceMatcher(None, inst_a.name.lower(), inst_b.name.lower()).ratio()
        
        # Check alias matches
        best_alias_sim = 0.0
        matched_alias = None
        aliases_a = [a.alias_name.lower() for a in (inst_a.aliases or [])] + [inst_a.name.lower()]
        aliases_b = [b.alias_name.lower() for b in (inst_b.aliases or [])] + [inst_b.name.lower()]

        for a1 in aliases_a:
            for b1 in aliases_b:
                sim = difflib.SequenceMatcher(None, a1, b1).ratio()
                if sim > best_alias_sim:
                    best_alias_sim = sim
                    matched_alias = f"'{a1}' ~ '{b1}'"

        score = max(name_sim, best_alias_sim)
        if score > 0.70:
            return score, f"Institution name/alias similarity ({score*100:.1f}%): {matched_alias or inst_a.name}"
        return score, None

    def compute_stage3_geo(self, inst_a: Optional[Institution], inst_b: Optional[Institution]) -> Tuple[float, Optional[str]]:
        if not inst_a or not inst_b:
            return 0.0, None
        
        score = 0.0
        reasons = []
        if inst_a.state.lower() == inst_b.state.lower():
            score += 0.4
            reasons.append(f"Same State: {inst_a.state}")
            if inst_a.district.lower() == inst_b.district.lower():
                score += 0.4
                reasons.append(f"Same District: {inst_a.district}")
                if inst_a.city.lower() == inst_b.city.lower():
                    score += 0.2
                    reasons.append(f"Same City: {inst_a.city}")

        reason_str = ", ".join(reasons) if reasons else None
        return min(score, 1.0), reason_str

    def compute_stage4_category(self, comp_a: Complaint, comp_b: Complaint) -> Tuple[float, Optional[str]]:
        if comp_a.category_id == comp_b.category_id:
            return 1.0, f"Identical Grievance Category: {comp_a.category.name if comp_a.category else 'Matched'}"
        return 0.1, None

    def compute_stage5_bm25(self, text_a: str, text_b: str) -> Tuple[float, Optional[str]]:
        tokens_a = tokenize_text(text_a)
        tokens_b = tokenize_text(text_b)
        if not tokens_a or not tokens_b:
            return 0.0, None

        corpus = [tokens_b]
        bm25 = BM25Okapi(corpus)
        raw_score = bm25.get_scores(tokens_a)[0]
        # Normalize BM25 score sigmoidally
        norm_score = float(1.0 / (1.0 + math.exp(-raw_score / 5.0))) if raw_score > 0 else 0.0

        if norm_score > 0.60:
            return norm_score, f"High lexical term match (BM25: {norm_score*100:.1f}%)"
        return norm_score, None

    def compute_stage6_vector_similarity(self, text_a: str, text_b: str) -> Tuple[float, Optional[str]]:
        if not text_a.strip() or not text_b.strip():
            return 0.0, None
        try:
            tfidf = self.vectorizer.fit_transform([text_a, text_b])
            cos_sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
            if cos_sim > 0.65:
                return cos_sim, f"High semantic text similarity ({cos_sim*100:.1f}%)"
            return cos_sim, None
        except Exception:
            return 0.0, None

    def compute_stage7_cross_bureau(self, comp_a: Complaint, comp_b: Complaint) -> Tuple[float, Optional[str]]:
        if comp_a.bureau_id != comp_b.bureau_id:
            b_a = comp_a.bureau.code if comp_a.bureau else "Bureau A"
            b_b = comp_b.bureau.code if comp_b.bureau else "Bureau B"
            return 1.0, f"Cross-bureau involvement detected: Simultaneous cases in {b_a} and {b_b}."
        return 0.2, "Same bureau jurisdiction."

    def evaluate_pair(
        self,
        comp_a: Complaint,
        comp_b: Complaint,
        inst_a: Optional[Institution],
        inst_b: Optional[Institution]
    ) -> Dict[str, Any]:
        reasons = []

        # Stage 1: Exact ID
        s1, r1 = self.compute_stage1_exact_id(comp_a, comp_b)
        if r1: reasons.append(r1)

        # Stage 2: Name & Alias
        s2, r2 = self.compute_stage2_name_fuzzy(inst_a, inst_b)
        if r2: reasons.append(r2)

        # Stage 3: Geo
        s3, r3 = self.compute_stage3_geo(inst_a, inst_b)
        if r3: reasons.append(r3)

        # Stage 4: Category
        s4, r4 = self.compute_stage4_category(comp_a, comp_b)
        if r4: reasons.append(r4)

        # Text preparation
        text_a = f"{comp_a.title} {comp_a.description}"
        text_b = f"{comp_b.title} {comp_b.description}"

        # Stage 5: BM25
        s5, r5 = self.compute_stage5_bm25(text_a, text_b)
        if r5: reasons.append(r5)

        # Stage 6: Vector Cosine
        s6, r6 = self.compute_stage6_vector_similarity(text_a, text_b)
        if r6: reasons.append(r6)

        # Stage 7: Cross Bureau
        s7, r7 = self.compute_stage7_cross_bureau(comp_a, comp_b)
        if r7: reasons.append(r7)

        # Weighted composite score
        # Exact/Name: 35%, Geo: 10%, Category: 15%, BM25: 15%, Vector: 15%, Cross Bureau: 10%
        inst_score = max(s1, s2)
        total_score = (
            (inst_score * 0.35) +
            (s3 * 0.10) +
            (s4 * 0.15) +
            (s5 * 0.15) +
            (s6 * 0.15) +
            (s7 * 0.10)
        )
        total_score = round(min(total_score, 1.0), 4)

        is_potential = total_score >= self.potential_threshold

        return {
            "total_score": total_score,
            "is_potential": is_potential,
            "stage_scores": {
                "exact_id": s1,
                "name_fuzzy": s2,
                "geo_proximity": s3,
                "category_match": s4,
                "bm25_text": s5,
                "vector_similarity": s6,
                "cross_bureau": s7,
            },
            "match_reasons": reasons,
            "recommended_action": (
                "CONFIRM_OVERLAP_COORDINATION" if total_score >= self.confirmed_threshold else
                "HUMAN_REVIEW_RECOMMENDED" if is_potential else
                "NO_SIGNIFICANT_OVERLAP"
            )
        }


async def scan_complaint_for_overlaps(
    db: AsyncSession,
    target_complaint_id: UUID
) -> List[OverlapCandidate]:
    target_comp = (
        await db.execute(
            select(Complaint)
            .options(
                selectinload(Complaint.institution).selectinload(Institution.aliases),
                selectinload(Complaint.bureau),
                selectinload(Complaint.category),
            )
            .where(Complaint.id == target_complaint_id)
        )
    ).scalar_one_or_none()

    if not target_comp:
        return []

    # Query active candidate complaints (exclude itself, only pending/active)
    candidates_query = (
        select(Complaint)
        .options(
            selectinload(Complaint.institution).selectinload(Institution.aliases),
            selectinload(Complaint.bureau),
            selectinload(Complaint.category),
        )
        .where(
            Complaint.id != target_complaint_id,
            Complaint.status.not_in(["Closed", "Disposed"])
        )
        .order_by(Complaint.created_at.desc())
        .limit(100)
    )
    existing_complaints = (await db.execute(candidates_query)).scalars().all()

    engine = OverlapDetectionEngine()
    created_candidates = []

    for other_comp in existing_complaints:
        # Check if pair already analyzed
        pair_exists = (
            await db.execute(
                select(OverlapCandidate).where(
                    (OverlapCandidate.complaint_a_id == target_comp.id) & (OverlapCandidate.complaint_b_id == other_comp.id) |
                    (OverlapCandidate.complaint_a_id == other_comp.id) & (OverlapCandidate.complaint_b_id == target_comp.id)
                )
            )
        ).scalar_one_or_none()
        if pair_exists:
            continue

        evaluation = engine.evaluate_pair(
            target_comp,
            other_comp,
            target_comp.institution,
            other_comp.institution
        )

        if evaluation["is_potential"]:
            candidate = OverlapCandidate(
                complaint_a_id=target_comp.id,
                complaint_b_id=other_comp.id,
                institution_id=target_comp.institution_id,
                stage1_exact_id_score=evaluation["stage_scores"]["exact_id"],
                stage2_name_fuzzy_score=evaluation["stage_scores"]["name_fuzzy"],
                stage3_geo_score=evaluation["stage_scores"]["geo_proximity"],
                stage4_category_score=evaluation["stage_scores"]["category_match"],
                stage5_bm25_score=evaluation["stage_scores"]["bm25_text"],
                stage6_vector_score=evaluation["stage_scores"]["vector_similarity"],
                stage7_bureau_score=evaluation["stage_scores"]["cross_bureau"],
                total_confidence_score=evaluation["total_score"],
                match_reasons=evaluation["match_reasons"],
                status="Pending"
            )
            db.add(candidate)
            target_comp.is_overlapping = True
            other_comp.is_overlapping = True
            created_candidates.append(candidate)

    if created_candidates:
        await db.commit()

    return created_candidates
