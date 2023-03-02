# Oanda-Bot（Wavenauts）の取引指標を計算するモジュール

## いつ使いますか？

Oanda-Bot(Wavenauts)の取引指標を計算したいときに```./main.py```を実行して下さい。

```bash
python ./main.py
```

## 何をしてくれますか？

以下を計算し、JSON形式で呼び出し元に返します。全てのフィールドはfloatです。

- TotalProf: 総利益
- Count: 取引数
- WinRate: 勝率
- ProfitPerTrade: 1取引当たり利益
- LongInfo: ロング情報
- ShortInfo: ショート情報
- DrawDown: ドローダウン
- ProfitFactor: プロフィット・ファクター
- RecoveryFactor: リアカバリ・ファクター