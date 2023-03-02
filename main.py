import oanda
import datetime
import sys
import json
import math
import pathlib

# **************************************:
# 初回取引時間
# 1670424900 -> 2022-12-07 23:55:00
# 初回クローズの取引ID：993
# ***************************************
START_UNIX = 1670424900
START_ID = "1002"
INIT_BALANCE = 250000
# tradeの型
#   'averageClosePrice': '136.345',
#   'closeTime': '2022-12-07T17:25:00.761756231Z',
#   'closingTransactionIDs': ['995'],
#   'currentUnits': '0',
#   'dividendAdjustment': '0.0000',
#   'id': '993',
#   'initialMarginRequired': '54716.4000',
#   'initialUnits': '10000',
#   'instrument': 'USD_JPY',
#   'openTime': '2022-12-07T15:05:00.839219973Z',
#   'price': '136.795',
#   'realizedPL': '-4500.0000',
#   'state': 'CLOSED'}]


def to_micro(dstr: str) -> int:
    dstr_micro = dstr[:-4] + "Z"
    dobj = datetime.datetime.strptime(
        dstr_micro, "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp = int(datetime.datetime.timestamp(dobj))
    return timestamp


def to_balance(pls):
    """[取引履歴、取引履歴、・・・]を残高の推移に変換する。drawdownの計算で使う。
    """
    balance = INIT_BALANCE
    ret = []
    for pl in pls:
        balance += pl
        ret.append(balance)
    return ret


def close_trades():
    """START_IDより新しい全てのCLOSE取引データを抽出する
    """
    # 最新データが[0]、ふ類のが最後。最大500データ。
    res_data = oanda.trades(conf, "USD_JPY")
    closed = res_data["trades"]

    lastId = closed[-1]["id"]
    cnt = 0

    # APIで取得できる取引データが500件がMAXのため、初回IDより前になるまでAPIを実行し続ける。
    # 1か月で約88件だったので、2023-05くらいに超える？
    while int(lastId) >= int(START_ID):
        print(f"lastId:{lastId} has not reached startId:{START_ID}. Looping.")
        prev_data = oanda.trades(conf, "USD_JPY", befID=lastId)
        prev_closed = prev_data["trades"]
        # データ連結
        closed += prev_closed
        # カウンター更新
        cnt += 1
        # 最後の取引IDを更新
        lastId = prev_closed[-1]["id"]

    # 500はAPIの最大データ抽出数。初回取引より前のデータは落とす
    for i, trade in enumerate(closed, 500 * cnt):
        if int(trade["id"]) < int(START_ID):
            closed = closed[:i]

    return closed


def totalPL(trades):
    return sum([float(t["realizedPL"]) for t in trades])


def drawdown(trades):
    """最大の下落額を返す。最小値から左側、最大値の右側それぞれについて、
    最大値-最小値を計算し、より額が大きい方を返す。

    Args:
        trades (_type_): _description_

    Returns:
        _type_: _description_
    """

    pls = [float(trade["realizedPL"]) for trade in trades]
    bls = to_balance(pls)
    # 最小値とそのインデックス
    worst_value = min(bls)
    worst_index = bls.index(worst_value)

    # 最小値の左側で最大値-最小値を計算
    left_targ = bls[:worst_index] + [INIT_BALANCE]
    left_best = max(left_targ)
    dd1 = left_best - worst_value

    # 最大値の右側で最大値-最小値を計算
    best_value = max(bls)
    best_index = bls.index(best_value)
    right_targ = bls[best_index:]
    right_worst = min(right_targ)
    dd2 = best_value - right_worst

    # 下落幅が大きい方を返す。
    if dd1 > dd2:
        return dd1
    return dd2


def profit_factor(trades):
    prof = 0.0
    loss = 0.0
    for trade in trades:
        pl = float(trade["realizedPL"])
        if pl > 0:
            prof += pl
        else:
            loss += pl
    ret = prof / abs(loss)
    # 小数点第三以下切り捨て
    return math.floor(ret*1000)/1000


def recovery_factor(trades):
    tpl = totalPL(trades)
    dd = drawdown(trades)
    ret = tpl/dd
    return math.floor(ret*1000)/1000


def profit_per_trade(trades) -> float:
    count = trade_count(trades)
    pl = totalPL(trades)
    ret = pl/count
    return math.floor(ret*1000)/1000


def trade_count(trades):
    return len(trades)


def long_info(trades):
    long = [trade for trade in trades if int(trade["initialUnits"]) > 0]
    count = trade_count(long)
    pl = totalPL(long)
    return {"count": count, "pl": pl}


def short_info(trades):
    short = [trade for trade in trades if int(trade["initialUnits"]) < 0]
    count = trade_count(short)
    pl = totalPL(short)
    return {"count": count, "pl": pl}


def win_rate(trades) -> float:
    count = trade_count(trades)
    wins = 0
    for trade in trades:
        if float(trade["realizedPL"]) > 0:
            wins += 1
    ret = wins/count
    return math.floor(ret*1000)/1000


# このプロジェクトのルートディレクトリ
root = pathlib.Path(__file__).parent
# confファイルのパス
conf_path = root / "key.json"

conf = oanda.load_key(conf_path)
data = close_trades()

evaluation = {
    "TotalPL": totalPL(data),
    "Count": trade_count(data),
    "WinRate": win_rate(data),
    "ProfitPerTrade": profit_per_trade(data),
    "LongInfo": long_info(data),
    "ShortInfo": short_info(data),
    "DrawDown": drawdown(data),
    "ProfitFactor": profit_factor(data),
    "RecoveryFactor": recovery_factor(data)
}

eval_json = json.dumps(evaluation)
sys.exit(eval_json)

# print(totalPL(data))
# print(trade_count(data))
# print(win_rate(data))
# print(profit_per_trade(data))
# print(long_info(data))
# print(short_info(data))
# print(drawdown(data))
# print(profit_factor(data))
# print(drawdown(data))
# print(recovery_factor(data))
