import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))
from swivel.vendors import W3
from time import sleep
from sys import exit
import math
import time
import datetime
from web3 import Web3
import json

from constants import(
    UNDERLYING,
    MATURITY,
    DECIMALS,
    NETWORK_STRING,
    AMOUNT,
    UPPER_RATE,
    LOWER_RATE,
    NUM_TICKS,
    COMPOUND_RATE_LEAN,
    EXPIRY_LENGTH,
    PUBLIC_KEY,
)

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

from helpers.orders import new_order, stringify

from helpers.http import (
    last_trade,
    limit_order,
    order,
    underlying_compound_rate,
)

from helpers.colors import(
    start,
    stop,
    blue,
    white,
    green,
    red,
    cyan,
    yellow,
    magenta,
)

def fetchPrice(underlying, maturity, network) -> float:
    trade = last_trade(underlying, maturity, network)
    return trade['price']

def initialPositionCreation(underlying, maturity, upperRate, lowerRate, amount, expiryLength):

    initialOrders = []
    numBuyOrders = 0
    numSellOrders = 0

    # establish the "market price"
    price = fetchPrice(underlying, math.trunc(maturity), network)

    # establish the mid-range rate
    midRate = (upperRate + lowerRate) / 2

    print(cyan('Current Price:'))
    print(white(price))
    price = float(price)
    # use safe allocation of allocated capital
    safeAmount = amount * .999 * 10**int(DECIMALS)

    # Sum martingale weight of all orders
    sum = 0
    for i in range (0, NUM_TICKS+1):
        weight = 2**i
        sum = sum + weight

    midTickAmount = (safeAmount / (sum)) 

    # annualize price to get rate
    timeDiff = maturity - time.time()
    timeModifier = (timeDiff / 31536000)

    marketRate = truncate((price / timeModifier * 100),8)
    print(yellow('Market Rate:'))
    print(white(f'{marketRate}%'))

    print(magenta('Your Mid Rate:'))
    print(white(f'{midRate}%'))
    print(' ')

    # determine upper / lower ranges
    upperDiff = upperRate - midRate
    lowerDiff = midRate - lowerRate
    lowerPrice = truncate((lowerRate * timeModifier / 100),5)
    upperPrice = truncate((upperRate * timeModifier / 100),5)
    midPrice = truncate((midRate * timeModifier / 100), 5)

    print(red('Upper (Sell nToken) Range:'))
    print(white(f'Rates: {midRate}% - {upperRate}%'))
    print(f'Prices: {midPrice} - {upperPrice}')
    print(green('Lower (Buy nToken) Range:'))
    print(white(f'Rates: {lowerRate}% - {midRate}%'))
    print(f'Prices: {lowerPrice} - {midPrice}\n')
    print(cyan('--------------------------'))
    print(white(' '))

    blankInput = input('Press Enter to continue...\n')

    if lowerDiff < 0 or upperDiff < 0:
        print('Error: Your rates are too high or low for a real range')
        exit(1)

    # determine how spread each tick is (-1 in order to have prices match at mid market price)
    upperTickDiff = upperDiff / (NUM_TICKS)
    lowerTickDiff = lowerDiff / (NUM_TICKS)

    # set initial order expiries
    expiry = float(time.time()) + expiryLength

    for i in range(1,NUM_TICKS+1):
        # determine specific tick's rate and price
        tickRate = midRate + (upperTickDiff * (i))
        tickPrice = tickRate * timeModifier / 100

        exponent = NUM_TICKS-i
        # determine order size (martingale weighted)

        tickAmount = midTickAmount * 2**i

        # set specific order sizes
        principal = tickAmount
        premium = principal*tickPrice
        tickOrderPrice = premium/principal

        if tickOrderPrice < price:
            # create, sign, and place the order
            tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principal), premium=int(premium), expiry=int(expiry))
            signature = vendor.sign_order(tickOrder, network, swivelAddress)
            numBuyOrders += 1
        else:
            # create, sign, and place the order
            tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principal), premium=int(premium), expiry=int(expiry))
            signature = vendor.sign_order(tickOrder, network, swivelAddress)
            numSellOrders += 1

        orderResponse = limit_order(stringify(tickOrder), signature, network)
        # store order and key
        orderKey = tickOrder['key'].hex()

        apiSuccess = False
        while apiSuccess == False:
            try:
                apiOrder = order(orderKey, network)
                apiSuccess = True
            except:
                print("Error: Failed to retrieve order from Swivel API")
                print("Retrying in 30s...")
                time.sleep(30)

        initialOrders.append(apiOrder)


        if tickOrderPrice < price:
            print(green('Buy Order #'+str(numBuyOrders)))
        else:
            print(red('Sell Order #'+str(numSellOrders)))
        print(white(f'Order Key: {orderKey}'))
        print(f'Order Price: {tickOrderPrice}')
        print(f'Order Rate: {tickRate}')
        principalString = str(principal/10**DECIMALS)
        print(f'Order Amount: {principalString} nTokens')
        print(f'Order Response: {orderResponse}\n')

    for i in range(1,NUM_TICKS+1):
        tickRate = midRate - (lowerTickDiff * (i))
        tickPrice = tickRate * timeModifier / 100

        exponent = NUM_TICKS-i

        tickAmount = midTickAmount * 2**i

        principal = tickAmount 
        premium = tickAmount * tickPrice
        tickOrderPrice = premium/principal

        if tickOrderPrice < price:
            # create, sign, and place the order
            tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principal), premium=int(premium), expiry=int(expiry))
            signature = vendor.sign_order(tickOrder, network, swivelAddress)
            numBuyOrders += 1
        else:
            # create, sign, and place the order
            tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principal), premium=int(premium), expiry=int(expiry))
            signature = vendor.sign_order(tickOrder, network, swivelAddress)
            numSellOrders += 1

        orderResponse = limit_order(stringify(tickOrder), signature, network)
        # store order and key
        orderKey = tickOrder['key'].hex()

        apiSuccess = False
        while apiSuccess == False:
            try:
                apiOrder = order(orderKey, network)
                apiSuccess = True
            except:
                print("Error: Failed to retrieve order from Swivel API")
                print("Retrying in 30s...")
                time.sleep(30)
        initialOrders.append(apiOrder)

        if tickOrderPrice < price:
            print(green('Buy Order #'+str(numBuyOrders)))
        else:
            print(red('Sell Order #'+str(numSellOrders)))
        print(white(f'Order Key: {orderKey}'))
        print(f'Order Price: {tickOrderPrice}')
        print(f'Order Rate: {tickRate}')
        principalString = str(principal/10**DECIMALS)
        print(f'Order Amount: {principalString} nTokens')
        print(f'Order Response: {orderResponse}\n')

    # Place the middle tick's order
    principal = midTickAmount
    premium = principal * midPrice

    # create, sign, and place the order
    if midPrice > price:
        tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principal), premium=int(premium), expiry=int(expiry))
        signature = vendor.sign_order(tickOrder, network, swivelAddress)
    else:
        tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principal), premium=int(premium), expiry=int(expiry))
        signature = vendor.sign_order(tickOrder, network, swivelAddress) 

    orderResponse = limit_order(stringify(tickOrder), signature, network)
    orderKey = tickOrder['key'].hex()

    apiSuccess = False
    while apiSuccess == False:
        try:
            apiOrder = order(orderKey, network)
            apiSuccess = True
        except:
            print("Error: Failed to retrieve order from Swivel API")
            print("Retrying in 30s...")
            time.sleep(30)
    initialOrders.append(apiOrder)
    if midPrice > price:
        print(red('Mid-Range Sell Order'))
    else:
        print(green('Mid-Range Buy Order'))
    print(white(f'Order Key: {orderKey}'))
    print(f'Order Price: {midPrice}')
    print(f'Order Rate: {midRate}')
    principalString = str(principal/10**DECIMALS)
    print(f'Order Amount: {principalString} nTokens')
    print(f'Order Response: {orderResponse}\n')

    return (initialOrders)

def combineAndPlace(queuedOrders, queuedOrderSignatures, timeDiff, newExpiry):
        usedOrderKeys = []
        newOrders = []
        # iterate through the orders
        for i in range (0, len(queuedOrders)):
            baseOrder = queuedOrders[i]
            baseOrderKey = queuedOrders[i]['key']
            baseOrderKey = baseOrderKey.hex()
            baseOrderSignature = queuedOrderSignatures[i]

            combinedPrincipal = float(baseOrder['principal'])
            combinedPremium = float(baseOrder['premium'])
            combined = False

            # if the order has not already been combined with another order
            if baseOrderKey not in usedOrderKeys:
                # iterate through the orders again to find orders that can be combined with the current order
                for j in range (0, len(queuedOrders)):

                    queuedOrder = queuedOrders[j]
                    queuedOrderKey = queuedOrders[j]['key'].hex()
                    # ensure not comparing to self
                    if baseOrderKey != queuedOrderKey:
                        queuedOrderPrice = queuedOrder['premium'] / queuedOrder['principal']
                        baseOrderPrice = baseOrder['premium'] / baseOrder['principal']
                        # if the two orders are within .005 of each other and the orderTypes are the same, combine the orders
                        if abs(queuedOrderPrice - baseOrderPrice) <= .00025 and queuedOrder['exit'] == baseOrder['exit']:
                                # add the amounts to the combined order 
                                combinedPrincipal += float(queuedOrder['principal'])
                                combinedPremium += float(queuedOrder['premium'])
                                usedOrderKey = queuedOrderKey
                                # mark the orders that were combined as "used"
                                usedOrderKeys.append(usedOrderKey)

                                printedUsedOrderKey = "0x..." + usedOrderKey[-4:]                     
                                printedBaseOrderKey = "0x..." + baseOrderKey[-4:]  

                                # print used order info
                                print(magenta('Combined Orders with a price of ' + str(truncate(queuedOrderPrice,4)) + f': {printedUsedOrderKey} and {printedBaseOrderKey}'))
                                print(white(f'Used Order: {usedOrderKey}\n'))

                                # set combined marker
                                combined = True 

                # if the order was not combined with any others, place the order
                if combined == False:
                    orderResponse = limit_order(stringify(baseOrder), baseOrderSignature, network)
                    orderKey = baseOrderKey
                    
                    apiSuccess = False
                    while apiSuccess == False:
                        try:
                            apiOrder = order(orderKey, network)
                            apiSuccess = True
                        except:
                            print("Error: Failed to retrieve order from Swivel API")
                            print("Retrying in 30s...")
                            time.sleep(30)

                    # establish order typestring + print order type
                    orderExit = apiOrder['order']['exit']

                    if orderExit == True:
                        typeString = "Sell"
                        print(red('Placed ' + typeString + ' Order:'))
                    else:
                        typeString = "Buy"
                        print(green('Placed ' + typeString + ' Order:'))
                    
                    orderPrice = float(apiOrder["meta"]["price"])
                    orderRate = truncate((orderPrice * 31536000/timeDiff),6) * 100

                    # print order info
                    print(f'Order Key: {orderKey}')
                    print(white(f'Order Price: {orderPrice}'))
                    print(f'Order Rate: {orderRate}%')
                    principalString = str(float(apiOrder["meta"]["principalAvailable"])/10**DECIMALS)
                    print(f'Order Amount: {principalString} nTokens')
                    print(f'Order Response: {orderResponse}\n')

                    # append the placed order to the list
                    newOrders.append(apiOrder)

                    # mark the order as "used"
                    usedOrderKeys.append(orderKey)    
                else:
                    # create and place the combined order
                    combinedOrder = new_order(PUBLIC_KEY, underlying=UNDERLYING, maturity=int(MATURITY), vault=True, exit=baseOrder['exit'], principal=int(combinedPrincipal), premium=int(combinedPremium), expiry=int(newExpiry))
                    signature = vendor.sign_order(combinedOrder, network, swivelAddress)
                    
                    orderResponse = limit_order(stringify(combinedOrder), signature, network)

                    combinedOrderPrice = float(combinedPremium) / float(combinedPrincipal)
                    combinedOrderKey = combinedOrder['key'].hex()

                    apiSuccess = False
                    while apiSuccess == False:
                        try:
                            apiOrder = order(combinedOrderKey, network)
                            apiSuccess = True
                        except:
                            print("Error: Failed to retrieve order from Swivel API")
                            print("Retrying in 30s...")
                            time.sleep(30)

                    # establish order typestring
                    orderExit = apiOrder['order']['exit']
                    if orderExit == True:
                        typeString = "Sell"
                    else:
                        typeString = "Buy"

                    orderRate = truncate((combinedOrderPrice * 31536000/timeDiff),6) * 100
                    # print order info
                    print(cyan('Placed Combined ' + typeString + ' Order:'))
                    print(f'Order Key: {combinedOrderKey}')
                    print(white(f'Order Price: {combinedOrderPrice}'))
                    print(f'Order Rate: {orderRate}%')
                    principalString = str(combinedPrincipal/10**DECIMALS)
                    print(f'Order Amount: {principalString} nTokens')
                    print(f'Order Response: {orderResponse}\n')

                    # mark the order as "used"
                    usedOrderKeys.append(baseOrderKey)   

                    # append the placed order to the list
                    newOrders.append(apiOrder)
        return (newOrders)

def adjustAndQueue(underlying, maturity, expiryLength, orders):

    queuedOrders = []
    queuedOrderSignatures = []

    apiSuccess = False
    while apiSuccess == False:
        try:
            newCompoundRate = underlying_compound_rate(underlying)
            apiSuccess = True
        except Exception as e:
            print('Error: Could not connect to Compound API')
            print('Retrying in 30s...')
            time.sleep(30)

    compoundRateDiff = truncate(((newCompoundRate - compoundRate) / compoundRate), 8)

    # establish the impact that time should make
    timeDiff = maturity - time.time()
    timeModifier = expiryLength / timeDiff
    newExpiry = float(time.time()) + expiryLength

    verb = ''
    print('Compound\'s Rate Has Changed:')
    if compoundRateDiff > 0:
        print(green(str(compoundRateDiff*100)+'%'))
        verb = 'increased'
        print(white('This change has ') + green(verb) + white(' nToken prices:'))
        print(green(str(truncate((float(compoundRateDiff)*100*float(COMPOUND_RATE_LEAN)),6))+'%')+ white(' based on your lean rate \n'))
    if compoundRateDiff < 0:
        print(red(str(compoundRateDiff*100)+'%'))
        verb = 'decreased'
        print(white('This change has ') + red(verb) + white(' nToken prices:'))
        print(red(str(truncate((float(compoundRateDiff)*100*float(COMPOUND_RATE_LEAN)),6))+'%')+ white(' based on your lean rate \n'))
    if compoundRateDiff == 0:
        print(yellow(str(compoundRateDiff*100)+'%'))
        print(white('This ') + yellow(str(truncate((float(compoundRateDiff)*100*float(COMPOUND_RATE_LEAN)),6))+'%') + white(' change does') + yellow(' not ') + white('impact nToken prices.\n'))

    
    print(str(expiryLength)+' seconds have passed since the last quote refresh.')
    print('This has' + red(' decreased ') + white('nToken prices:'))
    print(cyan(str(timeModifier*100)+'%\n'))

    time.sleep(5)

    # For every order in the provided range, check if it has been filled at all. If it has, place a reversed order at the same price (similar to uniswap v3)
    for i in range (0, len(orders)):
        orderKey = orders[i]['order']['key']

        apiSuccess = False
        while apiSuccess == False:
            try:
                returnedOrder = order(orderKey, network)
                apiSuccess = True
            except:
                print("Error: Failed to retrieve order from Swivel API")
                print("Retrying in 30s...")
                time.sleep(30)

        principalDiff = float(orders[i]['meta']['principalAvailable']) - float(returnedOrder['meta']['principalAvailable'])

        # determine if the order has been filled, and if it is large enough to queue again
        if returnedOrder['meta']['principalAvailable'] != orders[i]['meta']['principalAvailable'] and (principalDiff >= (float(orders[i]['order']['principal']) * .05)):

            # adjust for time difference
            price = float(orders[i]['meta']['price'])
            newPrice = price - (price * timeModifier)

            # adjust for changes in underlying compound rate
            compoundAdjustedImpact = newPrice * (COMPOUND_RATE_LEAN * compoundRateDiff)
            compoundAdjustedPrice = newPrice + compoundAdjustedImpact

            premiumDiff = principalDiff * compoundAdjustedPrice

            orderType = orders[i]['order']['exit']

            print(magenta('Reversing An Orders Filled Volume...'))

            # determine order type and create the new order
            if orderType == True:
                reversedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principalDiff), premium=int(premiumDiff), expiry=int(newExpiry))
                signature = vendor.sign_order(reversedOrder, network, swivelAddress)     
                reversedTypeString = 'Buy'
                typeString = 'Sell'
                print(green('Queued ('+reversedTypeString+') Order:'))

            else:
                reversedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principalDiff), premium=int(premiumDiff), expiry=int(newExpiry))
                signature = vendor.sign_order(reversedOrder, network, swivelAddress)    
                reversedTypeString = 'Sell' 
                typeString = 'Buy'
                print(red('Queued ('+reversedTypeString+') Order:'))

            # append the reversed order to the queue
            queuedOrders.append(reversedOrder)
            queuedOrderSignatures.append(signature)

            # print order info
            print(f'Order Key: {reversedOrder["key"].hex()}')
            print(white(f'Order Price: {compoundAdjustedPrice}'))
            principalString = str(principalDiff/10**DECIMALS)
            print(f'Order Amount: {principalString} nTokens\n')

            # if the order is completely filled (or 95% filled), ignore it, otherwise replace the remaining order volume
            if float(returnedOrder['meta']['principalAvailable']) <= (float(orders[i]['order']['principal']) * .05):
                pass
            else:
                # replace whatever volume has not been filled
                replacedPrincipal = float(returnedOrder['meta']['principalAvailable'])
                recplacedPremium = replacedPrincipal * compoundAdjustedPrice
                
                replacedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=orderType, principal=int(replacedPrincipal), premium=int(recplacedPremium), expiry=int(newExpiry))
                signature = vendor.sign_order(replacedOrder, network, swivelAddress)

                # append the replaced order to the queue
                queuedOrders.append(replacedOrder)
                queuedOrderSignatures.append(signature)

                # print order info
                print(cyan('Replacing An Orders Unfilled Volume...'))
                if orderType == True:
                    print(red('Queued (' + typeString + ') Order:'))
                else:
                    print(green('Queued (' + typeString + ') Order:'))

                print(f'Order Key: {replacedOrder["key"].hex()}')
                print(white(f'Order Price: {compoundAdjustedPrice}'))
                principalString = str(replacedPrincipal/10**DECIMALS)
                print(f'Order Amount: {principalString} nTokens\n')
                

        # if the order has not been filled, adjust for time difference and queue a new order at the same rate and principal
        else:
            # adjust for time difference
            price = float(orders[i]['meta']['price'])
            newPrice = price - (price * timeModifier)

            # adjust for changes in underlying compound rate
            compoundAdjustedImpact = newPrice * (COMPOUND_RATE_LEAN * compoundRateDiff)
            compoundAdjustedPrice = newPrice + compoundAdjustedImpact               

            # determine the new premium amount
            duplicatePrincipal = float(orders[i]['order']['principal'])
            duplicatePremium = duplicatePrincipal * compoundAdjustedPrice

            orderExit = orders[i]['order']['exit']

            # establish order typestring
            if orderExit == True:
                typeString = "Sell"
            else:
                typeString = "Buy"
            duplicateOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=orderExit, principal=int(duplicatePrincipal), premium=int(duplicatePremium), expiry=int(newExpiry))
            signature = vendor.sign_order(duplicateOrder, network, swivelAddress)

            # append the duplicate order to the queue
            queuedOrders.append(duplicateOrder)
            queuedOrderSignatures.append(signature)

            # print order info
            print(yellow('Queued duplicate (' + typeString + ') Order:'))
            print(f'Order Key: {duplicateOrder["key"].hex()}')
            print(white(f'Order Price: {compoundAdjustedPrice}'))
            principalString = str(duplicatePrincipal/10**DECIMALS)
            print(f'Order Amount: {principalString} nTokens\n')

    # print queued orders
    print(magenta('Queued Orders:'))
    for i in range(len(queuedOrders)):
        orderExit = queuedOrders[i]['exit']
        orderKey = "0x..." + queuedOrders[i]['key'].hex()[-4:]
        if orderExit == True:
            orderType = "Sell nTokens"
        else:
            orderType = "Buy nTokens"
        orderPrice = round(float(queuedOrders[i]['premium']) / float(queuedOrders[i]['principal']),6)
        orderNum = i+1
        print(white(f'{orderNum}. Type: {orderType}   Order Key: {orderKey}   Order Price: {orderPrice}'))
    print('')
    return (queuedOrders, queuedOrderSignatures, timeDiff, newExpiry)

def rangeMultiTickMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength):
    print('Current Time:')
    print(datetime.datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S\n'))
    newOrders = []
    queuedOrderSignatures = []
    queuedOrders = []

    if initializor == 0:
        initialPositionCreation(underlying, maturity, upperRate, lowerRate, amount, expiryLength)
    else:
        # store new compound rate and establish difference
        (queuedOrders, queuedOrderSignatures) = adjustAndQueue(underlying, maturity, expiryLength, orders)

        newOrders = combineAndPlace(queuedOrders,queuedOrderSignatures, timeDiff)
        return (newOrders)

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------Setup-------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------

provider = Web3.HTTPProvider("<YOUR_PROVIDER_KEY>") # Can be left blank. Orders can be created without a provider.
vendor = W3(provider, PUBLIC_KEY)

if NETWORK_STRING == "mainnet":
    network = 1
    swivelAddress = "0x3b983B701406010866bD68331aAed374fb9f50C9"
elif NETWORK_STRING == "rinkeby":
    network = 4
    swivelAddress = "0x4ccD4C002216f08218EdE1B13621faa80CecfC98"
else:
    print("Invalid network")
    exit(1)

#-----------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------Initialize------------------------------------------------------------ 
#-----------------------------------------------------------------------------------------------------------------------
start()
orders = []
initializor = 0

recoverString = input('Do you need to recover your orders from a crash? (y/n) : ').upper()
loop = True
while loop == True:

    print('Current Time:')
    print(datetime.datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S\n'))
    queuedOrders = []
    queuedOrderSignatures = []
    if recoverString == 'N':
        if initializor == 0:
            (orders) = initialPositionCreation(UNDERLYING, MATURITY, UPPER_RATE, LOWER_RATE, AMOUNT, EXPIRY_LENGTH)
            compoundRate = underlying_compound_rate(UNDERLYING)
        else:
            (queuedOrders, queuedOrderSignatures, timeDiff, newExpiry) = adjustAndQueue(UNDERLYING, MATURITY, EXPIRY_LENGTH, orders)

            orders = combineAndPlace(queuedOrders,queuedOrderSignatures, timeDiff, newExpiry)

        with open("orders/orders.json", "w", encoding="utf-8") as writeJsonfile:
            json.dump(orders, writeJsonfile, indent=4,default=str) 
        with open("orders/compound.json", "w", encoding="utf-8") as writeJsonfile:
            json.dump(compoundRate, writeJsonfile, indent=4,default=str) 
    else:
        try:
            orders = json.load(open('orders/orders.json'))
            compoundRate = json.load(open('orders/compound.json'))

            (queuedOrders, queuedOrderSignatures, timeDiff, newExpiry) = adjustAndQueue(UNDERLYING, MATURITY, EXPIRY_LENGTH, orders)

            orders = combineAndPlace(queuedOrders,queuedOrderSignatures, timeDiff, newExpiry)

            with open("orders/orders.json", "w", encoding="utf-8") as writeJsonfile:
                json.dump(orders, writeJsonfile, indent=4,default=str) 
            with open("orders/compound.json", "w", encoding="utf-8") as writeJsonfile:
                json.dump(compoundRate, writeJsonfile, indent=4,default=str)
        except:
            print('No orders to recover...')
            input('Press enter to exit...')
            exit(1)

    initializor += 1
    compoundRate = underlying_compound_rate(UNDERLYING)

    # sleep the expiry length
    countdownRuns = math.floor(EXPIRY_LENGTH/30)
    printsRemaining = countdownRuns
    # print time remaining for each countdown run
    for i in range (0, countdownRuns):
        timeRemaining = printsRemaining * 30
        printsRemaining = printsRemaining - 1
        print(cyan(f'{timeRemaining} Seconds Until Orders Are Refreshed...'))
        print(white(' '))
        time.sleep(30)
stop()