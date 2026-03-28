#!/usr/bin/env python3
"""
Q10 Reducer: Average Response Time per URL
Input:  <url_path> \t <ms>|1
Output: <url_path> \t <avg_ms> \t <count>  (sorted by avg desc)
"""
import sys
from itertools import groupby

def read_pairs():
    for line in sys.stdin:
        parts = line.strip().split("\t", 1)
        if len(parts) == 2:
            try:
                ms, cnt = parts[1].split("|")
                yield parts[0], int(ms), int(cnt)
            except ValueError:
                pass

results = []
for key, group in groupby(read_pairs(), key=lambda x: x[0]):
    items = list(group)
    total_ms = sum(i[1] for i in items)
    total_cnt = sum(i[2] for i in items)
    avg = total_ms / total_cnt if total_cnt else 0
    results.append((avg, key, total_cnt))

for avg, url, count in sorted(results, reverse=True)[:50]:
    print(f"{url}\t{avg:.1f}\t{count}")
