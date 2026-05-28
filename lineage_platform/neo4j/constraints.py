"""
Neo4j constraint and index definitions for the Metadata Lineage Engine.

These are applied via schema_manager.ensure_constraints() at startup.
See schema_manager.py for the runtime logic.
"""

# Unique constraints (plan §5.3)
UNIQUE_CONSTRAINTS = {
    "QlikScript": "id",
    "QlikTable": "id",
    "Connection": "id",
    "Table": "fully_qualified_name",
    "Attribute": "id",
}

# Performance indexes
INDEXES = {
    "QlikChart": "name",
    "Table": "name",
    "Variable": "name",
}
