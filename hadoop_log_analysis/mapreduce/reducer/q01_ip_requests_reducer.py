#!/usr/bin/env python3
"""
Q1 Reducer: Requests per IP Address
Input:  <ip> \t 1  (sorted by IP)
Output: <ip> \t <count>
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

# Output sorted descending by count
for count, ip in sorted(results, reverse=True):
    print(f"{ip}\t{count}")
