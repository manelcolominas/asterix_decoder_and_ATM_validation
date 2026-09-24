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
    def __init__(self,item_type: DataItemType,content: Any):
        self.item_type = item_type
        self.content = content


class DataField:
    def __init__(self,item: DataItem,field_type: DataFieldType):
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

    I048_010 = "I048/010"
    I048_030 = "I048/030"
    I048_042 = "I048/042"
    I048_060 = "I048/060"
    I048_065 = "I048/065"
    I048_080 = "I048/080"
    I048_100 = "I048/100"
    I048_110 = "I048/110"
    I048_161 = "I048/161"
    I048_170 = "I048/170"
    I048_200 = "I048/200"
    I048_210 = "I048/210"
    I048_220 = "I048/220"
    I048_230 = "I048/230"
    I048_240 = "I048/240"
    I048_260 = "I048/260"