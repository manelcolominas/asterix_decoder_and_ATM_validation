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
    def __init__(self,item_type: DataItemType, content: Any):
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

    # NOT INTERESTING DataItem's

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