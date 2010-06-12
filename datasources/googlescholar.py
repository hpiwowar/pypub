import re
import time
import urllib2
from utils.cache import TimedCache
from datasources import fieldname, datasourcesError
from datasources import DataSource
from pyparsing import *
import unicodedata
import glob
import os
import re
from collections import defaultdict

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
    
stripEmbeddedTags = lambda tokens: re.sub("<.+?>", "", tokens[0])
stripComma = lambda tokens: tokens[0].strip(",")
stripHelip = lambda tokens: tokens[0].replace("&hellip;", "^")		        
stripDash = lambda tokens: tokens[0].replace(" - ", " ")		        
first_author_initials_pattern = Word(alphas.upper(), min=1, max=3)
#    first_author_lastname_pattern = SkipTo(",")  # | "-"
first_author_lastname_pattern = Word(printables) #+ Suppress(",")
first_author_lastname_pattern.setParseAction(stripComma)
journal_pattern = SkipTo(',') 
journal_pattern.setParseAction(stripEmbeddedTags, stripHelip, stripDash)
year_pattern = Word(nums, exact=4)
citation_pattern = Suppress('<span class=gs_a>') + first_author_initials_pattern("initials") + first_author_lastname_pattern("lastname") + Suppress(SkipTo('- ')) + Suppress('- ') + journal_pattern("journal") + Suppress(',') + year_pattern("year") + Suppress("-")

def get_citations_from_page(page_raw):
    # Replace ampersands
    page_noamps = re.sub(r"&amp;", "&", page_raw)
    # "Remove accents" 
    page = unicodedata.normalize('NFKD', unicode(page_noamps, 'utf-8')).encode('ASCII', 'ignore')
    page_iter = get_iter('<h3.*?Related articles', page)
    items = []
    for page_excerpt_match in page_iter:
        page_excerpt_text = page_excerpt_match.group()
        new_items = get_dict_of_hits(citation_pattern, page_excerpt_text)        
        if not new_items:
            print page_excerpt_text
        items.append(new_items)
    return(items)

def get_citations_from_directories(dir_name=".", key_prefix="", output_filename="output.txt"):
    files = glob.glob(dir_name)
    citations = []
    out_file = open(output_filename, "w")
    for filename in files:
        print filename
        page = open(filename, "r").read()
        items = get_citations_from_page(page)
        key_suffix = get_name_of_inner_subdirectory(filename)
        file_prefix = os.path.basename(filename)
        keyname = key_prefix + file_prefix + key_suffix
        new_citations = convert_items_to_lookup_strings(items, keyname)        
        for cite in new_citations:
            out_file.write(cite + "\n")
            print cite
        out_file.flush()
        print "Number of new citations:", len(new_citations)
        citations += new_citations
    out_file.close()
    return(citations)
                
def get_name_of_inner_subdirectory(filename):
    the_dirname = os.path.dirname(filename)
    the_lowest_subdir = os.path.basename(the_dirname)
    return(the_lowest_subdir)

def convert_items_to_lookup_strings(items, keyname="test"):
    lookup_strings = ["|".join([item['journal'], item['year'], "", "", item["lastname"] + " " + item["initials"], keyname]) for item in items]
        
    #for line in lookup_strings:
    #    print(line)
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
        
