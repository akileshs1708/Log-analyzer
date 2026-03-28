#!/usr/bin/env python3
"""
Q3 Reducer: Requests per Day and per Hour
Input:  <type:key> \t 1  (sorted)
Output: <type:key> \t <count>
"""
import sys
from itertools import groupby

def read_pairs():
    for line in sys.stdin:
        parts = line.strip().split("\t", 1)
        if len(parts) == 2:
            yield parts[0], int(parts[1])

for key, group in groupby(read_pairs(), key=lambda x: x[0]):
    total = sum(v for _, v in group)
    print(f"{key}\t{total}")
