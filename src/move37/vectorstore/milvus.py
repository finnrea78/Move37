"""Milvus-backed vector store for note chunks."""

from __future__ import annotations

import os
from typing import Any

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility


EMBEDDING_DIMENSIONS = 3072


class NoteMilvusStore:
    """Encapsulate collection lifecycle and note-chunk operations."""

    def __init__(self, uri: str | None = None, collection_name: str | None = None) -> None:
        self.uri = uri or os.environ.get("MOVE37_MILVUS_URI", "http://milvus-standalone:19530")
        self.collection_name = collection_name or os.environ.get("MOVE37_MILVUS_COLLECTION", "note_chunks_v1")
        connections.connect(alias="default", uri=self.uri)
        self.collection = self._ensure_collection()

    def _ensure_collection(self) -> Collection:
        if utility.has_collection(self.collection_name):
            collection = Collection(self.collection_name)
        else:
            schema = CollectionSchema(
                fields=[
                    FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=255),
                    FieldSchema(name="owner_subject", dtype=DataType.VARCHAR, max_length=255),
                    FieldSchema(name="note_id", dtype=DataType.INT64),
                    FieldSchema(name="note_title", dtype=DataType.VARCHAR, max_length=255),
                    FieldSchema(name="linked_activity_id", dtype=DataType.VARCHAR, max_length=255),
                    FieldSchema(name="source_type", dtype=DataType.VARCHAR, max_length=32),
                    FieldSchema(name="source_filename", dtype=DataType.VARCHAR, max_length=255),
                    FieldSchema(name="chunk_index", dtype=DataType.INT64),
                    FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="content_sha256", dtype=DataType.VARCHAR, max_length=64),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIMENSIONS),
                ],
                enable_dynamic_field=False,
            )
            collection = Collection(self.collection_name, schema=schema)
            collection.create_index(
                "embedding",
                {"index_type": "AUTOINDEX", "metric_type": "COSINE", "params": {}},
            )
        collection.load()
        return collection

    def replace_note_chunks(self, rows: list[dict[str, Any]], note_id: int) -> None:
        self.delete_note_chunks(note_id)
        if rows:
            self.collection.insert(rows)
            self.collection.flush()

    def delete_note_chunks(self, note_id: int) -> None:
        self.collection.delete(f"note_id == {int(note_id)}")

    def search(self, *, subject: str, embedding: list[float], top_k: int = 8) -> list[dict[str, Any]]:
        results = self.collection.search(
            data=[embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {}},
            limit=top_k,
            expr=f'owner_subject == "{subject.replace(chr(34), "")}"',
            output_fields=[
                "note_id",
                "note_title",
                "linked_activity_id",
                "chunk_id",
                "chunk_index",
                "chunk_text",
                "source_type",
                "source_filename",
            ],
        )
        hits: list[dict[str, Any]] = []
        for hit in results[0]:
            entity = hit.entity
            hits.append(
                {
                    "noteId": int(entity.get("note_id")),
                    "noteTitle": entity.get("note_title"),
                    "linkedActivityId": entity.get("linked_activity_id") or None,
                    "chunkId": entity.get("chunk_id"),
                    "chunkIndex": int(entity.get("chunk_index")),
                    "score": float(hit.distance),
                    "snippet": entity.get("chunk_text"),
                    "sourceType": entity.get("source_type"),
                    "sourceFilename": entity.get("source_filename"),
                }
            )
        return hits
