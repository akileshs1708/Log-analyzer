#!/usr/bin/env python3
"""
Q13 Reducer: Suspicious IP Detection
Input:  <ip> \t <type>|1
Output: <ip> \t <error_count> \t <sensitive_count> \t <bot_count> \t <risk_score>
"""
import sys
from itertools import groupby
from collections import defaultdict

def read_triplets():
    for line in sys.stdin:
        parts = line.strip().split("\t", 1)
        if len(parts) == 2:
            ip = parts[0]
            tag, val = parts[1].split("|")
            yield ip, tag, int(val)

results = defaultdict(lambda: defaultdict(int))
for ip, tag, val in sorted(read_triplets(), key=lambda x: x[0]):
    results[ip][tag] += val

output = []
for ip, counts in results.items():
    errors = counts.get("error", 0)
    sensitive = counts.get("sensitive", 0)
    bots = counts.get("bot", 0)
    # Simple risk score: weighted sum
    risk = errors * 2 + sensitive * 5 + bots * 1
    if risk > 0:
        output.append((risk, ip, errors, sensitive, bots))

for risk, ip, errors, sensitive, bots in sorted(output, reverse=True):
    print(f"{ip}\t{errors}\t{sensitive}\t{bots}\t{risk}")
