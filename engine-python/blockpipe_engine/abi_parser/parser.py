from .lexer import HumanReadableLexer
from .token import (
    Token,
    TokenIdentifier,
    TokenNumber,
    TokenTyWithSize,
    SYMBOL_OPEN_PAREN,
    SYMBOL_CLOSE_PAREN,
    SYMBOL_OPEN_BRACKET,
    SYMBOL_CLOSE_BRACKET,
    SYMBOL_COMMA,
    TOKEN_TY_ADDRESS,
    TOKEN_TY_BOOL,
    TOKEN_TY_BYTE,
    TOKEN_TY_BYTES,
    TOKEN_TY_STRING,
    TOKEN_KEYWORD_ANONYMOUS,
    TOKEN_KEYWORD_EVENT,
    TOKEN_KEYWORD_INDEXED,
)
from .types import (
    Event,
    EventParam,
    ParamType,
    ParamTypeAddress,
    ParamTypeArray,
    ParamTypeBool,
    ParamTypeBytes,
    ParamTypeFixedBytes,
    ParamTypeFixedArray,
    ParamTypeInt,
    ParamTypeString,
    ParamTypeTuple,
    ParamTypeUint,
)


class HumanReadableParser:
    def __init__(self, input):
        self.lexer = HumanReadableLexer(input)

    def take_event(self) -> Event:
        name = self.take_identifier(TOKEN_KEYWORD_EVENT)
        self.take_exact(SYMBOL_OPEN_PAREN)
        inputs = self.take_event_params()
        self.take_exact(SYMBOL_CLOSE_PAREN)
        anonymous = False
        if self.lexer.peek_token() == TOKEN_KEYWORD_ANONYMOUS:
            anonymous = True
            self.lexer.next_token()
        return Event(name.identifier, inputs, anonymous)

    def take_event_params(self) -> list[EventParam]:
        if self.lexer.peek_token() == SYMBOL_CLOSE_PAREN:
            return []
        events = []
        while True:
            events.append(self.take_event_param())
            token = self.lexer.peek_token()
            if token == SYMBOL_CLOSE_PAREN:
                break
            elif token == SYMBOL_COMMA:
                self.lexer.next_token()
            else:
                raise ValueError(
                    f'Expected "," or ")"; but got "{token}"')
        return events

    def take_event_param(self) -> EventParam:
        ty = self.take_param()
        name = ''
        indexed = False
        while True:
            token = self.lexer.peek_token()
            if token == TOKEN_KEYWORD_INDEXED:
                indexed = True
                self.lexer.next_token()
            elif isinstance(token, TokenIdentifier):
                name = token.identifier
                self.lexer.next_token()
            else:
                break
        return EventParam(name, ty, indexed)

    def take_params(self) -> list[ParamType]:
        params = []
        if self.lexer.peek_token() == SYMBOL_CLOSE_PAREN:
            return params
        while True:
            params.append(self.take_param())
            token = self.lexer.peek_token()
            if token == SYMBOL_CLOSE_PAREN:
                break
            elif token == SYMBOL_COMMA:
                self.lexer.next_token()
                continue
            else:
                raise ValueError(f'Expected "," or ")"; got "{token}"')
        return params

    def take_param(self) -> ParamType:
        token = self.lexer.next_token()
        if token == SYMBOL_OPEN_PAREN:
            ty = ParamTypeTuple(self.take_params())
            self.take_exact(SYMBOL_CLOSE_PAREN)
        elif token == TOKEN_TY_ADDRESS:
            ty = ParamTypeAddress()
        elif token == TOKEN_TY_BOOL:
            ty = ParamTypeBool()
        elif token == TOKEN_TY_BYTE:
            ty = ParamTypeBytes()
        elif token == TOKEN_TY_BYTES:
            ty = ParamTypeBytes()
        elif token == TOKEN_TY_STRING:
            ty = ParamTypeString()
        elif isinstance(token, TokenTyWithSize):
            if token.ty == 'int':
                ty = ParamTypeInt(token.size)
            elif token.ty == 'uint':
                ty = ParamTypeUint(token.size)
            elif token.ty == 'bytes':
                ty = ParamTypeFixedBytes(token.size)
            else:
                raise ValueError(f'Unknown type "{token.ty}"')
        else:
            raise ValueError(f'Expected a type; but got "{token}"')
        return self.take_array_tail(ty)

    def take_array_tail(self, ty) -> ParamType:
        if self.lexer.peek_token() != SYMBOL_OPEN_BRACKET:
            return ty
        self.lexer.next_token()
        token = self.lexer.peek_token()
        if isinstance(token, TokenNumber):
            ty = ParamTypeFixedArray(ty, token.number)
            self.lexer.next_token()
        else:
            ty = ParamTypeArray(ty)
        self.take_exact(SYMBOL_CLOSE_BRACKET)
        return self.take_array_tail(ty)

    def take_identifier(self, prefix_token: Token) -> TokenIdentifier:
        self.take_exact(prefix_token)
        v = self.lexer.next_token()
        if not isinstance(v, TokenIdentifier):
            raise ValueError(f'Expected an identifier; but got "{v}"')
        return v

    def take_exact(self, token: Token) -> None:
        v = self.lexer.next_token()
        if v != token:
            raise ValueError(f'Unexpected token; expect "{token}"; got "{v}"')


def parse_event(input):
    return HumanReadableParser(input).take_event()
