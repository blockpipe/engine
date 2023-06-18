import pytest

from blockpipe_engine.abi_parser.lexer import HumanReadableLexer
from blockpipe_engine.abi_parser.token import (
    parse_symbol,
    parse_token,
    TokenSymbol,
    TokenIdentifier,
    TokenKeyword,
    TokenTy,
    TokenTyWithSize,
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
    assert parse_token('(') == TokenSymbol('(')
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
