class HumanReadableLexer:
    SYMBOLS = ('(', ')', '[', ']', ',')

    def __init__(self, input):
        self.input = input
        self.loc = 0
        self.peeked = None

    @classmethod
    def is_terminator(cls, token):
        return token in cls.SYMBOLS or token == ' '

    def peek_token(self):
        if self.peeked is None:
            self.peeked = self.next_token()
        return self.peeked

    def next_token(self):
        if self.peeked is not None:
            v = self.peeked
            self.peeked = None
            return v
        if self.loc >= len(self.input):
            return None
        if self.input[self.loc] == ' ':
            self.loc += 1
            return self.next_token()
        if self.input[self.loc] in self.SYMBOLS:
            self.loc += 1
            return self.input[self.loc - 1]
        start_loc = self.loc
        while self.loc < len(self.input) and not self.is_terminator(self.input[self.loc]):
            self.loc += 1
        return self.input[start_loc:self.loc]
