import socket


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.buffer = bytearray()
        self.buffer_index = 0

    def write(self, data):
        self.sock.sendall(len(data).to_bytes(4, 'big'))
        self.sock.sendall(data)

    def read(self):
        size = int.from_bytes(self._read_exact(4), 'big')
        return self._read_exact(size)

    def _read_exact(self, num_bytes):
        if self.buffer_index > 65536:
            self.buffer = self.buffer[self.buffer_index:]
            self.buffer_index = 0
        while len(self.buffer) - self.buffer_index < num_bytes:
            new_data = self.sock.recv(4096)
            if not new_data:
                raise IOError('Could not receive enough data')
            self.buffer.extend(new_data)
        data = self.buffer[self.buffer_index:self.buffer_index + num_bytes]
        self.buffer_index += num_bytes
        return data
