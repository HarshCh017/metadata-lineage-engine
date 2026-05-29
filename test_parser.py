from pathlib import Path
import json

from lineage_platform.parsers.qlikview.qvs_parser import QVSParser

INPUT_DIR = Path("data/input/qlikview")

parser = QVSParser()

qvs_files = [
    f for f in INPUT_DIR.glob("*.qvs")
    if not f.name.startswith("._")
]

print(f"\nFound {len(qvs_files)} QVS files\n")

for qvs_file in qvs_files:

    print("=" * 80)
    print(f"Parsing File: {qvs_file.name}")
    print("=" * 80)

    try:
        result = parser.parse(file_path=str(qvs_file))

        # If using Pydantic model
        if hasattr(result, "model_dump"):
            print(json.dumps(result.model_dump(), indent=2))

        else:
            print(result)

        print("\nSUCCESS\n")

    except Exception as e:
        print("\nFAILED\n")
        print(str(e))