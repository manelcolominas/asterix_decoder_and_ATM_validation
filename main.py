from pathlib import Path

from models import AsterixMessage, CategoryMessage, DataRecord, DataField, DataItem, DataItemType, DataFieldType


FIXED_LENGTHS = {
    DataItemType.I021_010: 2,
    DataItemType.I021_131: 8,
    DataItemType.I021_080: 3,
    DataItemType.I021_073: 3,
    DataItemType.I021_070: 2,
    DataItemType.I021_145: 2,
    DataItemType.I021_170: 6,

    DataItemType.I021_161: 2,
    DataItemType.I021_015: 1,
    DataItemType.I021_071: 3,
    DataItemType.I021_130: 6,
    DataItemType.I021_072: 3,
    DataItemType.I021_150: 2,
    DataItemType.I021_151: 2,
    DataItemType.I021_074: 4,
    DataItemType.I021_075: 3,
    DataItemType.I021_076: 4,
    DataItemType.I021_140: 2,
    DataItemType.I021_210: 1,
    DataItemType.I021_230: 2,
    DataItemType.I021_152: 2,
    DataItemType.I021_200: 1,
    DataItemType.I021_155: 2,
    DataItemType.I021_157: 2,
    DataItemType.I021_160: 4,
    DataItemType.I021_165: 2,
    DataItemType.I021_077: 3,
    DataItemType.I021_020: 1,
    DataItemType.I021_146: 2,
    DataItemType.I021_148: 2,
    DataItemType.I021_016: 1,
    DataItemType.I021_008: 1,
    DataItemType.I021_132: 1,
    DataItemType.I021_260: 7,
    DataItemType.I021_400: 1,

    DataItemType.I048_010: 2,
    DataItemType.I048_140: 3,
    DataItemType.I048_040: 4,
    DataItemType.I048_070: 2,
    DataItemType.I048_090: 2,
    DataItemType.I048_220: 3,
    DataItemType.I048_240: 6,
    DataItemType.I048_161: 2,
    DataItemType.I048_200: 4,
    DataItemType.I048_230: 2,
}

EXTENDED_ITEMS = {
    DataItemType.I021_040,
    DataItemType.I048_020,
    DataItemType.I048_170,  # 1+ octets, terminated by FX = 0
}

REPETITIVE_ITEMS = {
    DataItemType.I048_250: 8,  # 1 + 8*n; first byte is repetition count
}

COMPOUND_ITEMS = {
    DataItemType.I048_130,  # compound: primary subfield indicator + subfields
    DataItemType.I021_REF,
}

COMPOUND_SUBFIELD_LENGTHS = {
    DataItemType.I048_130: (1, 1, 1, 1, 1, 1, 1),
    DataItemType.I021_REF: (1, 1, 1, 1, 1, 1, 1),
}

CAT021_FRN_MAP = {
    3: DataItemType.I021_161,
    4: DataItemType.I021_015,
    5: DataItemType.I021_071,
    6: DataItemType.I021_130,

    8: DataItemType.I021_072,
    9: DataItemType.I021_150,
    10: DataItemType.I021_151,

    13: DataItemType.I021_074,
    14: DataItemType.I021_075,
    
    15: DataItemType.I021_076,
    16: DataItemType.I021_140,
    17: DataItemType.I021_090,
    18: DataItemType.I021_210,


    20: DataItemType.I021_230,

    22: DataItemType.I021_152,
    23: DataItemType.I021_200,
    24: DataItemType.I021_155,
    25: DataItemType.I021_157,
    26: DataItemType.I021_160,
    27: DataItemType.I021_165,
    28: DataItemType.I021_077,

    30: DataItemType.I021_020,
    31: DataItemType.I021_220,
    32: DataItemType.I021_146,
    33: DataItemType.I021_148,
    34: DataItemType.I021_110,

    35: DataItemType.I021_016,
    36: DataItemType.I021_008,
    37: DataItemType.I021_271,
    38: DataItemType.I021_132,
    39: DataItemType.I021_250,
    40: DataItemType.I021_260,
    41: DataItemType.I021_400,
    42: DataItemType.I021_295,
}


CAT048_FRN_MAP = {
    12: DataItemType.I048_042,
    15: DataItemType.I048_210,
    16: DataItemType.I048_030,
    17: DataItemType.I048_080,
    18: DataItemType.I048_100,
    19: DataItemType.I048_110,
    20: DataItemType.I048_120,
    22: DataItemType.I048_260,
    23: DataItemType.I048_055,
    24: DataItemType.I048_050,
    25: DataItemType.I048_065,
    26: DataItemType.I048_060,
    27: DataItemType.SP_DATA_ITEM,
    28: DataItemType.RE_DATA_ITEM,
}


def run_app():
    binary_file_path = Path(
        r"C:\Users\manel\Documents\Educació\Universitat\6è any\1r Quadrimestre"
        r"\Projectes per a la Gestió del Trànsit Aeri\Projectes\Projecte 2 i 3"
        r"\asterix_radar.ast"
    )

    run_pipeline(binary_file_path)


def run_pipeline(binary_file_path: Path) -> list[AsterixMessage]:
    data = read_asterix_messages_bytes(binary_file_path)
    asterix_messages = decode_asterix_messages(data)
    return asterix_messages


def read_asterix_messages_bytes(binary_file_path: Path) -> bytes:
    data = binary_file_path.read_bytes()
    return data


def decode_asterix_messages(data: bytes) -> list[AsterixMessage]:
    messages: list[AsterixMessage] = []
    offset = 0

    while offset < len(data):
        if offset + 3 > len(data):
            break

        category_value = data[offset]
        length = int.from_bytes(data[offset + 1:offset + 3], "big")

        end = offset + length
        message_bytes = data[offset:end]

        if category_value in CategoryMessage._value2member_map_:
            messages.append(decode_asterix_message(message_bytes))

        offset = end

    return messages


def decode_asterix_message(data: bytes) -> AsterixMessage:

    category_value = data[0]
    length = int.from_bytes(data[1:3], "big")

    category = CategoryMessage(category_value)

    payload = data[3:]
    records = decode_records_message(category, payload)

    asterix_message = AsterixMessage(category=category, length=length, records=records)
    return asterix_message


def decode_records_message(category: CategoryMessage, data: bytes) -> list[DataRecord]:
    records: list[DataRecord] = []
    offset = 0
    while offset < len(data):
        fspec, offset = parse_fspec(data, offset)
        fields: list[DataField] = []

        for frn, bit in enumerate(fspec, start=1):
            if bit == 0:
                continue
            item_type = map_frn_to_item_type(category, frn)
            if item_type == DataItemType.I048_130:
                print(DataItemType.I048_130)
            # if item_type is None:
            #     raise ValueError(
            #         f"FRN no mapat: categoria={category.name}, "
            #         f"frn={frn}, fspec={fspec}, offset={offset}"
            #     )
            item, offset = decode_data_item(item_type, data, offset)            
            if item_type in INTERESTING_ITEMS:
                fields.append(
                    DataField(
                        item=item,
                        field_type=get_field_type(item_type),
                    )
                )
            field_type = get_field_type(item_type)
            field = DataField(item=item, field_type=field_type)
            fields.append(field)

        records.append(DataRecord(fspec=fspec, fields=fields))

    return records


def parse_fspec(data: bytes, offset: int) -> tuple[list[int], int]:
    fspec: list[int] = []

    while True:
        fspec_octet = data[offset]
        offset += 1

        for bit_position in range(7, 0, -1):
            fspec.append((fspec_octet >> bit_position) & 1)

        if fspec_octet & 1 == 0:
            break

    return fspec, offset


def map_frn_to_item_type(category: CategoryMessage,frn: int) -> DataItemType:
    if category == CategoryMessage.CAT021:
        mapping = {
            1: DataItemType.I021_010,
            2: DataItemType.I021_040,
            7: DataItemType.I021_131,
            11: DataItemType.I021_080,
            12: DataItemType.I021_073,
            19: DataItemType.I021_070,
            21: DataItemType.I021_145,
            29: DataItemType.I021_170,
            48: DataItemType.I021_REF,
        }
        return mapping.get(frn)

    if category == CategoryMessage.CAT048:
        mapping = {
            1: DataItemType.I048_010,
            2: DataItemType.I048_140,
            3: DataItemType.I048_020,
            4: DataItemType.I048_040,
            5: DataItemType.I048_070,
            6: DataItemType.I048_090,
            7: DataItemType.I048_130,
            8: DataItemType.I048_220,
            9: DataItemType.I048_240,
            10: DataItemType.I048_250,
            11: DataItemType.I048_161,
            13: DataItemType.I048_200,
            14: DataItemType.I048_170,
            21: DataItemType.I048_230,
        }
        return mapping.get(frn)

    return None


def get_field_type(item_type: DataItemType) -> DataFieldType:
    if item_type in FIXED_LENGTHS:
        return DataFieldType.FIXED
    if item_type in EXTENDED_ITEMS:
        return DataFieldType.EXTENDED
    if item_type in REPETITIVE_ITEMS:
        return DataFieldType.REPETITIVE
    if item_type in COMPOUND_ITEMS:
        return DataFieldType.COMPOUND
    raise ValueError(f"No field type rule defined for {item_type}")


def decode_data_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[DataItem, int]:
    field_type = get_field_type(item_type)

    if field_type == DataFieldType.FIXED:
        return decode_fixed_item(item_type, data, offset)
    if field_type == DataFieldType.EXTENDED:
        return decode_extended_item(item_type, data, offset)
    if field_type == DataFieldType.REPETITIVE:
        return decode_repetitive_item(item_type, data, offset)
    if field_type == DataFieldType.COMPOUND:
        return decode_compound_item(item_type, data, offset)

    raise ValueError(f"No decode rule defined for {item_type}")


def decode_fixed_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[DataItem, int]:
    length = FIXED_LENGTHS[item_type]
    content = data[offset:offset + length]
    data_item = DataItem(item_type=item_type, content=content)
    return data_item, offset + length


def decode_extended_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[DataItem, int]:
    content = bytearray()
    while True:
        octet = data[offset]
        content.append(octet)
        offset += 1
        if octet & 1 == 0:  # FX = 0 -> fi de les extensions
            break
    data_item = DataItem(item_type=item_type, content=bytes(content))
    return data_item, offset


def decode_repetitive_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[DataItem, int]:
    rep_count = data[offset]
    offset += 1
    subfield_size = REPETITIVE_ITEMS[item_type]
    total_length = rep_count * subfield_size
    content = data[offset:offset + total_length]
    data_item = DataItem(item_type=item_type, content=content)
    return data_item, offset + total_length


def decode_compound_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[DataItem, int]:
    start_offset = offset
    presence_bits, offset = parse_fspec(data, offset)

    lengths = COMPOUND_SUBFIELD_LENGTHS[item_type]
    content_length = sum(
        lengths[index]
        for index, present in enumerate(presence_bits)
        if present and index < len(lengths)
    )

    end_offset = offset + content_length
    content = data[start_offset:end_offset]

    return DataItem(item_type=item_type, content=content), end_offset


if __name__ == "__main__":
    run_app()