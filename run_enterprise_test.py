import pytest
import sys
import os

def run_enterprise_test():
    print("="*60)
    print("Initiating Enterprise Governance Platform Validation")
    print("="*60)
    
    os.environ["PYTHONPATH"] = "."
    
    print("\n[1/3] Running Full Integrity & Semantic Validation Suite...")
    exit_code_tests = pytest.main(["tests/", "-v"])
    if exit_code_tests != 0:
        print("[FAIL] Core validation suite failed.")
        sys.exit(exit_code_tests)
        
    print("\n[2/3] Running High-Density Governance Stress Tests (10M scale simulated)...")
    exit_code_bench = pytest.main(["benchmarks/test_graph_density.py", "-v"])
    if exit_code_bench != 0:
        print("[FAIL] Graph density stress tests failed.")
        sys.exit(exit_code_bench)
        
    print("\n[3/3] Running Temporal Latency Benchmarks...")
    exit_code_temporal = pytest.main(["benchmarks/test_temporal_benchmark.py", "-v"])
    if exit_code_temporal != 0:
        print("[FAIL] Temporal benchmarks failed.")
        sys.exit(exit_code_temporal)
        
    print("="*60)
    print("[SUCCESS] All Enterprise Validation Gates Passed Successfully.")
    print("="*60)

if __name__ == "__main__":
    run_enterprise_test()
