import gc
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
    # binary_file_path = Path( r"inputs\asterix_radar.ast") # cat048
    binary_file_path = Path( r"inputs\asterix_adsb.ast") # cat021
    # binary_file_path = Path( r"inputs\asterix_combinado.ast") # cat048 + cat021

    run_pipeline(binary_file_path)


def run_pipeline(binary_file_path: Path) -> list[AsterixMessage]:
    data = read_asterix_messages_bytes(binary_file_path)
    asterix_messages = decode_asterix_messages(data)
    return asterix_messages


def read_asterix_messages_bytes(binary_file_path: Path) -> bytes:
    data = binary_file_path.read_bytes()
    return data


def decode_asterix_messages(data: bytes) -> list[AsterixMessage]:
    # Decoding allocates millions of long-lived, acyclic objects. The cyclic GC
    # would repeatedly re-scan them without freeing anything, so pause it here
    # and restore the caller's previous state afterwards.
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        return decode_asterix_messages(data)
    finally:
        if gc_was_enabled:
            gc.enable()


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


# Lookup tables: for every possible FSPEC octet, its 7 presence bits and the
# 1-based positions of the bits that are set.
FSPEC_BITS = tuple(tuple((octet >> bit) & 1 for bit in range(7, 0, -1)) for octet in range(256))
FSPEC_SET = tuple(tuple(pos for pos, bit in enumerate(bits, start=1) if bit) for bits in FSPEC_BITS)

# Per-category dispatch cache: frn -> (item_type, field_type, is_interesting, fixed_length)
DISPATCH_CACHE: dict = {}

def get_dispatch(category: CategoryMessage) -> dict:
    table = DISPATCH_CACHE.get(category)
    if table is None:
        table = {}
        for frn, item_type in FRN_MAPS.get(category, {}).items():
            spec = ITEM_SPECS.get(item_type)
            if spec is None:
                continue  # falls back to the generic path, which raises as before
            table[frn] = (item_type, spec.field_type, item_type in INTERESTING_DATA_ITEMS, spec.length)
        DISPATCH_CACHE[category] = table
    return table


def parse_fspec_with_frns(data: bytes, offset: int) -> tuple[list[int], list[int], int]:
    fspec: list[int] = []
    frns: list[int] = []
    base = 0

    while True:
        fspec_octet = data[offset]
        offset += 1

        fspec.extend(FSPEC_BITS[fspec_octet])
        for pos in FSPEC_SET[fspec_octet]:
            frns.append(base + pos)
        base += 7

        if fspec_octet & 1 == 0:
            break

    return fspec, frns, offset


def decode_records_message(category: CategoryMessage, data: bytes) -> list[DataRecord]:
    records: list[DataRecord] = []
    offset = 0
    data_len = len(data)
    dispatch = get_dispatch(category)

    if category == CategoryMessage.CAT021:
        decoder = decode_data_item_cat021
    elif category == CategoryMessage.CAT048:
        decoder = decode_data_item_cat048
    else:
        decoder = None

    while offset < data_len:
        fspec, frns, offset = parse_fspec_with_frns(data, offset)
        fields: list[DataField] = []

        for frn in frns:
            entry = dispatch.get(frn)

            if entry is not None:
                item_type, field_type, interesting, length = entry
                if field_type is DataFieldType.FIXED:
                    new_offset = offset + length
                    raw_content = bytes(data[offset:new_offset]) if interesting else None
                else:
                    var_decoder = VARIABLE_DECODERS.get(field_type)
                    if var_decoder is None:
                        entry = None  # unknown field type -> generic path raises as before
                    else:
                        raw_content, new_offset = var_decoder(item_type, data, offset)

            if entry is None:
                # Generic (original) path: unknown FRN / missing spec raise exactly as before.
                item_type = map_frn_to_item_type(category, frn)
                field_type = get_field_type(item_type)
                item, offset = decode_data_item(category, item_type, data, offset)
                if item is None:
                    continue
                fields.append(DataField(item=item, field_type=field_type))
                continue

            offset = new_offset
            if not interesting:
                continue

            subfield = decoder(item_type, raw_content)
            item = DataItem(item_type=item_type, content=[subfield])
            fields.append(DataField(item=item, field_type=field_type))

        records.append(DataRecord(fspec=fspec, fields=fields))

    return records


def parse_fspec(data: bytes, offset: int) -> tuple[list[int], int]:
    fspec, frns, offset = parse_fspec_with_frns(data, offset)
    return fspec, offset


def map_frn_to_item_type(category: CategoryMessage,frn: int) -> DataItemType:
    return FRN_MAPS.get(category, {}).get(frn)


def get_field_type(item_type: DataItemType) -> DataFieldType:
    return ITEM_SPECS[item_type].field_type


def decode_data_item(category: CategoryMessage, item_type: DataItemType, data: bytes, offset: int) -> tuple[DataItem | None, int]:
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

    if item_type not in INTERESTING_DATA_ITEMS:
        return None, new_offset

    if category == CategoryMessage.CAT021:
        subfield = decode_data_item_cat021(item_type, raw_content)
    elif category == CategoryMessage.CAT048:
        subfield = decode_data_item_cat048(item_type, raw_content)

    return DataItem(item_type=item_type, content=[subfield]), new_offset


def decode_fixed_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[bytes, int]:
    length = ITEM_SPECS[item_type].length
    content = data[offset:offset + length]
    return bytes(content), offset + length


def decode_extended_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[bytes, int]:
    content = bytearray()
    max_octets = ITEM_SPECS[item_type].max_octets

    while offset < len(data):
        octet = data[offset]
        content.append(octet)
        offset += 1

        if (octet & 0x01) == 0 or len(content) == max_octets:
            return bytes(content), offset


def decode_repetitive_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[bytes, int]:
    start_offset = offset
    rep_count = data[offset]
    offset += 1
    subfield_size = ITEM_SPECS[item_type].repetition_size

    end_offset = offset + rep_count * subfield_size
    return data[start_offset:end_offset], end_offset


def decode_compound_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[bytes, int]:
    start_offset = offset
    presence_bits = []

    while True:

        fspec_octet = data[offset]
        offset += 1
        presence_bits.extend((fspec_octet >> bit_position) & 1 for bit_position in range(7, 0, -1))

        if (fspec_octet & 0x01) == 0:
            break

    lengths = ITEM_SPECS[item_type].subfield_lengths

    content_length = sum(lengths[index] for index, bit in enumerate(presence_bits) if bit and index < len(lengths))
    end_offset = offset + content_length

    return data[start_offset:end_offset], end_offset


def decode_length_indicated_item(item_type: DataItemType, data: bytes, offset: int) -> tuple[bytes, int]:
    length = data[offset]

    end_offset = offset + length

    content = data[offset:end_offset]
    return content, end_offset


VARIABLE_DECODERS = {
    DataFieldType.EXTENDED: decode_extended_item,
    DataFieldType.REPETITIVE: decode_repetitive_item,
    DataFieldType.COMPOUND: decode_compound_item,
    DataFieldType.LENGTH_INDICATED: decode_length_indicated_item,
}


if __name__ == "__main__":
    run_app()