import os
import hashlib
from neo4j import GraphDatabase
from datetime import datetime

from lineage_platform.models.qlik_models import QlikViewApp, SourceType


class GraphWriter:
    """
    Enterprise Neo4j Graph Writer
    Writes lineage metadata into Neo4j.
    """

    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def _generate_id(self, canonical_str: str) -> str:
        return hashlib.sha256(canonical_str.encode()).hexdigest()[:16]

    # =====================================================
    # MAIN WRITE METHOD
    # =====================================================

    def write_app(self, app: QlikViewApp):

        with self.driver.session() as session:

            # =================================================
            # Create Qlik Script Node
            # =================================================

            session.run(
                """
                MERGE (q:QlikScript {
                    name: $app_name
                })

                SET q.id = coalesce(q.id, $id),
                    q.type = 'qlik_script',
                    q.source_system = 'QlikView',
                    q.created_at = coalesce(
                        q.created_at,
                        $created_at
                    )
                """,
                app_name=app.app_name,
                id=self._generate_id(f"qlik_script::{app.app_name}"),
                created_at=str(datetime.utcnow()),
            )

            # =================================================
            # Process Subroutines
            # =================================================
            for sub in app.subroutines:
                session.run(
                    """
                    MERGE (s:Subroutine {name: $sub_name})
                    SET s.id = coalesce(s.id, $id)
                    WITH s
                    MATCH (q:QlikScript {name: $app_name})
                    MERGE (q)-[:DEFINES_SUBROUTINE]->(s)
                    """,
                    sub_name=sub.name,
                    id=self._generate_id(f"subroutine::{app.app_name}.{sub.name}"),
                    app_name=app.app_name
                )

            # =================================================
            # Process Dashboards (XML)
            # =================================================
            for sheet in app.sheets:
                session.run(
                    """
                    MERGE (s:QlikSheet {name: $sheet_title})
                    SET s.id = coalesce(s.id, $id), s.sheet_id = $sheet_id
                    WITH s
                    MATCH (q:QlikScript {name: $app_name})
                    MERGE (q)-[:CONTAINS_SHEET]->(s)
                    """,
                    sheet_title=sheet.title,
                    sheet_id=sheet.sheet_id,
                    id=self._generate_id(f"qliksheet::{app.app_name}.{sheet.sheet_id}"),
                    app_name=app.app_name
                )
                
                for chart in sheet.charts:
                    session.run(
                        """
                        MERGE (c:QlikChart {name: $chart_title})
                        SET c.id = coalesce(c.id, $id), c.chart_id = $chart_id
                        WITH c
                        MATCH (s:QlikSheet {sheet_id: $sheet_id})
                        MERGE (s)-[:DISPLAYS_CHART]->(c)
                        """,
                        chart_title=chart.title,
                        chart_id=chart.chart_id,
                        id=self._generate_id(f"qlikchart::{app.app_name}.{chart.chart_id}"),
                        sheet_id=sheet.sheet_id
                    )
                    
                    for field in chart.fields:
                        session.run(
                            """
                            MATCH (c:QlikChart {chart_id: $chart_id})
                            MERGE (a:Attribute {name: $field_name})
                            MERGE (c)-[:USES_FIELD]->(a)
                            """,
                            chart_id=chart.chart_id,
                            field_name=field
                        )

            for load in app.loads:

                # ---------------------------------------------
                # Create QlikTable
                # ---------------------------------------------

                session.run(
                    """
                    MERGE (t:QlikTable {
                        name: $table_name
                    })

                    SET t.id = coalesce(t.id, $id),
                        t.layer = 'transform',
                        t.source_system = 'QlikView',
                        t.is_mapping_load = $is_mapping_load,
                        t.lineage_partial = $lineage_partial,
                        t.created_at = coalesce(
                            t.created_at,
                            $created_at
                        )
                    """,
                    table_name=load.table_name,
                    id=self._generate_id(f"qlik_table::{app.app_name}.{load.table_name}"),
                    is_mapping_load=load.is_mapping_load,
                    lineage_partial=load.lineage_partial,
                    created_at=str(datetime.utcnow()),
                )

                # ---------------------------------------------
                # CONTAINS_TABLE
                # ---------------------------------------------

                session.run(
                    """
                    MATCH (q:QlikScript {
                        name: $app_name
                    })

                    MATCH (t:QlikTable {
                        name: $table_name
                    })

                    MERGE (q)-[:CONTAINS_TABLE]->(t)
                    """,
                    app_name=app.app_name,
                    table_name=load.table_name,
                )

                # ---------------------------------------------
                # CONCATENATE
                # ---------------------------------------------

                if load.concatenates_to:
                    session.run(
                        """
                        MATCH (t:QlikTable {name: $table_name})
                        MATCH (target:QlikTable {name: $target_table})
                        MERGE (t)-[:CONCATENATES_INTO]->(target)
                        """,
                        table_name=load.table_name,
                        target_table=load.concatenates_to,
                    )

                # ---------------------------------------------
                # Source lineage
                # ---------------------------------------------

                if load.source_table:
                    if load.source_type == SourceType.RESIDENT or load.source_type == "RESIDENT":
                        session.run(
                            """
                            MATCH (t:QlikTable {name: $table_name})
                            MATCH (s:QlikTable {name: $source_table})
                            MERGE (t)-[:DERIVES_FROM_TABLE {via: 'resident'}]->(s)
                            """,
                            table_name=load.table_name,
                            source_table=load.source_table,
                        )
                    else:
                        fqn = f"UNKNOWN.UNKNOWN.{load.source_table}"
                        session.run(
                            """
                            MERGE (s:Table {
                                name: $source_table
                            })

                            SET s.id = coalesce(s.id, $id),
                                s.fully_qualified_name = coalesce(s.fully_qualified_name, $fqn),
                                s.type = 'source_table',
                                s.created_at = coalesce(s.created_at, $created_at)
                            """,
                            source_table=load.source_table,
                            fqn=fqn,
                            id=self._generate_id(f"table::{fqn}"),
                            created_at=str(datetime.utcnow()),
                        )

                        session.run(
                            """
                            MATCH (t:QlikTable {
                                name: $table_name
                            })

                            MATCH (s:Table {
                                name: $source_table
                            })

                            MERGE (t)-[:LOADS_FROM_TABLE]->(s)
                            """,
                            table_name=load.table_name,
                            source_table=load.source_table,
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

                        SET a.id = coalesce(a.id, $id),
                            a.role = coalesce(a.role, 'dimension'),
                            a.datatype = coalesce(a.datatype, 'string'),
                            a.is_calculated = coalesce(a.is_calculated, false),
                            a.formula = coalesce(a.formula, ''),
                            a.source_system = 'QlikView',
                            a.created_at = coalesce(a.created_at, $created_at)
                        """,
                        field_name=field,
                        id=self._generate_id(f"attribute::{app.app_name}.{load.table_name}.{field}"),
                        created_at=str(datetime.utcnow()),
                    )

                    session.run(
                        """
                        MATCH (t:QlikTable {
                            name: $table_name
                        })

                        MATCH (a:Attribute {
                            name: $field_name
                        })

                        MERGE (t)-[:HAS_FIELD]->(a)
                        """,
                        table_name=load.table_name,
                        field_name=field,
                    )
                    
                    if field == "*" and load.source_table:
                        session.run(
                            """
                            MATCH (src:QlikTable {name: $source_table})-[:HAS_FIELD]->(src_attr:Attribute)
                            MATCH (t:QlikTable {name: $table_name})
                            MERGE (t)-[:HAS_FIELD]->(src_attr)
                            """,
                            source_table=load.source_table,
                            table_name=load.table_name
                        )
                    
                    if field in load.sql_columns and load.source_table:
                        physical_col = load.sql_columns[field]
                        session.run(
                            """
                            MATCH (a:Attribute {name: $field_name})
                            MERGE (pc:TableColumn {name: $physical_col, table: $source_table})
                            SET pc.id = coalesce(pc.id, $pc_id)
                            MERGE (a)-[:DERIVES_FROM]->(pc)
                            """,
                            field_name=field,
                            physical_col=physical_col,
                            source_table=load.source_table,
                            pc_id=self._generate_id(f"tablecolumn::{load.source_table}.{physical_col}")
                        )

            # =================================================
            # Synthetic lineage
            # =================================================

            for synth_field in app.fields:

                if not synth_field.is_synthetic:
                    continue

                # ---------------------------------------------
                # Calculated attribute node
                # ---------------------------------------------

                session.run(
                    """
                    MERGE (a:Attribute {
                        name: $field_name
                    })

                    SET a.id = coalesce(a.id, $id),
                        a.is_calculated = true,
                        a.formula = $formula,
                        a.role = 'measure',
                        a.datatype = 'decimal',
                        a.source_system = 'QlikView',
                        a.created_at = coalesce(a.created_at, $created_at)
                    """,
                    field_name=synth_field.name,
                    formula=synth_field.formula or "",
                    id=self._generate_id(f"attribute::{app.app_name}.SYNTHETIC.{synth_field.name}"),
                    created_at=str(datetime.utcnow()),
                )

                # ---------------------------------------------
                # Source attributes
                # ---------------------------------------------

                for source_field in synth_field.source_fields:

                    session.run(
                        """
                        MERGE (s:Attribute {
                            name: $source_field
                        })

                        SET s.id = coalesce(s.id, $id)
                        """,
                        source_field=source_field,
                        id=self._generate_id(f"attribute::{app.app_name}.SYNTHETIC.{source_field}"),
                    )

                    session.run(
                        """
                        MATCH (a:Attribute {
                            name: $field_name
                        })

                        MATCH (s:Attribute {
                            name: $source_field
                        })

                        MERGE (a)-[:DERIVES_FROM]->(s)
                        """,
                        field_name=synth_field.name,
                        source_field=source_field,
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

                    SET a.id = coalesce(a.id, $id)
                    """,
                    source_table=join.source_table,
                    id=self._generate_id(f"qlik_table::{app.app_name}.{join.source_table}"),
                )

                session.run(
                    """
                    MERGE (b:QlikTable {
                        name: $target_table
                    })

                    SET b.id = coalesce(b.id, $id)
                    """,
                    target_table=join.target_table,
                    id=self._generate_id(f"qlik_table::{app.app_name}.{join.target_table}"),
                )

                session.run(
                    """
                    MATCH (a:QlikTable {
                        name: $source_table
                    })

                    MATCH (b:QlikTable {
                        name: $target_table
                    })

                    MERGE (a)-[r:JOINS_WITH]->(b)

                    SET r.type = $join_type,
                        r.created_at = coalesce(r.created_at, $created_at)
                    """,
                    source_table=join.source_table,
                    target_table=join.target_table,
                    join_type=join.join_type,
                    created_at=str(datetime.utcnow()),
                )

            # =================================================
            # CONNECTIONS
            # =================================================

            for conn in app.connections:
                session.run(
                    """
                    MERGE (c:Connection {name: $conn_name})
                    SET c.id = coalesce(c.id, $id),
                        c.connection_string = coalesce(c.connection_string, $conn_string),
                        c.created_at = coalesce(c.created_at, $created_at)
                    """,
                    conn_name=conn.connection_name,
                    conn_string=conn.connection_string,
                    id=self._generate_id(f"connection::{app.app_name}.{conn.connection_name}"),
                    created_at=str(datetime.utcnow()),
                )
                session.run(
                    """
                    MATCH (q:QlikScript {name: $app_name})
                    MATCH (c:Connection {name: $conn_name})
                    MERGE (q)-[:USES_CONNECTION]->(c)
                    """,
                    app_name=app.app_name,
                    conn_name=conn.connection_name,
                )

    # =====================================================
    # CLEANUP
    # =====================================================

    def close(self):
        """
        Properly close Neo4j driver.
        Prevents driver cleanup warnings.
        """
        if self.driver:
            self.driver.close()
            self.driver = None
