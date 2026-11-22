# AICTE NEXUS — Hybrid RAG Architecture

## 1. Overview

AICTE NEXUS implements a **Hybrid Retrieval-Augmented Generation (RAG)** architecture combining:
1. **Lexical Retrieval (BM25Okapi)**: High precision on exact terms, AICTE permanent IDs, regulation clause codes, and complaint numbers.
2. **Dense Semantic Retrieval (TF-IDF & Vector Cosine)**: Robust semantic matching capturing synonymy, alternate phraseology, and thematic intent.
3. **Reciprocal Rank Fusion & Reranking**: Weighted score combination ($0.5 \times \text{BM25} + 0.5 \times \text{Vector}$) with candidate thresholding.
4. **Mandatory Bureau Access Filtering**: Non-superuser officers can only retrieve documents and complaints within their authorized bureau scope.

---

## 2. Mathematical Scoring Model

For query $Q$ and candidate document $D_i$ in corpus $C$:

$$\text{BM25Score}(D_i, Q) = \sum_{t \in Q} \text{IDF}(t) \cdot \frac{f(t, D_i) \cdot (k_1 + 1)}{f(t, D_i) + k_1 \cdot \left(1 - b + b \cdot \frac{|D_i|}{\text{avgdl}}\right)}$$

$$\text{VectorScore}(D_i, Q) = \frac{\vec{V}_Q \cdot \vec{V}_{D_i}}{\|\vec{V}_Q\| \|\vec{V}_{D_i}\|}$$

$$\text{HybridScore}(D_i, Q) = w_{\text{bm25}} \cdot \overline{\text{BM25Score}}(D_i, Q) + w_{\text{vector}} \cdot \text{VectorScore}(D_i, Q)$$

Where default weights are:
- $w_{\text{bm25}} = 0.5$
- $w_{\text{vector}} = 0.5$

---

## 3. Homogeneous Corpus Edge Case Handling

In small or single-complaint test databases, standard BM25 IDF can become negative when $(N - n) \le 0$. AICTE NEXUS includes a deterministic token-overlap fallback to ensure positive candidate ranking under all corpus distributions:

```python
if max_bm25 > 0:
    bm25_scores = [max(0.0, float(s / max_bm25)) for s in raw_bm25_scores]
else:
    q_set = set(query_tokens)
    bm25_scores = [float(len(q_set & set(dt)) / max(len(q_set), 1)) for dt in tokenized_corpus]
```

---

## 4. Observability & Query Logging

Every retrieval operation is asynchronously committed to the `retrieval_logs` database table with:
- Query text
- BM25 match count
- Vector match count
- Top ranked candidates with score breakdowns
- Execution latency in milliseconds
