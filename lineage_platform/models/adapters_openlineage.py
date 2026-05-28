import uuid
from datetime import datetime, UTC
from typing import Dict, Any
from lineage_platform.models.intermediate import GraphModel

class OpenLineageAdapter:
    """
    Transforms the internal Intermediate Metadata GraphModel into standard 
    OpenLineage RunEvent JSON structures.
    
    This abstracts Neo4j away and provides an interoperable metadata format.
    """

    def __init__(self, namespace: str = "qlikview://enterprise"):
        self.namespace = namespace

    def to_openlineage_events(self, graph: GraphModel) -> list[Dict[str, Any]]:
        """
        Converts the graph model to a list of OpenLineage RunEvents.
        Each ProcessNode becomes a Job with a Run, and LineageEdges translate 
        to inputs and outputs for that Run.
        """
        events = []
        
        # Build lookup for fast navigation
        datasets_by_id = {d.id: d for d in graph.datasets}
        
        now = datetime.now(UTC).isoformat() + "Z"

        for process in graph.processes:
            run_id = str(uuid.uuid4())
            
            # Find inputs and outputs for this specific process
            inputs = []
            outputs = []
            
            for edge in graph.lineage_edges:
                # In a real traversal, we'd map edges directly connected to the process.
                # For this adapter, we map the datasets directly.
                if edge.edge_type == "LOADS" and edge.source_id == process.id:
                    if edge.target_id in datasets_by_id:
                        ds = datasets_by_id[edge.target_id]
                        inputs.append({
                            "namespace": self.namespace,
                            "name": ds.fully_qualified_name
                        })
                elif edge.edge_type == "CREATES" and edge.source_id == process.id:
                    if edge.target_id in datasets_by_id:
                        ds = datasets_by_id[edge.target_id]
                        outputs.append({
                            "namespace": self.namespace,
                            "name": ds.fully_qualified_name
                        })

            event = {
                "eventType": "COMPLETE",
                "eventTime": now,
                "run": {
                    "runId": run_id
                },
                "job": {
                    "namespace": self.namespace,
                    "name": process.name
                },
                "inputs": inputs,
                "outputs": outputs,
                "producer": "metadata-lineage-engine/2.1.0"
            }
            events.append(event)

        return events
