from __future__ import annotations

import tempfile
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from move37.db.seed_mock_data import seed_mock_data
from move37.models import Base
from move37.repositories.activity_graph import ActivityGraphRepository


class SeedMockDataTest(unittest.TestCase):
    def test_seed_mock_data_populates_graph_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            database_url = f"sqlite+pysqlite:///{tmpdir}/move37-seed.db"
            engine = create_engine(database_url, future=True)
            Base.metadata.create_all(engine)
            engine.dispose()

            first_seeded = seed_mock_data("local-user", database_url=database_url)
            second_seeded = seed_mock_data("local-user", database_url=database_url)

            self.assertTrue(first_seeded)
            self.assertFalse(second_seeded)

            check_engine = create_engine(database_url, future=True)
            try:
                session_factory = sessionmaker(bind=check_engine, autoflush=False, autocommit=False, expire_on_commit=False)
                with session_factory() as session:
                    repository = ActivityGraphRepository(session)
                    snapshot = repository.get_snapshot("local-user")
            finally:
                check_engine.dispose()

            self.assertIsNotNone(snapshot)
            self.assertGreater(len(snapshot["nodes"]), 0)
            self.assertIn("wake-early", {node["id"] for node in snapshot["nodes"]})


if __name__ == "__main__":
    unittest.main()
