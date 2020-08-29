import json
import finnhub
from datetime import datetime
from time import gmtime, strftime

API_KEY = "bshlqpfrh5r9t1gn0q70"  #from website
DATA_FILE = r"D:\mockdata.json"  #local file to store info

finnhub_client = None


def init():
    global finnhub_client
    finnhub_client = finnhub.Client(api_key=API_KEY)
    #initialize API

def load_data():
    with open(DATA_FILE) as file:
        readfile = file.read()
    data = json.loads(readfile)
    return data
    #loads data from file into memory

def save_data(data):
    with open(DATA_FILE, "w") as file:
        file.write(json.dumps(data, indent=4))
    #dumps data from memory into file

def cash_count(delta, data):
    print(data)
    place = data["cash"]


    data["cash"] = place

    return data
    #useless

def update_log(ticker, count, data, action, price):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data["transaction_log"].append({"ticker": ticker, "action": action, "date": time, "count": count, "price": price})
    #updates transaction log in file

def get_price(ticker):

    quote = finnhub_client.quote(ticker)
    if quote == None or "c" not in quote:
        return None
    tickerPrice = quote["c"]
    return tickerPrice
    #gets the current price of the stock

def getProfit(data):
    for i in range(len(data["portfolio"])):
        current_price = get_price(data["portfolio"][i]["ticker"])
        pricePaid = data["portfolio"][i]["pricePaid"]
        count = data["portfolio"][i]["count"]
        profit = (current_price * count) - (pricePaid * count)
        data["portfolio"][i]["profit"] = round(profit, 2)
        save_data(data)
    return
    #gets the profit made on each stock holding

def buy(data):
    while True:
        ticker = input("Enter ticker symbol: ")
        ticker = ticker.strip()
        if ticker == "":
            return

        countStr = input("Enter number of shares to buy: ")
        try:
            count = int(countStr)
        except:
            print("Invalid count. Try again")
            continue
        if count <= 0:
            print("Invalid count. Try again")
            continue
        tickerPrice = get_price(ticker)
        if tickerPrice == None:
            print("Invalid symbol")
            continue
        totalValue = tickerPrice * count
        if data['cash'] < totalValue:
            print("You don't have enough money to make this transaction")
            print("Ticker price: %f. Total needed: %f" % (tickerPrice, totalValue))
            continue
        data['cash'] -= totalValue
        data['cash'] = round(data['cash'], 2)
        for ele in data["portfolio"]:
            if ele["ticker"] == ticker:
                ele["pricePaid"] = round(((ele["pricePaid"] * ele["count"]) + (tickerPrice * count)) / (ele["count"] + count), 2)
                ele["count"] += count
                break
        else:
            tickerData = {"ticker": ticker, "pricePaid": tickerPrice, "count": count, "totalPrice(holding)": round(count*tickerPrice, 2), "profit": 0}
            data["portfolio"].append(tickerData)

        confirm = input("You are about to buy {} shares of {} at {} per share. Do you wish to proceed? Enter 'y' to proceed: ".format(count, ticker, tickerPrice))
        if confirm == "y":
            update_log(ticker, count, data, "buy", tickerPrice)
            save_data(data)
            print("You have purchased {} shares of {} at {} per share".format(count, ticker, tickerPrice))
            print("You have ${} remaining".format(data["cash"]))
            return
        else:
            print("You have cancelled this purchase")
            return

    #allows the user to buy stock

def sell(data):
    while True:
        ticker = input("Enter ticker symbol: ")
        ticker = ticker.strip()
        if ticker == "":
            return
        for ele in data["portfolio"]:
            if ele["ticker"] == ticker:
                break
        else:
            print("You do not own this stock")
            continue
        countStr = input("Enter number of shares to sell: ")
        try:
            count = int(countStr)
        except:
            print("Invaild count. Try again")
            continue
        if count <= 0:
            print("Invalid count. Try again")
            continue
        shareCount = 0
        tickerPrice = get_price(ticker)

        if tickerPrice == None:
            print("Invalid symbol")
            continue
        totalValue = tickerPrice * count
        for i in range(len(data["portfolio"])):
            if data["portfolio"][i]["ticker"] == ticker:
                shareCount += data["portfolio"][i]["count"]
        if count > shareCount:
            print("You do not have that many shares")
            print("You only have {} shares".format(shareCount))
            continue
        data["cash"] += totalValue
        for i in range(len(data["portfolio"])):
            if data["portfolio"][i]["ticker"] == ticker:
                data["portfolio"][i]["count"] -= count
                if data["portfolio"][i]["count"] == 0:
                    data["portfolio"].remove(data["portfolio"][i])
        confirm = input(("You are about to sell {} shares of {} at {} per share. Do you wish to proceed? Enter 'y' to proceed: ".format(count, ticker, tickerPrice)))
        if confirm == "y":
            update_log(ticker, count, data, "sell", tickerPrice)
            save_data(data)
            print("You have sold {} shares of {} at {} per share".format(count, ticker, tickerPrice))
            print("Account value: {}".format(round(data["cash"], 2)))
            return
        else:
            print("You have cancelled this sale")
            return

    #allows user to sell stock



init()
data = load_data()

getProfit(data)
#gets the profit, initializes client, loads data into memory

print(("commands: 'buy', 'sell', 'log', 'balance', 'portfolio'"))

def main_menu():
    portfolioValue = 0
    while True:
        user_action = input("What do you want to do? ")
        if user_action == "":
            continue
        user_action.strip()
        if user_action == "":
            break
        if user_action == "buy":
            print("You have ${}".format(round(data["cash"], 2)))
            buy(data)

        elif user_action == "sell":
            print("Your holdings: ")
            for ele in data["portfolio"]:
                print(ele)
            sell(data)

        elif user_action == "log":
            print("Transaction Log: ")
            for ele in data["transaction_log"]:
                print(ele)

        elif user_action == "balance":
            print("You have ${}".format(data["cash"]))

        elif user_action == "portfolio":
            print("Your holdings: ")
            for ele in data["portfolio"]:
                portfolioValue += ele["totalPrice(holding)"]
                print(ele)
            portfolioValue = round(portfolioValue, 2)
            print("Portfolio Value: {}".format(portfolioValue))


        else:
            print("That command is not recognized")

main_menu()

#creates the main menu




