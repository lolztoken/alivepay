import pandas as pd
from hiveengine.api import Api
from hiveengine.tokenobject import Token
import datetime

api = Api(url = "https://engine.rishipanthee.com/")

token = str("ALIVEM")
getHolders = str("zombiepatrol,aliveprojects,youarealive,alive.chat,aliveandthriving,iamalivechalleng,wearealive,null")
payToken = str("AWESOME")
payAmount = float(0.043)
payMemo = str("Daily payout based on your ALIVEM stake.")

holders = api.find_all("tokens", "balances", query = {"symbol": token})

df = pd.DataFrame(holders)
df.drop(columns = ["_id", "balance", "pendingUnstake", "delegationsIn"], inplace = True)

df["pendingUndelegations"] = df["pendingUndelegations"].astype(float)
df["stake"] = df["stake"].astype(float)
df["delegationsOut"] = df["delegationsOut"].astype(float)

df = df.assign(ownedStake = df.sum(axis = 1, numeric_only = True))

tk = Token(token, api = api)
tokenInfo = tk.get_info()
decNum = tokenInfo["precision"]
df["ownedStake"] = df["ownedStake"].round(decNum)

df.drop(columns = ["symbol", "stake", "delegationsOut", "pendingUndelegations"], inplace = True)

df.sort_values(by=["ownedStake"], inplace = True, ascending = False)

dropHolders = getHolders.split(',')
while len(dropHolders) >= 1:
  indexHolder = df[df["account"] == dropHolders[0]].index
  df.drop(indexHolder, inplace = True)
  print("Successfully removed: ", dropHolders[0])
  del dropHolders[0]

ptk = Token(payToken, api = api)
payTokenInfo = ptk.get_info()
payDec = payTokenInfo["precision"]

sumStake = float(df["ownedStake"].sum())

df = df.assign(amount = (payAmount * (df.sum(axis = 1, numeric_only = True) / sumStake)))
df["amount"] = df["amount"].astype(float)
indexZero2 = df[df["amount"] < 0.00000001].index
df.drop(indexZero2, inplace = True)
df["amount"] = df["amount"].round(payDec)

sumAmount = df["amount"].sum().round(payDec)
print("Sum payout: ", sumAmount, payToken)
df["amount"] = df["amount"].astype(str)

df = df.assign(symbol = payToken)
df = df.assign(memo = payMemo)

df.drop(columns = ["ownedStake"], inplace = True)

now = datetime.datetime.now()
month = now.strftime("%b")
day = now.strftime("%d")
year = now.strftime("%y")
fileName = payToken + "-" + month + day + year + ".csv"
print("File name: ", fileName)

path = r"~/alivepay/pay/"

df.to_csv(path+fileName, index = False)
