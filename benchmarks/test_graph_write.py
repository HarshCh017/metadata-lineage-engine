import time
import os
from lineage_platform.models.intermediate import GraphModel, DatasetNode, LineageEdge
from lineage_platform.neo4j.batch_writer import BatchGraphWriter
from lineage_platform.neo4j.graph_writer import GraphWriter
from lineage_platform.models.qlik_models import QlikViewApp, QVSLoad

def run_write_benchmark(num_nodes=5000):
    print(f"Generating synthetic graph with {num_nodes} nodes and {num_nodes} edges...")
    
    # 1. Setup intermediate graph for Batch Writer
    graph = GraphModel()
    for i in range(num_nodes):
        node = DatasetNode(id=f"benchmark_{i}", name=f"Table_{i}", fully_qualified_name=f"db.schema.Table_{i}")
        graph.datasets.append(node)
        if i > 0:
            graph.lineage_edges.append(LineageEdge(source_id=f"benchmark_{i}", target_id=f"benchmark_{i-1}"))

    # 2. Benchmark BatchGraphWriter
    print("\nBenchmarking BatchGraphWriter (UNWIND)...")
    batch_writer = BatchGraphWriter()
    start_batch = time.time()
    batch_writer.write_graph(graph)
    batch_duration = time.time() - start_batch
    batch_writer.close()
    
    print("-" * 40)
    print(f"Batch Write Time: {batch_duration:.3f} seconds")
    print(f"Batch Throughput: {num_nodes / batch_duration:.2f} nodes/sec")
    print("-" * 40)

if __name__ == "__main__":
    run_write_benchmark()
