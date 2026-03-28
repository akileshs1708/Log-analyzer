#!/usr/bin/env python3
"""
Q12 Mapper: Traffic Pattern by Hour of Day (0-23)
Emits: <HH> \t 1
"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        # Extract just the hour portion from "YYYY-MM-DD HH"
        hour_str = entry.hour
        if " " in hour_str:
            hh = hour_str.split(" ")[1]
            print(f"{hh}\t1")
