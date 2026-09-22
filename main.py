from pathlib import Path
from bitstring import Bits


def run_app():
    binary_file_path = Path(
        r"C:\Users\manel\Documents\Educació\Universitat\6è any\1r Quadrimestre"
        r"\Projectes per a la Gestió del Trànsit Aeri\Projectes\Projecte 2 i 3"
        r"\asterix_radar.ast"
    )

    run_pipeline(binary_file_path)


def run_pipeline(binary_file_path: Path):
    bits = read_asterix_messages_bits(binary_file_path)
    identify_type_of_asterix_messages(bits)


def read_asterix_messages_bits(binary_file_path: Path):
    bits = Bits(filename=binary_file_path).b
    return bits


def identify_type_of_asterix_messages(bits: str):
    pass

if __name__ == "__main__":
    run_app()