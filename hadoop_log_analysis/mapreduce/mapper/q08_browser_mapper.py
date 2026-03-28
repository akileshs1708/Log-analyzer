#!/usr/bin/env python3
"""Q8 Mapper: Browser Family Distribution"""
import sys, os
sys.path.append(os.getcwd())
from log_parser import parse_line

for line in sys.stdin:
    entry = parse_line(line)
    if entry:
        print(f"{entry.browser_family}\t1")
