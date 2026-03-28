#!/usr/bin/env python3
"""
Q6 Mapper: Top Error URLs (4xx/5xx responses)
Emits: <url_path>|<status> \t 1
"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry and entry.is_error:
        print(f"{entry.url_path}|{entry.status}\t1")
