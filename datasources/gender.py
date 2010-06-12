import re
import time
import urllib2
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from utils.cache import TimedCache
from datasources import fieldname, datasourcesError
from datasources.pubmed import filter_pmids
from datasources import ochsner, DataSource, GEO_ACCESSION_PATTERN, GEO_PLATFORM_PATTERN, PMID_PATTERN
from datasources import urlopener

# Format of url
#http://www.gpeters.com/names/baby-names.php?name=Heather&button=Go

BABY_NAME_GUESSER_URL = "http://www.gpeters.com/names/baby-names.php?name=%s&button=Go"
BABY_NAME_STRING = """<p>Based on popular usage, it is <b>(?P<factor>.+) times more common</b> for <b>(.+)</b> to be a (?P<boygirl>.+)'s name."""
BABY_NAME_PATTERN = re.compile(BABY_NAME_STRING, re.DOTALL)

# inverse for MALE
FEMALE_FACTOR_THRESHOLD = 1.5
MALE_FACTOR_THRESHOLD = 1/FEMALE_FACTOR_THRESHOLD
    
@TimedCache(timeout_in_seconds=60*60*24*7)
def get_gender_page(query_string):
    response = uncached_get_geo_page(query_string, urlopener)
    return(response)
    
def uncached_get_geo_page(first_name, opener=None):
    if not opener:
        opener = urllib2.build_opener()
    if not first_name:
        return(None)
    query_url = BABY_NAME_GUESSER_URL %first_name
    page = opener.open(query_url).read()
    # Be nice to the server
    time.sleep(1/2)
    return(page)        

@TimedCache(timeout_in_seconds=60*60*24*7)
def get_female_factor(first_name):
    if not first_name:
        return(None)
    if (len(first_name) < 2):
        return(None)
    page = get_gender_page(first_name)
    matches = BABY_NAME_PATTERN.search(page)
    if not matches:
        return(None)
    try:
        factor = float(matches.group("factor"))
    except ValueError:
        return(None)
    if "girl" in matches.group("boygirl"):
        female_factor = factor
    else:
        female_factor = 1/factor
    return(female_factor)
        
def get_female_factors(names):
    response = [get_female_factor(name) for name in names]
    return response

# Too many duplicates of this.  Need to refactor duplicate code!
def _map_booleans_to_flags(list_of_True_False):
    mapping = {True:'1', False:'0'}
    list_of_flags = [mapping[i] for i in list_of_True_False]
    return(list_of_flags)

def is_female(names):
    response_bools = [None < get_female_factor(name) > FEMALE_FACTOR_THRESHOLD for name in names]
    response = _map_booleans_to_flags(response_bools)
    return response

def is_male(names):
    response_bools = [None < get_female_factor(name) < MALE_FACTOR_THRESHOLD for name in names]
    response = _map_booleans_to_flags(response_bools)
    return response
    
def is_gender_not_found(names):
    response_bools = [None==get_female_factor(name) for name in names]
    response = _map_booleans_to_flags(response_bools)
    return response    






