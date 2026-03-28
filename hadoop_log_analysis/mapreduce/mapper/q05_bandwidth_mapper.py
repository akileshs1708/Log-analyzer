#!/usr/bin/env python3
"""
Q5 Mapper: Bandwidth (bytes) Consumed per URL
Emits: <url_path> \t <bytes>
"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        print(f"{entry.url_path}\t{entry.bytes_sent}")
