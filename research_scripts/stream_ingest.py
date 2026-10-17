import sys
import io
from datetime import datetime
from zoneinfo import ZoneInfo
from jesse.services.custom_candle_import import import_custom_candle_csv

def main():
    if len(sys.argv) < 2:
        print("Usage: python stream_ingest.py <SYMBOL> [TIMEZONE]")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    tz_name = sys.argv[2] if len(sys.argv) > 2 else "America/Chicago"
    tz = ZoneInfo(tz_name)

    candles = []
    header = sys.stdin.readline()
    if not header:
        print("Empty stream")
        return

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        if len(parts) < 7:
            continue
        try:
            date_str = parts[0]
            time_str = parts[1].zfill(4)
            o = float(parts[2])
            h = float(parts[3])
            l = float(parts[4])
            c = float(parts[5])
            v = float(parts[6])

            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            hour = int(time_str[:2])
            minute = int(time_str[2:4])

            dt = datetime(year, month, day, hour, minute, tzinfo=tz)
            ts_ms = int(dt.timestamp() * 1000)
            candles.append((ts_ms, o, h, l, c, v))
        except Exception:
            continue

    if not candles:
        print(f"No valid candles parsed for {symbol}")
        return

    # Sort and deduplicate
    candles.sort(key=lambda x: x[0])
    deduped = []
    seen = set()
    for item in candles:
        if item[0] not in seen:
            seen.add(item[0])
            deduped.append(item)

    # Build CSV in memory
    buf = io.BytesIO()
    buf.write(b"timestamp,open,high,low,close,volume\n")
    for ts, o, h, l, c, v in deduped:
        line_bytes = f"{ts},{o:.2f},{h:.2f},{l:.2f},{c:.2f},{v:.0f}\n".encode('utf-8')
        buf.write(line_bytes)

    buf.seek(0)

    # Persist via Jesse's official custom candle importer
    column_mapping = {
        'timestamp': 'timestamp',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume',
    }
    report = import_custom_candle_csv(buf, symbol, 'unix_ms', column_mapping)
    print(f"[{symbol}] Imported {len(deduped)} candles successfully. First: {deduped[0][0]}, Last: {deduped[-1][0]}")

if __name__ == "__main__":
    main()
