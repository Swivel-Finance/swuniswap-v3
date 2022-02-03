import os

# Market
UNDERLYING = os.getenv("UNDERLYING", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")  # The underlying token address
MATURITY = float(os.getenv("MATURITY", 1656039600))  # The Swivel market maturity in unix
DECIMALS = float(os.getenv("DECIMALS", 6))  # The decimals of the underlying token
NETWORK_STRING = os.getenv("NETWORK", "mainnet")

# Position
AMOUNT = float(os.getenv("AMOUNT", 50000))  # The amount of n/zcTokens to use market-making
# Assumes a 50/50 range distribution around current market rates. If distributions are uneven, more n/zcTokens are required
UPPER_RATE = float(os.getenv("UPPER_RATE", 5.5))  # The highest rate at which to quote
LOWER_RATE = float(os.getenv("LOWER_RATE", 2.75))  # The lowest rate at which to quote
NUM_TICKS = int(3)  # The number of liquidity ticks to split your amount into (Per side + 1 at market price)
COMPOUND_RATE_LEAN = float(
    1)  # How much your quote should change when Compound’s rate varies (e.g. 1 = 1:1 change in price)
EXPIRY_LENGTH = float(600)  # How often orders should be refreshed (in seconds)

PUBLIC_KEY = "0xb42Af00422f53e09FC97C3Af041Ddd0B19E936A5"
