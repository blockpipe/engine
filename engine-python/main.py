from dataclasses import dataclass
import typer
import msgpack

from blockpipe_engine.abi_parser import parse_event
from blockpipe_engine.app.singlefile import SingleFileApplication
from blockpipe_engine.client import Client
from blockpipe_engine.msg import MsgGetLogs, MsgLog


def main():
    client = Client('0.0.0.0', 9167)
    code = open('./example_program.py', 'r').read()
    app = SingleFileApplication(code)

    filters = app.get_filters()
    msg = MsgGetLogs(8500000, 8700000, filters)
    client.write(msg.to_bytes())
    while True:
        data = client.read()
        if not data:
            break
        v = msgpack.unpackb(data)
        if 'End' in v:
            break
        log = MsgLog.from_bytes(v)
        app.apply_log(log)
    client.write(msgpack.packb('Bye'))
    print(app.query('/total_supply').json())


if __name__ == '__main__':
    typer.run(main)
