#!/usr/bin/env python3
"""Q12 Reducer: Traffic Pattern by Hour of Day"""
import sys
from itertools import groupby

def read_pairs():
    for line in sys.stdin:
        parts = line.strip().split("\t", 1)
        if len(parts) == 2:
            yield parts[0], int(parts[1])

results = {}
for key, group in groupby(read_pairs(), key=lambda x: x[0]):
    results[key] = sum(v for _, v in group)

# Output sorted by hour (00-23)
for hh in sorted(results.keys()):
    print(f"{hh}\t{results[hh]}")
