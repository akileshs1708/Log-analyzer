#!/usr/bin/env python3
"""
Q2 Reducer: Most Requested URLs
Input:  <url_path> \t 1  (sorted)
Output: <url_path> \t <count>  (sorted desc)
"""
import sys
from itertools import groupby

def read_pairs():
    for line in sys.stdin:
        parts = line.strip().split("\t", 1)
        if len(parts) == 2:
            yield parts[0], int(parts[1])

results = []
for key, group in groupby(read_pairs(), key=lambda x: x[0]):
    total = sum(v for _, v in group)
    results.append((total, key))

for count, url in sorted(results, reverse=True):
    print(f"{url}\t{count}")
