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
    # Time of Day: 3 octets que formen un enter sense signe
    value = int.from_bytes(data[0:3], "big")
    # LSB = 1/128 s -> passem a segons des de mitjanit (UTC)
    time_seconds = value / 128
    return DataItemSubfield(pos=0, content=[time_seconds])

def decode_data_item_I048_020(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_040(data: bytes) -> DataItemSubfield:
    pass
    
def decode_data_item_I048_070(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_090(data: bytes) -> DataItemSubfield:
    # Flight Level: ajuntem els 2 octets en un sol numero de 16 bits
    value = int.from_bytes(data[0:2], "big")
    # Bit 16: V (0 = validat, 1 = no validat)
    v = (value >> 15) & 1
    # Bit 15: G (0 = per defecte, 1 = garbled)
    g = (value >> 14) & 1
    # Bits 14-1: Flight Level en complement a 2
    fl = value & 0x3FFF
    # Si el bit 14 es 1, el numero es negatiu
    if fl >= 0x2000:
        fl = fl - 0x4000
    # LSB = 1/4 FL
    flight_level = fl / 4
    return DataItemSubfield(pos=0, content=[v, g, flight_level])

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