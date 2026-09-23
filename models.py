class AsterixMessage:
    category: CATKind
    length: int
    data_record: DataRecord

class CATKind:
    CAT021=21
    CAT048=48

class DataRecord:
    fspec: list[int]
    data_fields: list[DataField]


class DataField:
    item: DataItem
    field_type: DataFieldType

class DataFieldType:
    FIXED = 1
    EXTENDED = 2
    REPETITIVE = 3
    COMPOUND = 4

class DataItem:
    number: int
    data_item: DataItemType
    content: object

class DataItemType:
    I021_010    # Data Source Identification
    I021_040    # Target Report Descriptor
    I021_131    # Position in WGS-84 co-ordinates, high res.
    I021_080    # Target Address
    I021_073    # Time of Message Reception of Position
    I021_070    # Mode 3/A Code
    I021_145    # Flight Level
    I021_170    # Target Identification
    I021_REF    # Reserved Expansion Field

    I048_170
    I048_230
    I048_030
    I048_YYY
    I048_260
    I048_220
    I048_240
    I048_010
    I048_042
    I048_060
    I048_065
    I048_080
    I048_100
    I048_110
    I048_161
    I048_200
    I048_210