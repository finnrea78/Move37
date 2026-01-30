RAG & Knowledge Fabric
======================

Ingestion Pipeline
------------------

- Source acquisition (PDF, HTML, Markdown).
- Chunking with structural metadata.
- Embedding and hybrid indexing.
- Storage of raw artifacts for replay.

Retrieval Strategy
------------------

- Hybrid retrieval: BM25 + vector similarity.
- Re-ranking: bge-reranker or ColBERT.
- Grounded output: citations required by policy.

Stores
------

- **Vector DB:** Qdrant or Weaviate.
- **Graph DB:** Neo4j for concept relationships.
- **Object Store:** MinIO for raw documents.
