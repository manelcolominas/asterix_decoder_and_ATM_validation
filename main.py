from pathlib import Path
from bitstring import Bits

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

        if length < 3:
            raise ValueError(f"Invalid ASTERIX message length at offset {offset}: {length}")

        end = offset + length
        if end > len(data):
            raise ValueError(f"Message exceeds file length at offset {offset}")

        message_bytes = data[offset:end]

        if category_value in CategoryMessage._value2member_map_:
            messages.append(decode_asterix_message(message_bytes))

        offset = end

    return messages


def decode_asterix_message(data: bytes) -> AsterixMessage:
    if len(data) < 3:
        raise ValueError(f"Too short to be an ASTERIX message: {len(data)} bytes")

    category_value = data[0]
    length = int.from_bytes(data[1:3], "big")

    category = CategoryMessage(category_value)

    payload = data[3:]
    records = decode_records_message(category, payload)

    return AsterixMessage(category=category, length=length, records=records)


def decode_records_message(category: CategoryMessage, data: bytes) -> list[DataRecord]:
    records: list[DataRecord] = []
    pos = 0

    while pos < len(data):
        # read the FSPEC bytes
        fspec_vector = []
        
        while True:
            if pos >= len(data):
                raise ValueError("Unexpected end of data while reading FSPEC")
        
            byte = data[pos]
            pos += 1
        
            # Store F1..F7, from most significant to least significant bit.
            for bit in range(7, 0, -1):
                fspec_vector.append(1 if byte & (1 << bit) else 0)
        
            # FX is only used to detect another FSPEC octet.
            if (byte & 0x01) == 0:
                break

        # collect active FRNs from the FSPEC
        active_frns = [
            index + 1
            for index, is_present in enumerate(fspec_vector)
            if is_present
        ]

        fields: list[DataField] = []

        for frn in active_frns:
            item_type = map_frn_to_item_type(category, frn)
            if item_type is None:
                raise ValueError(f"Unsupported FRN {frn} for CAT{category.value}")

            raw_value = read_data_item_bytes(data, pos, item_type)
            item = DataItem(item_type=item_type, content=raw_value)
            fields.append(DataField(item=item, field_type=DataFieldType.FIXED))
            pos += len(raw_value)

        records.append(DataRecord(fspec=fspec_vector, fields=fields))

    return records


def map_frn_to_item_type(category: CategoryMessage, frn: int):
    # Example mapping for CAT021. The exact mapping depends on the UAP.
    if category == CategoryMessage.CAT021:
        mapping = {
            1: DataItemType.I021_010,
            2: DataItemType.I021_040,
            3: DataItemType.I021_070,
            4: DataItemType.I021_073,
            5: DataItemType.I021_080,
            6: DataItemType.I021_131,
            7: DataItemType.I021_145,
            8: DataItemType.I021_170,
            9: DataItemType.I021_REF,
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


def read_data_item_bytes(data: bytes, pos: int, item_type: DataItemType) -> bytes:
    if item_type in FIXED_LENGTHS:
        length = FIXED_LENGTHS[item_type]
    elif item_type in EXTENDED_ITEMS:
        if pos >= len(data):
            raise ValueError(f"Missing length indicator for {item_type}")
        length = 1 + data[pos]
    elif item_type in REPETITIVE_ITEMS:
        if pos >= len(data):
            raise ValueError(f"Missing repetition count for {item_type}")
        repeat_count = data[pos]
        subfield_size = REPETITIVE_ITEMS[item_type]
        length = 1 + repeat_count * subfield_size
    elif item_type in COMPOUND_ITEMS:
        if pos >= len(data):
            raise ValueError(f"Missing compound length for {item_type}")
        length = 1 + data[pos]
    else:
        length = 1

    # if pos + length > len(data):
    #     raise ValueError(f"Not enough bytes to read {item_type}")

    return data[pos:pos + length]


if __name__ == "__main__":
    run_app()