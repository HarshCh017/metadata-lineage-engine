from pathlib import Path


class FileDiscovery:

    @staticmethod
    def discover_qvs_files(root_path: str):
        """
        Recursively discover all QVS files.
        """

        root = Path(root_path)

        if not root.exists():

            print(f"Input path does not exist: {root_path}")

            return []

        files = [f for f in root.rglob("*.qvs") if not f.name.startswith("._")]

        return files
