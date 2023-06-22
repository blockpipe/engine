from collections import defaultdict
from fastapi import FastAPI
from fastapi.testclient import TestClient


class ApplicationBase:
    def __init__(self):
        self.app = FastAPI()
        self.client = TestClient(self.app)
        self.handlers = defaultdict(list)

    def _add_handler(self, address, topic0, func):
        self.handlers[(address, topic0)].append(func)

    def _add_route(self, path, func):
        self.app.get(path)(func)

    def get_filters(self):
        return list(self.handlers.keys())

    def apply_log(self, log):
        for func in self.handlers[(log.address, log.topics[0])]:
            func(log)

    def query(self, path):
        return self.client.get(path)
