import urllib2
import re
from utils.urllib2cache import Urllib2CacheHandler
from utils.cache import TimedCache
from datasources import fieldname, datasourcesError, URL_CACHE_DIR


@TimedCache(timeout_in_seconds=60*60*24*7)
def get_smd_download():
    #seems like I need to read this page first, to reset the data?
    first_url = "http://smd.stanford.edu/cgi-bin/tools/display/listMicroArrayData.pl?tableName=publication"
    dummy_page = urllib2.urlopen(first_url).read()

    base_url = "http://smd.stanford.edu/MicroArray/tmp/prosrvWORLD.xls"
    urlopener = urllib2.build_opener(Urllib2CacheHandler(URL_CACHE_DIR, max_age = 60*60*24*7))
    page = urlopener.open(base_url).read()
    #page = urllib2.urlopen(base_url).read()
    return(page)
    
def query_smd_for_pmid(pmid):
    #TimedCache().is_bypass_cache(True)
    page = get_smd_download()
    #TimedCache().is_bypass_cache(False)        
    successful_search_pattern = r"list_uids=" + pmid + "\W"
    search_pattern_result = re.search(successful_search_pattern, page)
    if search_pattern_result:
        search_found_pmid = '1'
    else:
        search_found_pmid = '0'
    return(search_found_pmid)
    
@fieldname("has_smd_data")
def has_data_submission(query_pmids):
    """Returns a list of flags (0 or 1) indicating whether the PubMed IDs are listed as
    a citation in SMD (the Standford Microarray Database).  
    """
    if not query_pmids:
        return([])
    else:
        found_in_smd = []
        for pmid in query_pmids:
            this_pmid_found_in_smd = query_smd_for_pmid(pmid)
            found_in_smd.append(this_pmid_found_in_smd)
        return(found_in_smd)
