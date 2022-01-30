# Market
UNDERLYING = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" # The underlying token address
MATURITY = float(1656039600) # The Swivel market maturity in unix
DECIMALS = float(6) # The decimals of the underlying token
NETWORK_STRING = "mainnet"

# Position
AMOUNT = float(50000) # The amount of n/zcTokens to use market-making
UPPER_RATE = float(5.5) # The highest rate at which to quote 
LOWER_RATE = float(2.75) # The lowest rate at which to quote 
NUM_TICKS = int(3) # The number of liquidity ticks to split your amount into (Per side + 1 at market price)
COMPOUND_RATE_LEAN = float(1) # How much your quote should change when Compound’s rate varies (e.g. 1 = 1:1 change in price) 
EXPIRY_LENGTH = float(600) # How often orders should be refreshed (in seconds) 

PUBLIC_KEY = "0xb42Af00422f53e09FC97C3Af041Ddd0B19E936A5"