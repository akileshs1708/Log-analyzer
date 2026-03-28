#!/usr/bin/env python3
"""
Q1 Mapper: Requests per IP Address
Emits: <ip> \t 1
"""
import sys
import os

sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        print(f"{entry.ip}\t1")
