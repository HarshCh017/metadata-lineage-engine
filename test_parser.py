from pathlib import Path
import json

from lineage_platform.parsers.qlikview.qlikview_parser import QlikViewParser

INPUT_DIR = Path("data/input/qlikview")

parser = QlikViewParser()

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
        result = parser.parse_file(qvs_file)

        # If using Pydantic model
        if hasattr(result, "model_dump"):
            print(json.dumps(result.model_dump(), indent=2))

        else:
            print(result)

        print("\nSUCCESS\n")

    except Exception as e:
        print("\nFAILED\n")
        print(str(e))