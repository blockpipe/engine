from dataclasses import dataclass


s = '''@__handler__
       event: Transfer(address indexed, address indexed, uint256)
       address: 0xba11d00c5f74255f56a5e366f4f77f5a186d7f55
    '''


@dataclass
class DocString:
    header: str
    kvs: dict[str, str]

    @classmethod
    def parse(cls, docstring):
        if not docstring:
            return None
        lines = []
        for line in docstring.splitlines():
            line = line.strip()
            if line:
                lines.append(line)
        if not lines:
            return None
        if not lines[0].startswith('@__') and lines[0].endswith('__'):
            return None
        header = lines[0][3:-2].strip()
        kvs = {}
        for line in lines[1:]:
            key, value = line.split(':', 1)
            kvs[key] = value.strip()
        return cls(header, kvs)


a = DocString.parse(s)
print(a)
