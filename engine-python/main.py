import os
import logging
import sys
import typer
import msgpack

from blockpipe_engine.app.singlefile import SingleFileApplication
from blockpipe_engine.client import Client
from blockpipe_engine.msg import MsgGetLogs, MsgLog
from blockpipe_engine.web import WebserverProcess
from blockpipe_engine.ap import ApplicationProcess


class PrintToLogger:
    def __init__(self, orig_stdout,  func):
        self.func = func
        self.orig_stdout = orig_stdout

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.func(line.rstrip())

    def flush(self):
        pass

    def isatty(self):
        return self.orig_stdout.isatty()


def configure_print_to_logger():
    logger = logging.getLogger()
    sys.stdout = PrintToLogger(sys.stdout, logger.info)
    sys.stderr = PrintToLogger(sys.stderr, logger.error)


def fork_spawn(parent_cls, parent_args, child_cls, child_args):
    child_recv_id, parent_send_id = os.pipe()
    parent_recv_id, child_send_id = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        os.close(parent_recv_id)
        os.close(parent_send_id)
        child = child_cls(*child_args)
        child.run_and_exit(child_recv_id, child_send_id)
        exit(0)
    else:  # parent
        os.close(child_recv_id)
        os.close(child_send_id)
        parent = parent_cls(*parent_args)
        parent.run_and_exit(parent_recv_id, parent_send_id)


def main():
    logging.basicConfig(format='[%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
    httpx_logger = logging.getLogger('httpx')
    httpx_logger.setLevel(logging.WARNING)
    configure_print_to_logger()

    code = open('./example_program.py', 'r').read()
    app = SingleFileApplication(code)

    fork_spawn(
        WebserverProcess,
        ('blockpipe', 8888),
        ApplicationProcess,
        (app, 9167),
    )

    # client = Client('0.0.0.0', 9167)

    # filters = app.get_filters()
    # msg = MsgGetLogs(8500000, 8700000, filters)
    # client.write(msg.to_bytes())
    # while True:
    #     data = client.read()
    #     if not data:
    #         break
    #     v = msgpack.unpackb(data)
    #     if 'End' in v:
    #         break
    #     log = MsgLog.from_bytes(v)
    #     app.apply_log(log)
    # client.write(msgpack.packb('Bye'))
    # print(app.query('/total_supply').json())


if __name__ == '__main__':
    typer.run(main)
