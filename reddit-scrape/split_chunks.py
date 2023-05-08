#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  1 19:03:05 2023

@author: sidvijay
"""


import json
import csv
from itertools import islice


# set the input file names
json_file = 'comments_filtered.json'
csv_file = 'comments_filtered.csv'

# set the output file names
out_prefix = 'comments_filtered'
out_suffix = '.json'
out_count = 1

# set the chunk size
chunk_size = 1000000



# read the CSV file in chunks and save to new files
with open(csv_file, 'r', errors='ignore') as f:
    reader = csv.reader(f)
    header = next(reader)
    for i, chunk in enumerate(iter(lambda: list(islice(reader, chunk_size)), [])):
        out_file = out_prefix + str(i+1) + '.csv'
        with open(out_file, 'w', newline='') as out:
            writer = csv.writer(out)
            writer.writerow(header)
            writer.writerows(chunk)