import re
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Token(ABC):
    @abstractmethod
    def to_string(self):
        raise NotImplementedError()


@dataclass
class TokenSymbol(Token):
    symbol: str

    def to_string(self):
        return self.symbol


@dataclass
class TokenKeyword(Token):
    keyword: str

    def to_string(self):
        return self.keyword


@dataclass
class TokenIdentifier(Token):
    identifier: str

    def to_string(self):
        return self.identifier


@dataclass
class TokenTy(Token):
    ty: str

    def to_string(self):
        return self.ty


@dataclass
class TokenTyWithSize(TokenTy):
    size: int

    def to_string(self):
        return f'{super().to_string()}{self.size}'


SYMBOL_MAPPING = {
    '{': TokenSymbol('{'),
    '}': TokenSymbol('}'),
    '[': TokenSymbol('['),
    ']': TokenSymbol(']'),
    '(': TokenSymbol('('),
    ')': TokenSymbol(')'),
    ';': TokenSymbol(';'),
    ',': TokenSymbol(','),
    '.': TokenSymbol('.'),
}


TOKEN_MAPPING = {**{
    'abstract': TokenKeyword('abstract'),
    'address': TokenTy('address'),
    'anonymous': TokenKeyword('anonymous'),
    'bool': TokenTy('bool'),
    'bytes': TokenTy('bytes'),
    'byte': TokenTy('byte'),
    'calldata': TokenKeyword('calldata'),
    'constant': TokenKeyword('constant'),
    'enum': TokenKeyword('enum'),
    'error': TokenKeyword('error'),
    'external': TokenKeyword('external'),
    'fallback': TokenKeyword('fallback'),
    'function': TokenKeyword('function'),
    'indexed': TokenKeyword('indexed'),
    'tuple': TokenKeyword('tuple'),
    'internal': TokenKeyword('internal'),
    'int': TokenTyWithSize('int', 256),
    'memory': TokenKeyword('memory'),
    'override': TokenKeyword('override'),
    'payable': TokenKeyword('payable'),
    'private': TokenKeyword('private'),
    'public': TokenKeyword('public'),
    'pure': TokenKeyword('pure'),
    'receive': TokenKeyword('receive'),
    'returns': TokenKeyword('returns'),
    'storage': TokenKeyword('storage'),
    'string': TokenTy('string'),
    'struct': TokenKeyword('struct'),
    'type': TokenKeyword('type'),
    'uint': TokenTyWithSize('uint', 256),
    'view': TokenKeyword('view'),
    'virtual': TokenKeyword('virtual'),
}, **{
    # uint8, uint16, uint24, ..., uint256
    f'uint{sz}': TokenTyWithSize('uint', sz) for sz in range(8, 257, 8)
}, **{
    # int8, int16, int24, ..., int256
    f'int{sz}': TokenTyWithSize('int', sz) for sz in range(8, 257, 8)
}, **{
    # bytes1, bytes2, bytes3, ..., bytes32
    f'bytes{sz}': TokenTyWithSize('bytes', sz) for sz in range(1, 33)
}}


def parse_symbol(value):
    if len(value) != 1:
        raise ValueError(
            f'Invalid symbol candidate: {value}; length must be 1')
    return SYMBOL_MAPPING.get(value)


def parse_token(value):
    if (res := SYMBOL_MAPPING.get(value)) is not None:
        return res
    if (res := TOKEN_MAPPING.get(value)) is not None:
        return res
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
        raise ValueError(f'Invalid identifier candidate: {value}')
    return TokenIdentifier(value)
