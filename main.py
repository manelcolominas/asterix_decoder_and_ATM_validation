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
    bits = read_asterix_messages_bits(binary_file_path)
    asterix_messages = decode_asterix_messages(bits)
    return asterix_messages


def read_asterix_messages_bits(binary_file_path: Path):
    bits = Bits(filename=binary_file_path)
    return bits


def decode_asterix_messages(data: bytes) -> list[AsterixMessage]:
    messages = []
    offset = 0

    while offset < len(data):
        length = int.from_bytes(data[offset + 1:offset + 3], "big")

        message_bytes = data[offset:offset + length]

        messages.append(decode_asterix_message(message_bytes))

        offset += length

    return messages


def decode_asterix_message(data: bytes) -> AsterixMessage:

    category_value = data[0]
    length = int.from_bytes(data[1:3], byteorder="big")

    try:
        category = CategoryMessage(category_value)
    except ValueError as error:
        raise ValueError(f"Unsupported ASTERIX category: {category_value}") from error

    return AsterixMessage(category=category,length=length,records=[])

if __name__ == "__main__":
    run_app()