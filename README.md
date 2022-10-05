# Language use and trends on incels.is

This repository contains the data and analyses performed for our manuscript the `Men who Hate Women: The Misogyny of Involuntarily Celibate Men` (which builds on data and qualitative work from our prior work: [10.1177/1097184X211017954](https://doi.org/10.1177/1097184X211017954)).  
This paper builds a qualitatively-developed glossary and performs descriptive quantiative analyses of language-use and trends on [https://incels.is/](https://incels.is/) (previously called incels.co among other iterations).

## Forum text scraping

The publicly accessible incels.is forum was scraped on `2021_04_15` using a custom beautifulsoup4 script `scripts/scrape_incels.py` (see [log](2021_04_15_inceldom_discussion_scrape/2021_04_15_inceldom_discussion_scrape.log) and [index](2021_04_15_inceldom_discussion_scrape/complete_submissions_index.txt) for scrape details).

## Quantitative analysis of qualitatively generated glossary

Key terms were identified by sociologist colleagues through qualitative grounded reading of a random sample of the scraped threads.
These were then used to develop a series of regular expressions to capture pluralisation/variation of terms being used.
The scraped forum text was then queried using these regular expressions (terms in `scripts/term_hiearchy.py`, script in scripts/generate_datasets_hierarchy.py`) which was then processed (`term_descriptive_statistics.ipynb`) to remove overlapping hits in accordance with a priority hierarchy of terms and categorised. For example, `Noodle whore` being counted as racist misogyny instead of counting towards a use of `whore`.  

This notebook was then used to generate:

- Table 1 (count data of numer of term use by category): `table1_usage_counts.tsv` 
- Table 2 (use of terms by number of participants): 
- Figure 1 (% of participants using misogynistic terms by number of total posts)
- Figure 3 (% of participants using terms of specific category by number of posts)
- Appendix B (List of Misogynistic Terms by Category)
- Appendix C (Top 25 Uses of Misogynistic Terms)


## Validity check of glossary 

As a validity check of these results, I also did a purely quantitative analysis of most-used words on the forum by extracting the lemmatized version of all nouns used in any comment/post (`scripts/extract_all_nouns.py`) to generate a frequency list (`noun_counts.tsv`).

## Incels.is and Incels.wiki URL references

Any specific page referenced in the manuscript was downloaded (e.g., FAQ, internal glossay documents explaining terms etc) were downloaded as PDFs on 2022-10-02 and archived in `archived_website_urls/`


## Regression analyses/trend of term use over time.

All regression analyses (mixed linear models, change linear models, and individual user models) can be found in `notebooks/2.trends_over_time_regression.ipynb`
This notebook was used to generate:

- Figure 2 (plot and table): `figure_2_relationship_between_time_and_term_use.png` `results/figure_2_relationship_between_time_and_term_use.csv`
- Appendix D (summary of individual models) `Appedix_D_individual_model_summaries.tsv`
- Individual model fits `appendix/individual_model_fits.csv`
- Monthly averages of term usage `appendix/monthly_averages_more_than_3_months.csv`
- Diagnostic plots looking at overall temporal trends `appendix/overall_trend_in_terms_being_used.png` and early/late users `appendix/comparing_prescrape_and_new_users.png`

