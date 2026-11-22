---
name: aicte-nexus-hybrid-rag
description: Hybrid retrieval architecture combining BM25 keyword matching with dense vector embeddings and role-based context filtering
---

# Hybrid RAG Skill - AICTE Nexus

## Retrieval Pipeline
1. **Document Ingestion & Chunking**: Extract text from complaints, regulatory notices, and attached PDFs. Chunk into overlapping semantic windows (500 tokens with 50-token overlap).
2. **Dual-Index Generation**:
   - **BM25 Keyword Index**: Built using `rank-bm25` over tokenized documents, tuned for exact institutional acronyms, section codes, and legal terms.
   - **Dense Vector Embeddings**: Sentence/document embeddings stored in PostgreSQL JSONB vectors, enabling semantic similarity across paraphrased descriptions and multilingual Hindi/English context.
3. **Hybrid Fusion**:
   - `HybridScore = α * BM25NormalizedScore + (1 - α) * VectorCosineScore` (default `α = 0.40`).
4. **Bureau & Role Access Filtering**: Before passing any retrieved context to the LLM or UI, filter chunks against the requesting user's bureau and clearance permissions.
5. **Attribution & Citations**: Every generated synthesis must include verifiable citations pointing to original complaint IDs and document hashes.
