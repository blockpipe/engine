import socket
import msgpack


class BufferedSocket:
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.buffer = b''

    def write(self, data):
        self.sock.sendall(len(data).to_bytes(4, 'big'))
        self.sock.sendall(data)

    def read(self):
        size = int.from_bytes(self._read_exact(4), 'big')
        return self._read_exact(size)

    def _read_exact(self, num_bytes):
        while len(self.buffer) < num_bytes:
            new_data = self.sock.recv(4096)
            if not new_data:
                raise IOError("Could not receive enough data")
            self.buffer += new_data

        result, self.buffer = self.buffer[:num_bytes], self.buffer[num_bytes:]
        return result


def main():
    s = BufferedSocket('0.0.0.0', 9167)
    s.write(msgpack.packb({
        'GetLogs': [
            (
                bytes.fromhex('ba11d00c5f74255f56a5e366f4f77f5a186d7f55'),
                bytes.fromhex(
                    'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
            ),
        ]
    }))
    while True:
        data = s.read()
        if not data:
            break
        v = msgpack.unpackb(data)
        print(v)
        if 'End' in v:
            break
    s.write(msgpack.packb('Bye'))


if __name__ == '__main__':
    main()
