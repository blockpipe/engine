from dataclasses import dataclass


class ParamType:
    pass


@dataclass
class ParamTypeAddress(ParamType):
    pass


@dataclass
class ParamTypeBytes(ParamType):
    pass


@dataclass
class ParamTypeInt(ParamType):
    size: int


@dataclass
class ParamTypeUint(ParamType):
    size: int


@dataclass
class ParamTypeBool(ParamType):
    pass


@dataclass
class ParamTypeString(ParamType):
    pass


@dataclass
class ParamTypeArray(ParamType):
    ty: ParamType


@dataclass
class ParamTypeFixedBytes(ParamType):
    size: int


@dataclass
class ParamTypeFixedArray(ParamType):
    ty: ParamType
    size: int


@dataclass
class ParamTypeTuple(ParamType):
    tys: list[ParamType]


@dataclass
class EventParam:
    name: str
    ty: ParamType
    indexed: bool


@dataclass
class Event:
    name: str
    inputs: list[EventParam]
    anonymous: bool
