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
    sac = data[0]
    sic = data[1]
    return DataItemSubfield(pos=0, content=[sac, sic])

def decode_data_item_I048_140(data: bytes) -> DataItemSubfield:
    pass

def decode_data_item_I048_020(data: bytes) -> DataItemSubfield:
    octet1 = data[0]

    typ = (octet1 >> 5) & 0b111
    sim = (octet1 >> 4) & 0b1
    rdp = (octet1 >> 3) & 0b1
    spi = (octet1 >> 2) & 0b1
    rab = (octet1 >> 1) & 0b1
    fx = octet1 & 0b1

    content = [typ, sim, rdp, spi, rab]

    if fx == 1:
        octet2 = data[1]

        tst = (octet2 >> 7) & 0b1
        err = (octet2 >> 6) & 0b1
        xpp = (octet2 >> 5) & 0b1
        me = (octet2 >> 4) & 0b1
        mi = (octet2 >> 3) & 0b1
        foe_fri = (octet2 >> 1) & 0b11
        fx2 = octet2 & 0b1

        content.extend([tst, err, xpp, me, mi, foe_fri])

        if fx2 == 1:
            octet3 = data[2]

            ads_b = (octet3 >> 6) & 0b11
            scn = (octet3 >> 4) & 0b11
            pai = (octet3 >> 2) & 0b11
            fx3 = octet3 & 0b1

            content.extend([ads_b, scn, pai])

    return DataItemSubfield(pos=0, content=content)

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