import requests
import pandas as pd
import numpy as np
import argparse
import os
from pathlib import Path
from requests_respectful import RespectfulRequester
import time
import sys
from bs4 import BeautifulSoup
import re
import unicodedata
import tqdm

rr = RespectfulRequester()

rr.register_realm('incels', max_requests=60, timespan=60)

def parse_thread_page(page):
    data = []
    for post in page.find_all('div', {'class': 'message-cell message-cell--main'}):

        postdate = post.find('time')
        postdate = postdate['data-time']

        post = post.find('div', {'class': 'message-content js-messageContent'})

        metadata = post.find('div', {'class': "message-userContent lbContainer js-lbContainer"})
        metadata = metadata['data-lb-caption-desc']

        poster = metadata.split(' · ')[0]

        body = post.find('div', {'class': 'bbWrapper'})
        body_text = ''
        for part in body.contents:

            if str(type(part)) == "<class 'bs4.element.Tag'>":
                if part.name == 'a':
                    body_text += f"[{part.text}]({part['href']})"
                elif part.name == 'div' or part.name == 'blockquote':
                    # skip quotes
                    pass
                    #for line in part.text.split('\n'):
                    #    line = line.strip().replace('Click to expand...', '')
                    #    if len(line) > 0:
                    #        body_text += f">{line}\n"
                else:
                    if hasattr(part, 'text'):
                        body_text += part.text
                    else:
                        body_text += part
            else:
                if hasattr(part, 'text'):
                    body_text += part.text
                else:
                    body_text += part

        clean_body_text = body_text.replace('\n', ' ').replace('"', '\'')
        data.append((postdate, poster, clean_body_text))
    return data


def make_filename(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '_', value)

    if len(value) == 0:
        return "no_ascii_title"

    return value[:100]


def parse_user_data(page):
    all_user_data = []

    for user_information in page.find_all('div', {'class': 'message-cell message-cell--user'}):
        user_data = {}

        #username
        try:
            username = user_information.find('h4', {'class': 'message-name'})
            user_data['username'] = username.span.span.text
        except AttributeError:
            user_data['username'] = np.nan

        try:
            user_data['forum_rank'] = user_information.find('h5', {'class': 'userTitle message-userTitle'}).text
        except AttributeError:
            user_data['forum_rank'] = np.nan


        try:
            posting_metadata = user_information.find('div', {'class': 'message-userExtras'})

            tag_count = 0
            for tag in posting_metadata.find_all('dt'):
                if tag.text == 'Joined':
                    user_data['date_joined_forum'] = tag.find_all_next('dd')[0].text
                elif tag.text == 'Posts':
                    user_data['number_of_posts'] = tag.find_all_next('dd')[0].text
                elif tag.text == 'Online':
                    user_data['time_on_forum'] = tag.find_all_next('dd')[0].text
        except AttributeError:
            pass

        # some users e.g. admin don't have every field especially time_on_forum so add an NA for that
        if len(user_data) != 5:
            needed_keys = set(['username', 'forum_rank', 'number_of_posts', 'time_on_forum', 'date_joined_forum'])
            missing_keys = needed_keys - user_data.keys()
            for key in missing_keys:
                user_data[key] = np.nan

        all_user_data.append(user_data)

    all_user_data = pd.DataFrame(all_user_data).drop_duplicates()

    return all_user_data


def get_already_downloaded(output_dir):
    downloaded_submissions = output_dir + "/complete_submissions_index.txt"
    if not os.path.exists(downloaded_submissions):
        already_downloaded = set()
        Path(downloaded_submissions).touch()
    else:
        already_downloaded = pd.read_csv(downloaded_submissions,
                                                     sep='\t',
                                                     names=['submission_url', 'comments_file', 'user_data_file'])
        already_downloaded = set(already_downloaded['submission_url'].values)
    return already_downloaded

def parse_incels(output_dir, base_url, area_url):

    base = rr.get(area_url, realms=['incels'], wait=True)
    base = BeautifulSoup(base.text, 'lxml')
    current_forum_page = base

    downloaded_submissions = get_already_downloaded(output_dir)

    page = 1
    final_page = False
    while current_forum_page.find('a', {'class': "pageNav-jump pageNav-jump--next"}) or final_page:
        # for each submission on this page of the inceldom forum, find all the posts
        for submission in tqdm.tqdm(current_forum_page.find_all('div', {'class': "structItem-cell structItem-cell--main"}), desc=f"Submission Page: {page}"):

            # next div usually contains comment information
            submission_metadata = submission.find_next_sibling('div')

            submission_reply_count = np.nan
            submission_views = np.nan
            for tag in submission_metadata.find_all('dt'):
                if tag.text == 'Replies':
                    submission_reply_count = tag.find_all_next('dd')[0].text
                elif tag.text == 'Views':
                    submission_views = tag.find_all_next('dd')[0].text

            post_create_time = int(submission.find('time')['data-time'])
            submission = submission.find('a', {'class': ""})

            submission_data = []
            user_data = pd.DataFrame({'username': [],
                 'forum_rank': [],
                 'date_joined_forum': [],
                 'time_on_forum': [],
                 'number_of_posts': []})


            if submission.has_attr("data-preview-url"):
                # if thread already downloaded skip to next
                first_page_submission_url = base_url + submission['href']
                if first_page_submission_url in downloaded_submissions:
                    continue

                submission_url = base_url + submission['href']
                submission_page = rr.get(submission_url, realms=['incels'], wait=True)
                submission_page = BeautifulSoup(submission_page.text, 'lxml')

                try:
                    submission_title = submission_page.h1.text.strip().replace('\xa0', ' ')
                except AttributeError:
                    print(f"Can't find missing for {submission_page}", file=sys.stderr)
                    print("Skipping", file=sys.stderr)
                    continue

                submission_data = parse_thread_page(submission_page)

                user_data = pd.concat([user_data, parse_user_data(submission_page)], ignore_index=True).drop_duplicates()

                # if there is more than one page in the submission move to the next pages and get the data
                while submission_page.find('a', {'class': "pageNav-jump pageNav-jump--next"}):
                    submission_url = submission_page.find('a', {'class': "pageNav-jump pageNav-jump--next"})['href']
                    submission_url = base_url + submission_url
                    submission_page = rr.get(submission_url, realms=['incels'], wait=True)
                    submission_page = BeautifulSoup(submission_page.text, 'lxml')
                    submission_data.extend(parse_thread_page(submission_page))
                    user_data = pd.concat([user_data, parse_user_data(submission_page)], ignore_index=True).drop_duplicates()

                # ensure no duplicate paths exist
                comments_output_path = f"{output_dir}/submissions/{make_filename(submission_title)}.tsv"
                ix = 0
                duplicate_name = False
                while os.path.exists(comments_output_path):
                    duplicate_name = True
                    comments_output_path = f"{output_dir}/submissions/{make_filename(submission_title)}-duplicate_submission_name_{ix}.tsv"
                    ix+=1
                if duplicate_name:
                    print(f"Using {comments_output_path} because duplicate submission title", file=sys.stderr)

                with open(comments_output_path, 'w') as out_fh:
                    out_fh.write(f'#created={post_create_time}\n')
                    out_fh.write(f"#title={submission_title}\n")
                    out_fh.write(f"#reply_count_at_start_of_scraping={submission_reply_count}\n")
                    out_fh.write(f"#views_at_start_of_scraping={submission_views}\n")
                    out_fh.write('created_utc\tauthor\tcomment\n')
                    for entry in submission_data:
                        out_fh.write(f'{entry[0]}\t{entry[1]}\t"{entry[2]}"\n')

                # ensure no duplicate names exist and if so add a duplicate index
                user_data_path = f"{output_dir}/user_data/{make_filename(submission_title)}.tsv"
                ix = 0
                duplicate_name = False
                while os.path.exists(user_data_path):
                    duplicate_name = True
                    user_data_path = f"{output_dir}/user_data/{make_filename(submission_title)}-duplicate_submission_name_{ix}.tsv"
                    ix+=1
                if duplicate_name:
                    print(f"Using {user_data_path} because of duplicate submission title", file=sys.stderr)

                with open(user_data_path, 'a') as out_fh:
                    out_fh.write(f'#created={post_create_time}\n')
                    out_fh.write(f"#title={submission_title}\n")
                    out_fh.write(f"#reply_count_at_start_of_scraping={submission_reply_count}\n")
                    out_fh.write(f"#views_at_start_of_scraping={submission_views}\n")
                    user_data.to_csv(out_fh, index=False, sep='\t')

                # once the entire submission has been downloaded add URL to complete list
                with open(output_dir + "/complete_submissions_index.txt", 'a') as out_fh:
                    out_fh.write(f"{first_page_submission_url}\t{comments_output_path}\t{user_data_path}\n")
                downloaded_submissions.add(first_page_submission_url)

        # get next page if it exists
        page += 1

        if not final_page:
            current_forum_page_url = current_forum_page.find('a', {'class': "pageNav-jump pageNav-jump--next"})['href']
            current_forum_page_url = base_url + current_forum_page_url
            current_forum_page = requests.get(current_forum_page_url)
            current_forum_page = BeautifulSoup(current_forum_page.text, 'lxml')
        elif final_page:
            break

        if not current_forum_page.find('a', {'class': "pageNav-jump pageNav-jump--next"}):
            final_page = True
            print(f"Final Page (page {page})", file=sys.stderr)


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Incel xenforo scraping tool")
    parser.add_argument('-b', '--base_url', type=str, default="https://incels.is",
                         help="Base URL for forum e.g., https://incels.is")
    parser.add_argument('-a', '--area_url', type=str, default="https://incels.is/forums/inceldom-discussion.2/",
                         help="URL for overall area of forum e.g., https://incels.is/froums/inceldom-discussion.2/")
    parser.add_argument('-o', '--output_dir', required=True, type=str,
                         help="Output dir path (will continue a scrape if dir already exists")

    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
        os.mkdir(os.path.join(args.output_dir, 'submissions'))

    if not os.path.exists(os.path.join(args.output_dir, 'user_data')):
        os.mkdir(os.path.join(args.output_dir, 'user_data'))

    print(f"Parsing: {args.area_url}", file=sys.stderr)
    parse_incels(args.output_dir, args.base_url, args.area_url)

