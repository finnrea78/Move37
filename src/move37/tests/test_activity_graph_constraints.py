from __future__ import annotations

import unittest

from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from move37.models import Base
from move37.models.activity_graph import (
    ActivityDependencyModel,
    ActivityGraphModel,
    ActivityNodeModel,
    ActivityScheduleModel,
)
from move37.services.activity_graph import ActivityGraphService


class ActivityGraphConstraintTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:", future=True)

        @event.listens_for(self.engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def tearDown(self) -> None:
        self.engine.dispose()

    def test_each_subject_can_seed_the_default_graph(self) -> None:
        service = ActivityGraphService(self.session_factory)

        first = service.get_graph("user-1")
        second = service.get_graph("user-2")

        self.assertNotEqual(first["graphId"], second["graphId"])
        self.assertIn("wake-early", {node["id"] for node in first["nodes"]})
        self.assertIn("wake-early", {node["id"] for node in second["nodes"]})

    def test_dependency_foreign_keys_are_graph_scoped(self) -> None:
        with self.session_factory() as session:
            first_graph = ActivityGraphModel(owner_subject="user-1")
            second_graph = ActivityGraphModel(owner_subject="user-2")
            session.add_all([first_graph, second_graph])
            session.flush()

            session.add_all(
                [
                    ActivityNodeModel(
                        graph_id=first_graph.id,
                        id="child",
                        position=0,
                        title="Child",
                        notes="",
                        real_time=0,
                    ),
                    ActivityNodeModel(
                        graph_id=second_graph.id,
                        id="parent",
                        position=0,
                        title="Parent",
                        notes="",
                        real_time=0,
                    ),
                ]
            )
            session.flush()

            session.add(
                ActivityDependencyModel(
                    graph_id=first_graph.id,
                    position=0,
                    parent_id="parent",
                    child_id="child",
                )
            )

            with self.assertRaises(IntegrityError):
                session.flush()

    def test_schedule_foreign_keys_are_graph_scoped(self) -> None:
        with self.session_factory() as session:
            first_graph = ActivityGraphModel(owner_subject="user-1")
            second_graph = ActivityGraphModel(owner_subject="user-2")
            session.add_all([first_graph, second_graph])
            session.flush()

            session.add_all(
                [
                    ActivityNodeModel(
                        graph_id=first_graph.id,
                        id="later",
                        position=0,
                        title="Later",
                        notes="",
                        real_time=0,
                    ),
                    ActivityNodeModel(
                        graph_id=second_graph.id,
                        id="earlier",
                        position=0,
                        title="Earlier",
                        notes="",
                        real_time=0,
                    ),
                ]
            )
            session.flush()

            session.add(
                ActivityScheduleModel(
                    graph_id=first_graph.id,
                    position=0,
                    earlier_id="earlier",
                    later_id="later",
                )
            )

            with self.assertRaises(IntegrityError):
                session.flush()

    def test_edge_tables_reject_self_references(self) -> None:
        graph_id = self._create_graph_with_node("node")

        with self.session_factory() as session:
            session.add(
                ActivityDependencyModel(
                    graph_id=graph_id,
                    position=0,
                    parent_id="node",
                    child_id="node",
                )
            )
            with self.assertRaises(IntegrityError):
                session.flush()

        with self.session_factory() as session:
            session.add(
                ActivityScheduleModel(
                    graph_id=graph_id,
                    position=0,
                    earlier_id="node",
                    later_id="node",
                )
            )
            with self.assertRaises(IntegrityError):
                session.flush()

    def _create_graph_with_node(self, node_id: str) -> int:
        with self.session_factory() as session:
            graph = ActivityGraphModel(owner_subject="user-1")
            session.add(graph)
            session.flush()
            session.add(
                ActivityNodeModel(
                    graph_id=graph.id,
                    id=node_id,
                    position=0,
                    title="Node",
                    notes="",
                    real_time=0,
                )
            )
            session.commit()
            return graph.id


if __name__ == "__main__":
    unittest.main()
