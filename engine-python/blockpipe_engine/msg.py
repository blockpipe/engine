import msgpack
from dataclasses import dataclass


@dataclass
class MsgGetLogs:
    from_block: int
    to_block: int
    filters: list[tuple[bytes, bytes]]

    def to_bytes(self):
        return msgpack.packb({
            'GetLogs': [self.from_block, self.to_block, self.filters],
        })


@dataclass
class MsgLog:
    block_number: int
    block_hash: bytes
    block_timestamp: int
    log_index: int
    tx_hash: bytes
    tx_index: int
    address: bytes
    topics: list[bytes]
    data: bytes

    @classmethod
    def from_bytes(cls, data):
        data = data['Row']
        return cls(
            block_number=data[0],
            block_hash=data[1],
            block_timestamp=data[2],
            log_index=data[3],
            tx_hash=data[4],
            tx_index=data[5],
            address=data[6],
            topics=data[7],
            data=data[8],
        )
