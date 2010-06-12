import re
import time
import urllib2
from utils.cache import TimedCache
from datasources import fieldname, datasourcesError
from datasources import DataSource
from pyparsing import *
import glob
import os
from collections import defaultdict

journal_translation = {"Am J Physiol Regulatory Integrative Comp Physiol":"Am J Physiol Regul Integr Comp Physiol",
"Am. J. Clinical Nutrition":"Am J Clin Nutr",
"Am. J. Roentgenol.":"AJR Am J Roentgenol",
"Appl. Envir. Microbiol.":"Appl Environ Microbiol",
"Blood (ASH Annual Meeting Abstracts)":"Blood",
"Evid. Based Complement. Altern. Med.":"Evid Based Complement Alternat Med",
"Genes &amp; Dev.":"Genes Dev",
"Sci. Aging Knowl. Environ.":"Sci Aging Knowledge Environ",
"The Plant Genome":"Plant Genome"}

def substituteTitle(tokens):
    orig_title = tokens[0]
    if orig_title in journal_translation:
        print orig_title
        return journal_translation[orig_title]
    else:
        return orig_title
        
# Note to get more than 10 at a time, would need to learn how to set the cookie that gets set here:
# http://www.scirus.com/srsapp/preferences

# docsum_iter = get_iter("<DocSum>.*?</DocSum>", summary_xml)
# for docsum in docsum_iter:
#        record_text = docsum.group()
def get_iter(pattern, text):
    # Then for i in iter, use i.group() as the zone
    docsum_pattern = re.compile(pattern, re.DOTALL)
    docsum_iter = docsum_pattern.finditer(text)
    return(docsum_iter)

stripWhitespaceAndComma = lambda tokens: tokens[0].strip(" ,")      
stripPeriod = lambda tokens: tokens[0].strip(".")      
removeStyle1 = lambda tokens:  tokens[0].replace(r'</FONT></STRONG>', "")
removeStyle2 = lambda tokens:  tokens[0].replace('<STRONG><FONT COLOR="#CC0000" STYLE="color:#CC0000;background:#FFFFFF;">', "")
#I want them to be case specific in this case to remove ambiguity
#strongStart, strongEnd = makeHTMLTags("strong")
strongStart, strongEnd = ("<strong>", "</strong>")
journal_pattern = Suppress(strongStart) + SkipTo(strongEnd) + Suppress(strongEnd) #+ Suppress(Optional(", </strong>"))
journal_pattern.setParseAction(removeStyle1, removeStyle2, stripWhitespaceAndComma, substituteTitle)
month_pattern = Word(alphanums + "/")
year_pattern = Word(nums, exact=4)
volume_pattern = Word(nums)
page_pattern = Word(alphanums) 
volume_and_page_pattern = volume_pattern("volume") + Suppress(":") + page_pattern("first_page")
doi_pattern = Combine(Word(nums + ".", min=5) + "/" + Word(alphanums + ".-/", min=5))
doi_pattern.setParseAction(stripPeriod)
citation_pattern = journal_pattern("journal") + Optional(month_pattern)("month") + year_pattern("year") + Suppress(";")  + Optional(volume_and_page_pattern) + Optional(doi_pattern("doi"))

def get_citations_from_page(page):    
    page_iter = get_iter('<TD VALIGN="TOP" WIDTH="526" COLSPAN="2" NOWRAP>.*?</TD>', page)
    items = []
    for page_excerpt_match in page_iter:
        page_excerpt_text = page_excerpt_match.group()
        new_items = get_dict_of_hits(citation_pattern, page_excerpt_text)        
        if not new_items:
            print page_excerpt_text
        items.append(new_items)
    return(items)

def get_keyname(key_prefix, filename):
    key_suffix = get_name_of_inner_subdirectory(filename)
    file_prefix = os.path.basename(filename)
    keyname = key_prefix + file_prefix + key_suffix
    return(keyname)
        
def get_citations_from_directories(dir_name=".", key_prefix="", output_filename="output"):
    bulk_matcher_filename = output_filename + "_bulk_matcher_input.txt"
    doi_matcher_filename = output_filename + "_doi_matcher_input.txt"
    files = glob.glob(dir_name)
    citations = []
    dois = []
    bulk_out_file = open(bulk_matcher_filename, "w")
    doi_out_file = open(doi_matcher_filename, "w")
    for filename in files:
        print filename
        keyname = get_keyname(key_prefix, filename)
        page = open(filename, "r").read()
        new_items = get_citations_from_page(page)
        
        new_bulk_citations = convert_items_to_lookup_strings(new_items, keyname)   
        bulk_out_file.write("\n".join(new_bulk_citations))
        bulk_out_file.flush()

        new_doi_citations = convert_dois_to_lookup_strings(new_items, keyname)           
        doi_out_file.write(" OR " + " OR ".join(new_doi_citations))
        doi_out_file.flush()
        
        print "Number of new citations: %d, dois:%d, total:%d" %(len(new_bulk_citations), len(new_doi_citations), len(new_items))
        citations += new_bulk_citations
        dois += new_doi_citations
    print "Total of new citations: %d, dois:%d, total:%d" %(len(citations), len(dois), len(citations+dois))
    bulk_out_file.close()
    doi_out_file.close()
    return(citations, dois)  
        
def get_name_of_inner_subdirectory(filename):
    the_dirname = os.path.dirname(filename)
    the_lowest_subdir = os.path.basename(the_dirname)
    return(the_lowest_subdir)
    
def convert_dois_to_lookup_strings(items, keyname="test"):
    lookup_strings = [item['doi']+"[doi]" for item in items if item['doi']]
    return(lookup_strings)
        
def convert_items_to_lookup_strings(items, keyname="test"):
    lookup_strings = []
    for item in items:
        if not item["doi"]:
            lookup_strings.append("|".join([item['journal'], item['year'], item['volume'], item['first_page'], "", keyname]))
    return(lookup_strings)
         
@TimedCache(timeout_in_seconds=60*60*24*7)            
def get_list_of_hits(pattern, text):
    items = pattern.searchString(text)
    flat_list = [item for [item] in items.asList()]
    return(flat_list)
    
@TimedCache(timeout_in_seconds=60*60*24*7)            
def get_dict_of_hits(pattern, text):
    default_items = defaultdict(str)
    items = pattern.searchString(text)
    if items:
        for key in items[0].keys():
            default_items[key] = items[0][key]
    else:
        print "\n\nPARSING ERROR:\n" + text
        default_items['id'] = text.split(",")[0]
    return(default_items)
    
def write_unique_strings(strings, filename):
    unique_strings = list(set(strings))
    fh = open(filename, "w")
    for st in unique_strings:
        fh.write(st + "\n")
    fh.close()
    return(unique_strings)
    