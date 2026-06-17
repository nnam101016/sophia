import requests
from config import GMGN_CONFIG

def analyze_token_traders(token_address, sort_by="entry_mc"):

    url = f"https://gmgn.ai/vas/api/v1/token_traders/sol/{token_address}"

    params = {
        **GMGN_CONFIG,
        "from_app": "gmgn",
        "app_ver": "20260611-977-e17d61d",
        "tz_name": "Asia/Bangkok",
        "tz_offset": 25200,
        "app_lang": "en-US",
        "os": "web",
        "worker": 0,
        "limit": 100,
        "orderby": "profit",
        "direction": "desc"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://gmgn.ai/",
        "Origin": "https://gmgn.ai"
    }

    r = requests.get(url, params=params, headers=headers, timeout=20)

    print("GMGN STATUS:", r.status_code)
    print("GMGN RESPONSE:", r.text[:300])

    if r.status_code != 200:
        raise Exception(f"GMGN blocked request: {r.status_code}")

    try:
        data = r.json()
    except Exception:
        raise Exception("GMGN did not return JSON")

    wallets = data.get("data", {}).get("list", [])



    def get_sort_value(w):

        if sort_by == "entry_mc":
            return w.get("avg_cost") or 0

        return w.get("realized_pnl") or 0



    wallets_sorted = sorted(
        wallets,
        key=get_sort_value,
        reverse=True
    )



    results = []


    for i, w in enumerate(wallets_sorted, 1):


        entry_mc = (
            w.get("avg_cost") or 0
        ) * 1e9


        exit_mc = (
            w.get("avg_sold") or 0
        ) * 1e9


        pnl_usd = (
            w.get("profit") or 0
        )


        pnl_pct = (
            w.get("realized_pnl") or 0
        ) * 100


        buy_txs = (
            w.get("buy_tx_count_cur") or 0
        )


        sell_txs = (
            w.get("sell_tx_count_cur") or 0
        )


        buy_vol = (
            w.get("buy_volume_cur") or 0
        )


        sell_vol = (
            w.get("sell_volume_cur") or 0
        )



        # keep terminal debug

        print(
            f"[{i}] {w['address']} "
            f"MC: ${entry_mc/1000:.1f}K -> "
            f"{f'${exit_mc/1000:.1f}K' if exit_mc else 'HOLD'} "
            f"PNL: ${pnl_usd:,.0f} ({pnl_pct:.1f}%)"
            f" || "
            f"{buy_txs} - {sell_txs} "
            f"(${buy_vol:,.0f} - ${sell_vol:,.0f})"
        )



        results.append(
            {

            "rank": i,

            "address":
            w["address"],

            "gmgn":
            f"https://gmgn.ai/sol/address/{w['address']}",

            "entry_mc":
            entry_mc,

            "exit_mc":
            exit_mc,

            "pnl":
            pnl_usd,

            "pnl_percent":
            pnl_pct,

            "buy_txs":
            buy_txs,

            "sell_txs":
            sell_txs,

            "buy_volume":
            buy_vol,

            "sell_volume":
            sell_vol

            }
        )


    return {
        "token": token_address,
        "count": len(results),
        "wallets": results
    }