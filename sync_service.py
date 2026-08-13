from datetime import datetime

from sqlalchemy import text

from database import EbpSession, ProductionSession

SYNC_TABLES = {
    "RangeItem":{
        "table": "dbo.RangeItem",
        "columns":["Id","Caption","ItemType", "xx_Article_bien"],
        "pk":"Id",
    },
    "RangeTypeElement": {
        "table": "dbo.RangeTypeElement",
        "columns": ["Id", "Code"],
        "pk": "Id",
    },
    "Storehouse": {
        "table": "dbo.Storehouse",
        "columns": ["Id", "Caption"],
        "pk": "Id",
    },
    "Item": {
        "table": "dbo.Item",
        "columns": [
            "Id", "Caption", "ItemType", "DefaultQuantity", "ParentRangeItemId",
            "RangeTypeElementId0", "DesComClear", "xx_MACHINE_TONNAGE",
            "xx_Article_Bien", "RealStock", "ActiveState", "ManageStock",
        ],
        "pk": "Id",
    },
}

def get_last_sync_version(sync_db, table_name: str) -> int:
    stmt = text("SELECT last_sync_version FROM dbo.sync_state WHERE table_name = :table_name")
    row = sync_db.execute(stmt, {"table_name": table_name}).fetchone()
    return row[0] if row else 0

def update_last_sync_version(sync_db, table_name: str, version: int):
    stmt = text("""
        UPDATE dbo.sync_state
        SET last_sync_version = :v, last_sync_date = GETDATE()
        WHERE table_name = :t    
        """
    )
    sync_db.execute(stmt,{"v": version, "t": table_name})
    
def get_current_change_version(ebp_db) -> int:
    stmt = text("SELECT CHANGE_TRACKING_CURRENT_VERSION()")
    row = ebp_db.execute(stmt).fetchone()
    return row[0] or 0

def initial_full_sync(table_name: str) -> dict

def sync_table_changes(table_name: str) -> dict:
    """ Synchronise les changements d'une table donnée, définie dans SYNC_TABLES"""
    
    config = SYNC_TABLES[table_name]
    full_table = config["table"]
    columns = config["columns"]
    pk = config["pk"]
    
    ebp_db = EbpSession()
    sync_db = ProductionSession()
    stats = {"table": table_name, "inserted_updated": 0, "deleted": 0, "from_version": 0, "to_version": 0}
    
    try:
        last_version = get_last_sync_version(sync_db, table_name)
        current_version = get_current_change_version(ebp_db)
        stats["from_version"] = last_version
        stats["to_version"] = current_version
        
        if current_version <= last_version:
            return stats
        
        columns_select = ", ".join(f"src.{c}" for c in columns)
        query = text(f"""
            SELECT ct.SYS_CHANGE_OPERATION, ct.{pk}, {columns_select}
            FROM CHANGETABLE(CHANGES {full_table}, :last_version) AS ct
            LEFT JOIN {full_table} src ON src.{pk} = ct.{pk}       
        """)
        
        changes = ebp_db.execute(query, {"last_version": last_version}).fetchall()
        
        for row in changes:
            op = row[0]
            row_id = row[1]
            
            if op == "D":
                stmt = text(f"DELETE FROM {full_table} WHERE {pk} = :id")
                sync_db.execute(stmt, {"id": row_id})
                stats["deleted"] +=1
            
            else:
                values = dict(zip(columns, row[2:]))
                values["sync_updated_at"] = datetime.now()
                
                exist_stmt = text(f"SELECT 1 FROM {full_table} WHERE {pk} = :id")
                exists = sync_db.execute(exist_stmt, {"id": row_id}).fetchone()
                
                if exists:
                    set_clause = ", ".join(f"{k} = :{k}" for k in values if k != pk)
                    update_stmt = text(f"UPDATE {full_table} SET {set_clause} WHERE {pk} = :{pk}")
                    sync_db.execute(update_stmt, values | {pk: row_id})
                    
                else:
                    cols = ", ".join(values.keys())
                    params = ", ".join(f":{k}" for k in values.keys())
                    sync_db.execute(text(f"INSERT INTO {full_table} ({cols}) VALUES ({params})"), values)
                    stats["inserted_updated"] += 1
                    
        update_last_sync_version(sync_db, table_name, current_version)
        sync_db.commit()
        
    except Exception:
        sync_db.rollback()
        raise
    
    finally:
        ebp_db.close()
        sync_db.close()
        
    return stats

def sync_all_tables() -> list[dict]:
    """Synchronise les tables dans SYNC_TABLES dans l'ordre"""
    results = []
    for table in SYNC_TABLES:
        results.append(sync_table_changes(table))
    return results