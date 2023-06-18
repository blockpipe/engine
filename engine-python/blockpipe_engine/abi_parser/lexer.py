from .token import parse_symbol, parse_token


class HumanReadableLexer:
    def __init__(self, input):
        self.input = input
        self.loc = 0
        self.peeked = None

    def peek_token(self):
        if self.peeked is None:
            self.peeked = self.next_token()
        return self.peeked

    def next_token(self):
        # If we have a peeked token, return it and clear it.
        if self.peeked is not None:
            v = self.peeked
            self.peeked = None
            return v
        # If we are at the end of the input, return None.
        if self.loc >= len(self.input):
            return None
        # Skip whitespace characters.
        if self.input[self.loc].isspace():
            self.loc += 1
            return self.next_token()
        # If we run into a symbol, then that is the next token.
        if (symbol := parse_symbol(self.input[self.loc])) is not None:
            self.loc += 1
            return symbol
        # Otherwise, this token spans until the next whitespace, symbol, or end of input.
        start_loc = self.loc
        while self.loc < len(self.input):
            if self.input[self.loc].isspace():
                break
            if parse_symbol(self.input[self.loc]) is not None:
                break
            self.loc += 1
        return parse_token(self.input[start_loc:self.loc])
