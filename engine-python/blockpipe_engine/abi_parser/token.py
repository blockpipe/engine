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
class TokenNumber(Token):
    number: int

    def to_string(self):
        return str(self.number)


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


SYMBOL_OPEN_BRACE = TokenSymbol('{')
SYMBOL_CLOSE_BRACE = TokenSymbol('}')
SYMBOL_OPEN_BRACKET = TokenSymbol('[')
SYMBOL_CLOSE_BRACKET = TokenSymbol(']')
SYMBOL_OPEN_PAREN = TokenSymbol('(')
SYMBOL_CLOSE_PAREN = TokenSymbol(')')
SYMBOL_COMMA = TokenSymbol(',')
SYMBOL_DOT = TokenSymbol('.')
SYMBOL_SEMICOLON = TokenSymbol(';')

SYMBOL_MAPPING = {symbol.to_string(): symbol for symbol in (
    SYMBOL_OPEN_BRACE,
    SYMBOL_CLOSE_BRACE,
    SYMBOL_OPEN_BRACKET,
    SYMBOL_CLOSE_BRACKET,
    SYMBOL_OPEN_PAREN,
    SYMBOL_CLOSE_PAREN,
    SYMBOL_SEMICOLON,
    SYMBOL_COMMA,
    SYMBOL_DOT,
)}


TOKEN_TY_ADDRESS = TokenTy('address')
TOKEN_TY_BOOL = TokenTy('bool')
TOKEN_TY_BYTES = TokenTy('bytes')
TOKEN_TY_BYTE = TokenTy('byte')
TOKEN_TY_STRING = TokenTy('string')
TOKEN_KEYWORD_ABSTRACT = TokenKeyword('abstract')
TOKEN_KEYWORD_ANONYMOUS = TokenKeyword('anonymous')
TOKEN_KEYWORD_CALLDATA = TokenKeyword('calldata')
TOKEN_KEYWORD_CONSTANT = TokenKeyword('constant')
TOKEN_KEYWORD_ENUM = TokenKeyword('enum')
TOKEN_KEYWORD_ERROR = TokenKeyword('error')
TOKEN_KEYWORD_EVENT = TokenKeyword('event')
TOKEN_KEYWORD_EXTERNAL = TokenKeyword('external')
TOKEN_KEYWORD_FALLBACK = TokenKeyword('fallback')
TOKEN_KEYWORD_FUNCTION = TokenKeyword('function')
TOKEN_KEYWORD_INDEXED = TokenKeyword('indexed')
TOKEN_KEYWORD_TUPLE = TokenKeyword('tuple')
TOKEN_KEYWORD_INTERNAL = TokenKeyword('internal')
TOKEN_KEYWORD_MEMORY = TokenKeyword('memory')
TOKEN_KEYWORD_OVERRIDE = TokenKeyword('override')
TOKEN_KEYWORD_PAYABLE = TokenKeyword('payable')
TOKEN_KEYWORD_PRIVATE = TokenKeyword('private')
TOKEN_KEYWORD_PUBLIC = TokenKeyword('public')
TOKEN_KEYWORD_PURE = TokenKeyword('pure')
TOKEN_KEYWORD_RECEIVE = TokenKeyword('receive')
TOKEN_KEYWORD_RETURNS = TokenKeyword('returns')
TOKEN_KEYWORD_STORAGE = TokenKeyword('storage')
TOKEN_KEYWORD_STRUCT = TokenKeyword('struct')
TOKEN_KEYWORD_TYPE = TokenKeyword('type')
TOKEN_KEYWORD_VIEW = TokenKeyword('view')
TOKEN_KEYWORD_VIRTUAL = TokenKeyword('virtual')

TOKEN_MAPPING = {**{token.to_string(): token for token in [
    TOKEN_TY_ADDRESS,
    TOKEN_TY_BOOL,
    TOKEN_TY_BYTES,
    TOKEN_TY_BYTE,
    TOKEN_TY_STRING,
    TOKEN_KEYWORD_ABSTRACT,
    TOKEN_KEYWORD_ANONYMOUS,
    TOKEN_KEYWORD_CALLDATA,
    TOKEN_KEYWORD_CONSTANT,
    TOKEN_KEYWORD_ENUM,
    TOKEN_KEYWORD_ERROR,
    TOKEN_KEYWORD_EVENT,
    TOKEN_KEYWORD_EXTERNAL,
    TOKEN_KEYWORD_FALLBACK,
    TOKEN_KEYWORD_FUNCTION,
    TOKEN_KEYWORD_INDEXED,
    TOKEN_KEYWORD_TUPLE,
    TOKEN_KEYWORD_INTERNAL,
    TOKEN_KEYWORD_MEMORY,
    TOKEN_KEYWORD_OVERRIDE,
    TOKEN_KEYWORD_PAYABLE,
    TOKEN_KEYWORD_PRIVATE,
    TOKEN_KEYWORD_PUBLIC,
    TOKEN_KEYWORD_PURE,
    TOKEN_KEYWORD_RECEIVE,
    TOKEN_KEYWORD_RETURNS,
    TOKEN_KEYWORD_STORAGE,
    TOKEN_KEYWORD_STRUCT,
    TOKEN_KEYWORD_TYPE,
    TOKEN_KEYWORD_VIEW,
    TOKEN_KEYWORD_VIRTUAL
]}, **{
    'int': TokenTyWithSize('int', 256),
    'uint': TokenTyWithSize('uint', 256),
    'byte': TokenTyWithSize('bytes', 1),
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
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
        return TokenIdentifier(value)
    if re.match(r'^[0-9]+$', value):
        return TokenNumber(int(value))
    raise ValueError(f'Invalid token value: "{value}"')
