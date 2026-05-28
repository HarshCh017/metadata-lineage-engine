import subprocess
import sys
import os

def run_benchmarks():
    env = os.environ.copy()
    # Add the project root to PYTHONPATH so imports resolve
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
    print("=" * 60)
    print(" ENTERPRISE BENCHMARK SUITE ")
    print("=" * 60)
    
    print("\n[1] Running Parser Throughput Benchmark...")
    subprocess.run([sys.executable, "benchmarks/test_throughput.py"], env=env)
    
    print("\n[2] Running Neo4j Batch Write Benchmark...")
    print("    (Note: Requires Neo4j to be running on localhost:7687)")
    subprocess.run([sys.executable, "benchmarks/test_graph_write.py"], env=env)
    
    print("\n[3] Running Incremental Refresh Benchmark...")
    subprocess.run([sys.executable, "benchmarks/test_incremental.py"], env=env)
    
    print("\n[4] Running Temporal Query Benchmark...")
    subprocess.run([sys.executable, "benchmarks/test_temporal_benchmark.py"], env=env)
    
    print("\n=" * 60)
    print(" BENCHMARKS COMPLETE ")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmarks()
