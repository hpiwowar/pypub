import sys
import os
import re
from utils.cache import TimedCache
import datasources
from datasources import fieldname, datasourcesError, DataSource
from collections import defaultdict

accession_pattern = re.compile("db=PubMed&term=(?P<accession>\d+)")

class GeoReuse(DataSource):
    def __init__(self, ids=[], filename=""):
        super(GeoReuse, self).__init__(ids, "geo_reuse")
        self.scrape_filename = filename
            
    def get_pmids(self):
        scrape_file = open(self.scrape_filename, "r")
        text = scrape_file.read()
        pmids = accession_pattern.findall(text)
        scrape_file.close()
        return(pmids)        

#@TimedCache(timeout_in_seconds=60*60*24*7)
def get_geo_reuse_pmids(filename=None):    
    # downloaded from http://www.ncbi.nlm.nih.gov/projects/geo/info/ucitations.html
    scrape_filename = "/Users/hpiwowar/Documents/Code/hpiwowar/pypub/trunk/src/rawdata/geo_reuse/geo_usage_citations.html"
    if not filename:
        filename = scrape_filename
    scrape = GeoReuse(filename = filename)
    all_pmids = scrape.get_pmids()
    return(all_pmids)
    
@fieldname("is_geo_reuse")    
def is_geo_reuse(query_pmids, filename=None):
    all_pmids = get_geo_reuse_pmids(filename)
    print len(all_pmids)
    in_reuse_flags = ['1' if (pmid in all_pmids) else '0' for pmid in query_pmids]
    return(in_reuse_flags)

    