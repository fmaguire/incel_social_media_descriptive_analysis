#!/usr/bin/env python

import pandas as pd
import re
import argparse
from pathlib import Path
import sys
import tqdm
from term_hiearchy import hierarchy

from nltk.tokenize import sent_tokenize, RegexpTokenizer
# word_tokenize splits punctuation separately which we don't want to count in wordcounts
wordcount_tokenizer = RegexpTokenizer(r'\w+')

def create_glossary_regexes():
    """
    Creates the regexes for the glossary terms
    """
    glossary = hierarchy
    return glossary


def search_for_glossary_terms(glossary, sub_scrape_index_csv):
    """
    Perform query of glossary regexes (created by create_glossary_regexes)
    and the path to one of the index_csvs for the appropriate scrape of forum subregion
    e.g., 2021_04_15_scrape/2021_04_15_inceldom_discussion_scrape/complete_submissions_index.txt
    """

    # set up dataframe to store hits in forum posts
    query_data = {'thread_title': [], 'thread_url': [], 'username': [], 'post_time': [],
                  'post_position': [], 'word_position': [],
                  'sentence_position': [],  'post_word_count': [],
                  'post_sentence_count': [], 'query_category': [],
                  'query_term': [], 'query_tidied_match': [], 'query_sentence': [],
                  'query_word_before_match': [], 'query_word_after_match': []}

    # create table to contain user_data i.e., one entry for each user
    user_data = pd.DataFrame({'username': [],
                              'forum_rank': [],
                              'date_joined_forum': [],
                              'time_on_forum': [],
                              'number_of_posts': []})
    user_data = pd.DataFrame()

    # user post data (for calculation of subset demonimatiors like total post count for users > 1000 posts etc)
    post_data= {"username": [], 'thread_url': [], 'post_time': [],
                'thread_title': [], 'post_position': [],
                'post_word_count': [], 'post_sentence_count': []}


    index = pd.read_csv(sub_scrape_index_csv, sep='\t',
                        names=['url', 'submissions', 'user_data'])

    # index contains filepaths relative to the subparse folder e.g., 2021_04_15_scrape/2021_04_15_ban_appeals_scrape/
    # therefore need to resolve this so reads work correctly
    scrape_folder = Path(sub_scrape_index_csv).parent.parent
    subscrape_folder = Path(sub_scrape_index_csv).parent
    index['submissions'] = index['submissions'].apply(lambda x: f"{scrape_folder}/{x}")
    index['user_data'] = index['user_data'].apply(lambda x: f"{scrape_folder}/{x}")


    # begin parse
    for thread_number, row in tqdm.tqdm(index.iterrows()):
        thread, post_data_csv, user_data_csv = row

        partial_table = pd.read_csv(user_data_csv, comment='#', sep='\t')
        partial_table['number_of_posts'] = partial_table['number_of_posts'].astype(str).str.replace(',', '').astype(float)

        user_data = pd.concat([user_data, partial_table], ignore_index=True)
        user_data = user_data.drop_duplicates()

        # first query the thread titles
        # get the thread title information from the metadata in post_data_csv
        with open(post_data_csv) as fh:
            thread_created=int(next(fh).replace('#created=', '').strip())
            title = next(fh).replace('#title=', '').strip()
            next(fh)
            next(fh)
            next(fh)
            user = next(fh).split('\t')[1]

        # navigate the nested glossary structure
        for term_category, term_set in glossary.items():
            for term_name, term in term_set.items():
                for match in re.finditer(term, title):
                    term_position = match.span('term')[0]
                    word_before = match.group('before')
                    term_match = match.group('term')
                    word_after = match.group('after')


                    word_ix = len(wordcount_tokenizer.tokenize(title[:term_position]))

                    # replace spaces and hyphens for compound term variants
                    tidied_match = term_match.lower().replace(' ', '').replace('-', '')

                    query_data['thread_title'].append(title)
                    query_data['thread_url'].append(thread)
                    query_data['username'].append(user)
                    query_data['post_position'].append("title")
                    query_data['sentence_position'].append("title")
                    query_data['word_position'].append(word_ix)
                    query_data['post_word_count'].append(len(wordcount_tokenizer.tokenize(title)))
                    query_data['post_sentence_count'].append(len(sent_tokenize(title)))
                    query_data['post_time'].append(thread_created)

                    query_data['query_category'].append(term_category)
                    query_data['query_term'].append(term_name)
                    query_data['query_word_before_match'].append(word_before)
                    query_data['query_tidied_match'].append(tidied_match)
                    query_data['query_word_after_match'].append(word_after)
                    query_data['query_sentence'].append(title)


        # this is needed because a couple of post data csvs are slightly mangled
        try:
            post_data_df = pd.read_csv(post_data_csv, sep='\t', comment='#', lineterminator='\n')
        except:
            print(f"Thread {post_data_csv} unreadable")
            continue

        try:
            for post_ix, row_data in post_data_df.iterrows():
                post_time, post_author, post = row_data

                post_data['thread_title'].append(title)
                post_data['thread_url'].append(thread)
                post_data['username'].append(post_author)
                post_data['post_position'].append(post_ix)
                post_data['post_time'].append(post_time)

                if type(post) != str:
                    post_data['post_word_count'].append(0)
                    post_data['post_sentence_count'].append(0)

                else:
                    post_word_count = len(wordcount_tokenizer.tokenize(post))
                    post_data['post_word_count'].append(post_word_count)

                    post_sentence_count = len(sent_tokenize(post))
                    post_data['post_sentence_count'].append(post_sentence_count)

                    # can't do this as a generator as we need to jump back to get word pos
                    sent_tokens = list(sent_tokenize(post))
                    for sent_ix, sent in enumerate(sent_tokens):

                        for term_category, term_set in glossary.items():
                            for term_name, term in term_set.items():
                                for match in re.finditer(term, sent):
                                    term_position = match.span('term')[0]
                                    word_before = match.group('before')
                                    term_match = match.group('term')
                                    word_after = match.group('after')

                                    #print()
                                    #print(f"Term={term_name}")
                                    #print(f"Sentence={sent}")
                                    #print(match_groups)
                                    #print(word_before, term_match, word_after)


                                    # replace spaces and hyphens for compound term variants
                                    tidied_match = term_match.lower().replace(' ', '').replace('-', '')

                                    words_in_sentences_before_match = len(wordcount_tokenizer.tokenize(". ".join(sent_tokens[:sent_ix])))

                                    sentence_up_to_query_match = sent[:term_position]
                                    words_before_match_in_sentence = len(wordcount_tokenizer.tokenize(sentence_up_to_query_match))
                                    match_word_position_within_post = words_in_sentences_before_match + words_before_match_in_sentence

                                    query_data['thread_title'].append(title)
                                    query_data['thread_url'].append(thread)
                                    query_data['username'].append(post_author)
                                    query_data['post_position'].append(post_ix)
                                    query_data['sentence_position'].append(sent_ix)
                                    query_data['word_position'].append(match_word_position_within_post)
                                    query_data['post_word_count'].append(post_word_count)
                                    query_data['post_sentence_count'].append(post_sentence_count)
                                    query_data['post_time'].append(post_time)

                                    query_data['query_category'].append(term_category)
                                    query_data['query_term'].append(term_name)


                                    query_data['query_word_before_match'].append(word_before)
                                    query_data['query_tidied_match'].append(tidied_match)
                                    query_data['query_word_after_match'].append(word_after)
                                    query_data['query_sentence'].append(sent.replace('\n', ' '))
        except Exception as e:
            print(f"Error parsing: {thread} {post_data_csv}")
            print(e)
            continue

    query_data = pd.DataFrame(query_data)
    post_data = pd.DataFrame(post_data)

    query_data.to_csv(f"{subscrape_folder}/hiearchy_query_data.tsv", sep='\t', index=False)

    # filter user_data
    user_data = user_data.sort_values(['username', 'number_of_posts'], ascending=False).drop_duplicates(subset=["username"], keep="first")
    user_data.to_csv(f"{subscrape_folder}/hierarchy_user_data.tsv", sep='\t', index=False)

    post_data.to_csv(f"{subscrape_folder}/hierarchy_post_data.tsv", sep='\t', index=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Parse scape for subarea of incels.co website")
    parser.add_argument('-i', '--index', required=True,
                        help="path to index file created by scrape")
    parser.add_argument('--overwrite', action='store_true', help="Overwrite existing summaries", default=False)
    args = parser.parse_args()

    term_glossary = create_glossary_regexes()
    subscrape_folder = Path(args.index).parent

    pre_existing = False
    for output in [f"{subscrape_folder}/hierarchy_query_data.tsv",
                   f"{subscrape_folder}/hierarchy_user_data.tsv",
                   f"{subscrape_folder}/hierarchy_user_post_data.tsv"]:

        if Path(output).exists():
            print(f"{output} already exists so stopping, use --overwrite to create new outputs")
            pre_existing = True
        print(output)

    if pre_existing:
        if args.overwrite:
            search_for_glossary_terms(term_glossary, args.index)
        else:
            sys.exit(0)
    else:
        search_for_glossary_terms(term_glossary, args.index)
