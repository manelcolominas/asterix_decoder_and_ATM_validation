from pathlib import Path
from bitstring import Bits

from models import AsterixMessage, CategoryMessage, DataRecord, DataField, DataItem, DataItemType, DataFieldType

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

    try:
        category = CategoryMessage(category_value)
    except ValueError as exc:
        raise ValueError(f"Unsupported ASTERIX category: {category_value}") from exc

    payload = data[3:]
    records = decode_records_message(payload, category)

    return AsterixMessage(category=category, length=length, records=records)


def decode_records_message(data: bytes, category: CategoryMessage) -> list[DataRecord]:
    records: list[DataRecord] = []
    pos = 0

    while pos < len(data):
        # read the FSPEC bytes
        fspec_bytes = []
        while True:
            if pos >= len(data):
                raise ValueError("Unexpected end of data while reading FSPEC")

            b = data[pos]
            fspec_bytes.append(b)
            pos += 1

            # FX bit is the LSB; if 0 => end of FSPEC
            if (b & 0x01) == 0:
                break

        # collect active FRNs from the FSPEC
        active_frns: list[int] = []
        for octet_index, fspec_byte in enumerate(fspec_bytes):
            # bits 7..1 are F1..F7 in that octet, bit 0 is FX
            for bit in range(7, 0, -1):
                if fspec_byte & (1 << bit):
                    frn = octet_index * 7 + (8 - bit)
                    active_frns.append(frn)

        fields: list[DataField] = []

        for frn in active_frns:
            item_type = map_frn_to_item_type(category, frn)
            if item_type is None:
                raise ValueError(f"Unsupported FRN {frn} for CAT{category.value}")

            raw_value = read_data_item_bytes(data, pos, item_type)
            item = DataItem(item_type=item_type, content=raw_value)
            fields.append(DataField(item=item, field_type=DataFieldType.FIXED))
            pos += len(raw_value)

        records.append(DataRecord(fspec=fspec_bytes, fields=fields))

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
        }
        return mapping.get(frn)

    if category == CategoryMessage.CAT048:
        mapping = {
            1: DataItemType.I048_010,
            2: DataItemType.I048_030,
            3: DataItemType.I048_042,
        }
        return mapping.get(frn)

    return None


def read_data_item_bytes(data: bytes, pos: int, item_type: DataItemType) -> bytes:
    # For now, use the spec lengths for the common items.
    lengths = {
        DataItemType.I021_010: 2,
        DataItemType.I021_040: 1,   # + possible extensions, handle separately if needed
        DataItemType.I021_070: 2,
        DataItemType.I021_073: 3,
        DataItemType.I021_080: 3,
        DataItemType.I048_010: 2,
        DataItemType.I048_030: 1,
        DataItemType.I048_042: 1,
    }

    length = lengths.get(item_type, 1)
    if pos + length > len(data):
        raise ValueError(f"Not enough bytes to read {item_type}")

    return data[pos:pos + length]


if __name__ == "__main__":
    run_app()