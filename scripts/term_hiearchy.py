#!/usr/bin/env python
import re
from collections import OrderedDict

hierarchy = OrderedDict()
hierarchy["Racist Misogyny"] = OrderedDict([('yellow cab', r'yellow(\s|-)?cabs?'),
								            ('puta', r'putas?'),
                       			            ('mammy', r'mammys?'),
		                                    ('jewish american princess', r'jewish(\s|-)?american(\s|-)?princesse?s?'),
                                            ('JAP', r'JAPs?'),
                       			            ('hoodrat', r'hood(\s|-)?rats?'),
                       			            ('gookette', r'gook(\s|-)?ettes?'),
		                                    ('big black vagina', r'big(\s|-)?black(\s|-)?vaginas?'),
                                            ('BBV', r'BBVs?')])

hierarchy["Racist Misogyny (if followed by other term)"] = OrderedDict([('curry', 'curr(y|ies)?'),
                       										           ('SEA', '\s+sea\s+'),
                       										           ('arab', 'arabs?'),
															           ('black', 'blacks?'),
															           ('nigga', 'niggas?'),
															           ('nigger', 'niggers?'),
															           ('noodle', 'noodles?'),
															           ('beaner', 'beaners?'),
															           ('ethnic', 'ethnics?'),
															           ('kike', 'kikes?'),
															           ('jew', 'jews?'),
															           ('khazar', 'khazars?'),
															           ('gook', 'gooks?'),
															           ('latina', 'latinas?'),
															           ('latinx', 'latinxs?'),
															           ('latin american', 'latin(\s|-)?americans?'),
															           ('mexican', 'mexicans?'),
															           ('hispanic', 'hispanics?'),
															           ('puerto rican', 'puerto(\s|-)?ricans?'),
															           ('spanish', 'spanish'),
															           ('spic', 'spics?'),
															           ('wetback', 'wet(\s|-)?backs?')])
hierarchy['Homophobic Misogyny'] = OrderedDict([('dyke', 'dykes?'),
										        ('muffdiver', 'muff(\s|-)?divers?'),
										        ('lesbo', 'lesbos?'),
 										        ('lez', 'lezz?e?r?s?')])

hierarchy["Stacy/Becky"] = OrderedDict([('stacy', 'stac(ie|y|ylite)s?'),
                                        ('becky', 'beck(y|ie)s?')])

hierarchy["Girl/Female"] = OrderedDict([('girl', 'girls?'),
                                        ('female', 'females?')])

hierarchy["Other Misogyny"] = OrderedDict([('warpig', 'war(\s|-)?pigs?'),
                                          ('twat', 'twats?'),
                                          ('toilet', 'toilets?'),
                                          ('smilf', 'smilfs?'),
                                          ('milf', 'milfs?'),
                                          ('thot', 'thots?'),
                                          ("streetwalker", "street(\s|-)?walkers?"),
                                          ("cum receptacle", "cum(\s|-)?receptacles?"),
                                          ("sperm receptacle", "sperm(\s|-)?receptacles?"),
                                          ('slut', 'sluts?'),
                                          ('sloot', 'sloots?'),
                                          ('slit', 'slits?'),
                                          ('skirt', 'skirts?'),
                                          ('skank', 'skanks?'),
                                          ('shit cunt', 'shit(\s|-)?cunts?'),
                                          ("scag", "s(c|k)ags?"),
                                          ('roastie', 'roast(ie|y)s?'),
                                          ('roast beef whores', 'roast(\s|-)?beef(\s|-)?whores?'),
                                          ('pussy', 'puss(y|ie)s?'),
                                          ('prostitute', 'prostitutes?'),
                                          ('mommy', 'm(o|u)mm(y|ie)s?'),
                                          ('milk truck','milk(\s|-)?trucks?'),
                                          ('milk factory', 'milk(\s|-)?factor(y|ie)s?'),
                                          ('landwhale', 'land(\s|-)?whales?'),
                                          ('karen', 'karens?'),
                                          ('insta thots', 'insta(gram)?(\s|-)?thots?'),
                                          ('hole', 'holes?'),
                                          ('hog', 'hogs?'),
                                          ('ho', '\s+hos?\s+'),
                                          ('hatchet wound', 'hatchet(\s|-)?wounds?'),
                                          ("gymthot", "gym(\s|-)?thots?"),
                                          ("cumgutter", "cum(\s|-)?gutters?"),
                                          ("gutterwhore", "gutter(\s|-)?whores?"),
                                          ('gold digger', 'gold(\s|-)?d?igg(er|ing)s?'),
                                          ('gasher', 'gashers?'),
                                          ('gash', 'gash(e)?s?'),
                                          ('femoid', 'femoids?'),
                                          ('feminazi', 'feminazis?'),
                                          ("femcel" , 'femcels?'),
                                          ('fat cow', 'fat(\s|-)?cows?'),
                                          ("escort", "escorts?"),
                                          ('chick', 'chicks?'),
                                          ('bird', 'birds?'),
                                          ('ditz', 'ditz(e)?s?'),
                                          ('cunt', 'cunts?'),
                                          ('cum dumpster', 'cum(\s|-)?dumpsters?'),
                                          ('cock tease', 'cock(\s|-)?teases?'),
                                          ('chicken head', 'chicken(\s|-)?heads?'),
                                          ('butterface', 'butter(\s|-)faces?'),
                                          ('butterbody', 'butter(\s|-)bod(y|ies)'),
                                          ('bitch', 'bitch(s|es)?'),
                                          ('bimbo', 'bimbos?'),
                                          ('bim', 'bims?'),
                                          ('foid', 'foids?'),
                                          ('whore', 'whores?'),
                                          ('CO', '\s+CO\s+'),
                                          ('fat ugly woman', 'fat(\s|-)?ugly(\s|-)wom(a|e)ns?'),
                                          ("HQNP", "HQNPs?"),
                                          ('JB', "JBs?"),
                                          ('jailbait', 'jailbaits?'),
                                          ("PJ", "\s+PJs?\s+"),
                                          ("plain jane", 'plain(\s|-)?janes?'),
                                          ('axe wound', 'axe(\s|-)?wounds?')])

hierarchy["Women/Lady"] = OrderedDict([("lesbian", "lesbians?"),
                                       ("lady", "lad(ie|y)s?"),
                                       ("woman", "wom(a|e)ns?"),
                                       ("sex worker", "sex(\s|-)?workers?"),
                                       ("transgender", "trans(\s|-)?gender"),
                                       ("trans", "trans")])

hierarchy['Transphobic'] = OrderedDict([('tranny', 'trann(y|ies)?'),
                                        ("shemale", 'shemales?')])

regex_prefix = r"(?P<before>^|\w*)(\s|-)?(?P<term>"
regex_suffix = r")(\s|-)?(?P<after>\w*|$)"
for category, terms in hierarchy.items():
    for term_name, term in terms.items():
        term = r"{0}{1}{2}".format(regex_prefix, term, regex_suffix)
        term = re.compile(term, re.IGNORECASE)
        hierarchy[category][term_name] = term

