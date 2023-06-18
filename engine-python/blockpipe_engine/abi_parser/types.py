from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from eth_abi.abi import decode as decode_abi
from eth_utils.abi import event_abi_to_log_topic, collapse_if_tuple


class ParamType(ABC):
    @abstractmethod
    def to_json(self):
        raise NotImplementedError()

    def parse_bytes32(self, data: bytes) -> Any:
        return data


class ParamTypeStaticSize(ParamType, ABC):
    @abstractmethod
    def parse_bytes32(self, data: bytes) -> Any:
        raise NotImplementedError()


@dataclass
class ParamTypeAddress(ParamTypeStaticSize):
    def parse_bytes32(self, data: bytes) -> Any:
        return data[-20:]

    def to_json(self):
        return {'type': 'address'}


@dataclass
class ParamTypeInt(ParamTypeStaticSize):
    size: int

    def parse_bytes32(self, data: bytes) -> Any:
        return int.from_bytes(data, 'big', signed=True)

    def to_json(self):
        return {'type': f'int{self.size}'}


@dataclass
class ParamTypeUint(ParamTypeStaticSize):
    size: int

    def parse_bytes32(self, data: bytes) -> Any:
        return int.from_bytes(data, 'big', signed=False)

    def to_json(self):
        return {'type': f'uint{self.size}'}


@dataclass
class ParamTypeBool(ParamTypeStaticSize):
    def parse_bytes32(self, data: bytes) -> Any:
        return any(v != '\00' for v in data)

    def to_json(self):
        return {'type': 'bool'}


@dataclass
class ParamTypeFixedBytes(ParamTypeStaticSize):
    size: int

    def parse_bytes32(self, data: bytes) -> Any:
        return data[:self.size]

    def to_json(self):
        return {'type': f'bytes{self.size}'}


@dataclass
class ParamTypeString(ParamType):
    def to_json(self):
        return {'type': 'string'}


@dataclass
class ParamTypeBytes(ParamType):
    def to_json(self):
        return {'type': 'bytes'}


@dataclass
class ParamTypeArray(ParamType):
    ty: ParamType

    def to_json(self):
        inner_json = self.ty.to_json()
        inner_json['type'] = f'{inner_json["type"]}[]'
        return inner_json


@dataclass
class ParamTypeFixedArray(ParamType):
    ty: ParamType
    size: int

    def to_json(self):
        inner_json = self.ty.to_json()
        inner_json['type'] = f'{inner_json["type"]}[{self.size}]'
        return inner_json


@dataclass
class ParamTypeTuple(ParamType):
    tys: list[ParamType]

    def to_json(self):
        return {'type': 'tuple', 'components': [ty.to_json() for ty in self.tys]}


@dataclass
class EventParam:
    name: str
    ty: ParamType
    indexed: bool

    def to_json(self):
        return {**{
            'name': self.name,
            'indexed': self.indexed,
        }, **self.ty.to_json()}


@dataclass
class Event:
    name: str
    inputs: list[EventParam]
    anonymous: bool

    def to_json(self):
        return {
            'name': self.name,
            'inputs': [input.to_json() for input in self.inputs],
            'anonymous': self.anonymous,
        }

    @cached_property
    def topic0(self):
        return event_abi_to_log_topic(self.to_json())

    @cached_property
    def can_fast_parse(self):
        return all(isinstance(input.ty, ParamTypeStaticSize) for input in self.inputs)

    @cached_property
    def argument_types(self):
        inputs = self.to_json()['inputs']
        return [collapse_if_tuple(input) for input in inputs]

    def parse_arguments(self, topics, data):
        if self.can_fast_parse:
            return self.fast_parse_arguments(topics, data)
        else:
            return self.slow_parse_arguments(topics, data)

    def fast_parse_arguments(self, topics, data):
        result = []
        indexed_count, unindexed_count = 0, 0
        for input in self.inputs:
            if input.indexed:
                span = topics[indexed_count + 1]
                indexed_count += 1
            else:
                span = data[unindexed_count * 32:(unindexed_count + 1) * 32]
                unindexed_count += 1
            result.append(input.ty.parse_bytes32(span))
        return result

    def slow_parse_arguments(self, topics, data):
        result = [None]*len(self.inputs)
        argument_types = self.argument_types
        indexed_count = 0
        unindexed_info = []
        for idx, input in enumerate(self.inputs):
            if input.indexed:
                indexed_count += 1
                span = topics[indexed_count]
                result[idx] = input.ty.parse_bytes32(span)
            else:
                unindexed_info.append((idx, argument_types[idx]))
        unindexed_values = decode_abi([t for _, t in unindexed_info], data)
        for idx, val in enumerate(unindexed_values):
            result[unindexed_info[idx][0]] = val
        return result
