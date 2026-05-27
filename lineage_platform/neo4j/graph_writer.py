from neo4j import GraphDatabase
from uuid import uuid4
from datetime import datetime

from lineage_platform.models.qlik_models import (
    QlikViewApp
)


class GraphWriter:

    """
    Writes lineage metadata into Neo4j.
    """

    def __init__(self):

        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "password")
        )

    # =====================================================
    # MAIN WRITE METHOD
    # =====================================================

    def write_app(
        self,
        app: QlikViewApp
    ):

        with self.driver.session() as session:

            # =================================================
            # Create Qlik Script Node
            # =================================================

            session.run(
                """
                MERGE (q:QlikScript {
                    name: $app_name
                })

                SET q.id = $id,
                    q.type = 'qlik_script',
                    q.source_system = 'QlikView',
                    q.created_at = $created_at
                """,
                app_name=app.app_name,
                id=str(uuid4()),
                created_at=str(datetime.utcnow())
            )

            # =================================================
            # Process LOADS
            # =================================================

            for load in app.loads:

                # ---------------------------------------------
                # Create QlikTable
                # ---------------------------------------------

                session.run(
                    """
                    MERGE (t:QlikTable {
                        name: $table_name
                    })

                    SET t.id = $id,
                        t.layer = 'transform',
                        t.source_system = 'QlikView',
                        t.created_at = $created_at
                    """,
                    table_name=load.table_name,
                    id=str(uuid4()),
                    created_at=str(datetime.utcnow())
                )

                # ---------------------------------------------
                # USES_TABLE
                # ---------------------------------------------

                session.run(
                    """
                    MATCH (q:QlikScript {
                        name: $app_name
                    })

                    MATCH (t:QlikTable {
                        name: $table_name
                    })

                    MERGE (q)-[:USES_TABLE]->(t)
                    """,
                    app_name=app.app_name,
                    table_name=load.table_name
                )

                # ---------------------------------------------
                # Source lineage
                # ---------------------------------------------

                if load.source_table:

                    session.run(
                        """
                        MERGE (s:Table {
                            name: $source_table
                        })

                        SET s.id = $id,
                            s.type = 'source_table',
                            s.created_at = $created_at
                        """,
                        source_table=load.source_table,
                        id=str(uuid4()),
                        created_at=str(datetime.utcnow())
                    )

                    session.run(
                        """
                        MATCH (t:QlikTable {
                            name: $table_name
                        })

                        MATCH (s:Table {
                            name: $source_table
                        })

                        MERGE (t)-[:READS_FROM]->(s)
                        """,
                        table_name=load.table_name,
                        source_table=load.source_table
                    )

                # ---------------------------------------------
                # Attributes
                # ---------------------------------------------

                for field in load.fields:

                    session.run(
                        """
                        MERGE (a:Attribute {
                            name: $field_name
                        })

                        SET a.id = $id,
                            a.role = 'dimension',
                            a.datatype = 'string',
                            a.is_calculated = false,
                            a.formula = '',
                            a.source_system = 'QlikView',
                            a.created_at = $created_at
                        """,
                        field_name=field,
                        id=str(uuid4()),
                        created_at=str(datetime.utcnow())
                    )

                    session.run(
                        """
                        MATCH (t:QlikTable {
                            name: $table_name
                        })

                        MATCH (a:Attribute {
                            name: $field_name
                        })

                        MERGE (t)-[:HAS_ATTRIBUTE]->(a)
                        """,
                        table_name=load.table_name,
                        field_name=field
                    )

            # =================================================
            # Synthetic lineage
            # =================================================

            for field in app.fields:

                if not field.is_synthetic:
                    continue

                # ---------------------------------------------
                # Calculated attribute node
                # ---------------------------------------------

                session.run(
                    """
                    MERGE (a:Attribute {
                        name: $field_name
                    })

                    SET a.id = $id,
                        a.is_calculated = true,
                        a.formula = $formula,
                        a.role = 'measure',
                        a.datatype = 'decimal',
                        a.source_system = 'QlikView',
                        a.created_at = $created_at
                    """,
                    field_name=field.name,
                    formula=field.formula or "",
                    id=str(uuid4()),
                    created_at=str(datetime.utcnow())
                )

                # ---------------------------------------------
                # Source attributes
                # ---------------------------------------------

                for source_field in field.source_fields:

                    session.run(
                        """
                        MERGE (s:Attribute {
                            name: $source_field
                        })

                        SET s.id = coalesce(
                            s.id,
                            $id
                        )
                        """,
                        source_field=source_field,
                        id=str(uuid4())
                    )

                    session.run(
                        """
                        MATCH (a:Attribute {
                            name: $field_name
                        })

                        MATCH (s:Attribute {
                            name: $source_field
                        })

                        MERGE (a)-[:DERIVED_FROM]->(s)
                        """,
                        field_name=field.name,
                        source_field=source_field
                    )

            # =================================================
            # JOINS
            # =================================================

            for join in app.joins:

                session.run(
                    """
                    MERGE (a:QlikTable {
                        name: $source_table
                    })

                    SET a.id = coalesce(
                        a.id,
                        $id
                    )
                    """,
                    source_table=join.source_table,
                    id=str(uuid4())
                )

                session.run(
                    """
                    MERGE (b:QlikTable {
                        name: $target_table
                    })

                    SET b.id = coalesce(
                        b.id,
                        $id
                    )
                    """,
                    target_table=join.target_table,
                    id=str(uuid4())
                )

                session.run(
                    """
                    MATCH (a:QlikTable {
                        name: $source_table
                    })

                    MATCH (b:QlikTable {
                        name: $target_table
                    })

                    MERGE (a)-[r:JOINED_WITH]->(b)

                    SET r.type = $join_type,
                        r.created_at = $created_at
                    """,
                    source_table=join.source_table,
                    target_table=join.target_table,
                    join_type=join.join_type,
                    created_at=str(datetime.utcnow())
                )

    # =====================================================
    # CLEANUP
    # =====================================================

    def close(self):

        self.driver.close()