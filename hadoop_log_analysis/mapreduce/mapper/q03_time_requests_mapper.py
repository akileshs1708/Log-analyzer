#!/usr/bin/env python3
"""
Q3 Mapper: Requests per Day and per Hour
Emits: day:<YYYY-MM-DD>    \t 1
       hour:<YYYY-MM-DD HH> \t 1
"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        print(f"day:{entry.date}\t1")
        print(f"hour:{entry.hour}\t1")
