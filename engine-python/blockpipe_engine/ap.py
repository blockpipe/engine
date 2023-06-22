import os
import msgpack

from .rw import Writer, ReaderNonBlocking, ReaderInterval, READ_INTERVAL, NO_DATA
from .msg import MsgGetLogs, MsgLog
from .client import Client


class ApplicationProcess:
    def __init__(self, app, port):
        self.app = app
        self.client = Client('0.0.0.0', port)

    def run_and_exit(self, recv_id, send_id):
        writer = Writer(send_id)
        reader = ReaderNonBlocking(os.dup(recv_id))
        msg = MsgGetLogs(8500000, 8700000, self.app.get_filters())
        self.client.write(msg.to_bytes())
        while True:
            e = reader.read()
            if e != NO_DATA:
                writer.write(self.app.query(e))
                continue
            data = self.client.read()
            if not data:
                break
            v = msgpack.unpackb(data)
            if 'End' in v:
                break
            log = MsgLog.from_bytes(v)
            self.app.apply_log(log)
        self.client.write(msgpack.packb('Bye'))
        reader.close()
        reader = ReaderInterval(recv_id, 0.5)
        while True:
            data = reader.read()
            if data == READ_INTERVAL:
                if os.getppid() == 1:
                    print('Parent process is dead. Exiting...')
                    break
                continue
            writer.write(self.app.query(data).json())
        reader.close()
        writer.close()
