import gc
from pathlib import Path
import time

from enum import Enum, IntEnum
from typing import Any


class AsterixMessage:
    def __init__(self,category: CategoryMessage,length: int,records: list[DataRecord]):
        self.category = category
        self.length = length
        self.records = records


class CategoryMessage(IntEnum):
    CAT021 = 21
    CAT048 = 48


class DataRecord:
    def __init__(self,fspec: list[int],fields: list[DataField]):
        self.fspec = fspec
        self.fields = fields


class DataItem:
    def __init__(self,item_type: DataItemType, content: list[DataItemSubfield]):
        self.item_type = item_type
        self.content = content


class DataField:
    def __init__(self,item: DataItem, field_type: DataFieldType):
        self.item = item
        self.field_type = field_type


class DataFieldType(Enum):
    FIXED = "fixed"
    EXTENDED = "extended"
    REPETITIVE = "repetitive"
    COMPOUND = "compound"
    LENGTH_INDICATED= "length_indicated"


class DataItemType(str, Enum):
    I021_010 = "I021/010"
    I021_040 = "I021/040"
    I021_070 = "I021/070"
    I021_073 = "I021/073"
    I021_080 = "I021/080"
    I021_131 = "I021/131"
    I021_145 = "I021/145"
    I021_170 = "I021/170"
    I021_REF = "I021/REF"

    # NOT INTERESTING DataItem's for CAT021

    I021_161 = "I021/161"
    I021_015 = "I021/015"
    I021_071 = "I021/071"
    I021_130 = "I021/130"
    I021_072 = "I021/072"
    I021_150 = "I021/150"
    I021_151 = "I021/151"
    I021_074 = "I021/074"
    I021_075 = "I021/075"
    I021_076 = "I021/076"
    I021_140 = "I021/140"
    I021_090 = "I021/090"
    I021_210 = "I021/210"
    I021_230 = "I021/230"
    I021_152 = "I021/152"
    I021_200 = "I021/200"
    I021_155 = "I021/155"
    I021_157 = "I021/157"
    I021_160 = "I021/160"
    I021_165 = "I021/165"
    I021_077 = "I021/077"
    I021_020 = "I021/020"
    I021_220 = "I021/220"
    I021_146 = "I021/146"
    I021_148 = "I021/148"
    I021_110 = "I021/110"
    I021_016 = "I021/016"
    I021_008 = "I021/008"
    I021_271 = "I021/271"
    I021_132 = "I021/132"
    I021_250 = "I021/250"
    I021_260 = "I021/260"
    I021_400 = "I021/400"
    I021_295 = "I021/295"
    I021_SPF = "I021/SPF"


    # CAT048 DataItem's
    I048_010 = "I048/010"
    I048_140 = "I048/140"
    I048_020 = "I048/020"
    I048_040 = "I048/040"
    I048_070 = "I048/070"
    I048_090 = "I048/090"
    I048_130 = "I048/130"
    I048_220 = "I048/220"
    I048_240 = "I048/240"
    I048_250 = "I048/250"
    I048_161 = "I048/161"
    I048_200 = "I048/200"
    I048_170 = "I048/170"
    I048_230 = "I048/230"

    # NOT INTERESTING DataItem's for CAT048

    I048_042 = "I048/042"
    I048_210 = "I048/210"
    I048_030 = "I048/030"
    I048_080 = "I048/080"
    I048_100 = "I048/100"
    I048_110 = "I048/110"
    I048_120 = "I048/120"
    I048_260 = "I048/260"
    I048_055 = "I048/055"
    I048_050 = "I048/050"
    I048_065 = "I048/065"
    I048_060 = "I048/060"
    SP_DATA_ITEM = "SP_DATA_ITEM"
    RE_DATA_ITEM = "RE_DATA_ITEM"


class DataItemSubfield:
    def __init__(self, pos: int, content: list[Any]):
        self.pos = pos
        self.content = content


class DataItemTypeSpec:
    def __init__(self, field_type: DataFieldType, length: int | None = None, repetition_size: int | None = None, subfield_lengths: tuple[int, ...] = (), max_octets: int | None = None):
        self.field_type = field_type
        self.length = length
        self.repetition_size = repetition_size
        self.subfield_lengths = subfield_lengths
        self.max_octets = max_octets


ITEM_SPECS = {
    # CAT021 interessants
    DataItemType.I021_010: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_040: DataItemTypeSpec(field_type=DataFieldType.EXTENDED),
    DataItemType.I021_070: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_073: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=3),
    DataItemType.I021_080: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=3),
    DataItemType.I021_131: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=8),
    DataItemType.I021_145: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_170: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=6),
    # DataItemType.I021_REF: DataItemTypeSpec(field_type=DataFieldType.COMPOUND, subfield_lengths=(1, 1, 1, 1, 1, 1)),
    DataItemType.I021_REF: DataItemTypeSpec(field_type=DataFieldType.LENGTH_INDICATED),

    # CAT021 no interessants
    DataItemType.I021_161: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_015: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    DataItemType.I021_071: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=3),
    DataItemType.I021_130: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=6),
    DataItemType.I021_072: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=3),
    DataItemType.I021_150: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),


    DataItemType.I021_151: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_074: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=4),
    DataItemType.I021_075: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=3),
    DataItemType.I021_076: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=4),
    DataItemType.I021_140: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),

    DataItemType.I021_090: DataItemTypeSpec(field_type=DataFieldType.EXTENDED),
    DataItemType.I021_210: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    DataItemType.I021_230: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_152: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),

    DataItemType.I021_200: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    DataItemType.I021_155: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_157: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_160: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=4),

    DataItemType.I021_165: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_077: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=3),
    DataItemType.I021_020: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    # DataItemType.I021_220: DataItemTypeSpec(field_type=DataFieldType.EXTENDED),
    DataItemType.I021_220: DataItemTypeSpec(field_type=DataFieldType.COMPOUND, subfield_lengths=(2, 2, 2, 1)),

    DataItemType.I021_146: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_148: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I021_110: DataItemTypeSpec(field_type=DataFieldType.COMPOUND),
    DataItemType.I021_016: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),

    DataItemType.I021_008: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    DataItemType.I021_271: DataItemTypeSpec(field_type=DataFieldType.EXTENDED, max_octets=2),
    DataItemType.I021_132: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    DataItemType.I021_250: DataItemTypeSpec(field_type=DataFieldType.REPETITIVE, repetition_size=8),

    DataItemType.I021_260: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=7),
    DataItemType.I021_400: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    # DataItemType.I021_295: DataItemTypeSpec(field_type=DataFieldType.EXTENDED),
    DataItemType.I021_295: DataItemTypeSpec(field_type=DataFieldType.COMPOUND, subfield_lengths=(1,)*23),
    # DataItemType.I021_SPF: DataItemTypeSpec(field_type=DataFieldType.COMPOUND, subfield_lengths=(1, 1, 1, 1, 1, 1)),
    DataItemType.I021_SPF: DataItemTypeSpec(field_type=DataFieldType.LENGTH_INDICATED),

    # CAT048 interessants
    DataItemType.I048_010: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I048_140: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=3),
    DataItemType.I048_020: DataItemTypeSpec(field_type=DataFieldType.EXTENDED),
    DataItemType.I048_040: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=4),
    DataItemType.I048_070: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I048_090: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),

    DataItemType.I048_130: DataItemTypeSpec(field_type=DataFieldType.COMPOUND,subfield_lengths=(1, 1, 1, 1, 1, 1, 1)),
    DataItemType.I048_220: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=3),
    DataItemType.I048_240: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=6),
    DataItemType.I048_250: DataItemTypeSpec(field_type=DataFieldType.REPETITIVE,repetition_size=8),
    DataItemType.I048_161: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),

    DataItemType.I048_170: DataItemTypeSpec(field_type=DataFieldType.EXTENDED),
    DataItemType.I048_200: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=4),
    DataItemType.I048_230: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),

    # CAT048 no interessants
    DataItemType.I048_042: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=4),
    
    DataItemType.I048_210: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=4),
    DataItemType.I048_030: DataItemTypeSpec(field_type=DataFieldType.EXTENDED),
    DataItemType.I048_080: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),

    DataItemType.I048_100: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=4),
    DataItemType.I048_110: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I048_120: DataItemTypeSpec(field_type=DataFieldType.EXTENDED),
    DataItemType.I048_260: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=7),

    DataItemType.I048_055: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    DataItemType.I048_050: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),
    DataItemType.I048_065: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=1),
    DataItemType.I048_060: DataItemTypeSpec(field_type=DataFieldType.FIXED, length=2),

    # DataItemType.SP_DATA_ITEM: DataItemTypeSpec(field_type=DataFieldType.COMPOUND, subfield_lengths=(1, 1, 1, 1, 1, 1)),
    # DataItemType.RE_DATA_ITEM: DataItemTypeSpec(field_type=DataFieldType.COMPOUND, subfield_lengths=(1, 1, 1, 1, 1, 1)),

    DataItemType.SP_DATA_ITEM: DataItemTypeSpec(field_type=DataFieldType.LENGTH_INDICATED),
    DataItemType.RE_DATA_ITEM: DataItemTypeSpec(field_type=DataFieldType.LENGTH_INDICATED),
}

FRN_MAPS = {
    CategoryMessage.CAT021: {
        1: DataItemType.I021_010,
        2: DataItemType.I021_040,
        3: DataItemType.I021_161,
        4: DataItemType.I021_015,
        5: DataItemType.I021_071,
        6: DataItemType.I021_130,
        7: DataItemType.I021_131,

        8: DataItemType.I021_072,
        9: DataItemType.I021_150,
        10: DataItemType.I021_151,
        11: DataItemType.I021_080,
        12: DataItemType.I021_073,
        13: DataItemType.I021_074,
        14: DataItemType.I021_075,

        15: DataItemType.I021_076,
        16: DataItemType.I021_140,
        17: DataItemType.I021_090,
        18: DataItemType.I021_210,
        19: DataItemType.I021_070,
        20: DataItemType.I021_230,
        21: DataItemType.I021_145,

        22: DataItemType.I021_152,
        23: DataItemType.I021_200,
        24: DataItemType.I021_155,
        25: DataItemType.I021_157,
        26: DataItemType.I021_160,
        27: DataItemType.I021_165,
        28: DataItemType.I021_077,

        29: DataItemType.I021_170,
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
        48: DataItemType.I021_REF,
        49: DataItemType.I021_SPF,
    },

    CategoryMessage.CAT048: {
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
        12: DataItemType.I048_042,
        13: DataItemType.I048_200,
        14: DataItemType.I048_170,

        15: DataItemType.I048_210,
        16: DataItemType.I048_030,
        17: DataItemType.I048_080,
        18: DataItemType.I048_100,
        19: DataItemType.I048_110,
        20: DataItemType.I048_120,
        21: DataItemType.I048_230,

        22: DataItemType.I048_260,
        23: DataItemType.I048_055,
        24: DataItemType.I048_050,
        25: DataItemType.I048_065,
        26: DataItemType.I048_060,
        27: DataItemType.SP_DATA_ITEM,
        28: DataItemType.RE_DATA_ITEM,
    }
}

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
    # binary_file_path = Path( r"inputs\asterix_adsb.ast") # cat021
    binary_file_path = Path( r"inputs\asterix_combinado.ast") # cat048 + cat021

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
        return decode_asterix_messages_impl(data)
    finally:
        if gc_was_enabled:
            gc.enable()


def decode_asterix_messages_impl(data: bytes) -> list[AsterixMessage]:
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
            # print(f"New message of category: {category_value}")
            # print(f"Message length: {length}, offset: {offset}, end: {end}")
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
            # print(f"Item type: {item_type}")
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


######################
######################  CAT021

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

######################  CAT048
######################  CAT048
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
    if len(data) != 4:
        raise ValueError(f"I048/040 requires 4 octets, got {len(data)}")

    rho_raw = int.from_bytes(data[0:2], byteorder="big")
    theta_raw = int.from_bytes(data[2:4], byteorder="big")

    rho_nm = rho_raw / 256
    theta_deg = theta_raw * 360 / 65536

    return DataItemSubfield(pos=1, content=[rho_nm, theta_deg])
    
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


if __name__ == "__main__":
    start_time =  time.perf_counter()
    run_app()
    end_time =  time.perf_counter()
    print(f"Execution time: {end_time - start_time} seconds")