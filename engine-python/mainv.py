from dataclasses import dataclass
import typer

from blockpipe_engine.abi_parser import parse_event


def main():
    ev = parse_event(
        'event Transfer (address indexed from , address indexed to, uint value)')
    print(ev.topic0)
    print(ev.argument_types)
    print(ev.parse_arguments([
        bytes.fromhex(
            'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
        bytes.fromhex(
            '000000000000000000000000a9d1e08c7793af67e9d92fe308d5697fb81d3e43'),
        bytes.fromhex(
            '000000000000000000000000207ac2929df2094b09bfdba0ec6c16b02bc940de'),
    ], bytes.fromhex('00000000000000000000000000000000000000000000000965ceede1b047c800')))


if __name__ == '__main__':
    typer.run(main)
