```
                                        Swuniswap-v3
                                   \
                                    \\
                                     \%,     ,'     , ,.
                                      \%\,';/J,";";";;,,.
                         ~.------------\%;((`);)));`;;,.,-----------,~
                        ~~:           ,`;@)((;`,`((;(;;);;,`         :~~
                       ~~ :           ;`(@```))`~ ``; );(;));;,      : ~~
                      ~~  :            `X `(( `),    (;;);;;;`       :  ~~
                     ~~~~ :            / `) `` /;~   `;;;;;;;);,     :  ~~~~
                    ~~~~  :           / , ` ,/` /     (`;;(;;;;,     : ~~~~
                      ~~~ :          (o  /]_/` /     ,);;;`;;;;;`,,  : ~~~
                       ~~ :           `~` `~`  `      ``;,  ``;" ';, : ~~
                        ~~:                             `'   `'  `'  :~~
                         ~`-----------------------------------------`~                

```

# Swuniswap-v3
A Uniswap v3 Equivalent for Swivel's Orderbook.

-----------

**Instructions:**

Set your upper and lower ranges and let Swuniswap-v3 run things from there!

For Strategy Information: https://swivel.substack.com/p/market-making-in-yield-markets

--------

## Installation

#### Install/ensure compatable python version
This is a python project, i'm just going to assume you have a python available. If not, do that first.
Scrivel expects at least a Python version of 3.7.3

#### Assure you have pip available
`which pip`. Depending on your system it may be aliased with ...3 so, `which pip3`. If not present install it.

#### Setting up a virtual environment

```
python3 -m venv /path/to/new/virtual/environment
```

https://docs.python.org/3/library/venv.html

With the env made, activate it.
```
../Scripts/activate.bat
```
Now you can move to installing things...

#### Installing dependencies

Clone this repo, cd into the directory, (activate your virtual env if you have not) then

    pip install -r requirements.txt

### Private key
If you are performing transactions via the Swivel.py Vendor a private key is expected to be available in the environment as `PRIVATE_KEY`.
This used to sign offline, your private key is never exposed or broadcast in any way.

#### Constants
You'll need to modify the constants located in `/constants/__init__.py`:

E.g.
```
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
```

This is just one example market, it could, of course, be any other active market. USDC, etc... Feel free to make
any constants you want for others obviously.

## Run Swuniswap-v3
A range strategy on Swivel's exchange can then be run by 

    python swuniswap-v3.py

# Todo
Profit.
