import subprocess
import sys

def run_benchmarks():
    print("=" * 60)
    print(" ENTERPRISE BENCHMARK SUITE ")
    print("=" * 60)
    
    print("\n[1] Running Parser Throughput Benchmark...")
    subprocess.run([sys.executable, "benchmarks/test_throughput.py"])
    
    print("\n[2] Running Neo4j Batch Write Benchmark...")
    print("    (Note: Requires Neo4j to be running on localhost:7687)")
    subprocess.run([sys.executable, "benchmarks/test_graph_write.py"])
    
    print("\n=" * 60)
    print(" BENCHMARKS COMPLETE ")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmarks()
