from lineage_platform.models.intermediate import GraphModel
import structlog

logger = structlog.get_logger()

class SemanticNormalizer:
    """
    Semantic Normalization Layer for the Metadata Engine.
    Ensures that the extracted intermediate graph is consistent, deduplicated,
    and ontologically sound before being exported to OpenLineage or written to Neo4j.
    """

    @classmethod
    def normalize(cls, graph: GraphModel) -> GraphModel:
        """
        Normalize the entire graph model in-place (or by returning a cleaned copy).
        """
        original_node_count = len(graph.fields) + len(graph.datasets) + len(graph.transformations)
        
        # 1. Deduplicate Fields by ID
        unique_fields = {}
        for f in graph.fields:
            if f.id not in unique_fields:
                unique_fields[f.id] = f
            else:
                # Merge properties if needed, but for now we just keep the first occurrence
                unique_fields[f.id].properties.update(f.properties)
        graph.fields = list(unique_fields.values())

        # 2. Deduplicate Datasets by ID
        unique_datasets = {}
        for d in graph.datasets:
            if d.id not in unique_datasets:
                unique_datasets[d.id] = d
        graph.datasets = list(unique_datasets.values())

        # 3. Standardize Casing for Fully Qualified Names
        for d in graph.datasets:
            if d.fully_qualified_name:
                # Ensure FQN is always upper case to prevent graph fragmentation 
                # (e.g. 'DB.schema.TABLE' vs 'db.SCHEMA.table')
                d.fully_qualified_name = d.fully_qualified_name.upper()

        # 4. Deduplicate Edges (Dependency and Lineage)
        unique_dep_edges = {(e.source_id, e.target_id, e.edge_type): e for e in graph.dependency_edges}
        graph.dependency_edges = list(unique_dep_edges.values())

        unique_lin_edges = {(e.source_id, e.target_id, e.edge_type): e for e in graph.lineage_edges}
        graph.lineage_edges = list(unique_lin_edges.values())

        new_node_count = len(graph.fields) + len(graph.datasets) + len(graph.transformations)
        
        if original_node_count != new_node_count:
            logger.info("normalization_complete", 
                        deduplicated_nodes=original_node_count - new_node_count,
                        final_fields=len(graph.fields),
                        final_datasets=len(graph.datasets))
            
        return graph
