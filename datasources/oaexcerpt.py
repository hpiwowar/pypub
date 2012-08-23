import re
import time
import urllib2
import os
import codecs
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from utils.cache import TimedCache
from datasources import fieldname, datasourcesError
from datasources import pubmedcentral
from datasources import urlopener

# info
# http://pmc.jensenlab.org/

# From http://reflect.cpr.ku.dk/pmc/
#You can access publications by PMCID or PMID and choose to download either the XML text files (.nxml) or the complete article archives (.tar.gz) using simple URLs:
#http://pmc.jensenlab.org/pmcid/13900.nxml
#http://pmc.jensenlab.org/pmcid/13900.tar.gz
#http://pmc.jensenlab.org/pmid/1990.nxml
#http://pmc.jensenlab.org/pmid/1990.tar.gz

#PMCID_URL = "http://pmc.jensenlab.org/pmcid/%s.nxml"
PMCID_URL = "http://130.225.75.221/pmcid/%s.nxml"
PMID_URL = "http://pmc.jensenlab.org/pmid/%s.nxml"

CACHED_ARTICLE_PMCID_PATTERN_NXML = "%s.nxml"
CACHED_ARTICLE_PMCID_PATTERN_HTML = "%s.html"

BABY_NAME_STRING = """<p>Based on popular usage, it is <b>(?P<factor>.+) times more common</b> for <b>(.+)</b> to be a (?P<boygirl>.+)'s name."""
BABY_NAME_PATTERN = re.compile(BABY_NAME_STRING, re.DOTALL)
    
@TimedCache(timeout_in_seconds=60*60*24*7)
def get_nxml_page(pmcid, cached_article_dir=None):
    response = uncached_get_oa_page(pmcid, urlopener, cached_article_dir)
    return(response)
    
def read_archived_file(cached_article_dir, pattern, pmcid):
    filename = os.path.join(cached_article_dir, pattern %pmcid)
    try:
        page = codecs.open(filename, "r", "utf-8").read()
    except IOError:
        page = None
    return(page)
    
def uncached_get_oa_page(pmcid, opener=None, cached_article_dir=None):
    if not pmcid:
        return(None)
    page = None
    if cached_article_dir:
        for pattern in [CACHED_ARTICLE_PMCID_PATTERN_NXML, CACHED_ARTICLE_PMCID_PATTERN_HTML]:
            page = read_archived_file(cached_article_dir, pattern, pmcid)
            if page:
                # if we have it then just return... mission accomplished.
                return page
    # Not in article cache directory, so now try to get it over the internets
    if not opener:
        opener = urllib2.build_opener()
    query_url = PMCID_URL %pmcid
    page = opener.open(query_url).read()
    # Be nice to the server
    time.sleep(1/3)
    return(page)        

def strip_xml(page):
    try:
        soup = BeautifulStoneSoup(page).findAll(text=True)
    except UnicodeEncodeError, e:
        return None
    doctext = " ".join(soup)
    return(doctext)

# Inspired by http://bytes.com/topic/python/answers/855851-searching-regular-expressions-string-overlap
def findall_overlapping(pattern, text, flags=0):
    pattern_compiled = re.compile(pattern, flags)
    start = 0
    found = []
    while True:
        m = pattern_compiled.search(text, start)
        if m is None:
            break
        start = m.start() + 1
        found.append(m.group(0))
    return(found)

def get_oa_excerpt(pmcid, pattern, num_leading_chars=100, num_trailing_chars=100, flags=0, cached_article_dir=None):
    padded_pattern = "(.{%d}%s.{%d})" %(num_leading_chars, pattern, num_trailing_chars)
    if not pmcid:
        return(None)
    page = get_nxml_page(pmcid, cached_article_dir)
    doctext = strip_xml(page)

    # this only finds nonoverlapping
    # if want overlapping, have a gander at this:  http://pypi.python.org/pypi/regex
    # or this http://www.regular-expressions.info/lookaround.html
    matches = findall_overlapping(padded_pattern, doctext, flags)
    if not matches:
        return(None)
    matches_join = "|".join([match for match in matches])
    excerpt = matches_join.encode("utf-8")
    #print excerpt
    return(excerpt)

def get_oa_excerpts(pmcids, pattern, num_leading_chars=200, num_trailing_chars=200, flags=0, cached_article_dir=None):
    #pmcids_are_oa = pubmedcentral.filter_for_open_access(pmcids)
    response = []
    for pmcid in pmcids:
        if True: # pmcid in pmcids_are_oa:
            excerpt = get_oa_excerpt(pmcid, pattern, num_leading_chars, num_trailing_chars, flags, cached_article_dir) 
            if not excerpt:
                excerpt = ""
        else:
            excerpt = ""
        print(pmcid, len(excerpt))
        response.append(excerpt)
    return response







