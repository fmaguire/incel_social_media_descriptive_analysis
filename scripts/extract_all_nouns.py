#!/bin/bash

from pathlib import Path
import spacy
import sys
import argparse
from collections import Counter
import pandas as pd
import tqdm

nlp = spacy.load("en_core_web_sm")

def thread_generator(index_fp):
    index = pd.read_csv(index_fp, sep='\t',
                        names=['url', 'submissions', 'user_data'])

    # index contains filepaths relative to the subparse folder e.g., 2021_04_15_scrape/2021_04_15_ban_appeals_scrape/
    # therefore need to resolve this so reads work correctly
    scrape_folder = Path(index_fp).parent.parent
    subscrape_folder = Path(index_fp).parent
    index['submissions'] = index['submissions'].apply(lambda x: f"{scrape_folder}/{x}")
    index['user_data'] = index['user_data'].apply(lambda x: f"{scrape_folder}/{x}")

    # begin parse
    for thread_number, row in tqdm.tqdm(index.iterrows()):
        thread, post_data_csv, user_data_csv = row
        try:
            post_data = pd.read_csv(post_data_csv, comment='#', sep='\t')
        except:
            continue

        for post_text in post_data['comment'].dropna().astype(str):
            yield post_text


def extract_nouns(threads):

    print("Extracting nouns")
    docs = nlp.pipe(threads)
    nouns = []
    for doc in docs:
        #compounds.append({doc.text:[doc[tok.i:tok.head.i+1] for tok in doc if tok.dep_=="compound"]})
        for tok in doc:
            if tok.pos_ == 'NOUN':
                nouns.append(tok.lemma_)

    print("Generating counts")
    noun_counter = Counter(nouns)

    count_dataframe = pd.DataFrame.from_records(noun_counter.most_common(), columns=['noun','count'])
    return count_dataframe


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Parse all nouns for subarea of incels.co website")
    parser.add_argument('-i', '--index', required=True,
                        help="path to index file created by scrape")
    parser.add_argument('--overwrite', action='store_true', help="Overwrite existing summaries", default=False)
    args = parser.parse_args()

    threads = thread_generator(args.index)

    subscrape_folder = Path(args.index).parent

    output = f"{subscrape_folder}/noun_counts.tsv"

    pre_existing = False
    if Path(output).exists():
        print(f"{output} already exists so stopping, use --overwrite to create new outputs")
        pre_existing = True

    if pre_existing:
        if args.overwrite:
            count_dataframe = extract_nouns(threads)
            count_dataframe.to_csv(output, sep='\t')
        else:
            sys.exit(0)
    else:
        count_dataframe = extract_nouns(threads)
        count_dataframe.to_csv(output, sep='\t')
