#!/usr/bin/env python3
"""
Q2 Mapper: Most Requested URLs
Emits: <url_path> \t 1
"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        print(f"{entry.url_path}\t1")
