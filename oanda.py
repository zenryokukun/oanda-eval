import json
import requests

# 本番 URL
LIVE_URL = "https://api-fxtrade.oanda.com"

# fpath:str -- key.jsonのパス
# Returns -> {"id":str,"key":str}


def load_key(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


# api_key:string -- apiトークン
# Returns -> {"Content-Type":string,"Authorization":string}
def default_header(api_key):
    return {
        "Content-Type": "application/json",
        # Bearerの後に半角スペースが必要です
        "Authorization": "Bearer " + api_key
    }


# conf (dict): key.jsonを読み取ったもの
# # pair (stsr): "USD_JPY","EUR_USD"等
def position(conf, pair):
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/positions/{pair}"
    header = default_header(conf["key"])
    res = requests.get(url, headers=header)
    return res.json()


# conf (dict): key.jsonを読み取ったもの
def account(conf):
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}"
    header = default_header(conf["key"])
    res = requests.get(url, headers=header)
    return res.json()


# conf (dict): key.jsonを読み取ったもの
def account_summary(conf):
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/summary"
    header = default_header(conf["key"])
    res = requests.get(url, headers=header)
    return res.json()


def get_orders(conf, pair, state="FILLED", count=500, befID=None):
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/orders"
    header = default_header(conf["key"])
    param = {
        "instrument": pair,
        "state": state,
        "count": count,
    }
    if befID:
        param["beforeID"] = befID

    res = requests.get(url, headers=header, params=param)
    return res.json()


def trades(conf, pair, state="CLOSED", count=500, befID=None):
    """
    取引データを抽出する。befIDを指定した場合、
    そのIDより前のデータが抽出される（指定したIDは含まれない）

    Args:
        conf (dict): _description_
        pair (string): USD_JPY,EUR_USD等
        state (str, optional): Defaults to "CLOSED".
        count (int, optional): Defaults to 500.
        befID (_type_, optional): Defaults to None.

    Returns:
        _type_: _description_
    """
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/trades"
    header = default_header(conf["key"])
    param = {
        "state": state,
        "instrument": pair,
        "count": count,
    }
    if befID:
        param["beforeID"] = befID
    res = requests.get(url, headers=header, params=param)
    return res.json()


def pending_orders(conf):
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/pendingOrders"
    header = default_header(conf["key"])
    res = requests.get(url, headers=header)
    return res.json()


def cancel_order(conf, specifier):
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/orders/{specifier}/cancel"
    header = default_header(conf["key"])
    res = requests.put(url, headers=header)
    return res.json()


def _base_order(
        conf, pair, units, price, order_type,
        tif="GTC", gtd_time=None,
        takeProfitOnFill=None, stopLossOnFill=None,
        trailingStopLossOnFill=None):

    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/orders"
    header = default_header(conf["key"])
    param = {
        "order": {
            "type": order_type,
            "instrument": pair,
            "units": units,
            "price": price,
            "timeInForce": tif,
        }
    }
    if takeProfitOnFill:
        param["order"]["takeProfitOnFill"] = takeProfitOnFill
    if stopLossOnFill:
        param["order"]["stopLossOnFill"] = stopLossOnFill
    if gtd_time:
        param["order"]["gtdTime"] = gtd_time
    # trailingStopLossを追加
    if trailingStopLossOnFill:
        param["order"]["trailingStopLossOnFill"] = trailingStopLossOnFill

    res = requests.post(url, headers=header, json=param)
    return res.json()


# 指値注文
def limit_order(conf, pair, units, price, tif="GTC", gtd_time=None,
                takeProfitOnFill=None, stopLossOnFill=None,
                trailingStopLossOnFill=None):
    return _base_order(conf, pair, units, price,
                       "LIMIT", tif, gtd_time,
                       takeProfitOnFill, stopLossOnFill,
                       trailingStopLossOnFill)


# 逆指値注文（STOP注文）
def stop_order(conf, pair, units, price, tif="GTC", gtd_time=None,
               takeProfOnFill=None, stopLossOnFill=None,
               trailingStopLossOnFill=None):
    return _base_order(conf, pair, units, price,
                       "STOP", tif, gtd_time,
                       takeProfOnFill, stopLossOnFill,
                       trailingStopLossOnFill)


# stopLoss,takeProfパラメタ用のdictを生成する関数[distance版]
def ifd_prm_dist(distance, tif="GTC", gtd_time=None):
    prm = {"distance": distance, "timeInForce": tif, }
    if gtd_time:
        prm["gtdTime"] = gtd_time
    return prm


# stopLoss,takeProfパラメタ用のdictを生成する関数[price版]
def ifd_prm(price, tif="GTC", gtd_time=None):
    prm = {"price": price, "timeInForce": tif, }
    if gtd_time:
        prm["gtdTime"] = gtd_time
    return prm


# 利確注文
def take_profit_order(conf, trade_id, price, tif="GTC", gtd_time=None):
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/orders"
    header = default_header(conf["key"])

    param = {
        "order": {
            "type": "TAKE_PROFIT",
            "tradeID": trade_id,
            "price": price,
            "timeInForce": tif,
        }
    }
    if gtd_time:
        param["order"]["gtdTime"] = gtd_time

    res = requests.post(url, headers=header, json=param)
    return res.json()


# 損切注文
def stop_loss_order(conf, trade_id, price, tif="GTC", gtd_time=None):
    account_id = conf["id"]
    url = LIVE_URL + f"/v3/accounts/{account_id}/orders"
    header = default_header(conf["key"])

    param = {
        "order": {
            "type": "STOP_LOSS",
            "tradeID": trade_id,
            "price": price,
            "timeInForce": tif,
        }
    }
    if gtd_time:
        param["order"]["gtdTime"] = gtd_time

    res = requests.post(url, headers=header, json=param)
    return res.json()


# 口座IDとapi-keyをファイルから取得
# conf = load_key("./key.json")
# **************************************************************************
# trailing_stop_order
# **************************************************************************
# trailStopOrder
# trail = ifd_prm_dist("0.2")
# res = stop_order(conf, "USD_JPY", 1000, "131", trailingStopLossOnFill=trail)
# pprint(res)
# **************************************************************************
# stop_loss_order,take_profit_order
# **************************************************************************
# tpo = take_profit_order(conf, "1411", 1.06)
# slo = stop_loss_order(conf, "1411", 1.07)

# pprint(tpo)
# pprint(slo)

# **************************************************************************
# IFD-OCO priceでのテスト
# **************************************************************************
# ifd-oco 「EUR_USDが1.06まで下がったら10units買い。1.08まで上がったら、利確、1.04まで下がったら損切」
# take_prof = ifd_prm("1.080")
# stop_loss = ifd_prm("1.06")
# res = limit_order(conf, "EUR_USD", 10, "1.0683",
#                   takeProfitOnFill=take_prof, stopLossOnFill=stop_loss)
# pprint(res)

# **************************************************************************
# IFD-OCO distanceでのテスト
# **************************************************************************
# take_prof = ifd_prm("1.065")
# stop_loss = ifd_prm("1.055")
# res = limit_order(conf, "EUR_USD", 10, "1.06",
#                   takeProfitOnFill=take_prof, stopLossOnFill=stop_loss)
# pprint(res)


# pend = pending_orders(conf)
# pprint(pend)

# 指値注文。
# limit_res = limit_order(conf, "EUR_USD", -10, "1.0750")

# ストップ注文
# stop_res = stop_order(conf, "EUR_USD", -10, "1.0150")

# pprint(limit_res, indent=1)
# pprint(stop_res, indent=1)

# pprint(pending_orders(conf))

# tp = take_profit_order(conf, "1225", "135")
# # pprint(tp)

# sp = stop_loss_order(conf, "1258", "1.0645")
# pprint(sp)

# co = cancel_order(conf, 1527)
# pprint(co)
