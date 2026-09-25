from pathlib import Path

from models import FRN_MAPS, ITEM_SPECS, AsterixMessage, CategoryMessage, DataRecord, DataField, DataItem, DataItemType, DataFieldType

from cat021_decoder import decode_data_item_cat021
from cat048_decoder import decode_data_item_cat048

INTERESTING_DATA_ITEMS = {
    DataItemType.I021_010,
    DataItemType.I021_040,
    DataItemType.I021_070,
    DataItemType.I021_073,
    DataItemType.I021_080,
    DataItemType.I021_131,
    DataItemType.I021_145,
    DataItemType.I021_170,
    DataItemType.I021_REF,

    DataItemType.I048_010,
    DataItemType.I048_140,
    DataItemType.I048_020,
    DataItemType.I048_040,
    DataItemType.I048_070,
    DataItemType.I048_090,
    DataItemType.I048_130,
    DataItemType.I048_220,
    DataItemType.I048_240,
    DataItemType.I048_250,
    DataItemType.I048_161,
    DataItemType.I048_200,
    DataItemType.I048_170,
    DataItemType.I048_230,
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
            print(item_type)
            item, offset = decode_data_item(category,item_type, data, offset)
            field = DataField(item=item,field_type=get_field_type(item_type))
            
            if item_type in INTERESTING_DATA_ITEMS:
                fields.append(field)
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


def map_frn_to_item_type(category: CategoryMessage,frn: int) -> DataItemType | None:
    return FRN_MAPS.get(category, {}).get(frn)


def get_field_type(item_type: DataItemType) -> DataFieldType:
    return ITEM_SPECS[item_type].field_type


def decode_data_item(category: CategoryMessage, item_type: DataItemType, data: bytes, offset: int) -> tuple[DataItem, int]:
    field_type = get_field_type(item_type)

    if field_type == DataFieldType.FIXED:
        raw_content, new_offset = decode_fixed_item(item_type, data, offset)
    elif field_type == DataFieldType.EXTENDED:
        raw_content, new_offset = decode_extended_item(item_type, data, offset)
    elif field_type == DataFieldType.REPETITIVE:
        raw_content, new_offset = decode_repetitive_item(item_type, data, offset)
    elif field_type == DataFieldType.COMPOUND:
        raw_content, new_offset = decode_compound_item(item_type, data, offset)
    elif field_type == DataFieldType.LENGTH_INDICATED:
        raw_content, new_offset = decode_length_indicated_item(item_type, data, offset)
    else:
        raise ValueError(f"No decode rule defined for {item_type}")

    if category == CategoryMessage.CAT021:
        subfield = decode_data_item_cat021(item_type, raw_content)
    elif category == CategoryMessage.CAT048:
        subfield = decode_data_item_cat048(item_type, raw_content)
    else:
        raise ValueError(f"Unsupported category: {category}")

    return DataItem(item_type=item_type,content=subfield), new_offset


def decode_fixed_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[bytes, int]:
    length = ITEM_SPECS[item_type].length
    content = data[offset:offset + length]
    return content, offset + length


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
    subfield_size = ITEM_SPECS[item_type].repetition_size
    total_length = rep_count * subfield_size
    content = data[offset:offset + total_length]
    data_item = DataItem(item_type=item_type, content=content)
    return data_item, offset + total_length


def decode_compound_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[DataItem, int]:
    start_offset = offset
    presence_bits, offset = parse_fspec(data, offset)

    lengths = ITEM_SPECS[item_type].subfield_lengths
    content_length = sum(
        lengths[index]
        for index, present in enumerate(presence_bits)
        if present and index < len(lengths)
    )

    end_offset = offset + content_length
    content = data[start_offset:end_offset]

    return DataItem(item_type=item_type, content=content), end_offset

def decode_length_indicated_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[bytes, int]:
    length = data[offset]

    if length < 1:
        raise ValueError(f"Invalid length for {item_type}: {length}")

    end_offset = offset + length

    if end_offset > len(data):
        raise ValueError(f"Truncated data item: {item_type}")

    content = data[offset:end_offset]
    return content, end_offset


if __name__ == "__main__":
    run_app()