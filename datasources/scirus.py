import re
import time
import glob
import os
from collections import defaultdict
import urllib2
from utils.cache import TimedCache
from datasources import fieldname, datasourcesError
from datasources import DataSource
from datasources import urlopener
from datasources.pubmed import filter_pmids
from pyparsing import *

base_url = """http://www.scirus.com/srsapp/search?"""
query_prefix = """&q="""
start_url_args = """sort=0&t=all"""
end_url_args = """&g=a&dt=all&ff=all&ds=jnl&ds=nom&ds=web&sa=all"""
journal_limits = """+(journal%3Acell+OR+journal%3Ascience+OR+journal%3ANature)&cn=all"""
cohort_limits = """&co=AND&t=any&q=microarray*+%22genome-wide%22+%22expression+profile*%22+++%22transcription+profil*%22&cn=all"""
date_limits = """&fdt=2007&tdt=2007"""
page_start_prefix = """&p="""


# Note to get more than 10 at a time, would need to learn how to set the cookie that gets set here:
# http://www.scirus.com/srsapp/preferences

def get_url_from_query(query, start=0):
    full_url = base_url + start_url_args + query_prefix + query + journal_limits + cohort_limits + date_limits + end_url_args + page_start_prefix + str(start)
    return(full_url)

def get_page_from_url(url):
    page = get_page_using_opener(url, urlopener)
    return(page)

# docsum_iter = get_iter("<DocSum>.*?</DocSum>", summary_xml)
# for docsum in docsum_iter:
#        record_text = docsum.group()
def get_iter(pattern, text):
    # Then for i in iter, use i.group() as the zone
    docsum_pattern = re.compile(pattern, re.DOTALL)
    docsum_iter = docsum_pattern.finditer(text)
    return(docsum_iter)
  
fontStart,fontEnd = makeHTMLTags("font")
journal_start = '<font class="srctitle">'
journal_end = "</font>,"
journal_pattern = Suppress(journal_start) + SkipTo(journal_end)("journal") + Suppress(journal_end)
volume_pattern = Word(nums)("volume")
issue_pattern = Suppress("(") + Word(alphanums)("issue") + Suppress(")")
page_pattern = Suppress("p.") + Word(alphanums)("first_page") + Optional("-") + Optional(Word(nums))
year = Word(nums, exact=4) 
year_pattern = SkipTo(year).suppress() + year("year") + Suppress("</font>")
#author_start = '<font class="authorname">'
#author_end = ","
#author_pattern = Suppress(author_start) + SkipTo(author_end)("author")     
doi_pattern = SkipTo("doi:") + Suppress("doi:") + Combine(Word(nums + ".", min=5) + "/" + Word(alphanums + ".-/", min=5))("doi") + Suppress("<br>")
volume_page_pattern = volume_pattern + Optional(issue_pattern) + Suppress(",") + page_pattern + year_pattern
citation_pattern = journal_pattern + Optional(doi_pattern) + Optional(volume_page_pattern)
    
def get_citations_from_page(page):    
    page_iter = get_iter('<td class="searchresultscol1"><input type="checkbox".*?</tr>', page)
    items = []
    for page_excerpt_match in page_iter:
        page_excerpt_text = page_excerpt_match.group()
        new_items = get_dict_of_hits(citation_pattern, page_excerpt_text)        
        if not new_items:
            print page_excerpt_text
        items.append(new_items)
    return(items)
            
def get_DOIs_from_page(page):
    DOI_pattern = Suppress("doi:") + Word(alphanums + "." + "/" + "-", min=5)
    DOI_set = set(get_list_of_hits(DOI_pattern, page))
    DOI_unique_list = list(DOI_set)
    return(DOI_unique_list)
    
def get_PMIDs_from_DOIs(DOIs):
    annotated_DOIs = [doi + "[doi]" for doi in DOIs]
    DOI_query_string = " OR ".join(annotated_DOIs)
    PMIDs = filter_pmids("1", DOI_query_string)
    return(PMIDs)
    
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
        
        print "Number of new citations + dois:", len(new_items)
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
            lookup_strings.append("|".join([item['journal'], item['year'], item['volume'], item['first_page'] + item['doi'], "", keyname]))
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
        print 1/0
        default_items['id'] = text.split(",")[0]
    return(default_items)
    
def write_unique_strings(strings, filename):
    unique_strings = list(set(strings))
    fh = open(filename, "w")
    for st in unique_strings:
        fh.write(st + "\n")
    fh.close()
    return(unique_strings)
    
    
def get_page_using_opener(url, opener=None):
    if not opener:
        opener = urllib2.build_opener()
    page = opener.open(url).read()
    #time.sleep(1/3)
    return(page)
