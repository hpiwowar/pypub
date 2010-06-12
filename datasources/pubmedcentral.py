# JOURNALS IMPACT FACTORS
from collections import defaultdict
import time
import re
import urllib2
from BeautifulSoup import BeautifulStoneSoup
from utils.cache import TimedCache
import EUtils
from EUtils import HistoryClient, ThinClient
from datasources import urlopener

EMAIL_CONTACT = "hpiwowar@gmail.com"
VERBOSE = True


def get_eutils_client():
    if VERBOSE:
        ThinClient.DUMP_URL = True
        ThinClient.DUMP_RESULT = True    

    eutils=EUtils.ThinClient.ThinClient(email=EMAIL_CONTACT, 
                                        opener=urlopener)
    return(eutils)
    
@TimedCache(timeout_in_seconds=60*60*24*7)
def filter_pmcids(query_pmcids, filter_string):
    if VERBOSE:
        print "filter %s" %filter_string
        
    if not query_pmcids:
        return([])
    try:
        entrez = HistoryClient.HistoryClient(eutils=get_eutils_client())
        pmcids_dbids = EUtils.DBIds("pmc", query_pmcids)
        pmcids_records = entrez.post(pmcids_dbids)
        filtered_pmcid_records = entrez.search(
                    '#%s AND %s' %(pmcids_records.query_key, filter_string), 
                    db="pmc") 
        filtered_pmcids = filtered_pmcid_records.dbids.ids
    except AttributeError:
        filtered_pmcids = []
    except EUtils.EUtilsError, e:
        if e.args[0].strip() == "Empty result - nothing todo":
            filtered_pmcids = []
        else:
            raise datasourcesError(e) 
    time.sleep(1/3)
    return(filtered_pmcids)
    
def list_of_tag_contents(my_soup, my_tag):
    return [hit.string for hit in my_soup(my_tag)]
    
def _extract_pmid_links_from_xml(raw_xml):
    try:
        soup = BeautifulStoneSoup(raw_xml)
        # Verify we got a valid page
        assert(soup.find("elinkresult"))  
        # Now get the linkset part
        linksetdb_soup = BeautifulStoneSoup(str(soup.find(text="pmc_pubmed").findParents('linksetdb'))[1:-1])
        pmids = list_of_tag_contents(linksetdb_soup, "id")
    except AttributeError:
        # No links found
        pmids = []
    return(pmids)
    
@TimedCache(timeout_in_seconds=60*60*24*7)
def search(query_string):
    if VERBOSE:
        print "filter %s" %query_string
    try:
        entrez = HistoryClient.HistoryClient(eutils=get_eutils_client())
        records = entrez.search(query_string, db="pmc")
        filtered_pmcids = records.dbids.ids
    except AttributeError:
        filtered_pmcids = []
    except EUtils.EUtilsError, e:
        if e.args[0].strip() == "Empty result - nothing todo":
            filtered_pmcids = []
        else:
            raise datasourcesError(e) 
    time.sleep(1/3)
    return(filtered_pmcids)
        
@TimedCache(timeout_in_seconds=60*60*24*7)
def pmcids_to_pmids(pmcids):
    entrez = HistoryClient.HistoryClient(eutils=get_eutils_client())
    pmcids_dbids = EUtils.DBIds("pmc", pmcids)
    pmcids_records = entrez.post(pmcids_dbids)
    pmc_link_query = pmcids_records.elink(db="pubmed")
    raw_xml = pmc_link_query.read()
    pmids = _extract_pmid_links_from_xml(raw_xml)
    return(pmids)
    
def get_unique_journals_from_pubmed_summary_xml(summary_xml):
    journals = pubmed.parse_summary(summary_xml, "Source")

    journal_pattern = re.compile('<Item Name="Source" Type="String">(?P<journal_name>.*)</Item>')
    journals = journal_pattern.findall(summary_xml)
    unique_journals = list(set(journals))
    print len(journals)
    print len(unique_journals)
    return(unique_journals)

def write_unique_journals(unique_journals):
    journals_filename = "miamescore/results/journals.txt"
    fh = open(journals_filename, "w")
    for j in unique_journals:
            fh.write(j + "\n")
    fh.close()

# Globals for now
journal_impact_factors = {}
journal_num_pubmeds = {}
journal_pmc_citations = {}

def query_for_impact_factors():
    cited_filename = "miamescore/results/journal_impact_factors.txt"
    fh = open(cited_filename, "w")

    read_journals_fh = open("miamescore/results/unique_journals.txt", "r")
    for journal in read_journals_fh:
        journal = journal.strip()
        if journal_impact_factors.has_key(journal):
            print "already computed for", journal
        else:
            print
            print journal
            history_client = pubmed.get_uncached_eutils_history_client()  # Bring this inside so it doesn't time out
            query = '"' + journal + '"[journal] AND ("gene expression profiling"[mesh] OR "Oligonucleotide Array Sequence Analysis"[mesh]) AND ("2003"[PDAT]:"2009/7/1"[PDAT])'
            pubmeds_in_journal = history_client.search(query)
            num_pubmeds_in_journal = len(pubmeds_in_journal)
            print "num_pubmeds_in_journal=", num_pubmeds_in_journal
            pmc_link_query = pubmeds_in_journal.elink(db="pmc")
            raw_xml = pmc_link_query.read()
            num_pmc_citations = pubmed._extract_num_pmc_citations_from_xml(raw_xml)
            try:
                impact_factor = round(float(num_pmc_citations)/num_pubmeds_in_journal, 2)
            except ZeroDivisionError:
                impact_factor = None
            journal_impact_factors[journal] = impact_factor
            journal_num_pubmeds[journal] = num_pubmeds_in_journal
            journal_pmc_citations[journal] = num_pmc_citations
            print "sleeping"
            time.sleep(30)
        string_to_write = journal + "|" + str(journal_impact_factors[journal]) + "|" + str(journal_num_pubmeds[journal]) + "|" + str(journal_pmc_citations[journal]) + "\n"
        print string_to_write
        fh.write(string_to_write)
        fh.flush()
    fh.close()
    
def get_impact_factor_dict_from_file(cited_filename="miamescore/results/journal_impact_factors.txt"):
    impact_factor_contents = open(cited_filename, "r").readlines()
    impact_factor_dict = defaultdict(str)
    for line in impact_factor_contents:
        sp = line.split("|")
        impact_factor_dict[sp[0]] = sp[1]
    return(impact_factor_dict)

