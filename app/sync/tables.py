
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
    "ItemComponent": {
        "table": "dbo.ItemComponent",
        "columns": ["Id", "ItemId", "ParentItemId", "Quantity"],
        "pk": "Id",
    },
    "StockDocument": {
        "table": "dbo.StockDocument",
        "columns": [
            "Id", "DocumentNumber", "NumberPrefix", "DocumentDate", "DocumentType",
            "DocumentStage", "StorehouseId", "TargetStorehouseId", "OriginDocumentId",
            "SerialId", "xx_Planning", "xx_Numero_planning_origine",
            "xx_bon_de_Fabrication", "xx_Etat_de_Production",
        ],
        "pk": "Id",
    },
    "StockMovement": {
        "table": "dbo.StockMovement",
        "columns": [
            "Id", "ItemId", "DocumentId", "DocumentLineId", "StorehouseId",
            "DocumentDate", "DocumentOrder", "DocumentNumber", "DocumentType",
            "DocumentSubType", "MovementType", "Quantity", "RealStock",
            "VirtualStock", "StockValue", "sysCreatedDate", "sysModifiedDate",
        ],
        "pk": "Id",
    },
    "StockDocumentLine": {
        "table": "dbo.StockDocumentLine",
        "columns": [
            "Id", "DocumentId", "LineType", "LineOrder", "Quantity", "RealQuantity",
            "PreviousTotalValue", "StockMovementId", "ItemId", "RangeItemId",
            "OriginLineId", "ParentLineId", "TopParentLineId", "RemainingQuantity",
            "StorehouseId", "sysCreatedDate",
        ],
        "pk": "Id",
    },
}

