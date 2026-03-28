#!/usr/bin/env python3
"""Q7 Mapper: HTTP Method Distribution (GET/POST/PUT/DELETE etc.)"""
import sys, os

sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        print(f"{entry.method}\t1")
