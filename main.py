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

EXTENDED_ITEMS = {DataItemType.I021_040, DataItemType.I048_020, DataItemType.I048_170}
REPETITIVE_ITEMS = {DataItemType.I048_250: 8}  # item_type -> subfield size in bytes
COMPOUND_ITEMS = {DataItemType.I048_130, DataItemType.I021_REF}


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
        fspec = parse_fspec(data)
        fields: list[DataField] = []

        for frn, bit in enumerate(fspec, start=1):
            if bit == 0:
                continue
            item_type = map_frn_to_item_type(category, frn)
            item, offset = decode_data_item(item_type, data, offset)
            field = DataField(item=item, field_type=get_field_type(item_type))
            fields.append(field)

        records.append(DataRecord(fspec=fspec, fields=fields))

    return records


def parse_fspec(data: bytes) -> list[int]:
    fspec: list[int] = []
    offset = 0

    while True:
        fspec_octet = data[offset]
        offset += 1

        for bit_position in range(7, 0, -1):
            fspec.append((fspec_octet >> bit_position) & 1)

        fx = fspec_octet & 1
        if fx == 0:
            break

    return fspec

def map_frn_to_item_type(category: CategoryMessage,frn: int):
    if category == CategoryMessage.CAT021:
        mapping = {
            1: DataItemType.I021_010,
            2: DataItemType.I021_040,
            19: DataItemType.I021_070,
            12: DataItemType.I021_073,
            11: DataItemType.I021_080,
            7: DataItemType.I021_131,
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
            12: DataItemType.I048_200,
            13: DataItemType.I048_170,
            14: DataItemType.I048_230,
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


if __name__ == "__main__":
    run_app()