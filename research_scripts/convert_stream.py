import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

def convert(input_stream, output_file, tz_name="America/Chicago"):
    tz = ZoneInfo(tz_name)
    lines_read = 0
    candles = []

    # Read header
    header = input_stream.readline()
    if not header:
        return 0

    for line in input_stream:
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
            lines_read += 1
        except Exception:
            continue

    # Sort by timestamp
    candles.sort(key=lambda x: x[0])

    # Deduplicate timestamps keeping the last or first
    deduped = []
    seen = set()
    for item in candles:
        if item[0] not in seen:
            seen.add(item[0])
            deduped.append(item)

    # Write output CSV
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("timestamp,open,high,low,close,volume\n")
        for ts, o, h, l, c, v in deduped:
            f.write(f"{ts},{o:.2f},{h:.2f},{l:.2f},{c:.2f},{v:.0f}\n")

    return len(deduped)

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "/home/research_scripts/cleaned.csv"
    tz = sys.argv[2] if len(sys.argv) > 2 else "America/Chicago"
    count = convert(sys.stdin, out_path, tz)
    print(f"Processed and wrote {count} candles to {out_path}")
