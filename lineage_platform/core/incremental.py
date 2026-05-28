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

    def calculate_hash(self, content: str, dependencies: list[str] = None, parser_version: str = "2.1.0", grammar_version: str = "1.0.0") -> dict:
        """
        Calculate a composite SHA-256 hash of the script content and its dependencies.
        """
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        dep_str = "".join(sorted(dependencies)) if dependencies else ""
        dependency_hash = hashlib.sha256(dep_str.encode('utf-8')).hexdigest()
        
        composite_str = f"{content_hash}|{dependency_hash}|{parser_version}|{grammar_version}"
        composite_hash = hashlib.sha256(composite_str.encode('utf-8')).hexdigest()
        
        return {
            "content_hash": content_hash,
            "dependency_hash": dependency_hash,
            "parser_version": parser_version,
            "grammar_version": grammar_version,
            "composite_hash": composite_hash
        }

    def has_changed(self, process_id: str, current_composite_hash: str) -> bool:
        """
        Check if a ProcessNode in Neo4j has a different hash than the current one.
        Returns True if changed or not found.
        """
        cypher = """
        MATCH (p:Process {id: $process_id})
        RETURN p.composite_hash AS composite_hash
        """
        with self.driver.session() as session:
            result = session.run(cypher, process_id=process_id).single()
            if result is None:
                return True # New script
            
            stored_hash = result.get("composite_hash")
            return stored_hash != current_composite_hash

    def expire_script_subgraph(self, process_id: str):
        """
        Instead of hard deleting the graph (Phase 10), we expire it temporally (Phase 11).
        This preserves the history for time-travel queries.
        """
        from datetime import datetime, UTC
        now = datetime.now(UTC).isoformat()
        
        cypher = """
        MATCH (p:Process {id: $process_id})-[:CREATES|LOADS]->(d:Dataset)
        OPTIONAL MATCH (d)-[r:DERIVES_FROM|GENERATED_BY]->()
        WHERE r.is_active = true
        SET r.is_active = false, r.valid_to = $now
        RETURN count(r) AS expired_count
        """
        with self.driver.session() as session:
            res = session.run(cypher, process_id=process_id, now=now).single()
            expired = res["expired_count"] if res else 0
            logger.info("temporal_expiration_complete", process_id=process_id, edges_expired=expired)
