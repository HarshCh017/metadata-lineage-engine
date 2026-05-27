import traceback

from lineage_platform.batch.file_discovery import (
    FileDiscovery
)

from lineage_platform.parsers.qlikview.qvs_parser import (
    QVSParser
)

from lineage_platform.neo4j.graph_writer import (
    GraphWriter
)


def main():

    print("=" * 60)
    print("PHASE 2 LINEAGE PLATFORM STARTING")
    print("=" * 60)

    try:

        # --------------------------------------------------
        # Discover QVS files
        # --------------------------------------------------

        files = FileDiscovery.discover_qvs_files(
            "data/input/qlikview"
        )

        print(f"Discovered {len(files)} QVS files")

        if not files:

            print("No QVS files found")
            return

        # --------------------------------------------------
        # Initialize parser
        # --------------------------------------------------

        parser = QVSParser()

        # --------------------------------------------------
        # Initialize graph writer
        # --------------------------------------------------

        graph_writer = GraphWriter()

        # --------------------------------------------------
        # Process files
        # --------------------------------------------------

        for file_path in files:

            print(f"\nProcessing: {file_path}")

            try:

                app = parser.parse(
                    str(file_path)
                )

                print(
                    f"Parsed app: {app.app_name}"
                )

                print(
                    f"Loads: {len(app.loads)}"
                )

                print(
                    f"Joins: {len(app.joins)}"
                )

                print(
                    f"Fields: {len(app.fields)}"
                )

                # ------------------------------------------
                # Write graph
                # ------------------------------------------

                graph_writer.write_app(
                    app
                )

                print(
                    "Graph write successful"
                )

            except Exception as file_error:

                print(
                    f"FAILED FILE: {file_path}"
                )

                traceback.print_exc()

        print("\n")
        print("=" * 60)
        print("PHASE 2 PROCESSING COMPLETE")
        print("=" * 60)

    except Exception:

        traceback.print_exc()


# =========================================================
# ENTRYPOINT
# =========================================================

if __name__ == "__main__":

    main()