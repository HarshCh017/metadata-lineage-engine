import os
from datetime import datetime, UTC
from neo4j import GraphDatabase
import structlog
from lineage_platform.models.intermediate import GraphModel

logger = structlog.get_logger()

class BatchGraphWriter:
    """
    Enterprise-scale batch writer for Neo4j.
    Uses UNWIND for massive parallel insertion of nodes and edges.
    """

    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def write_graph(self, graph: GraphModel):
        """
        Write the intermediate GraphModel to Neo4j in batches.
        """
        now = str(datetime.now(UTC))

        try:
            with self.driver.session() as session:
                # 1. Write ProcessNodes
                if graph.processes:
                    session.run("""
                        UNWIND $processes AS p
                        MERGE (n:Process {id: p.id})
                        SET n.name = p.name,
                            n.process_type = p.process_type,
                            n.source_system = p.source_system,
                            n.created_at = coalesce(n.created_at, $now)
                        // Dynamic properties not fully supported by UNWIND directly 
                        // without apoc, but we map explicit fields here
                    """, processes=[p.__dict__ for p in graph.processes], now=now)
                    
                    # Backwards compatibility labels for Qlik
                    session.run("""
                        MATCH (n:Process {process_type: 'qlik_script'})
                        SET n:QlikScript
                    """)
                    session.run("""
                        MATCH (n:Process {process_type: 'subroutine'})
                        SET n:Subroutine
                    """)

                # 2. Write DatasetNodes
                if graph.datasets:
                    session.run("""
                        UNWIND $datasets AS d
                        MERGE (n:Dataset {id: d.id})
                        SET n.name = d.name,
                            n.fully_qualified_name = d.fully_qualified_name,
                            n.layer = d.layer,
                            n.source_system = d.source_system,
                            n.created_at = coalesce(n.created_at, $now)
                    """, datasets=[d.__dict__ for d in graph.datasets], now=now)
                    
                    session.run("""
                        MATCH (n:Dataset {layer: 'transform', source_system: 'QlikView'})
                        SET n:QlikTable
                    """)
                    session.run("""
                        MATCH (n:Dataset {layer: 'source'})
                        SET n:Table
                    """)

                # 3. Write FieldNodes
                if graph.fields:
                    session.run("""
                        UNWIND $fields AS f
                        MERGE (n:Attribute {id: f.id})
                        SET n.name = f.name,
                            n.data_type = f.data_type,
                            n.role = f.role,
                            n.source_system = f.source_system,
                            n.created_at = coalesce(n.created_at, $now)
                    """, fields=[f.__dict__ for f in graph.fields], now=now)

                # 3.5 Write TransformationNodes
                if graph.transformations:
                    session.run("""
                        UNWIND $transforms AS t
                        MERGE (n:Transformation {id: t.id})
                        SET n.expression = t.expression,
                            n.transformation_type = t.transformation_type,
                            n.source_parser = t.source_parser,
                            n.lineage_depth = t.lineage_depth,
                            n.deterministic = t.deterministic,
                            n.aggregate = t.aggregate,
                            n.created_at = coalesce(n.created_at, $now)
                    """, transforms=[t.__dict__ for t in graph.transformations], now=now)

                # 4. Write Dependency Edges
                if graph.dependency_edges:
                    session.run("""
                        UNWIND $edges AS e
                        MATCH (s {id: e.source_id})
                        MATCH (t {id: e.target_id})
                        CALL apoc.create.relationship(s, e.edge_type, {}, t) YIELD rel
                        RETURN count(rel)
                    """, edges=[e.__dict__ for e in graph.dependency_edges])

                # 5. Write Lineage Edges
                if graph.lineage_edges:
                    session.run("""
                        UNWIND $edges AS e
                        MATCH (s {id: e.source_id})
                        MATCH (t {id: e.target_id})
                        CALL apoc.create.relationship(s, e.edge_type, {}, t) YIELD rel
                        RETURN count(rel)
                    """, edges=[e.__dict__ for e in graph.lineage_edges])

        except Exception as e:
            # apoc.create.relationship requires APOC plugin. 
            # If not available, fallback to manual MATCH/MERGE for known edge types
            logger.warning("apoc_failed_falling_back_to_manual_edges", error=str(e))
            self._write_edges_manual(graph.dependency_edges, graph.lineage_edges)

    def _write_edges_manual(self, deps, lineages):
        # Fallback for standard Neo4j without APOC
        with self.driver.session() as session:
            for e in deps:
                session.run(f"""
                    MATCH (s {{id: $source_id}})
                    MATCH (t {{id: $target_id}})
                    MERGE (s)-[:{e.edge_type}]->(t)
                """, source_id=e.source_id, target_id=e.target_id)
            for e in lineages:
                session.run(f"""
                    MATCH (s {{id: $source_id}})
                    MATCH (t {{id: $target_id}})
                    MERGE (s)-[:{e.edge_type}]->(t)
                """, source_id=e.source_id, target_id=e.target_id)

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None
