import msgpack

from blockpipe_engine.client import Client
from blockpipe_engine.msg import MsgGetLogs, MsgLog


def main():
    s = Client('0.0.0.0', 9167)
    msg = MsgGetLogs(
        from_block=10000000,
        to_block=10100000,
        filters=[(
            bytes.fromhex('ba11d00c5f74255f56a5e366f4f77f5a186d7f55'),
            bytes.fromhex(
                'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
        )],
    )
    s.write(msg.to_bytes())
    while True:
        data = s.read()
        if not data:
            break
        v = msgpack.unpackb(data)
        if 'End' in v:
            break
        print(MsgLog.from_bytes(v))
    s.write(msgpack.packb('Bye'))


if __name__ == '__main__':
    main()
