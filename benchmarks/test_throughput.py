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

def test_parser_throughput():
    print("Generating synthetic 50,000 line Qlik script...")
    script_path = generate_large_script(50000)
    
    file_size_mb = os.path.getsize(script_path) / (1024 * 1024)
    print(f"File Size: {file_size_mb:.2f} MB")
    
    parser = QVSParser()
    
    print("Starting parse benchmark...")
    start = time.time()
    app = parser.parse(str(script_path))
    end = time.time()
    
    duration = end - start
    throughput = file_size_mb / duration if duration > 0 else 0
    
    print("-" * 40)
    print(f"Time Taken  : {duration:.3f} seconds")
    print(f"Throughput  : {throughput:.2f} MB/s")
    print(f"Tables Found: {len(app.loads)}")
    print("-" * 40)
    
    if script_path.exists():
        script_path.unlink()

if __name__ == "__main__":
    test_parser_throughput()
