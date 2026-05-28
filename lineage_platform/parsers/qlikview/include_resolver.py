import re
from pathlib import Path
import os

class IncludeResolver:
    """
    Resolves QlikView $(Include) and $(Must_Include) directives.
    """
    
    INCLUDE_PATTERN = re.compile(r"\$\(\s*(?:Must_)?Include=([^)]+)\s*\)", re.IGNORECASE)

    @staticmethod
    def resolve_includes(content: str, base_path: Path, depth: int = 0) -> str:
        """
        Recursively replaces $(Include=...) directives with the contents of the referenced files.
        """
        max_depth = int(os.getenv("QLIK_MAX_INCLUDE_DEPTH", "10"))
        
        if depth > max_depth:
            print("WARNING: Max include depth reached.")
            return content

        def replace_include(match):
            rel_path = match.group(1).strip()
            
            # Strip quotes
            if (rel_path.startswith("'") and rel_path.endswith("'")) or \
               (rel_path.startswith('"') and rel_path.endswith('"')):
                rel_path = rel_path[1:-1]
            
            # Resolve path relative to the current file, or against QLIK_INCLUDE_ROOT
            include_root = os.getenv("QLIK_INCLUDE_ROOT")
            if include_root:
                target_path = Path(include_root) / rel_path
            else:
                target_path = base_path.parent / rel_path
                
            if target_path.exists():
                included_content = target_path.read_text(encoding="utf-8", errors="ignore")
                return IncludeResolver.resolve_includes(included_content, target_path, depth + 1)
            else:
                print(f"WARNING: Included file not found: {target_path}")
                return ""

        return IncludeResolver.INCLUDE_PATTERN.sub(replace_include, content)
