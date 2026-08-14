""""
Script d'inspection des tables dans EBP
"""

import sys
from database import ebp_engine
from sqlalchemy import inspect

def inspect_table(table_name: str):
    inspector = inspect(ebp_engine)
    
    if table_name not in inspector.get_table_names(schema="dbo"):
        print(f" Table '{table_name}' introuvable dans le scéma dbo.")
    
    print(f"\n=== Colonnes de dbo.{table_name} ===")
    for col in inspector.get_columns(table_name, schema="dbo"):
        nullable = "NULL" if col["nullable"] else "NOT NULL"
        print(f"  {col['name']:<35} {str(col['type']):<25} {nullable}")
        
    print(f"\n=== Index ===")
    for idx in inspector.get_indexes(table_name, schema="dbo"):
        print(f"  {idx['name']}: {idx['column_names']} (unique={idx['unique']})")
        
if __name__ == "__main__":
    table = sys.argv[1] if len(sys.argv) > 1 else "RangeItem"
    inspect_table(table)