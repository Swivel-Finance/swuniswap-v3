# Market
UNDERLYING = "0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa" # The underlying token address
MATURITY = float(1669957199) # The Swivel market maturity in unix
DECIMALS = float(18) # The decimals of the underlying token
NETWORK_STRING = "rinkeby"

# Position
AMOUNT = float(10000) # The amount of nTokens to use market-making
UPPER_RATE = float(13) # The highest rate at which to quote 
LOWER_RATE = float(9.5) # The lowest rate at which to quote 
NUM_TICKS = int(3) # The number of liquidity ticks to split your amount into (Per side + 1 at market price)
COMPOUND_RATE_LEAN = float(1) # How much your quote should change when Compound’s rate varies (e.g. 1 = 1:1 change in price) 
EXPIRY_LENGTH = float(60) # How often orders should be refreshed (in seconds) 

PUBLIC_KEY = "0x3f60008Dfd0EfC03F476D9B489D6C5B13B3eBF2C"