import time
from decimal import Decimal
import pandas as pd
import pyarrow as pa
from bitcoin.rpc import RawProxy

def get_block_subsidy(height):
    halvings = height // 210000
    subsidy = Decimal('50.0')
    return subsidy / (Decimal('2') ** halvings)

def process_block(p, height):

    block_hash = p.getblockhash(height)
    block = p.getblock(block_hash, 3)
    
    block_time = block.get("time", 0)
    block_subsidy = get_block_subsidy(height)
    
    transactions_data = []
    for tx in block.get("tx", []):
        vin = tx.get("vin", [])
        vout = tx.get("vout", [])

        is_coinbase = bool(vin and "coinbase" in vin[0])

        sum_inputs = Decimal('0')
        if not is_coinbase:
            for input_item in vin:
                prevout = input_item.get("prevout", {})
                value_in = prevout.get("value", Decimal('0'))
                if not isinstance(value_in, Decimal):
                    value_in = Decimal(str(value_in))
                sum_inputs += value_in

        sum_outputs = Decimal('0')
        for out_item in vout:
            value_out = out_item.get("value", Decimal('0'))
            if not isinstance(value_out, Decimal):
                value_out = Decimal(str(value_out))
            sum_outputs += value_out

        fee = Decimal('0')
        if not is_coinbase:
            fee = sum_inputs - sum_outputs

        tx_data = {
            "block_hash": block_hash,
            "block_height": height,
            "timestamp": block_time,
            "miner_reward": block_subsidy,
            "txid": tx.get("txid", ""),
            "input_value": sum_inputs,
            "output_value": sum_outputs,
            "fee": fee,
            "size": tx.get("size", 0),
            "weight": tx.get("weight", 0)
        }
        transactions_data.append(tx_data)
    return transactions_data

def safe_process_block(p, height, max_retries=3):
    """
    Mechanizm retry w razie Broken pipe i podobnych błędów.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return process_block(p, height)
        except Exception as e:
            msg = str(e)
            if ("Broken pipe" in msg or "Request-sent" in msg or
                "ConnectionResetError" in msg or "Connection refused" in msg):
                print(f"[!] Błąd połączenia przy bloku {height}, próba {attempt}/{max_retries}")
                time.sleep(5)
                # Odnawiamy obiekt RawProxy
                p = RawProxy(service_url="http://rpcDT:DanTom@127.0.0.1:8332")
            else:
                raise
    print(f"[!] Nie udało się pobrać bloku {height} po {max_retries} próbach.")
    return []

def export_data_to_parquet(p, start_block, end_block, output_file):
    all_txs = []
    for i, height in enumerate(range(start_block, end_block + 1)):
        print(f"Przetwarzam blok {height}...")
        tx_list = safe_process_block(p, height)
        all_txs.extend(tx_list)

        if i % 100 == 0 and i > 0:
            time.sleep(0.05)

    df = pd.DataFrame(all_txs)

    for col in ["miner_reward", "input_value", "output_value", "fee"]:
        if col in df.columns:
            df[col] = df[col].astype(float)

    df.to_parquet(output_file, index=False, compression='snappy')
    print(f"Zapisano {len(df)} transakcji w pliku {output_file}")

def main():

    block_step = 25000
    max_block = 800000

    start = 0
    while start <= max_block:
        end = start + block_step - 1
        if end > max_block:
            end = max_block

        # Nowe połączenie RPC dla każdej paczki
        p = RawProxy(service_url="http://rpcDT:DanTom@127.0.0.1:8332")

        output_file = f"dane_{start}_{end}.parquet"
        print(f"\n--- Przetwarzanie bloków {start} - {end} ---\n")

        start_time = time.time()
        export_data_to_parquet(p, start, end, output_file)
        end_time = time.time()

        duration = end_time - start_time
        start_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        end_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))

        with open("log_pobierania.txt", "a", encoding="utf-8") as logfile:
            logfile.write(
                f"Zakres bloków: {start}-{end}\n"
                f"Czas rozpoczęcia: {start_str}\n"
                f"Czas zakończenia: {end_str}\n"
                f"Czas trwania: {duration:.2f} sekund\n"
                "Status: SUKCES\n"
                "--------------------------\n"
            )

        time.sleep(3)

if __name__ == '__main__':
    main()

