import requests
from requests.structures import CaseInsensitiveDict

# the current api-dev exposed for swivel api with a format placeholder
swivel_api_route = 'https://api-dev.swivel.exchange/v2/{}'
kovan_api_route = 'https://api-main.swivel.exchange/v2/{}'

# update as needed...
param_keys = ('underlying', 'maturity', 'depth', 'status')

# a user may want to view non active orders
non_active_order_status = ('expired', 'cancelled', 'full', 'insolvent')

def new_params(**kwargs):
    params = {}

    for key in kwargs:
        if key in param_keys:
            params[key] = kwargs[key]

    return params

def compound_c_tokens():
    """Given an underlying, return the current compound price"""
    # Comment out when no longer using Rinkeby

    url = "https://api.compound.finance/api/v2/ctoken"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    # comment out when no longer using Rinkeby
    n = "mainnet"
    data = '{"network":'+n+'}'

    resp = requests.post(url, headers=headers, data=data)
    return resp.json()

# No test networks are supported by the Compound API at this time
def underlying_compound_rate(u):
    """Return the current compound token price"""
    cTokens = compound_c_tokens()
    # Comment out when no longer using Rinkeby
    u = "0x6b175474e89094c44da98b954eedeac495271d0f"
    for c in cTokens['cToken']:
        if c['underlying_address'] == u:
            return float(c['supply_rate']['value'])

def invalidate_order(u, m, n):
    """Given an order key, invalidate it"""
    if n == 4:

        route = swivel_api_route.format('orders/{}')
        params = new_params(underlying=u, maturity=m)
        resp = requests.delete(route, params=params, auth=('<____>','<____>'))
        return resp.status_code, resp.reason
    if n == 42:

        route = kovan_api_route.format('orders/{}')
        params = new_params(underlying=u, maturity=m)
        resp = requests.delete(route, params=params)
        return resp.status_code, resp.reason

def orderbook(u, m, d, n):
    """Given an underlying:maturity market pair, fetch the current orderbook"""
    if n == 4:
        params = new_params(underlying=u, maturity=m, depth=d)
        resp = requests.get(swivel_api_route.format('orderbook'), params=params)
        return resp.json()
    if n == 42:
        params = new_params(underlying=u, maturity=m, depth=d)
        resp = requests.get(kovan_api_route.format('orderbook'), params=params)
        return resp.json()
        

def markets(n, status=None):
    """Fetch all markets or only active (non-matured) from the Swivel API"""
    if n == 4:
        params = None    
        if status != None:
            params = new_params(status=status)

        resp = requests.get(swivel_api_route.format('markets'), params=params)
        return resp.json()

    if n == 42:
        params = None    
        if status != None:
            params = new_params(status=status)

        resp = requests.get(kovan_api_route.format('markets'), params=params)
        return resp.json()

def last_trade(u, m, n):
    """Given an underlying:maturity market pair, fetch the most recent fill activity"""
    if n == 4:
        params = new_params(underlying=u, maturity=m, depth=1)
        resp = requests.get(swivel_api_route.format('fills'), params=params)
        return resp.json()[0]
    if n == 42:
        params = new_params(underlying=u, maturity=m, depth=1)
        resp = requests.get(kovan_api_route.format('fills'), params=params)
        return resp.json()[0]

def orders(u, m, a, n, status=None):
    """Given a market return a list of the orders by the given address

    Description:
        Note that the status keyword may be passed to view non-active orders of the given status

    Parameters:
        u (string) market underlying
        m (int) market maturity
        a (string) public key (address) owner of the orders

        status (string) optional. one of non_active_order_status if desired

    Returns:
        List of orders belonging to the given maker
    """
    if n == 4:
        route = swivel_api_route.format('users/{}/orders'.format(a))
        params = new_params(underlying=u, maturity=m)

        if status !=None:
            params['status'] = status

        resp = requests.get(route, params)
        return resp.json()
    if n == 42:
        route = kovan_api_route.format('users/{}/orders'.format(a))
        params = new_params(underlying=u, maturity=m)

        if status !=None:
            params['status'] = status

        resp = requests.get(route, params)
        return resp.json()

def order(k, n):
    """Given a key, return the order it belongs to"""
    if n == 4:
        route = swivel_api_route.format('orders/{}'.format(k))
        resp= requests.get(route)
        return resp.json()
    if n == 42:
        route = kovan_api_route.format('orders/{}'.format(k))
        resp= requests.get(route)
        return resp.json()

def limit_order(o, s, n):
    """Given an order and a signature, place it with the swivel api

    Returns:
        http status code, reason
    """
    if n == 4:
        resp = requests.post(swivel_api_route.format('orders'), json={'order': o, 'signature': s})
        return resp.status_code, resp.reason
    if n == 42:
        resp = requests.post(kovan_api_route.format('orders'), json={'order': o, 'signature': s})
        return resp.status_code, resp.reason

