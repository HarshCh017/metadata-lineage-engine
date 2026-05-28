from lineage_platform.models.qlik_models import QlikViewApp, SourceType
from lineage_platform.models.intermediate import (
    GraphModel, DatasetNode, FieldNode, ProcessNode, LineageEdge, DependencyEdge
)
from lineage_platform.core.hashing import generate_deterministic_id


class QlikToIntermediateAdapter:
    """
    Transforms the QlikViewApp model into the generic Intermediate Metadata Model.
    """

    @staticmethod
    def _generate_id(canonical_str: str) -> str:
        return generate_deterministic_id(canonical_str)

    @staticmethod
    def transform(app: QlikViewApp) -> GraphModel:
        graph = GraphModel()

        # 1. Process Node (Qlik Script)
        script_id = QlikToIntermediateAdapter._generate_id(f"qlik_script::{app.app_name}")
        script_node = ProcessNode(
            id=script_id,
            name=app.app_name,
            process_type="qlik_script",
            source_system="QlikView",
            properties={"type": "qlik_script"}
        )
        graph.processes.append(script_node)

        # 2. Process Subroutines
        for sub in app.subroutines:
            sub_id = QlikToIntermediateAdapter._generate_id(f"subroutine::{app.app_name}.{sub.name}")
            sub_node = ProcessNode(
                id=sub_id,
                name=sub.name,
                process_type="subroutine",
                source_system="QlikView"
            )
            graph.processes.append(sub_node)
            graph.dependency_edges.append(DependencyEdge(
                source_id=script_id,
                target_id=sub_id,
                edge_type="DEFINES_SUBROUTINE"
            ))

        # 3. Process Datasets (Tables)
        for load in app.loads:
            table_id = QlikToIntermediateAdapter._generate_id(f"qlik_table::{app.app_name}.{load.table_name}")
            table_node = DatasetNode(
                id=table_id,
                name=load.table_name,
                fully_qualified_name=f"UNKNOWN.UNKNOWN.{load.table_name}",
                layer="transform",
                source_system="QlikView",
                properties={"is_mapping_load": load.is_mapping_load, "lineage_partial": load.lineage_partial}
            )
            graph.datasets.append(table_node)

            graph.dependency_edges.append(DependencyEdge(
                source_id=script_id,
                target_id=table_id,
                edge_type="CONTAINS_TABLE"
            ))

            # Fields for this table
            for field in load.fields:
                field_id = QlikToIntermediateAdapter._generate_id(f"attribute::{app.app_name}.{load.table_name}.{field}")
                field_node = FieldNode(
                    id=field_id,
                    name=field,
                    role="dimension",
                    data_type="string",
                    source_system="QlikView"
                )
                graph.fields.append(field_node)
                graph.dependency_edges.append(DependencyEdge(
                    source_id=table_id,
                    target_id=field_id,
                    edge_type="HAS_FIELD"
                ))

            # Source Table Mapping
            if load.source_table:
                if load.source_type == SourceType.RESIDENT or load.source_type == "RESIDENT":
                    src_table_id = QlikToIntermediateAdapter._generate_id(f"qlik_table::{app.app_name}.{load.source_table}")
                    graph.lineage_edges.append(LineageEdge(
                        source_id=table_id,
                        target_id=src_table_id,
                        edge_type="DERIVES_FROM_TABLE",
                        properties={"via": "resident"}
                    ))
                else:
                    # Build FQN from connection if possible
                    database = "UNKNOWN"
                    schema = "UNKNOWN"
                    if app.connections:
                        last_conn = app.connections[-1]
                        if last_conn.database_name:
                            database = last_conn.database_name
                        if last_conn.server:
                            schema = last_conn.server
                    fqn = f"{database}.{schema}.{load.source_table}"

                    src_table_id = QlikToIntermediateAdapter._generate_id(f"table::{fqn}")
                    src_node = DatasetNode(
                        id=src_table_id,
                        name=load.source_table,
                        fully_qualified_name=fqn,
                        layer="source",
                        source_system="UNKNOWN"  # Physical
                    )
                    # We might add duplicates if multiple loads use the same table, graph writer will merge by ID
                    graph.datasets.append(src_node)

                    graph.lineage_edges.append(LineageEdge(
                        source_id=table_id,
                        target_id=src_table_id,
                        edge_type="LOADS_FROM_TABLE"
                    ))

                    # Physical Columns lineage
                    for field in load.fields:
                        if field in load.sql_columns:
                            physical_col = load.sql_columns[field]
                            pc_id = QlikToIntermediateAdapter._generate_id(f"attribute::{load.source_table}.{physical_col}")
                            pc_node = FieldNode(
                                id=pc_id,
                                name=physical_col,
                                source_system="physical"
                            )
                            graph.fields.append(pc_node)
                            graph.dependency_edges.append(DependencyEdge(
                                source_id=src_table_id,
                                target_id=pc_id,
                                edge_type="HAS_COLUMN"
                            ))

                            qlik_field_id = QlikToIntermediateAdapter._generate_id(f"attribute::{app.app_name}.{load.table_name}.{field}")
                            graph.lineage_edges.append(LineageEdge(
                                source_id=qlik_field_id,
                                target_id=pc_id,
                                edge_type="DERIVES_FROM"
                            ))

            if load.concatenates_to:
                target_table_id = QlikToIntermediateAdapter._generate_id(f"qlik_table::{app.app_name}.{load.concatenates_to}")
                graph.lineage_edges.append(LineageEdge(
                    source_id=table_id,
                    target_id=target_table_id,
                    edge_type="CONCATENATES_INTO"
                ))

        # 4. Joins
        for join in app.joins:
            src_id = QlikToIntermediateAdapter._generate_id(f"qlik_table::{app.app_name}.{join.source_table}")
            tgt_id = QlikToIntermediateAdapter._generate_id(f"qlik_table::{app.app_name}.{join.target_table}")
            graph.dependency_edges.append(DependencyEdge(
                source_id=src_id,
                target_id=tgt_id,
                edge_type="JOINS_WITH",
                properties={"type": join.join_type}
            ))

        return graph
