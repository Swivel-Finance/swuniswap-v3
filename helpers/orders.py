import time, json
from web3 import Web3

order_keys = ('underlying', 'maturity', 'vault', 'exit', 'principal', 'premium', 'expiry')

def order_key(a):
    """Produce a unique order key

    Parameters:
        a (string) address of the ordering account

    Description:
        We add the unix epoch timestamp along with the address to form a 'key'

    Returns:
        Keccak of the assembled 'key'
    """

    key = '{}{}'.format(a, time.time())
    return Web3.keccak(Web3.toBytes(text=key))

def new_order(a, **kwargs):
    """Produce an order

    Parameters
        a (string) address of the ordering account
        kwargs optional keyword args which, if an actual order key, will be included:
            underlying (string)
            maturity (int)
            vault (bool)
            exit (bool)
            principal (int)
            premium (int)
            expiry (int)

    Returns:
        the assembled order
    """

    order = {'key': order_key(a), 'maker': a}

    for key in kwargs:
        if key in order_keys:
            order[key] = kwargs[key]

    return order

def stringify(o):
    """Given an order, return an order that the swivel api will accept

    Description:
        The Swivel Api expects that all values for an order (except bools) are strings

    Parameters:
        o (dict) an Order dict

    Returns:
        The strinfified order
    """

    order = {
        'key': o['key'].hex(),
        'maker': o['maker'],
        'underlying': o['underlying'],
        'maturity': str(o['maturity']),
        'vault': o['vault'],
        'exit': o['exit'],
        'principal': str(o['principal']),
        'premium': str(o['premium']),
        'expiry': str(o['expiry']),
    }

    return order

def parse(o):
    """Given an order from the swivel api, return an order H.O.C methods will accept

    Description:
        This is the reverse of stringify, use it to prepare a stringified order for use with H.O.C methods

    Parameters:
        o (dict) stringified order

    Returns:
        The non stringified order
    """

    order = {
        'key': Web3.toBytes(hexstr=o['key']),
        'maker': o['maker'],
        'underlying': o['underlying'],
        'maturity': int(o['maturity']),
        'principal': int(o['principal']),
        'premium': int(o['premium']),
        'expiry': int(o['expiry']),
    }

    for key in ('vault', 'exit'):
        if o[key] == 'true':
            order[key] = True
        else:
            order[key] = False

    return order
