from blockpipe_engine.abi_parser.token import parse_token, TokenKeyword, TokenTy, TokenTyWithSize


def test_parse_token():
    assert parse_token('unknown') is None
    assert parse_token('bytes33') is None
    assert parse_token('indexed') == TokenKeyword('indexed')
    assert parse_token('string') == TokenTy('string')
    assert parse_token('uint') == TokenTyWithSize('uint', 256)
    assert parse_token('int64') == TokenTyWithSize('int', 64)
    assert parse_token('bytes8') == TokenTyWithSize('bytes', 8)
