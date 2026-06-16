import asyncio
import aiohttp
import itertools
import json
from collections import defaultdict
from datetime import datetime, timedelta
from config import GMGN_CONFIG, HELIUS_API_KEY

# =========================================================
# CONFIG
# =========================================================

HELIUS_KEY = HELIUS_API_KEY

BASE_URL = "https://api.helius.xyz/v0"

TARGET_TOKEN = "DXpEvktt2Wc7AaKcb3ReLEE3SrTkT2bJPgBqbWjBAGS"

# your wallet identity file
IDENTITY_FILE = r"C:\Users\thang\Desktop\send_Q.txt"

# =========================================================
# SETTINGS
# =========================================================

TOP_WALLETS = 100

TX_LIMIT = 100

RECENT_UNIQUE_TOKENS = 10

MIN_SEQUENCE_LENGTH = 3

MIN_SHARED_TOKENS = 5

CONCURRENT_REQUESTS = 10

# =========================================================
# EXCLUDED TOKENS
# =========================================================

EXCLUDED_TOKENS = {

    # SOL
    "So11111111111111111111111111111111111111112",

    # USDC
    "EPjFWdd5AufqSSqeM2qN1xzyb5pC8G4wEGGkZwyTDt1v",

    # USDT
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",

    # JUP
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",  

    # USDC
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
}

# =========================================================
# BOT LABELS
# =========================================================

BOT_LABELS = {

    "Axiom": [
        "axiom",
    ],

    "Photon": [
        "photon",
    ],

    "BonkBot": [
        "bonkbot",
        "bonk"
    ],

    "Padre": [
        "padre",
    ],

    "Trojan": [
        "trojan",
    ],

    "BullX": [
        "bullx",
    ]
}

# =========================================================
# CONCURRENCY
# =========================================================

sem = asyncio.Semaphore(CONCURRENT_REQUESTS)

# =========================================================
# LOAD IDENTITIES
# =========================================================

def load_wallet_identities():

    try:

        with open(IDENTITY_FILE, "r", encoding="utf-8") as f:

            data = json.load(f)

        mapping = {}

        for item in data:

            wallet = item.get("trackedWalletAddress")
            name = item.get("name")

            if wallet and name:

                mapping[wallet] = {
                    "name": name,
                    "emoji": item.get("emoji", ""),
                    "groups": item.get("groups", [])
                }

        print(f"\nLoaded {len(mapping)} wallet identities.")

        return mapping

    except Exception as e:

        print(f"\nFailed to load identity file: {e}")

        return {}

# =========================================================
# GENERIC GET
# =========================================================

async def fetch_json(session, url):

    async with sem:

        try:

            await asyncio.sleep(0.05)

            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:

                if resp.status != 200:

                    print(f"HTTP {resp.status}: {url}")

                    return None

                return await resp.json()

        except Exception as e:

            print(f"REQUEST FAILED: {e}")

            return None

# =========================================================
# FORMAT TIMESTAMP
# =========================================================

def format_timestamp(ts):

    if not ts:
        return "Unknown"

    try:

        dt = datetime.utcfromtimestamp(ts)

        # convert to GMT+7
        dt = dt + timedelta(hours=7)

        return dt.strftime("%Y-%m-%d %H:%M:%S GMT+7")

    except:

        return str(ts)

# =========================================================
# FETCH TOP HOLDERS
# =========================================================

async def get_top_holders(session, mint):

    holders = {}

    cursor = None

    page = 1

    while True:

        print(f"Fetching holder page {page}...")

        url = (
            f"https://mainnet.helius-rpc.com/"
            f"?api-key={HELIUS_KEY}"
        )

        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getTokenAccounts",
            "params": {
                "mint": mint,
                "limit": 1000,
                **({"cursor": cursor} if cursor else {})
            }
        }

        try:

            async with session.post(url, json=payload) as resp:

                data = await resp.json()

        except Exception as e:

            print(e)

            break

        result = data.get("result")

        if not result:
            break

        accounts = result.get(
            "token_accounts",
            []
        )

        if not accounts:
            break

        for acct in accounts:

            owner = acct.get("owner")

            amount = int(
                acct.get("amount", 0)
            )

            if owner:

                holders[owner] = (
                    holders.get(owner, 0)
                    + amount
                )

        cursor = result.get("cursor")

        if not cursor:
            break

        page += 1

    sorted_wallets = sorted(
        holders.items(),
        key=lambda x: x[1],
        reverse=True
    )

    wallets = [
        w
        for w, _ in sorted_wallets[:TOP_WALLETS]
    ]

    print(f"\nCollected {len(wallets)} wallets.")

    return wallets

# =========================================================
# DETECT BOT
# =========================================================

def detect_bot(tx):

    text_blob = json.dumps(tx).lower()

    for bot_name, keywords in BOT_LABELS.items():

        for keyword in keywords:

            if keyword in text_blob:
                return bot_name

    return "Unknown"

# =========================================================
# FETCH PARSED HISTORY
# =========================================================

async def get_wallet_sequence(session, wallet):

    url = (
        f"{BASE_URL}/addresses/"
        f"{wallet}/transactions"
        f"?api-key={HELIUS_KEY}"
        f"&limit={TX_LIMIT}"
    )

    txs = await fetch_json(session, url)

    if not txs:
        return {
            "sequence": [],
            "bot": "Unknown",
            "entries": {}
        }

    sequence = []

    entries = {}

    detected_bot = "Unknown"

    for tx in txs:

        try:

            # ---------------------------------------------
            # BOT DETECTION
            # ---------------------------------------------

            if detected_bot == "Unknown":

                detected_bot = detect_bot(tx)

            # ---------------------------------------------
            # TIMESTAMP
            # ---------------------------------------------

            timestamp = tx.get("timestamp")

            # ---------------------------------------------
            # TOKEN TRANSFERS
            # ---------------------------------------------

            token_transfers = tx.get(
                "tokenTransfers",
                []
            )

            for transfer in token_transfers:

                mint = transfer.get("mint")

                if not mint:
                    continue

                if mint in EXCLUDED_TOKENS:
                    continue

                if mint not in sequence:

                    sequence.append(mint)

                    entries[mint] = {
                        "timestamp": timestamp,
                        "signature": tx.get("signature")
                    }

            # ---------------------------------------------
            # SWAP EVENTS
            # ---------------------------------------------

            events = tx.get("events", {})

            swap = events.get("swap")

            if swap:

                token_inputs = swap.get(
                    "tokenInputs",
                    []
                )

                token_outputs = swap.get(
                    "tokenOutputs",
                    []
                )

                for item in (
                    token_inputs + token_outputs
                ):

                    mint = item.get("mint")

                    if not mint:
                        continue

                    if mint in EXCLUDED_TOKENS:
                        continue

                    if mint not in sequence:

                        sequence.append(mint)

                        entries[mint] = {
                            "timestamp": timestamp,
                            "signature": tx.get("signature")
                        }

            if len(sequence) >= RECENT_UNIQUE_TOKENS:

                break

        except:
            continue

    return {
        "sequence": sequence[:RECENT_UNIQUE_TOKENS],
        "bot": detected_bot,
        "entries": entries
    }

# =========================================================
# BUILD GRAPH
# =========================================================

def build_graph(wallet_sequences):

    graph = defaultdict(set)

    wallets = list(wallet_sequences.keys())

    total_pairs = (
        len(wallets)
        * (len(wallets) - 1)
        // 2
    )

    checked = 0

    for w1, w2 in itertools.combinations(wallets, 2):

        checked += 1

        if checked % 5000 == 0:

            print(
                f"Compared "
                f"{checked}/{total_pairs}"
            )

        seq1 = set(wallet_sequences[w1]["sequence"])

        seq2 = set(wallet_sequences[w2]["sequence"])

        shared = seq1 & seq2

        if len(shared) >= MIN_SHARED_TOKENS:

            graph[w1].add(w2)
            graph[w2].add(w1)

            print("\nMATCH FOUND")
            print("-" * 50)

            print(f"Wallet A: {w1}")
            print(f"Wallet B: {w2}")

            print(f"\nShared ({len(shared)}):")

            for token in shared:
                print(f"  - {token}")

    return graph

# =========================================================
# FIND CLUSTERS
# =========================================================

def find_clusters(graph):

    visited = set()

    clusters = []

    for wallet in graph:

        if wallet in visited:
            continue

        cluster = set()

        stack = [wallet]

        while stack:

            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)

            cluster.add(current)

            for neighbor in graph[current]:

                if neighbor not in visited:
                    stack.append(neighbor)

        clusters.append(cluster)

    return clusters

# =========================================================
# MAIN
# =========================================================

async def main():

    identity_map = load_wallet_identities()

    async with aiohttp.ClientSession() as session:

        print("\nFetching holders...\n")

        holders = await get_top_holders(
            session,
            TARGET_TOKEN
        )

        print("\nFetching wallet behavior...\n")

        tasks = [
            get_wallet_sequence(session, w)
            for w in holders
        ]

        sequences = await asyncio.gather(*tasks)

        wallet_sequences = {}

        for wallet, data in zip(holders, sequences):

            seq = data["sequence"]

            if len(seq) >= MIN_SEQUENCE_LENGTH:

                wallet_sequences[wallet] = data

        # =====================================================
        # DEBUG OUTPUT
        # =====================================================

        print("\n" + "=" * 70)
        print("WALLET SEQUENCES")
        print("=" * 70)

        for i, (wallet, data) in enumerate(
            wallet_sequences.items(),
            1
        ):

            seq = data["sequence"]

            # -------------------------------------------------
            # WALLET DISPLAY
            # -------------------------------------------------

            if wallet in identity_map:

                info = identity_map[wallet]

                wallet_display = (
                    f"{wallet} "
                    f"({info.get('emoji', '')} "
                    f"{info.get('name', '')})"
                )

            else:

                wallet_display = wallet

            print(f"\n[{i}] {wallet_display}")

            print(
                f"GMGN: https://gmgn.ai/sol/address/{wallet}"
            )

            print(f"BOT: {data['bot']}")

            print(f"SEQUENCE LENGTH: {len(seq)}")

            for token in seq:

                print(f"  - {token}")

                entry = data["entries"].get(token)

                if entry:

                    print(
                        f"    ENTRY TX: "
                        f"{entry['signature']}"
                    )

                    print(
                        f"    ENTRY TIME: "
                        f"{format_timestamp(entry['timestamp'])}"
                    )

        # =====================================================
        # BUILD GRAPH
        # =====================================================

        print("\nBuilding graph...\n")

        graph = build_graph(wallet_sequences)

        # =====================================================
        # FIND CLUSTERS
        # =====================================================

        print("\nFinding clusters...\n")

        clusters = find_clusters(graph)

        clusters.sort(
            key=lambda x: len(x),
            reverse=True
        )

        # =====================================================
        # OUTPUT
        # =====================================================

        print("\n" + "=" * 70)
        print("CLUSTERS")
        print("=" * 70)

        cluster_count = 0

        for cluster in clusters:

            if len(cluster) <= 1:
                continue

            cluster_count += 1

            print(f"\nCLUSTER #{cluster_count}")
            print(f"SIZE: {len(cluster)}")

            print("-" * 50)

            token_frequency = defaultdict(int)

            for wallet in cluster:

                for token in wallet_sequences[wallet]["sequence"]:

                    token_frequency[token] += 1

            common = sorted(
                token_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )

            print("\nShared Narrative Tokens:")

            for token, freq in common[:15]:

                print(f"  {token} ({freq})")

            bots = defaultdict(int)

            for wallet in cluster:

                bot = wallet_sequences[wallet]["bot"]

                bots[bot] += 1

            dominant_bot = max(
                bots.items(),
                key=lambda x: x[1]
            )[0]

            wr_scores = []

            for wallet in cluster:

                seq_len = len(
                    wallet_sequences[wallet]["sequence"]
                )

                wr_scores.append(
                    min(100, seq_len * 10)
                )

            cluster_wr = round(
                sum(wr_scores) / len(wr_scores),
                2
            )

            print(f"\nDOMINANT BOT: {dominant_bot}")
            print(f"EST WR: {cluster_wr}%")

            print("\nWallets:\n")

            for wallet in cluster:

                data = wallet_sequences[wallet]

                # -------------------------------------------------
                # WALLET + IDENTITY
                # -------------------------------------------------

                if wallet in identity_map:

                    info = identity_map[wallet]

                    wallet_display = (
                        f"{wallet} "
                        f"({info.get('emoji', '')} "
                        f"{info.get('name', '')})"
                    )

                else:

                    wallet_display = wallet

                print(wallet_display)

                print(
                    f"GMGN: "
                    f"https://gmgn.ai/sol/address/{wallet}"
                )

                print(f"BOT: {data['bot']}")

                wallet_wr = min(
                    100,
                    len(data["sequence"]) * 10
                )

                print(f"WR: {wallet_wr}%")

                print()

            print("=" * 70)
            print(f"TOTAL CLUSTERS: {cluster_count}")
            print("=" * 70)



            # =========================================================
            # API OUTPUT
            # =========================================================

            api_clusters = []


            cluster_index = 0


            for cluster in clusters:

                if len(cluster) <= 1:
                    continue


                cluster_index += 1


                # shared tokens

                token_frequency = defaultdict(int)


                for wallet in cluster:

                    for token in wallet_sequences[wallet]["sequence"]:

                        token_frequency[token] += 1



                shared_tokens = []


                for token, freq in sorted(
                    token_frequency.items(),
                    key=lambda x:x[1],
                    reverse=True
                )[:15]:

                    shared_tokens.append(
                        {
                            "address": token,
                            "count": freq
                        }
                    )



                # dominant bot

                bots = defaultdict(int)


                for wallet in cluster:

                    bots[
                        wallet_sequences[wallet]["bot"]
                    ] += 1


                dominant_bot = max(
                    bots.items(),
                    key=lambda x:x[1]
                )[0]



                # WR

                wr_scores = []


                for wallet in cluster:

                    score = min(
                        100,
                        len(
                            wallet_sequences[wallet]["sequence"]
                        ) * 10
                    )

                    wr_scores.append(score)



                cluster_wr = round(
                    sum(wr_scores) / len(wr_scores),
                    2
                )



                # wallets

                api_wallets = []


                for wallet in cluster:


                    data = wallet_sequences[wallet]


                    api_wallets.append(
                        {

                            "address": wallet,


                            "gmgn":
                            f"https://gmgn.ai/sol/address/{wallet}",


                            "bot":
                            data["bot"],


                            "wr":
                            min(
                                100,
                                len(data["sequence"]) * 10
                            )


                        }
                    )



                api_clusters.append(
                    {

                        "cluster":
                        cluster_index,


                        "size":
                        len(cluster),


                        "dominant_bot":
                        dominant_bot,


                        "est_wr":
                        cluster_wr,


                        "shared_tokens":
                        shared_tokens,


                        "wallets":
                        api_wallets

                    }
                )



            return {

                "token":
                TARGET_TOKEN,


                "clusters":
                cluster_count,


                "wallets_scanned":
                len(wallet_sequences),


                "results":
                api_clusters

            }

# =========================================================

#if __name__ == "__main__":
#    asyncio.run(main())

async def analyze_token(token_address):

    global TARGET_TOKEN

    TARGET_TOKEN = token_address

    return await main()