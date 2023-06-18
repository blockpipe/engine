from .lexer import HumanReadableLexer


class HumanReadableParser:
    def __init__(self, input):
        self.lexer = HumanReadableLexer(input)

    @classmethod
    def parse_event(cls, input):
        cls(input).take_event()

    def take_event(self):
        name = self.take_identifier('event')
        self.take_exact('(')
        inputs = self.take_event_params()
        self.take_exact(')')
        anonymous = False
        if self.lexer.peek_token() == 'anonymous':
            anonymous = True
            self.lexer.next_token()
        return {
            'type': 'event',
            'name': name,
            'anonymous': anonymous,
            'inputs': inputs,
        }

    def take_event_params(self):
        events = []
        if self.lexer.peek_token() == ')':
            return events
        while True:
            events.append(self.take_event_param())
            token = self.lexer.peek_token()
            if token == ')':
                break
            elif token == ',':
                self.lexer.next_token()
                continue
            else:
                raise ValueError(f'Expected "," or ")"; got "{token}"')
        return events

    def take_event_param(self):
        kind = self.take_param()
        name = ""
        indexed = False
        while True:
            token = self.lexer.peek_token()
            if token == 'indexed':
                indexed = True
                self.lexer.next_token()
            elif token not in HumanReadableLexer.SYMBOLS:
                name = token
                self.lexer.next_token()
            else:
                break
        event = {
            'type': kind,
            'name': name,
            'indexed': indexed,
        }
        if isinstance(kind, list):
            event['type'] = 'tuple'
            event['components'] = kind
        return event

    def take_params(self):
        params = []
        if self.lexer.peek_token() == ')':
            return params
        while True:
            params.append(self.take_param())
            token = self.lexer.peek_token()
            if token == ')':
                break
            elif token == ',':
                self.lexer.next_token()
                continue
            else:
                raise ValueError(f'Expected "," or ")"; got "{token}"')
        return params

    def take_param(self):
        token = self.lexer.next_token()
        if token == '(':
            ty = []
            for kind in self.take_params():
                if isinstance(kind, list):
                    ty.append({'type': 'tuple', 'components': kind})
                else:
                    ty.append({'type': kind})
            self.take_exact(')')
        else:
            ty = token
        return ty
        # TODO: Handle tail array

    def take_identifier(self, keyword):
        if (v := self.lexer.next_token()) != keyword:
            raise ValueError(f'Expected "{keyword}"; got "{v}"')
        return self.lexer.next_token()

    def take_exact(self, keyword):
        if (v := self.lexer.next_token()) != keyword:
            raise ValueError(f'Expected "{keyword}"; got "{v}"')
