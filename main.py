from pathlib import Path
from bitstring import Bits

from models import AsterixMessage

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
    bits = Bits(filename=binary_file_path).b
    return bits


def decode_asterix_messages(bits: str) -> list[AsterixMessage]:
    pass

if __name__ == "__main__":
    run_app()