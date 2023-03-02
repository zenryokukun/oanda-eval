# Oanda-Bot（Wavenauts）の取引指標を計算するスクリプト

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

## 備考

**sys.exit(JSONString)**でexitするため、status codeは0（正常）以外になります。stderrのほうに
出力される場合もあるので、実行環境や呼び出し元の機能を確認してください。

将来的に**print(JSONString)**として、呼び出し元でstdoutを拾うやり方に変える可能性があります。