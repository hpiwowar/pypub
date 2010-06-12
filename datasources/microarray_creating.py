import sys
import os
import re
import xlrd
from utils.cache import TimedCache
import datasources
from datasources import fieldname, datasourcesError, DataSource, GEO_ACCESSION_PATTERN, ARRAYEXPRESS_ACCESSION_PATTERN
from datasources import pubmed
from datasources import pubmedcentral
from datasources import portal_pmids

# Parse portal results to get inputs to Pubmed Batch Citation lookup    
def write_portal_pmid_lookup_input(subdir=".", 
                                   filenames="*.html",
                                    extract_highwire=True, 
                                    extract_googlescholar=False, 
                                    extract_scirus=False):
    all_citation_strings_to_lookup = []

    if (extract_highwire):
        highwire_pattern = os.path.join("/Users/hpiwowar/Documents/Projects/Thesis/Data/ArticleSearch/Highwire", subdir, filenames)
        output_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/PMIDlookup/highwire"
        list_of_highwire_citation_strings = highwire.get_citations_from_directories(highwire_pattern, "", output_filename)
        all_citation_strings_to_lookup += list_of_highwire_citation_strings

    if (extract_googlescholar):
        googlescholar_pattern = os.path.join("/Users/hpiwowar/Documents/Projects/Thesis/Data/ArticleSearch/GoogleScholar", subdir, filenames)
        output_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/PMIDlookup/googlescholar"
        list_of_googlescholar_citation_strings = googlescholar.get_citations_from_directories(googlescholar_pattern, "", output_filename)
        all_citation_strings_to_lookup += list_of_googlescholar_citation_strings

    if (extract_scirus):
        scirus_pattern = os.path.join("/Users/hpiwowar/Documents/Projects/Thesis/Data/ArticleSearch/Scirus", subdir, filenames)
        output_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/PMIDlookup/scirus"
        list_of_scirus_citation_strings = scirus.get_citations_from_directories(scirus_pattern, "", output_filename)
        all_citation_strings_to_lookup += list_of_scirus_citation_strings
    return(all_citation_strings_to_lookup)
    
# Get PubMed Central PubMed IDs
pmc_abstract_or_title = '(microarray[ab] OR microarrays[ab] OR genome-wide[ab] OR "expression profile"[ab] OR "expression profiles"[ab] OR "transcription profile"[ab] OR "transcription profiling"[ab] OR microarray[ti] OR microarrays[ti] OR genome-wide[ti] OR "expression profile"[ti] OR "expression profiles"[ti] OR "transcription profile"[ti] OR "transcription profiling"[ti])'
pmc_date = '("2000/1/1"[epubdat] : "2010/1/1"[epubdat])'
or_part = "(" + " OR ".join(['"rneasy"[text]', '"trizol"[text]', '"real-time pcr"[text]']) + ")"
and_part = "(" + " AND ".join(['"gene expression"[text]', '"microarray"[text]', '"cell"[text]', '"rna"[text]']) + ")"
not_part = '("tissue microarray*"[text] OR "cpg island*"[text])'
pmc_query = " AND ".join([pmc_abstract_or_title, pmc_date, and_part, or_part]) + ' NOT '  + not_part

def get_pmc_results(query):    
    pmcids = pubmedcentral.search(query)
    pmids = pubmedcentral.pmcids_to_pmids(pmcids)
    return(pmids)

# Get filter ready for PubMed abstracts and titles
pubmed_abstract_or_title = '(microarray[tiab] OR microarrays[tiab] OR genome-wide[tiab] OR "expression profile"[tiab] OR "expression profiles"[tiab] OR "transcription profile"[tiab] OR "transcription profiling"[tiab])'
pubmed_date = '"2000/1/1"[DP]:"2011/1/1"[DP]'  # or maybe try epdat
pubmed_article_type_exclusions = '(Editorial[ptyp] OR Letter[ptyp] OR Meta-Analysis[ptyp] OR Review[ptyp] OR Comment[ptyp] OR Interview[ptyp] OR Lectures[ptyp] OR News[ptyp] OR Newspaper Article[ptyp])'
pubmed_query = " AND ".join([pubmed_abstract_or_title, pubmed_date]) + " NOT " + pubmed_article_type_exclusions
    
@TimedCache(timeout_in_seconds=60*60*24*7)    
def get_all_pmids():
    print "Getting PMC results"
    pmc_pmids = get_pmc_results(pmc_query)
    print "Getting other portal results"
    portal_pmids = datasources.portal_pmids.get_all_pmids()
    all_pmids_before_filter = pmc_pmids + portal_pmids
    print "Filtering in PubMed"
    all_pmids_after_filter = pubmed.filter_pmids(all_pmids_before_filter, pubmed_query)
    return(all_pmids_after_filter)
    
def is_microarray_data_creation(query_pmids):
    in_get_all_pmids = [pmid in get_all_pmids() for pmid in query_pmids]
    flags_for_microarray_data_creation = _map_booleans_to_flags(in_get_all_pmids)
    return(flags_for_microarray_data_creation)
        
def get_all_gds_pmids(pmids):
    all_pmids_after_filter = pubmed.filter_pmids(pmids, "pubmed_gds[filter]")
    return(all_pmids_after_filter)

ae_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/ArrayExpress/scrape.txt"

def get_complete_arrayexpress_pmids():
    scrape = arrayexpress_scrape.ArrayExpressScrape(filename = ae_filename)
    pmids = scrape.get_pmids()
    return(pmids)

def get_all_ae_pmids(query_pmids, complete_ae_pmids):
    all_ae_pmids = [pmid for pmid in query_pmids if pmid in complete_ae_pmids]  
    return(all_ae_pmids)  

def get_all_shared_pmids(gds_pmids, ae_pmids):
    all_shared_pmids = list(set(gds_pmids + ae_pmids))
    return(all_shared_pmids)
        
if (False):
    pmids = get_all_pmids()
    print(len(pmids))

    pmc_pmids = get_pmc_results(pmc_query)
    portal_pmids = datasources.portal_pmids.get_all_pmids()
    all_pmids_before_filter = pmc_pmids + portal_pmids
    pmids = pubmed.filter_pmids(all_pmids_before_filter, pubmed_query)
    gds_pmids = get_all_gds_pmids(pmids)
    complete_ae_pmids = get_complete_arrayexpress_pmids()
    ae_pmids = get_all_ae_pmids(pmids, complete_ae_pmids)
    shared_pmids = get_all_shared_pmids(gds_pmids, ae_pmids)
    shared_proportion = (len(shared_pmids)+0.0)/len(pmids)
    print shared_proportion

# Too many duplicates of this.  Need to refactor duplicate code!
def _map_booleans_to_flags(list_of_True_False):
    mapping = {True:'1', False:'0'}
    list_of_flags = [mapping[i] for i in list_of_True_False]
    return(list_of_flags)

# Too many duplicates of this.  Need to refactor duplicate code!
def get_is_in_flags(query_pmids, base_pmids):
    if not query_pmids:
        return([])
    pmid_passes_filter = [(pmid in base_pmids) for pmid in query_pmids]   
    flag_pmid_passes_filter = _map_booleans_to_flags(pmid_passes_filter)
    return(flag_pmid_passes_filter)
    

@fieldname("pmid")    
def pmid(query_pmids):
    return(query_pmids)

@fieldname("is_microarray_data_creation")        
def is_microarray_data_creation(query_pmids):
    all_microarray_creating_pmids = get_all_pmids()
    in_get_all_pmids = [pmid in all_microarray_creating_pmids for pmid in query_pmids]
    flags_for_microarray_data_creation = _map_booleans_to_flags(in_get_all_pmids)
    return(flags_for_microarray_data_creation)
            

# Parse portal results to get inputs to Pubmed Batch Citation lookup    
def write_portal_pmid_lookup_input(subdir=".", 
                                   filenames="*.html",
                                    extract_highwire=True, 
                                    extract_googlescholar=False, 
                                    extract_scirus=False):
    all_citation_strings_to_lookup = []

    if (extract_highwire):
        highwire_pattern = os.path.join("/Users/hpiwowar/Documents/Projects/Thesis/Data/ArticleSearch/Highwire", subdir, filenames)
        output_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/PMIDlookup/highwire"
        list_of_highwire_citation_strings = highwire.get_citations_from_directories(highwire_pattern, "", output_filename)
        all_citation_strings_to_lookup += list_of_highwire_citation_strings

    if (extract_googlescholar):
        googlescholar_pattern = os.path.join("/Users/hpiwowar/Documents/Projects/Thesis/Data/ArticleSearch/GoogleScholar", subdir, filenames)
        output_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/PMIDlookup/googlescholar"
        list_of_googlescholar_citation_strings = googlescholar.get_citations_from_directories(googlescholar_pattern, "", output_filename)
        all_citation_strings_to_lookup += list_of_googlescholar_citation_strings

    if (extract_scirus):
        scirus_pattern = os.path.join("/Users/hpiwowar/Documents/Projects/Thesis/Data/ArticleSearch/Scirus", subdir, filenames)
        output_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/PMIDlookup/scirus"
        list_of_scirus_citation_strings = scirus.get_citations_from_directories(scirus_pattern, "", output_filename)
        all_citation_strings_to_lookup += list_of_scirus_citation_strings
    return(all_citation_strings_to_lookup)
    
# Get PubMed Central PubMed IDs
pmc_abstract_or_title = '(microarray[ab] OR microarrays[ab] OR genome-wide[ab] OR "expression profile"[ab] OR "expression profiles"[ab] OR "transcription profile"[ab] OR "transcription profiling"[ab] OR microarray[ti] OR microarrays[ti] OR genome-wide[ti] OR "expression profile"[ti] OR "expression profiles"[ti] OR "transcription profile"[ti] OR "transcription profiling"[ti])'
pmc_date = '("2000/1/1"[epubdat] : "2010/1/1"[epubdat])'
or_part = "(" + " OR ".join(['"rneasy"[text]', '"trizol"[text]', '"real-time pcr"[text]']) + ")"
and_part = "(" + " AND ".join(['"gene expression"[text]', '"microarray"[text]', '"cell"[text]', '"rna"[text]']) + ")"
not_part = '("tissue microarray*"[text] OR "cpg island*"[text])'
pmc_query = " AND ".join([pmc_abstract_or_title, pmc_date, and_part, or_part]) + ' NOT '  + not_part

def get_pmc_results(query):    
    pmcids = pubmedcentral.search(query)
    pmids = pubmedcentral.pmcids_to_pmids(pmcids)
    return(pmids)

# Get filter ready for PubMed abstracts and titles
pubmed_abstract_or_title = '(microarray[tiab] OR microarrays[tiab] OR genome-wide[tiab] OR "expression profile"[tiab] OR "expression profiles"[tiab] OR "transcription profile"[tiab] OR "transcription profiling"[tiab])'
pubmed_date = '"2000/1/1"[DP]:"2011/1/1"[DP]'  # or maybe try epdat
pubmed_article_type_exclusions = '(Editorial[ptyp] OR Letter[ptyp] OR Meta-Analysis[ptyp] OR Review[ptyp] OR Comment[ptyp] OR Interview[ptyp] OR Lectures[ptyp] OR News[ptyp] OR Newspaper Article[ptyp])'
pubmed_query = " AND ".join([pubmed_abstract_or_title, pubmed_date]) + " NOT " + pubmed_article_type_exclusions
    
def get_all_pmids():
    pmc_pmids = get_pmc_results(pmc_query)
    portal_pmids = datasources.portal_pmids.get_all_pmids()
    all_pmids_before_filter = pmc_pmids + portal_pmids
    all_pmids_after_filter = pubmed.filter_pmids(all_pmids_before_filter, pubmed_query)
    return(all_pmids_after_filter)
        
def get_all_gds_pmids(pmids):
    all_pmids_after_filter = pubmed.filter_pmids(pmids, "pubmed_gds[filter]")
    return(all_pmids_after_filter)

ae_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/ArrayExpress/scrape.txt"

def get_complete_arrayexpress_pmids():
    scrape = arrayexpress_scrape.ArrayExpressScrape(filename = ae_filename)
    pmids = scrape.get_pmids()
    return(pmids)

def get_all_ae_pmids(query_pmids, complete_ae_pmids):
    all_ae_pmids = [pmid for pmid in query_pmids if pmid in complete_ae_pmids]  
    return(all_ae_pmids)  

def get_all_shared_pmids(gds_pmids, ae_pmids):
    all_shared_pmids = list(set(gds_pmids + ae_pmids))
    return(all_shared_pmids)
        
if (False):
    pmids = get_all_pmids()
    print(len(pmids))

    pmc_pmids = get_pmc_results(pmc_query)
    portal_pmids = datasources.portal_pmids.get_all_pmids()
    all_pmids_before_filter = pmc_pmids + portal_pmids
    pmids = pubmed.filter_pmids(all_pmids_before_filter, pubmed_query)
    gds_pmids = get_all_gds_pmids(pmids)
    complete_ae_pmids = get_complete_arrayexpress_pmids()
    ae_pmids = get_all_ae_pmids(pmids, complete_ae_pmids)
    shared_pmids = get_all_shared_pmids(gds_pmids, ae_pmids)
    shared_proportion = (len(shared_pmids)+0.0)/len(pmids)
    print shared_proportion

# Too many duplicates of this.  Need to refactor duplicate code!
def _map_booleans_to_flags(list_of_True_False):
    mapping = {True:'1', False:'0'}
    list_of_flags = [mapping[i] for i in list_of_True_False]
    return(list_of_flags)

# Too many duplicates of this.  Need to refactor duplicate code!
def get_is_in_flags(query_pmids, base_pmids):
    if not query_pmids:
        return([])
    pmid_passes_filter = [(pmid in base_pmids) for pmid in query_pmids]   
    flag_pmid_passes_filter = _map_booleans_to_flags(pmid_passes_filter)
    return(flag_pmid_passes_filter)
    
