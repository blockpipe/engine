from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class ParamType(ABC):
    pass


class ParamTypeStaticSize(ParamType, ABC):
    @abstractmethod
    def parse_bytes32(self, data: bytes) -> Any:
        raise NotImplementedError()


@dataclass
class ParamTypeAddress(ParamTypeStaticSize):
    def parse_bytes32(self, data: bytes) -> Any:
        return data[-20:]


@dataclass
class ParamTypeInt(ParamTypeStaticSize):
    size: int

    def parse_bytes32(self, data: bytes) -> Any:
        return int.from_bytes(data, 'big', signed=True)


@dataclass
class ParamTypeUint(ParamTypeStaticSize):
    size: int

    def parse_bytes32(self, data: bytes) -> Any:
        return int.from_bytes(data, 'big', signed=False)


@dataclass
class ParamTypeBool(ParamTypeStaticSize):
    def parse_bytes32(self, data: bytes) -> Any:
        return any(v != '\00' for v in data)


@dataclass
class ParamTypeFixedBytes(ParamTypeStaticSize):
    size: int

    def parse_bytes32(self, data: bytes) -> Any:
        return data[:self.size]


@dataclass
class ParamTypeString(ParamType):
    def has_dynamic_size(self) -> bool:
        return True


@dataclass
class ParamTypeBytes(ParamType):
    def has_dynamic_size(self) -> bool:
        return True


@dataclass
class ParamTypeArray(ParamType):
    ty: ParamType

    def has_dynamic_size(self) -> bool:
        return True


@dataclass
class ParamTypeFixedArray(ParamType):
    ty: ParamType
    size: int

    def has_dynamic_size(self) -> bool:
        return True


@dataclass
class ParamTypeTuple(ParamType):
    tys: list[ParamType]

    def has_dynamic_size(self) -> bool:
        return True


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
