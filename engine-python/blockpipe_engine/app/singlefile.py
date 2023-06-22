from eth_utils.conversions import to_bytes
from inspect import getmembers, isfunction
from types import ModuleType

from .base import ApplicationBase
from ..abi_parser import parse_event


def parse_doc(docstring):
    if not docstring:
        return None
    lines = []
    for line in docstring.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    kvs = {}
    for line in lines:
        tokens = line.split(':', 1)
        if len(tokens) != 2:
            return None
        kvs[tokens[0]] = tokens[1].strip()
    if not kvs:
        return None
    return kvs


def wrap_handler_function(func, event):
    def wrapper(log):
        args = event.parse_arguments(log.topics, log.data)
        return func(log, *args)
    return wrapper


class SingleFileApplication(ApplicationBase):
    def __init__(self, code):
        super().__init__()
        try:
            compiled_code = compile(code, '<blockpipe_app>', 'exec')
            module = ModuleType('application')
            exec(compiled_code, module.__dict__)
        except Exception as e:
            # TODO: update error message
            raise e
        for _, func in getmembers(module, isfunction):
            if func.__doc__ is None:
                continue
            attributes = parse_doc(func.__doc__.strip())
            if attributes is None:
                continue
            if 'event' in attributes and 'address' in attributes:
                event = parse_event(f'event {attributes["event"]}')
                address = to_bytes(hexstr=attributes['address'])
                self._add_handler(address, event.topic0,
                                  wrap_handler_function(func, event))
            if 'event' in attributes and 'addresses' in attributes:
                event = parse_event(f'event {attributes["event"]}')
                for addr in attributes['addresses'].split(','):
                    address = to_bytes(hexstr=addr.strip())
                    self._add_handler(address, event.topic0,
                                      wrap_handler_function(func, event))
            if 'path' in attributes:
                path = attributes['path']
                self._add_route(path, func)
