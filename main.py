import gc
from pathlib import Path
import time

from enum import Enum, IntEnum
from functools import partial
from typing import Any


from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor


# The decoder creates tens of millions of these objects. __slots__ makes them
# smaller and faster to create/free, and __reduce__ lets pickle (used to send
# results back from the worker processes) rebuild them with a plain
# constructor call instead of a per-object state dict.

class AsterixMessage:
    __slots__ = ("category", "length", "records")

    def __init__(self,category: CategoryMessage,length: int,records: list[DataRecord]):
        self.category = category
        self.length = length
        self.records = records

    def __reduce__(self):
        return AsterixMessage, (self.category, self.length, self.records)


class CategoryMessage(IntEnum):
    CAT021 = 21
    CAT048 = 48


class DataRecord:
    __slots__ = ("fspec", "fields")

    def __init__(self,fspec: list[int],fields: list[DataField]):
        self.fspec = fspec
        self.fields = fields

    def __reduce__(self):
        return DataRecord, (self.fspec, self.fields)


class DataItem:
    __slots__ = ("item_type", "content")

    def __init__(self,item_type: DataItemType, content: list[DataItemSubfield]):
        self.item_type = item_type
        self.content = content

    def __reduce__(self):
        return DataItem, (self.item_type, self.content)


class DataField:
    __slots__ = ("item", "field_type")

    def __init__(self,item: DataItem, field_type: DataFieldType):
        self.item = item
        self.field_type = field_type

    def __reduce__(self):
        return DataField, (self.item, self.field_type)


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
    __slots__ = ("pos", "content")

    def __init__(self, pos: int, content: list[Any]):
        self.pos = pos
        self.content = content

    def __reduce__(self):
        return DataItemSubfield, (self.pos, self.content)


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


def iter_asterix_chunks(data: bytes, chunk_size: int = 1 << 20) -> Iterator[bytes]:
    # Splits the file into contiguous chunks of roughly chunk_size bytes, always
    # cut at message boundaries. Sending a few big bytes objects to the workers is
    # much cheaper than pickling one bytes object per message.
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")

    data_len = len(data)
    chunk_start = 0
    offset = 0

    while offset < data_len:
        if offset + 3 > data_len:
            raise ValueError(f"Incomplete ASTERIX header at offset {offset}")

        length = (data[offset + 1] << 8) | data[offset + 2]

        if length < 3:
            raise ValueError(f"Invalid ASTERIX message length {length} at offset {offset}")

        offset += length
        if offset > data_len:
            raise ValueError(f"Incomplete ASTERIX message at offset {offset - length}")

        if offset - chunk_start >= chunk_size:
            yield data[chunk_start:offset]
            chunk_start = offset

    if chunk_start < data_len:
        yield data[chunk_start:]


def decode_message_chunk(chunk: bytes) -> list[AsterixMessage]:
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        messages: list[AsterixMessage] = []
        offset = 0
        chunk_len = len(chunk)
        while offset < chunk_len:
            end = offset + ((chunk[offset + 1] << 8) | chunk[offset + 2])
            if chunk[offset] in CATEGORY_VALUES:
                messages.append(decode_asterix_message(chunk, offset, end))
            offset = end
        return messages
    finally:
        if gc_was_enabled:
            gc.enable()


def decode_asterix_messages_impl(data: bytes) -> list[AsterixMessage]:
    with ProcessPoolExecutor() as executor:
        decoded_chunks = executor.map(decode_message_chunk, iter_asterix_chunks(data))
        return [message for chunk in decoded_chunks for message in chunk]


CATEGORY_VALUES = frozenset(CategoryMessage._value2member_map_)


def decode_asterix_message(data: bytes, start: int = 0, end: int | None = None) -> AsterixMessage:
    # Decodes the message that starts at data[start]. Working with offsets into
    # the original buffer avoids copying every message and its payload.
    length = (data[start + 1] << 8) | data[start + 2]
    if end is None:
        end = start + length

    category = CategoryMessage(data[start])
    records = decode_records_message(category, data, start + 3, end)

    return AsterixMessage(category, length, records)


# Lookup table: for every possible FSPEC octet, its 7 presence bits.
FSPEC_BITS = tuple(tuple((octet >> bit) & 1 for bit in range(7, 0, -1)) for octet in range(256))

# Per-category dispatch cache, see build_fspec_dispatch().
DISPATCH_CACHE: dict = {}


def get_dispatch(category: CategoryMessage) -> tuple[tuple[tuple, ...], ...]:
    table = DISPATCH_CACHE.get(category)
    if table is None:
        table = build_fspec_dispatch(category)
        DISPATCH_CACHE[category] = table
    return table


def build_fspec_dispatch(category: CategoryMessage) -> tuple[tuple[tuple, ...], ...]:
    # table[k][octet] is the tuple of field entries announced by the k-th FSPEC
    # octet when it has that value, in FRN order. Each entry is
    #   (item_type, field_type, fixed_length, end_fn, end_param, decode_fn)
    # - fixed_length is set for FIXED items; otherwise end_fn(data, offset, end_param)
    #   returns where the item ends.
    # - decode_fn is None for items we skip, so they are never sliced nor decoded.
    # An FRN without a definition maps to None and makes decoding fail.
    frn_map = FRN_MAPS.get(category, {})
    item_decoders = ITEM_DECODERS.get(category, {})

    entries: dict[int, tuple | None] = {}
    for frn, item_type in frn_map.items():
        spec = ITEM_SPECS.get(item_type)
        if spec is None:
            continue

        field_type = spec.field_type
        fixed_length = None
        end_fn = None
        end_param = None

        if field_type is DataFieldType.FIXED:
            fixed_length = spec.length
        elif field_type is DataFieldType.EXTENDED:
            end_fn, end_param = extended_item_end, spec.max_octets
        elif field_type is DataFieldType.REPETITIVE:
            end_fn, end_param = repetitive_item_end, spec.repetition_size
        elif field_type is DataFieldType.COMPOUND:
            end_fn, end_param = compound_item_end, compound_octet_tables(spec.subfield_lengths)
        elif field_type is DataFieldType.LENGTH_INDICATED:
            end_fn = length_indicated_item_end
        else:
            continue

        decode_fn = None
        if item_type in INTERESTING_DATA_ITEMS:
            decode_fn = item_decoders.get(item_type, decode_data_item_not_implemented)

        entries[frn] = (item_type, field_type, fixed_length, end_fn, end_param, decode_fn)

    max_frn = max(frn_map, default=0)
    octet_count = (max_frn + 6) // 7

    table = []
    for k in range(octet_count):
        per_octet = []
        for octet in range(256):
            row = []
            for pos, bit in enumerate(FSPEC_BITS[octet], start=1):
                if bit:
                    row.append(entries.get(k * 7 + pos))
            per_octet.append(tuple(row))
        table.append(tuple(per_octet))
    return tuple(table)


def decode_records_message(category: CategoryMessage, data: bytes, offset: int = 0, end: int | None = None) -> list[DataRecord]:
    if end is None:
        end = len(data)

    records: list[DataRecord] = []
    dispatch = get_dispatch(category)
    dispatch_len = len(dispatch)
    fspec_bits = FSPEC_BITS

    while offset < end:
        # FSPEC: collect the presence bits and the entries of the fields present.
        fspec: list[int] = []
        present: tuple = ()
        k = 0
        while True:
            fspec_octet = data[offset]
            offset += 1
            fspec += fspec_bits[fspec_octet]
            if k < dispatch_len:
                present += dispatch[k][fspec_octet]
            elif fspec_octet & 0xFE:
                raise ValueError(f"Unknown FRN in FSPEC octet {k + 1} for {category.name}")
            k += 1
            if not fspec_octet & 1:
                break

        fields: list[DataField] = []
        for entry in present:
            if entry is None:
                raise ValueError(f"Undefined FRN in FSPEC {fspec} for {category.name}")

            item_type, field_type, fixed_length, end_fn, end_param, decode_fn = entry
            if fixed_length is not None:
                item_end = offset + fixed_length
            else:
                item_end = end_fn(data, offset, end_param)

            if decode_fn is not None:
                subfield = decode_fn(data[offset:item_end])
                fields.append(DataField(DataItem(item_type, [subfield]), field_type))

            offset = item_end

        records.append(DataRecord(fspec, fields))

    return records


def parse_fspec(data: bytes, offset: int) -> tuple[list[int], int]:
    fspec: list[int] = []
    while True:
        fspec_octet = data[offset]
        offset += 1
        fspec += FSPEC_BITS[fspec_octet]
        if not fspec_octet & 1:
            return fspec, offset


def map_frn_to_item_type(category: CategoryMessage,frn: int) -> DataItemType:
    return FRN_MAPS.get(category, {}).get(frn)


def get_field_type(item_type: DataItemType) -> DataFieldType:
    return ITEM_SPECS[item_type].field_type


# Variable-length items: each function returns the offset where the item that
# starts at data[offset] ends.

def extended_item_end(data: bytes, offset: int, max_octets: int | None) -> int:
    limit = offset + max_octets if max_octets else -1
    while True:
        octet = data[offset]
        offset += 1
        if not octet & 1 or offset == limit:
            return offset


def repetitive_item_end(data: bytes, offset: int, repetition_size: int) -> int:
    return offset + 1 + data[offset] * repetition_size


def compound_octet_tables(subfield_lengths: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    # tables[k][octet] = total length of the subfields flagged by the k-th
    # primary-subfield octet. Subfields without a known length count as 0.
    tables = []
    for k in range((len(subfield_lengths) + 6) // 7):
        lengths = subfield_lengths[k * 7:k * 7 + 7]
        tables.append(tuple(
            sum(length for length, bit in zip(lengths, FSPEC_BITS[octet]) if bit)
            for octet in range(256)
        ))
    return tuple(tables)


def compound_item_end(data: bytes, offset: int, octet_tables: tuple[tuple[int, ...], ...]) -> int:
    content_length = 0
    k = 0
    while True:
        octet = data[offset]
        offset += 1
        if k < len(octet_tables):
            content_length += octet_tables[k][octet]
        k += 1
        if not octet & 1:
            return offset + content_length


def length_indicated_item_end(data: bytes, offset: int, _param: None) -> int:
    return offset + data[offset]


def decode_data_item_not_implemented(data: bytes) -> DataItemSubfield | None:
    return None


######################
######################  CAT021

def decode_data_item_cat021(item_type: DataItemType, data: bytes) -> DataItemSubfield:
    return CAT021_ITEM_DECODERS[item_type](data)

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
    return CAT048_ITEM_DECODERS[item_type](data)

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


######################  Item decoder lookup

# The CAT021 decoders also receive their item type, bound here with partial so
# every decoder can be called as decoder(data).
CAT021_ITEM_DECODERS = {
    DataItemType.I021_010: partial(decode_data_item_I021_010, DataItemType.I021_010),
    DataItemType.I021_040: partial(decode_data_item_I021_040, DataItemType.I021_040),
    DataItemType.I021_070: partial(decode_data_item_I021_070, DataItemType.I021_070),
    DataItemType.I021_073: partial(decode_data_item_I021_073, DataItemType.I021_073),
    DataItemType.I021_080: partial(decode_data_item_I021_080, DataItemType.I021_080),
    DataItemType.I021_131: partial(decode_data_item_I021_131, DataItemType.I021_131),
    DataItemType.I021_145: partial(decode_data_item_I021_145, DataItemType.I021_145),
    DataItemType.I021_170: partial(decode_data_item_I021_170, DataItemType.I021_170),
    DataItemType.I021_REF: partial(decode_data_item_I021_REF, DataItemType.I021_REF),
}

CAT048_ITEM_DECODERS = {
    DataItemType.I048_010: decode_data_item_I048_010,
    DataItemType.I048_140: decode_data_item_I048_140,
    DataItemType.I048_020: decode_data_item_I048_020,
    DataItemType.I048_040: decode_data_item_I048_040,
    DataItemType.I048_070: decode_data_item_I048_070,
    DataItemType.I048_090: decode_data_item_I048_090,
    DataItemType.I048_130: decode_data_item_I048_130,
    DataItemType.I048_220: decode_data_item_I048_220,
    DataItemType.I048_240: decode_data_item_I048_240,
    DataItemType.I048_250: decode_data_item_I048_250,
    DataItemType.I048_161: decode_data_item_I048_161,
    DataItemType.I048_200: decode_data_item_I048_200,
    DataItemType.I048_170: decode_data_item_I048_170,
    DataItemType.I048_230: decode_data_item_I048_230,
}

ITEM_DECODERS = {
    CategoryMessage.CAT021: CAT021_ITEM_DECODERS,
    CategoryMessage.CAT048: CAT048_ITEM_DECODERS,
}


if __name__ == "__main__":
    start_time =  time.perf_counter()
    run_app()
    end_time =  time.perf_counter()
    print(f"Execution time: {end_time - start_time} seconds")