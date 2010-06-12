import sys
import os
import re
import xlrd
from utils.cache import TimedCache
import datasources
from datasources import fieldname, datasourcesError, DataSource, GEO_ACCESSION_PATTERN, ARRAYEXPRESS_ACCESSION_PATTERN

class PortalPMIDs(DataSource):
    def __init__(self, ids=[]):
        super(PortalPMIDs, self).__init__(ids, "portal_pmids")

    def all_pmids(self):
        return(_get_pmid_column())
                
def _get_local_filename():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    datafile = os.path.join(this_dir, '..', 'rawdata', 'portal_pmids', 'portal_pmids.xls')
    return(datafile)

@TimedCache(timeout_in_seconds=60*60*24*7)    
def _get_column_from_number(column_number, source_filename):
    if not source_filename:
        source_filename = _get_local_filename()
    wb = xlrd.open_workbook(source_filename)
    sh = wb.sheet_by_name("raw")
    column = sh.col_values(column_number)
    return(column)
    
def _get_pmid_column(source_filename=None):
    raw_column = _get_column_from_number(10, source_filename)  #"pmid" is in column K which is index 10
    pmid_column = [str(cell)[:-2] for cell in raw_column]  #"pmid" is in column K which is index 10
    return(pmid_column)

def _get_data_location_column(source_filename=None):
    raw_column = _get_column_from_number(0, source_filename) 
    return(raw_column)
    
def _map_booleans_to_flags(list_of_True_False):
    mapping = {True:'1', False:'0'}
    list_of_flags = [mapping[i] for i in list_of_True_False]
    return(list_of_flags)

def _get_flags_for_filter(query_pmids, filtered_pmids):
    pmid_passes_filter = [(pmid in filtered_pmids) for pmid in query_pmids]   
    flag_pmid_passes_filter = _map_booleans_to_flags(pmid_passes_filter)
    return(flag_pmid_passes_filter)

def _get_flags_for_pattern(query_pmids, data_location_query_string, source_filename):
    if not query_pmids:
        return([])
    filtered_pmids = filter_pmids(query_pmids, data_location_query_string, source_filename)
    flag_pmid_passes_filter = _get_flags_for_filter(query_pmids, filtered_pmids)
    return(flag_pmid_passes_filter)

@fieldname("found_by_highwire")    
def found_by_highwire(query_pmids, source_filename=None):
    matching_pattern = "highwire"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern, source_filename)
    return(flag_pmid_passes_filter)
    
@fieldname("found_by_googlescholar")    
def found_by_googlescholar(query_pmids, source_filename=None):
    matching_pattern = "googlescholar"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern, source_filename)
    return(flag_pmid_passes_filter)
    
@fieldname("found_by_scirus")    
def found_by_scirus(query_pmids, source_filename=None):
    matching_pattern = "scirus"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern, source_filename)
    return(flag_pmid_passes_filter)

@fieldname("pmid")    
def pmid(query_pmids):
    return(query_pmids)
        
@fieldname("data_locations")
def list_data_locations(query_pmids):
    pmid_column = _get_pmid_column()
    data_location_column = _get_data_location_column()
    filtered_pmids = []
    for pmid in query_pmids:
        rownum = pmid_column.index(pmid)
        filtered_pmids.append(data_location_column[rownum])
    return(filtered_pmids)
             
def filter_pmids(query_pmids, data_location_query_string, source_filename):
    pmid_column = _get_pmid_column(source_filename)    
    if data_location_query_string:
        data_location_column = _get_data_location_column(source_filename)  
        pmid_rownum_column = [(rownum, pmid) for rownum, pmid in enumerate(pmid_column)]
        filtered_pmid_column = [pmid for (rownum, pmid) in pmid_rownum_column if re.search(data_location_query_string, data_location_column[rownum])]
    else:
        filtered_pmid_column = pmid_column
    filtered_pmids = [pmid for pmid in filtered_pmid_column if pmid in query_pmids]        
    return(filtered_pmids)

@TimedCache(timeout_in_seconds=60*60*24*7)        
def get_all_pmids(sourcedata_filename=None):
    pmid_column_without_header = _get_pmid_column(sourcedata_filename)[1:]
    return(pmid_column_without_header)

### Now add some PMC Stuff

from datasources import pubmedcentral

# Get PubMed Central PubMed IDs
pmc_abstract_or_title = '(microarray[ab] OR microarrays[ab] OR genome-wide[ab] OR "expression profile"[ab] OR "expression profiles"[ab] OR "transcription profile"[ab] OR "transcription profiling"[ab] OR microarray[ti] OR microarrays[ti] OR genome-wide[ti] OR "expression profile"[ti] OR "expression profiles"[ti] OR "transcription profile"[ti] OR "transcription profiling"[ti])'
pmc_date = '("2000/1/1"[epubdat] : "2010/1/1"[epubdat])'
or_part = "(" + " OR ".join(['"rneasy"[text]', '"trizol"[text]', '"real-time pcr"[text]']) + ")"
and_part = "(" + " AND ".join(['"gene expression"[text]', '"microarray"[text]', '"cell"[text]', '"rna"[text]']) + ")"
not_part = '("tissue microarray*"[text] OR "cpg island*"[text])'
pmc_query = " AND ".join([pmc_abstract_or_title, pmc_date, and_part, or_part]) + ' NOT '  + not_part

@TimedCache(timeout_in_seconds=60*60*24*7)
def get_pmc_results(query):    
    pmcids = pubmedcentral.search(query)
    pmids = pubmedcentral.pmcids_to_pmids(pmcids)
    return(pmids)

@fieldname("portal_pmids_found_by_pmc")    
def found_by_pmc(query_pmids, query_string=None):
    if not query_string:
        query_string = pmc_query
    all_pmids = get_pmc_results(query_string)
    found_in_pmc_flags = ['1' if (pmid in all_pmids) else '0' for pmid in query_pmids]
    return(found_in_pmc_flags)
    