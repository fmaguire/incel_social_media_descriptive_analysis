# Incels Paper 2: Descriptive analysis of incels.co

Incels.co was scraped on `2021_04_15` using a custom beautifulsoup4 script `scripts/scrape_incels.py` (see [log](2021_04_15_inceldom_discussion_scrape/2021_04_15_inceldom_discussion_scrape.log) and [index](2021_04_15_inceldom_discussion_scrape/complete_submissions_index.txt) for scrape details).

## Quantitative Analysis of Key Terms Identified Qualitatively

The posting information was then queried using a set of regular expressions (terms in `scripts/term_hiearchy.py`, script in scripts/generate_datasets_hierarchy.py`) which was then processed (`term_descriptive_statistics.ipynb`) to remove overlapping hits in accordance with a priority hierarchy of terms and categorised. For example, `Noodle whore` being counted as racist misogyny instead of counting towards a use of `whore`.

These queries were developed by Mike and Jaymes doing qualitative analysis of forum posts.

This notebook was then used to generate `table1_usage_counts.tsv`

## Natural Language Processing Analysis of Most-Used Words

As a sanity/validity check of these results, I also did a purely quantitative analysis of most-used words on the forum by extracting the lemmatized version of all nouns used in any comment/post (`scripts/extract_all_nouns.py`) to generate a frequency list (`noun_counts.tsv`).
