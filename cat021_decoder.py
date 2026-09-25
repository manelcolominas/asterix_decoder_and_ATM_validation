
from models import DataItemSubfield, DataItemType

def decode_data_item_cat021(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    if item_type == DataItemType.I021_010:
        return decode_data_item_I021_010(item_type, data)
    if item_type == DataItemType.I021_040:
        return decode_data_item_I021_040(item_type, data)
    if item_type == DataItemType.I021_070:
        return decode_data_item_I021_070(item_type, data)
    if item_type == DataItemType.I021_073:
        return decode_data_item_I021_073(item_type, data)
    if item_type == DataItemType.I021_080:
        return decode_data_item_I021_080(item_type, data)
    if item_type == DataItemType.I021_131:
        return decode_data_item_I021_131(item_type, data)
    if item_type == DataItemType.I021_145:
        return decode_data_item_I021_145(item_type, data)
    if item_type == DataItemType.I021_170:
        return decode_data_item_I021_170(item_type, data)
    if item_type == DataItemType.I021_REF:
        return decode_data_item_I021_REF(item_type, data)

def decode_data_item_I021_010(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I021_040(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I021_070(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I021_073(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I021_080(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I021_131(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I021_145(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I021_170(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I021_REF(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    pass