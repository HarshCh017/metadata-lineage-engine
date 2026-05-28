import hashlib
from typing import Optional
from neo4j import GraphDatabase
import structlog

logger = structlog.get_logger()

class IncrementalProcessor:
    """
    Handles Change-Aware Lineage Refresh.
    Detects if a script has changed since the last parse to avoid expensive 
    full-graph regenerations.
    """

    def __init__(self, driver: GraphDatabase.driver):
        self.driver = driver

    def calculate_hash(self, content: str) -> str:
        """
        Calculate a SHA-256 hash of the script content.
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def has_changed(self, process_id: str, current_hash: str) -> bool:
        """
        Check if a ProcessNode in Neo4j has a different hash than the current one.
        Returns True if changed or not found.
        """
        cypher = """
        MATCH (p:Process {id: $process_id})
        RETURN p.script_hash AS script_hash
        """
        with self.driver.session() as session:
            result = session.run(cypher, process_id=process_id).single()
            if result is None:
                return True # New script
            
            stored_hash = result.get("script_hash")
            return stored_hash != current_hash

    def drop_script_subgraph(self, process_id: str):
        """
        If a script has changed, we must drop its previously generated specific lineage 
        before re-inserting to prevent orphaned graph artifacts.
        
        Note: This drops downstream relationships originating explicitly from this script's datasets.
        In a mature enterprise system, this is handled via time-travel / temporal graphs, 
        but for Phase 10 we implement a hard differential drop.
        """
        # Delete only edges that were specifically created by this process
        # We find datasets created by this process, and delete their DERIVES_FROM edges.
        cypher = """
        MATCH (p:Process {id: $process_id})-[:CREATES|LOADS]->(d:Dataset)
        OPTIONAL MATCH (d)-[r:DERIVES_FROM|GENERATED_BY]->()
        DELETE r
        """
        with self.driver.session() as session:
            res = session.run(cypher, process_id=process_id)
            logger.info("differential_drop_complete", process_id=process_id, counters=res.consume().counters.relationships_deleted)
