import time
import os
from lineage_platform.models.intermediate import GraphModel, DatasetNode, LineageEdge, FieldNode
from lineage_platform.neo4j.batch_writer import BatchGraphWriter


def run_write_benchmark(num_tables=1000, num_columns_total=50000):
    print(f"Generating synthetic graph with {num_tables} tables and {num_columns_total} columns...")

    # 1. Setup intermediate graph for Batch Writer
    graph = GraphModel()
    cols_per_table = num_columns_total // num_tables

    for i in range(num_tables):
        node = DatasetNode(id=f"benchmark_{i}", name=f"Table_{i}", fully_qualified_name=f"db.schema.Table_{i}")
        graph.datasets.append(node)

        # Add realistic columns
        for c in range(cols_per_table):
            field = FieldNode(id=f"benchmark_{i}_col_{c}", name=f"Col_{c}", data_type="VARCHAR")
            graph.fields.append(field)

        if i > 0:
            graph.lineage_edges.append(LineageEdge(source_id=f"benchmark_{i}", target_id=f"benchmark_{i - 1}"))

    # 1.5 Benchmark Normalization
    print("Benchmarking Semantic Normalizer...")
    from lineage_platform.core.normalization import SemanticNormalizer
    start_norm = time.time()
    graph = SemanticNormalizer.normalize(graph)
    norm_duration = time.time() - start_norm
    print(f"Normalization Time: {norm_duration:.3f} seconds")

    # 2. Benchmark BatchGraphWriter
    print("\nBenchmarking BatchGraphWriter (UNWIND)...")
    batch_writer = BatchGraphWriter()
    start_batch = time.time()
    batch_writer.write_graph(graph)
    batch_duration = time.time() - start_batch
    batch_writer.close()

    total_nodes = num_tables + num_columns_total

    print("-" * 40)
    print(f"Batch Write Time: {batch_duration:.3f} seconds")
    print(f"Batch Throughput: {total_nodes / batch_duration:.2f} nodes/sec")
    print("-" * 40)

    import json
    from datetime import datetime
    result = {
        "timestamp": datetime.now().isoformat(),
        "benchmark": "neo4j_write",
        "num_tables": num_tables,
        "num_columns": num_columns_total,
        "normalization_seconds": norm_duration,
        "batch_write_seconds": batch_duration,
        "throughput_nodes_sec": total_nodes / batch_duration
    }

    os.makedirs("benchmarks/results", exist_ok=True)
    with open(f"benchmarks/results/graph_write_{int(time.time())}.json", "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    run_write_benchmark()
