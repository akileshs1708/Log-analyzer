#!/usr/bin/env python3
"""Q4 Reducer: HTTP Status Code Distribution"""
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

for count, code in sorted(results, reverse=True):
    print(f"{code}\t{count}")
