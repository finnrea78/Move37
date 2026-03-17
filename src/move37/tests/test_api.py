from __future__ import annotations

import os
import tempfile
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from move37.api.server import create_app
from move37.models import Base


class ApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.database_dir = tempfile.TemporaryDirectory()
        self.old_env = {
            "MOVE37_DATABASE_URL": os.environ.get("MOVE37_DATABASE_URL"),
            "MOVE37_API_BEARER_TOKEN": os.environ.get("MOVE37_API_BEARER_TOKEN"),
            "MOVE37_API_BEARER_SUBJECT": os.environ.get("MOVE37_API_BEARER_SUBJECT"),
        }
        os.environ["MOVE37_DATABASE_URL"] = (
            f"sqlite+pysqlite:///{self.database_dir.name}/move37-test.db"
        )
        os.environ["MOVE37_API_BEARER_TOKEN"] = "test-token"
        os.environ["MOVE37_API_BEARER_SUBJECT"] = "api-user"
        engine = create_engine(os.environ["MOVE37_DATABASE_URL"], future=True)
        Base.metadata.create_all(engine)
        engine.dispose()
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.database_dir.cleanup()
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_auth_me_requires_token(self) -> None:
        response = self.client.get("/v1/auth/me")

        self.assertEqual(response.status_code, 401)

    def test_auth_me_returns_subject(self) -> None:
        response = self.client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer test-token"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["subject"], "api-user")

    def test_graph_bootstraps_default_data(self) -> None:
        response = self.client.get(
            "/v1/graph",
            headers={"Authorization": "Bearer test-token"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(len(payload["nodes"]), 0)
        self.assertIn("graphId", payload)

    def test_create_note_creates_note_and_parentless_graph_node(self) -> None:
        response = self.client.post(
            "/v1/notes",
            headers={"Authorization": "Bearer test-token"},
            json={"title": "Recovery notes", "body": "Hydrate after long run."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["note"]["title"], "Recovery notes")
        self.assertEqual(payload["note"]["ingestStatus"], "pending")
        note_nodes = [node for node in payload["graph"]["nodes"] if node["kind"] == "note"]
        self.assertEqual(len(note_nodes), 1)
        self.assertEqual(note_nodes[0]["title"], "Recovery notes")
        self.assertEqual(note_nodes[0]["linkedNoteId"], payload["note"]["id"])
        parent_edges = [
            edge for edge in payload["graph"]["dependencies"] if edge["childId"] == note_nodes[0]["id"]
        ]
        self.assertEqual(parent_edges, [])

    def test_import_txt_notes_creates_one_note_per_file(self) -> None:
        response = self.client.post(
            "/v1/notes/import",
            headers={"Authorization": "Bearer test-token"},
            files=[
                ("files", ("morning.txt", b"Wake at 06:00", "text/plain")),
                ("files", ("training.txt", b"Tempo run on Thursday", "text/plain")),
            ],
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["notes"]), 2)
        titles = {note["title"] for note in payload["notes"]}
        self.assertEqual(titles, {"morning", "training"})
        note_node_titles = {node["title"] for node in payload["graph"]["nodes"] if node["kind"] == "note"}
        self.assertTrue({"morning", "training"}.issubset(note_node_titles))


if __name__ == "__main__":
    unittest.main()
