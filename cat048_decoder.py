from models import DataItemType, DataItemSubfield

def decode_data_item_cat048(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    if item_type == DataItemType.I048_010:
        return decode_data_item_I048_010(data)
    if item_type == DataItemType.I048_140:
        return decode_data_item_I048_140(data)
    if item_type == DataItemType.I048_020:
        return decode_data_item_I048_020(data)
    if item_type == DataItemType.I048_040:
        return decode_data_item_I048_040(data)
    if item_type == DataItemType.I048_070:
        return decode_data_item_I048_070(data)
    if item_type == DataItemType.I048_090:
        return decode_data_item_I048_090(data)
    if item_type == DataItemType.I048_130:
        return decode_data_item_I048_130(data)
    if item_type == DataItemType.I048_220:
        return decode_data_item_I048_220(data)
    if item_type == DataItemType.I048_240:
        return decode_data_item_I048_240(data)
    if item_type == DataItemType.I048_250:
        return decode_data_item_I048_250(data)
    if item_type == DataItemType.I048_161:
        return decode_data_item_I048_161(data)
    if item_type == DataItemType.I048_200:
        return decode_data_item_I048_200(data)
    if item_type == DataItemType.I048_170:
        return decode_data_item_I048_170(data)
    if item_type == DataItemType.I048_230:
        return decode_data_item_I048_230(data)

def decode_data_item_I048_010(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_140(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_020(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_040(data: bytes) -> DataItemSubfield:
    pass
    
def decode_data_item_I048_070(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_090(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_130(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_220(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_240(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_250(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_161(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_200(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_170(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_230(data: bytes) -> DataItemSubfield:
    pass