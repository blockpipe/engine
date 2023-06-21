import sys
from enum import Enum
from typing import Callable

from fastapi import FastAPI
from fastapi.testclient import TestClient


BLOCKPIPE_APP_NAME = '<blockpipe_app>'


def show_traceback(formatted_traceback):
    while len(formatted_traceback) > 1:
        if not formatted_traceback[0].startswith(f'  File "{BLOCKPIPE_APP_NAME}"'):
            formatted_traceback.pop(0)
        else:
            break
    for line in formatted_traceback:
        print(line, end='', file=sys.stderr)
    return len(formatted_traceback)


class VmStatus(Enum):
    SKIP = 'SKIP'  # Vm is skipping through blocks to find the first relevant block
    SYNC = 'SYNC'  # Vm is syncing blocks with the blockchain
    LIVE = 'LIVE'  # Vm is live, processing live logs as they come
    STOP = 'STOP'  # Vm is stopped due to an error


class Vm:
    def __init__(self, module, query_handler):
        self.app = FastAPI()
        self.client = TestClient(self.app)
        self.module = module
        self.status = VmStatus.SKIP
        self.query_handler = query_handler

    def register_handler(self, address: bytes, topic0: bytes, func: Callable[[int], None]):
        pass

    def register_route(self, path: str, func):
        pass

    def query(self, query: str):
        try:
            response = self.query_handler.query(query)
        except Exception:
            pass
        pass

    def skip_to_block(self, block_number):
        if self.status == VmStatus.STOP:
            raise ValueError('Vm is stopped')
        if block_number <= self.block_number:
            raise ValueError('Cannot skip to a block before the current block')
        self.block_number = block_number
        self.block_hash = None

    def apply_block(self, block_number, block_hash, parent_hash, logs):
        pass
