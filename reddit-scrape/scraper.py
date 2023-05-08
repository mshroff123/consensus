#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 01:30:50 2023

@author: sidvijay
"""



import zstandard
import os
import json
import sys
import csv
from datetime import datetime
import logging.handlers
import pandas as pd
import re

log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

def read_and_decode(reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0):
	chunk = reader.read(chunk_size)
	bytes_read += chunk_size
	if previous_chunk is not None:
		chunk = previous_chunk + chunk
	try:
		return chunk.decode()
	except UnicodeDecodeError:
		if bytes_read > max_window_size:
			raise UnicodeError(f"Unable to decode frame after reading {bytes_read:,} bytes")
		return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name):
	with open(file_name, 'rb') as file_handle:
		buffer = ''
		reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)
		while True:
			chunk = read_and_decode(reader, 2**27, (2**29) * 2)
			if not chunk:
				break
			lines = (buffer + chunk).split("\n")

			for line in lines[:-1]:
				yield line, file_handle.tell()

			buffer = lines[-1]
		reader.close()

def is_question(comment_text):
    if not isinstance(comment_text, str):
        return False
    # Regular expression to match question patterns
    question_regex = r"(what|why|how|when|where|who|which)\b.*\?"

    # Check if the comment text matches the question pattern
    match = re.search(question_regex, comment_text, re.IGNORECASE)
    return match is not None


if __name__ == "__main__":
    input_file_paths = ['bodybuilding_submissions.zst', 'careerguidance_submissions.zst', 'college_submissions.zst', 
                        'Fitness_submissions.zst', 'Health_submissions.zst', 'needadvice_submissions.zst', 
                        'nutrition_submissions.zst', 'personalfinance_submissions.zst', 'productivity_submissions.zst', 
                        'Supplements_submissions.zst', 'travel_submissions.zst']
    output_file_path = 'submissions_filtered.csv'
    
    comments_file_paths = ['bodybuilding_comments.zst', 'careerguidance_comments.zst', 'college_comments.zst',
                   'Fitness_comments.zst', 'Health_comments.zst', 'needadvice_comments.zst',
                   'nutrition_comments.zst', 'personalfinance_comments.zst', 'productivity_comments.zst',
                   'Supplements_comments.zst', 'travel_comments.zst']
    
    comments_output_file_path = 'comments_filtered.csv'
    
    fields = ['id', 'title', 'selftext', 'num_comments', 'subreddit']
    comments_fields = ['id', 'link_id', 'parent_id', 'subreddit', 'body']

    file_size = sum([os.stat(file_path).st_size for file_path in input_file_paths])
    file_lines = 0
    file_bytes_processed = 0
    line = None
    created = datetime.now()
    bad_lines = 0
    output_obj_list = []
    submission_ids = set()
    for input_file_path in input_file_paths:
        print(input_file_path + " submission")
        try:
            for line, file_bytes_processed in read_lines_zst(input_file_path):
                try:
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        continue
                    if not isinstance(obj.get('num_comments'), int):
                        continue
                    if obj.get('num_comments') <= 8:
                        continue
                    if not isinstance(obj.get('title'), str):
                        continue
                    if not isinstance(obj.get('selftext'), str):
                        continue
                    if not is_question(obj.get('title')):
                        continue

                    output_obj_list.append([obj[field] for field in fields])
                    submission_ids.add(obj['id'])
                except json.JSONDecodeError as err:
                    bad_lines += 1
                file_lines += 1
                if file_lines % 100000 == 0:
                    log.info(f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {file_lines:,} : {bad_lines:,} : {(file_bytes_processed / file_size) * 100:.0f}%")
        except KeyError as err:
            log.info(f"Object has no key: {err}")
            log.info(line)
        except Exception as err:
            log.info(err)
            log.info(line)

    df = pd.DataFrame(output_obj_list, columns=fields)
    json_obj_df = df.to_json(orient='records')

    # write JSON object to file
    with open('submissions_filtered.json', 'w') as json_file:
        json_file.write(json_obj_df)
        
    #df.to_csv(output_file_path, index=False)

    comments_output_obj_list = []
    comments_counter = 1
    for comments_file_path in comments_file_paths:
        print(comments_file_path + " comments")
        try:
            for line, file_bytes_processed in read_lines_zst(comments_file_path):
                if comments_counter % 10000 == 0: 
                    print(comments_counter)
                    
                comments_counter+=1
                try:
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        continue
                    if not isinstance(obj.get('link_id'), str):
                        continue
                    if obj['link_id'][3:] not in submission_ids:
                        continue
                    if not isinstance(obj.get('body'), str):
                        continue
                    if obj['body'] == '[deleted]':
                        continue
                    if obj['body'] == '[removed]':
                        continue

                    comments_output_obj_list.append([obj[field] for field in comments_fields])
                except json.JSONDecodeError as err:
                    bad_lines += 1
                file_lines += 1
                #if file_lines % 100000 == 0:
                    #log.info(f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {file_lines:,} : {bad_lines:,} : {(file_bytes_processed / file_size) * 100:.0f}%")
        except KeyError as err:
            log.info(f"Object has no key: {err}")
            log.info(line)
        except Exception as err:
            log.info(err)
            log.info(line)

    comments_df = pd.DataFrame(comments_output_obj_list, columns=comments_fields)
    json_obj = comments_df.to_json(orient='records')

    # write JSON object to file
    with open('comments_filtered.json', 'w') as json_file:
        json_file.write(json_obj)
        
    #comments_df.to_csv(comments_output_file_path)





