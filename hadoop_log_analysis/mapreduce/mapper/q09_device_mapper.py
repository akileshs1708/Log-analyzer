#!/usr/bin/env python3
"""Q9 Mapper: Device Type Distribution (Desktop/Mobile/Tablet/Bot)"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        device = "Bot" if entry.is_bot else entry.device_type
        print(f"{device}\t1")
