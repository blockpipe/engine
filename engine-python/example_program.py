'''
version: 0.0.1
start_block: 7000000
network: ethereum_mainnet
context: tx_hash
'''
from collections import defaultdict


balances = defaultdict(int)
lastest_transaction = {}


def handle_transfer(ctx, _from, _to, _value):
    '''event: Transfer(address indexed, address indexed, uint256)
       address: 0xba11d00c5f74255f56a5e366f4f77f5a186d7f55
    '''
    balances[_from] -= _value
    balances[_to] += _value
    lastest_transaction[_from] = lastest_transaction[_to] = ctx.tx_hash


def api_get_balance(address):
    '''path: /balance/{address}'''
    return balances[address]


def api_get_total_supply():
    '''path: /total_supply'''
    return -balances['\x00'*20]
