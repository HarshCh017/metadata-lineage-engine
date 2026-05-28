import time
import os
from pathlib import Path
from lineage_platform.parsers.qlikview.qvs_parser import QVSParser

def generate_large_script(lines: int) -> Path:
    script_path = Path("large_benchmark.qvs")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write("SET vBenchmark = 1;\n")
        for i in range(lines // 10):
            f.write(f"Load{i}:\n")
            f.write(f"LOAD Field1 AS F{i}_1, Field2 AS F{i}_2, Field3 AS F{i}_3\n")
            f.write(f"FROM [lib://Data/Source_{i}.csv] (txt);\n\n")
    return script_path

import tracemalloc
import json
from datetime import datetime

def test_parser_throughput():
    print("Generating synthetic 50,000 line Qlik script...")
    script_path = generate_large_script(50000)
    
    file_size_mb = os.path.getsize(script_path) / (1024 * 1024)
    print(f"File Size: {file_size_mb:.2f} MB")
    
    # We will use the new ANTLRQVSParser to track fallback metrics
    from lineage_platform.parsers.qlikview.antlr_parser import ANTLRQVSParser
    parser = ANTLRQVSParser()
    
    print("Starting parse benchmark...")
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tracemalloc.start()
    start = time.time()
    
    app, metadata = parser.parse(content)
    
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    duration = end - start
    throughput = file_size_mb / duration if duration > 0 else 0
    peak_mb = peak / (1024 * 1024)
    
    print("-" * 40)
    print(f"Time Taken       : {duration:.3f} seconds")
    print(f"Throughput       : {throughput:.2f} MB/s")
    print(f"Peak Memory      : {peak_mb:.2f} MB")
    print(f"Fallback Triggered: {metadata.fallback_triggered}")
    print("-" * 40)
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "benchmark": "throughput",
        "file_size_mb": file_size_mb,
        "duration_seconds": duration,
        "throughput_mb_s": throughput,
        "peak_memory_mb": peak_mb,
        "fallback_triggered": metadata.fallback_triggered,
        "engine": metadata.parser_engine
    }
    
    os.makedirs("benchmarks/results", exist_ok=True)
    with open(f"benchmarks/results/throughput_{int(time.time())}.json", "w") as f:
        json.dump(result, f, indent=2)
    
    if script_path.exists():
        script_path.unlink()

if __name__ == "__main__":
    test_parser_throughput()
