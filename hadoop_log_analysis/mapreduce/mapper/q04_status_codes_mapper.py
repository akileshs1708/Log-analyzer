#!/usr/bin/env python3
"""
Q4 Mapper: HTTP Status Code Distribution
Emits: <status_code> \t 1
"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        print(f"{entry.status}\t1")
