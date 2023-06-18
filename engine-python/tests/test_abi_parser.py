import pytest

from blockpipe_engine.abi_parser import parse_event
from blockpipe_engine.abi_parser.lexer import HumanReadableLexer
from blockpipe_engine.abi_parser.token import (
    parse_symbol,
    parse_token,
    TokenSymbol,
    TokenIdentifier,
    TokenNumber,
    TokenKeyword,
    TokenTy,
    TokenTyWithSize,
)
from blockpipe_engine.abi_parser.types import (
    Event,
    EventParam,
    ParamTypeAddress,
    ParamTypeArray,
    ParamTypeBytes,
    ParamTypeFixedArray,
    ParamTypeInt,
    ParamTypeString,
    ParamTypeTuple,
    ParamTypeUint,
)


def test_parse_symbol():
    with pytest.raises(ValueError):
        parse_symbol('!!')
    assert parse_symbol(';') == TokenSymbol(';')
    assert parse_symbol('?') == None


def test_parse_token():
    with pytest.raises(ValueError):
        parse_token('3hello')
    assert parse_token('unknown') == TokenIdentifier('unknown')
    assert parse_token('bytes33') == TokenIdentifier('bytes33')
    assert parse_token('bytes33') == TokenIdentifier('bytes33')
    assert parse_token('123') == TokenNumber(123)
    assert parse_token('indexed') == TokenKeyword('indexed')
    assert parse_token('string') == TokenTy('string')
    assert parse_token('uint') == TokenTyWithSize('uint', 256)
    assert parse_token('int64') == TokenTyWithSize('int', 64)
    assert parse_token('bytes8') == TokenTyWithSize('bytes', 8)


def test_lexer_next_token():
    lexer = HumanReadableLexer(
        'event  Hello (  string indexed a,  indexed uint256[] )')
    assert lexer.next_token() == TokenKeyword('event')
    assert lexer.next_token() == TokenIdentifier('Hello')
    assert lexer.next_token() == TokenSymbol('(')
    assert lexer.next_token() == TokenTy('string')
    assert lexer.next_token() == TokenKeyword('indexed')
    assert lexer.next_token() == TokenIdentifier('a')
    assert lexer.next_token() == TokenSymbol(',')
    assert lexer.next_token() == TokenKeyword('indexed')
    assert lexer.next_token() == TokenTyWithSize('uint', 256)
    assert lexer.next_token() == TokenSymbol('[')
    assert lexer.next_token() == TokenSymbol(']')
    assert lexer.next_token() == TokenSymbol(')')
    assert lexer.next_token() is None


def test_parse_event():
    event = parse_event(
        'event MyTest(address[] indexed a, (uint, int32, bytes) b, string[32][] c)')
    assert event == Event(
        name='MyTest',
        inputs=[EventParam(
            name='a',
            ty=ParamTypeArray(ty=ParamTypeAddress()),
            indexed=True,
        ), EventParam(
            name='b',
            ty=ParamTypeTuple(tys=[
                ParamTypeUint(size=256),
                ParamTypeInt(size=32),
                ParamTypeBytes(),
            ]),
            indexed=False,
        ), EventParam(
            name='c',
            ty=ParamTypeArray(
                ty=ParamTypeFixedArray(ty=ParamTypeString(), size=32),
            ),
            indexed=False)],
        anonymous=False,
    )
