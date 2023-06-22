import pickle
import time
import os
import selectors
import fcntl
import errno


class Signal:
    def __init__(self, v):
        self.v = v

    def __str__(self):
        return self.v

    def __repr__(self):
        return f'Signal({self.v})'

    def __eq__(self, lhs):
        return isinstance(lhs, Signal) and lhs.v == self.v


READ_INTERVAL = Signal('READ_INTERVAL')
NO_WRITER = Signal('NO_WRITER')
NO_DATA = Signal('NO_DATA')


class Writer:
    def __init__(self, fd):
        self.f = os.fdopen(fd, 'wb')

    def write(self, v):
        data = pickle.dumps(v)
        self.f.write(len(data).to_bytes(4, 'big'))
        self.f.write(data)
        self.f.flush()

    def close(self):
        self.f.close()


class Reader:
    def __init__(self, fd):
        self.fd = fd
        self.buffer = bytearray()
        self.buffer_index = 0

    def parse_data(self):
        if self.buffer_index > 4096:
            self.buffer = self.buffer[self.buffer_index:]
            self.buffer_index = 0
        if len(self.buffer) - self.buffer_index < 4:
            return None
        size = int.from_bytes(
            self.buffer[self.buffer_index:self.buffer_index+4], 'big')
        if len(self.buffer) - self.buffer_index < 4+size:
            return None
        data = self.buffer[self.buffer_index+4:self.buffer_index+4+size]
        self.buffer_index += 4+size
        return pickle.loads(data)

    def read(self):
        while True:
            data = self.parse_data()
            if data is not None:
                return data
            buf = os.read(self.fd, 1024)
            if not buf:
                return NO_WRITER
            self.buffer.extend(buf)

    def close(self):
        os.close(self.fd)


class ReaderNonBlocking(Reader):
    def __init__(self, fd):
        super().__init__(fd)
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def read(self):
        try:
            buf = os.read(self.fd, 1024)
            if not buf:
                return NO_WRITER
            self.buffer.extend(buf)
        except BlockingIOError as e:
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                pass
            else:
                raise
        data = self.parse_data()
        if data is not None:
            return data
        return NO_DATA


class ReaderInterval(Reader):
    def __init__(self, fd, timeout):
        super().__init__(fd)
        self.timeout = timeout
        self.last_timeout = 0
        self.selector = selectors.DefaultSelector()
        self.selector.register(fd, selectors.EVENT_READ)

    def read(self):
        while True:
            now = time.time()
            if now > self.last_timeout + self.timeout:
                self.last_timeout = now
                return READ_INTERVAL
            data = self.parse_data()
            if data is not None:
                return data
            events = self.selector.select(self.timeout / 10)
            if events:
                buf = os.read(self.fd, 1024)
                if not buf:
                    return NO_WRITER
                self.buffer.extend(buf)

    def close(self):
        return super().close()
