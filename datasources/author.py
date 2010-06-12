import re
import time
import urllib2
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from utils import world
from utils.cache import TimedCache
from datasources import fieldname, datasourcesError
from datasources import DataSource
from datasources import urlopener
from datasources import pubmed
from datasources import gender
from datasources import authority_excerpt as authority

@fieldname("author_first_authors_first_name")
def first_author_first_name(pmids):
    first_names = pubmed.first_author_first_name(pmids)
    return(first_names)

@fieldname("author_last_author_first_name")
def last_author_first_name(pmids):
    first_names = pubmed.last_author_first_name(pmids)
    return(first_names)

@fieldname("author_first_author_female")
def first_author_female(pmids):
    first_names = first_author_first_name(pmids)
    female = gender.is_female(first_names)
    return(female)

@fieldname("last_first_author_female")
def last_author_female(pmids):
    first_names = last_author_first_name(pmids)
    female = gender.is_female(first_names)
    return(female)

@fieldname("author_first_author_male")
def first_author_male(pmids):
    first_names = first_author_first_name(pmids)
    male = gender.is_male(first_names)
    return(male)

@fieldname("last_first_author_male")
def last_author_male(pmids):
    first_names = last_author_first_name(pmids)
    male = gender.is_male(first_names)
    return(male)

@fieldname("author_first_author_gender_not_found")
def first_author_gender_not_found(pmids):
    first_names = first_author_first_name(pmids)
    gender_not_found = gender.is_gender_not_found(first_names)
    return(gender_not_found)

@fieldname("last_first_author_gender_not_found")
def last_author_gender_not_found(pmids):
    first_names = last_author_first_name(pmids)
    gender_not_found = gender.is_gender_not_found(first_names)
    return(gender_not_found)

@fieldname("first_author_num_all_pubs")
def first_author_num_all_pubs(pmids):
    all_pubs_list = authority.first_author_all_pubs(pmids)
    counts = [len(pubs) for pubs in all_pubs_list]
    return(counts)

@fieldname("last_author_num_all_pubs")
def last_author_num_all_pubs(pmids):
    all_pubs_list = authority.last_author_all_pubs(pmids)
    counts = [len(pubs) for pubs in all_pubs_list]
    return(counts)
    
def filter_for_previous(pmids, pubs_list):
    prev_pubs_list = []
    for pmid, all_pubs in zip(pmids, pubs_list):
        prev_pubs = [pmid_pub for pmid_pub in all_pubs if int(pmid_pub) < int(pmid)]
        #print prev_pubs
        prev_pubs_list.append(prev_pubs)
    return prev_pubs_list

@TimedCache(timeout_in_seconds=60*60*24*7)
def first_author_prev_pubs(pmids):
    all_pubs_list = authority.first_author_all_pubs(pmids)
    prev_pubs_list = filter_for_previous(pmids, all_pubs_list)
    return(prev_pubs_list)

@TimedCache(timeout_in_seconds=60*60*24*7)
def last_author_prev_pubs(pmids):
    all_pubs_list = authority.last_author_all_pubs(pmids)
    prev_pubs_list = filter_for_previous(pmids, all_pubs_list)
    return(prev_pubs_list)
        
@fieldname("first_author_num_prev_pubs")
def first_author_num_prev_pubs(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    counts = [len(prev_pubs) for prev_pubs in prev_pubs_list]
    return(counts)

@fieldname("last_author_num_prev_pubs")
def last_author_num_prev_pubs(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    counts = [len(prev_pubs) for prev_pubs in prev_pubs_list]
    return(counts)

def filter_aggregate_attributes(pmid_bundle_list, key):
    response = []
    for pmid_bundle in pmid_bundle_list:
        attributes = authority.get_aggregate_attributes(pmid_bundle)
        response.append(attributes[key])
    return(response)

#    attribute_names = ('in_genbank', 'in_pdb', 'in_swissprot', 'is_microarray_data_creation', 'in_ae_or_geo', 'is_geo_reuse', 'is_meta_analysis', 'is_multicenter_study', 'is_open_access')

@fieldname("first_author_num_prev_microarray_creations")
def first_author_num_prev_microarray_creation(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_microarray_data_creation')
    return(response)    

@fieldname("last_author_num_prev_microarray_creations")
def last_author_num_prev_microarray_creation(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_microarray_data_creation')
    return(response)    

@fieldname("first_author_num_prev_oa")
def first_author_num_prev_oa(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_open_access')
    return(response)    

@fieldname("last_author_num_prev_oa")
def last_author_num_prev_oa(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_open_access')
    return(response)    

@fieldname("first_author_num_prev_genbank_sharing")
def first_author_num_prev_genbank_sharing(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'in_genbank')
    return(response)    

@fieldname("last_author_num_prev_genbank_sharing")
def last_author_num_prev_genbank_sharing(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'in_genbank')
    return(response)    

@fieldname("first_author_num_prev_pdb_sharing")
def first_author_num_prev_pdb_sharing(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'in_pdb')
    return(response)    

@fieldname("last_author_num_prev_pdb_sharing")
def last_author_num_prev_pdb_sharing(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'in_pdb')
    return(response)    

@fieldname("first_author_num_prev_swissprot_sharing")
def first_author_num_prev_swissprot_sharing(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'in_swissprot')
    return(response)    

@fieldname("last_author_num_prev_swissprot_sharing")
def last_author_num_prev_swissprot_sharing(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'in_swissprot')
    return(response)    

@fieldname("first_author_num_prev_geoae_sharing")
def first_author_num_prev_geoae_sharing(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'in_ae_or_geo')
    return(response)    

@fieldname("last_author_num_prev_geoae_sharing")
def last_author_num_prev_geoae_sharing(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'in_ae_or_geo')
    return(response)    

@fieldname("first_author_num_prev_geo_reuse")
def first_author_num_prev_geo_reuse(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_geo_reuse')
    return(response)    

@fieldname("last_author_num_prev_geo_reuse")
def last_author_num_prev_geo_reuse(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_geo_reuse')
    return(response)    

@fieldname("first_author_num_prev_multi_center")
def first_author_num_prev_multi_center(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_multicenter_study')
    return(response)    

@fieldname("last_author_num_prev_multi_center")
def last_author_num_prev_multi_center(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_multicenter_study')
    return(response)    

@fieldname("first_author_num_prev_meta_analysis")
def first_author_num_prev_meta_analysis(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_meta_analysis')
    return(response)    

@fieldname("last_author_num_prev_meta_analysis")
def last_author_num_prev_meta_analysis(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = filter_aggregate_attributes(prev_pubs_list, 'is_meta_analysis')
    return(response)    

@TimedCache(timeout_in_seconds=60*60*24*7)
def get_number_times_cited_in_pmc(pmids):
    pmc_citation_counts = pubmed.express_number_times_cited_in_pmc(pmids)
    return(pmc_citation_counts)
    
@fieldname("first_author_num_prev_pmc_cites")
def first_author_num_prev_pmc_cites(pmids):
    prev_pubs_list = first_author_prev_pubs(pmids)
    response = []
    for prev_pubs in prev_pubs_list:
        if not prev_pubs:
            num_cites = 0
        else:
            num_cites = sum(get_number_times_cited_in_pmc(prev_pubs))
        response.append(num_cites)
    return(response)    

@fieldname("last_author_num_prev_pmc_cites")
def last_author_num_prev_pmc_cites(pmids):
    prev_pubs_list = last_author_prev_pubs(pmids)
    response = []
    for prev_pubs in prev_pubs_list:
        if not prev_pubs:
            num_cites = 0
        else:
            num_cites = sum(get_number_times_cited_in_pmc(prev_pubs))
        response.append(num_cites)
    return(response)  

@fieldname("first_author_year_first_pub")
def first_author_year_first_pub(pmids):
    pubs_list = first_author_prev_pubs(pmids)
    min_pmids = []
    for pubs in pubs_list:
        pmid_ints = [int(pmid) for pmid in pubs]
        if pmid_ints:
            min_pmids.append(str(min(pmid_ints)))
        else:
            min_pmids.append(None)
    #print(min_pmids)
    response = authority.get_min_year(min_pmids)
    return(response)    

@fieldname("last_author_year_first_pub")
def last_author_year_first_pub(pmids):
    pubs_list = last_author_prev_pubs(pmids)
    min_pmids = []
    for pubs in pubs_list:
        pmid_ints = [int(pmid) for pmid in pubs]
        if pmid_ints:
            min_pmids.append(str(min(pmid_ints)))
        else:
            min_pmids.append(None)
    print(min_pmids)
    response = authority.get_min_year(min_pmids)
    return(response)    
