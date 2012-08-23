import time
import re
import urllib2
from utils.cache import TimedCache
import pyparsing
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
from collections import defaultdict
import EUtils
from EUtils import HistoryClient, ThinClient
import utils
from utils.tidbits import flat_list
from datasources import fieldname, datasourcesError
from datasources import DataSource
from datasources import urlopener

__metaclass__ = type
EMAIL_CONTACT = "hpiwowar@gmail.com"
VERBOSE = True


class PubMed(DataSource):
    def __init__(self, ids=[]):
        super(PubMed, self).__init__(ids, "pubmed")
        
    def geo_accession_numbers(self):
        geo_accessions = linked_geo_dataset_accessions(self.ids)
        return(geo_accessions)

        
@TimedCache(timeout_in_seconds=60*60*24*7)        
def linked_geo_dataset_accessions(pmids):
    response = []
    eutils = get_eutils_client()
    for pmid in pmids:
        if not pmid:
            gds_ids = None
        else:
            raw_xml = _get_gds_links_from_pmid(pmid)
            gds_ids = _extract_gds_ids_from_xml(raw_xml)

        if not gds_ids:
            response.append(None)
        else:
            raw_html = _get_doc_summary_from_gds_ids(gds_ids)
            response.append(_extract_gds_accession_from_html(raw_html))
        time.sleep(1/3)
    return(response)

@TimedCache(timeout_in_seconds=60*60*24*7)
def _get_pmc_links_from_pmid(pmid):
    eutils = get_eutils_client()
    pmids_dbids = EUtils.DBIds("pubmed", pmid)
    raw_xml = eutils.elink_using_dbids(pmids_dbids, db="pmc").read()
    return(raw_xml)
        
@TimedCache(timeout_in_seconds=60*60*24*7)
def _get_gds_links_from_pmid(pmid):
    eutils = get_eutils_client()
    pmids_dbids = EUtils.DBIds("pubmed", pmid)
    xml = eutils.elink_using_dbids(pmids_dbids, db="gds").read()            
    return(xml)

@TimedCache(timeout_in_seconds=60*60*24*7)
def _get_doc_summary_from_gds_ids(gds_ids):
    eutils = get_eutils_client()    
    gds_dbids = EUtils.DBIds("gds", gds_ids)        
    raw_html = eutils.efetch_using_dbids(gds_dbids, rettype="docsum", retmode="html").read()
    return(raw_html)
                
def get_eutils_client():
    if VERBOSE:
        ThinClient.DUMP_URL = True
        #ThinClient.DUMP_RESULT = True
    else:
        ThinClient.DUMP_URL = False    
            
    eutils_client=EUtils.ThinClient.ThinClient(email=EMAIL_CONTACT)
#    eutils_client=EUtils.ThinClient.ThinClient(email=EMAIL_CONTACT, 
#                                        opener=urlopener)
    return(eutils_client)

def get_eutils_history_client():
    if VERBOSE:
        ThinClient.DUMP_URL = True
        #ThinClient.DUMP_RESULT = True    
    else:
        ThinClient.DUMP_URL = False    

    thin_client = get_eutils_client()
    history_client=EUtils.HistoryClient.HistoryClient(thin_client)
    return(history_client)

# Heather look into whether this caching works?
#@TimedCache(timeout_in_seconds=60*5)
def get_history_client_post(pmids):
    history_client = get_eutils_history_client()
    pmids_dbids = EUtils.DBIds("pubmed", pmids)
    the_post = history_client.post(pmids_dbids)
    return(history_client, the_post)

def get_uncached_eutils_history_client():
    if VERBOSE:
        ThinClient.DUMP_URL = True
        #ThinClient.DUMP_RESULT = True    
    else:
        ThinClient.DUMP_URL = False    

    eutils=EUtils.HistoryClient.HistoryClient(EUtils.ThinClient.ThinClient(email=EMAIL_CONTACT))
    return(eutils)

@TimedCache(timeout_in_seconds=60*60*24*7)
def get_summary_xml(pmids):
    if VERBOSE:
        print "get_summary_xml for %s" %pmids
    if not pmids:
        return("")
    (client, the_post) = get_history_client_post(pmids)
    the_esummary = the_post.esummary()
    summary_xml = the_esummary.read()
    if ("<title>Bad Gateway!</title>" in summary_xml):
        summary_xml = ""
    time.sleep(1/3)
    return(summary_xml)
                
@TimedCache(timeout_in_seconds=60*60*24*7)
def get_medline_citation_xml(pmids):
    if VERBOSE:
        print "get_medline_citation_xml for %s" %pmids
    if not pmids:
        return("")    
    (client, the_post) = get_history_client_post(pmids)
    the_efetch = the_post.efetch(retmode="xml")
    medline_citation_xml = the_efetch.read()
    if ("<title>Bad Gateway!</title>" in medline_citation_xml):
        medline_citation_xml = ""
    time.sleep(1/3)
    return(medline_citation_xml)
    
#@TimedCache(timeout_in_seconds=60*60*24*7)
def parse_summary(raw_xml, tag):
    pattern = re.compile('<Item Name="' + tag + '.*">(.*?)</Item>')
    values = pattern.findall(raw_xml)
    return(values)

# Using pyparsing... but too slow?    
# @TimedCache(timeout_in_seconds=60*60*24*7)
# def parse_medline_citation(raw_xml, tag):
#     if VERBOSE:
#         print "parse_medline_citation for %s" %tag
#     try:
#         start, end = pyparsing.makeHTMLTags(tag)
#         tag_pattern = start.suppress() + pyparsing.SkipTo(end)("contents") + end.suppress()
#         values = tag_pattern.searchString(raw_xml)._asStringList()
#     except AttributeError:
#         # No links found
#         values = []
#     return(values)

#@TimedCache(timeout_in_seconds=60*60*24*7)
def parse_medline_citation(raw_xml, tag):
    if VERBOSE:
        print "parse_medline_citation for %s" %tag
    try:
        pattern = "<%s( .+?)*?>\W*(?P<contents>.*?)\W*</%s>" %(tag,tag)  # Not greedy
        matches = re.finditer(pattern, raw_xml, re.DOTALL)
        values = [m.group("contents") for m in matches]
    except AttributeError:
        # No links found
        values = []
    return(values)
    
# Can't cache because too big
def get_soup(raw_xml):
    soup = BeautifulStoneSoup(raw_xml)
    return(soup)

# Was too slow... too much souping
#@TimedCache(timeout_in_seconds=60*60*24*7)
#def parse_medline_citation(raw_xml, tag):
#    if VERBOSE:
#        print "parse_medline_citation for %s" %tag
#    try:
#        soup = get_soup(raw_xml)
        # Verify we got a valid page
        #assert(soup("pubmedarticle"))
        # Now get the linkset part
#       values = list_of_tag_contents(soup, tag)
#   except AttributeError:
        # No links found
#        values = []
#    return(values)
        
def list_of_tag_contents(my_soup, my_tag):
    return [hit.string for hit in my_soup(my_tag.lower())]

def _extract_pmc_citations_from_xml(raw_xml):
    try:
        soup = get_soup(raw_xml)
        # Verify we got a valid page
        assert(soup.find("elinkresult"))  
        # Now get the linkset part
        linksetdb_soup = BeautifulStoneSoup(str(soup.find(text="pubmed_pmc_refs").findParents('linksetdb'))[1:-1])
        pmc_citations = list_of_tag_contents(linksetdb_soup, "id")
    except AttributeError:
        # No links found
        pmc_citations = []
    return(pmc_citations)

        
def _extract_num_pmc_citations_from_xml(raw_xml):
    pmc_citations = _extract_pmc_citations_from_xml(raw_xml)
    num_pmc_citations = len(pmc_citations)
    return(num_pmc_citations)

def total_number_times_cited_in_pmc(pmids):
    raw_xml = _get_pmc_links_from_pmid(pmids)
    response = _extract_num_pmc_citations_from_xml(raw_xml)
    return(response)

@TimedCache(timeout_in_seconds=60*60*24*7)
def _get_pubmed_links_from_pmid(pmid):
    eutils = get_eutils_client()
    pmids_dbids = EUtils.DBIds("pubmed", pmid)
    raw_xml = eutils.elink_using_dbids(pmids_dbids, db="pubmed").read()
    return(raw_xml)
    
def _extract_link_ids_from_xml(raw_xml, link_section_name):
    try:
        soup = get_soup(raw_xml)
        # Verify we got a valid page
        assert(soup.find("elinkresult"))  
        # Now get the linkset part
        linksetdb_soup = BeautifulStoneSoup(str(soup.find(text=link_section_name).findParents('linksetdb'))[1:-1])
        link_ids = list_of_tag_contents(linksetdb_soup, "id")
    except AttributeError:
        # No links found
        link_ids = []
    return(link_ids)

def pubmed_citation_tuples(pmids, link_section_name):
    response = []
    count = 0
    for pmid in pmids:
        count += 1
        raw_xml = _get_pubmed_links_from_pmid(pmid)
        citations = _extract_link_ids_from_xml(raw_xml, link_section_name)
        print citations
        response.append((pmid, citations))
        time.sleep(1/3)
    return(response)
        
def get_what_cites_this_tuples(given_pmids):
    # This returns PMIDs for papers in PMC that cite the given PMIDs
    what_cites_this_tuples = pubmed_citation_tuples(given_pmids, "pubmed_pubmed_citedin")
    return(what_cites_this_tuples)
    
def get_what_this_cites_tuples(given_pmids):
    # This returns PMIDs for papers cited by the given PMIDs that are in PMC
    what_this_cites_tuples = pubmed_citation_tuples(given_pmids, "pubmed_pubmed_refs")
    return(what_this_cites_tuples)
  
def pmc_citations(pmids):
    response = []
    count = 0
    for pmid in pmids:
        count += 1
        raw_xml = _get_pmc_links_from_pmid(pmid)
        citations = _extract_pmc_citations_from_xml(raw_xml)
        print citations
        response.append((pmid, citations))
        time.sleep(1/3)
    return(response)
    
#@TimedCache(timeout_in_seconds=60*60*24*7)
def _extract_gds_ids_from_xml(raw_xml):
    try:
        soup = get_soup(raw_xml)
        #print soup.prettify()
        # Verify we got a valid page
        assert(soup.find("elinkresult"))  
        # Now get the linkset part
        linksetdb_soup = BeautifulStoneSoup(str(soup.find(text="pubmed_gds").findParents('linksetdb'))[1:-1])
        gds_ids = list_of_tag_contents(linksetdb_soup, "id")
    except AttributeError:
        # No links found
        gds_ids = []
    return(gds_ids)

def _extract_gds_accession_from_html(raw_html):
    pattern = "\n\d+: (?P<accession>[GSE0-9]+) record:"
    gds_accessions = re.findall(pattern, raw_html)
    first_accession = gds_accessions[0]
    return(first_accession)

def _get_year(date_str):
# Assumes date is in format "yyyyOTHERTHINGS"
    try:
        year = date_str[0:4]
    except TypeError:
        year = None
    return(year)
    
# docsum_iter = get_iter("<DocSum>.*?</DocSum>", summary_xml)
# for docsum in docsum_iter:
#        record_text = docsum.group()
def get_iter(text, pattern):
    # Then for i in iter, use i.group() as the zone
    docsum_pattern = re.compile(pattern, re.DOTALL)
    docsum_iter = docsum_pattern.finditer(text)
    return(docsum_iter)
    
def get_pmid_from_summary(raw_xml):
    id_start, id_end = pyparsing.makeHTMLTags("Id")
    id_pattern = id_start.suppress() + pyparsing.Word(pyparsing.nums, min=1)("pmid") + id_end.suppress()
    try:
        pmids = id_pattern.searchString(raw_xml).asList()[0]
    except IndexError:
        pmids = []
    return pmids

@TimedCache(timeout_in_seconds=60*60*24*7)
def get_summary_dict(pmids):
    summary_dict = defaultdict(str)
    summary_xml = get_summary_xml(pmids)
    pattern = re.compile("<DocSum>.*?</DocSum>", re.DOTALL)
    all_citations = pattern.findall(summary_xml)
    for individual_xml in all_citations:
        pmids = get_pmid_from_summary(individual_xml)
        for pmid in pmids:
            summary_dict[pmid] = individual_xml
    return(summary_dict)

@TimedCache(timeout_in_seconds=60*60*24*7)    
def _filter_summary_for_pattern(query_pmids, pattern):
    summary_dict = get_summary_dict(query_pmids)
    filtered_dict = defaultdict(str)
    for pmid in query_pmids:
        raw_xml = summary_dict[pmid]
        filtered_dict[pmid] = parse_summary(raw_xml, pattern)
    response = [filtered_dict[pmid] for pmid in query_pmids]
    return(response)

pmc_cites_pattern_string = """<DocSum>.*?""" + \
"""<Item Name="ArticleIds" Type="List">.*?""" + \
"""<Item Name="pubmed" Type="String">(?P<pmid>\d+?)</Item>.*?""" + \
"""<Item Name="PmcRefCount" Type="Integer">(?P<pmcrefcount>\d+?)</Item>.*?""" + \
"""</DocSum>"""
pmid_pmc_cites_pattern = re.compile(pmc_cites_pattern_string, re.DOTALL)

@TimedCache(timeout_in_seconds=60*60*24*7)    
def get_express_pmc_citations(query_pmids):
    raw_xml = get_summary_xml(query_pmids)
    iterator = pmid_pmc_cites_pattern.finditer(raw_xml)
    matchdict = defaultdict(int)
    for match in iterator:
        matchdict[match.group("pmid")] = int(match.group("pmcrefcount"))
    response = [matchdict[pmid] for pmid in query_pmids]
    return(response)
    
@fieldname("express_pubmed_number_times_cited_in_pmc")
def express_number_times_cited_in_pmc(pmids):
    response = get_express_pmc_citations(pmids)
    return(response)

#def get_pmid_from_medline_citation(raw_xml):
#    id_start, id_end = pyparsing.makeHTMLTags("PMID")
#    id_pattern = id_start.suppress() + pyparsing.Word(pyparsing.nums, min=3)("pmid") + id_end.suppress()
#    pmids = id_pattern.searchString(raw_xml).asList()[0]
#    return pmids

pubmedarticle_pattern = re.compile("<PubmedArticle>.*?</PubmedArticle>", re.DOTALL)
    
@TimedCache(timeout_in_seconds=60*60*24*7)
def get_medline_citation_dict(pmids):
    medline_citation_dict = defaultdict(str)
    medline_citation_xml = get_medline_citation_xml(pmids)
    all_citations = pubmedarticle_pattern.findall(medline_citation_xml)
    for individual_xml in all_citations:
        pmids = get_pmid_from_medline_citation(individual_xml)
        for pmid in pmids:
            medline_citation_dict[pmid] = individual_xml
    return(medline_citation_dict)

pmid_pattern = re.compile("<MedlineCitation .+?>\W*<PMID>(\d+?)</PMID>", re.DOTALL)

def get_pmid_from_medline_citation(raw_xml):
    pmids = pmid_pattern.findall(raw_xml)
    return pmids
        
@TimedCache(timeout_in_seconds=60*60*24*7)
def _filter_medline_citation_for_pattern(query_pmids, pattern):
    medline_citation_dict = get_medline_citation_dict(query_pmids)
    filtered_dict = defaultdict(str)
    for pmid in query_pmids:
        raw_xml = medline_citation_dict[pmid]
        filtered_dict[pmid] = parse_medline_citation(raw_xml, pattern)
    response = [filtered_dict[pmid] for pmid in query_pmids]
    return(response)

boolean_mapping = {True:'1', False:'0'}
    
# Too many duplicates of this.  Need to refactor duplicate code!
def _map_booleans_to_flags(list_of_True_False):
    list_of_flags = [boolean_mapping[i] for i in list_of_True_False]
    return(list_of_flags)

# Too many duplicates of this.  Need to refactor duplicate code!
def _get_flags_for_pattern(query_pmids, data_location_query_string):
    if not query_pmids:
        return([])
    filtered_pmids = filter_pmids(query_pmids, data_location_query_string)
    pmid_passes_filter = [(pmid in filtered_pmids) for pmid in query_pmids]   
    flag_pmid_passes_filter = _map_booleans_to_flags(pmid_passes_filter)
    return(flag_pmid_passes_filter)
    
###@TimedCache(timeout_in_seconds=60*60*24*7)
def filter_pmids(query_pmids, pubmed_filter_string):
    print "filter_pmids for %s" %query_pmids
    if VERBOSE:
        print "filter_pmids for %s" %query_pmids
        
    if not query_pmids:
        return([])
    try:
        time.sleep(1/3)
        (client, the_post) = get_history_client_post(query_pmids)
        filtered_pmid_records = client.search(
                    '#%s AND (%s)' %(the_post.query_key, pubmed_filter_string), 
                    db="pubmed") 
        print len(filtered_pmid_records)
        filtered_pmids = filtered_pmid_records.dbids.ids
    except AttributeError:
        filtered_pmids = []
    except EUtils.EUtilsError, e:
        if e.args[0].strip() == "Empty result - nothing todo":
            filtered_pmids = []
        else:
            raise datasourcesError(e) 
    return(filtered_pmids)

@TimedCache(timeout_in_seconds=60*60*24*7)
def search(pubmed_filter_string):
    if VERBOSE:
        print "filter_pmids for %s" %pubmed_filter_string
    try:
        time.sleep(1/3)
        entrez = get_eutils_history_client()
        filtered_pmid_records = entrez.search(pubmed_filter_string, db="pubmed") 
        filtered_pmids = filtered_pmid_records.dbids.ids
    except AttributeError:
        filtered_pmids = []
    except EUtils.EUtilsError, e:
        if e.args[0].strip() == "Empty result - nothing todo":
            filtered_pmids = []
        else:
            raise datasourcesError(e) 
    return(filtered_pmids)
    
def get_pmid_from_citation(journal="", year="", volume="", firstpage="", firstauthor="", key=""):
    components = []
    if journal:
        components.append('"%s"[Jour]' %(journal))
    if volume:
        components.append('"%s"[volume]' %(str(volume)))
    if firstpage:
        components.append('"%s"[page]' %(str(firstpage)))
    if year:
        components.append('"%s"[pdat]' %(str(year)))
    if firstauthor:
        components.append('"%s"[first author]' %(firstauthor))
    query = " AND ".join(components)
    try:
        pmids = search(query)
    except IndexError:
        pmids = [] 
    return pmids
    
#@fieldname("pubmed_number_times_cited_in_pmc")
#def number_times_cited_in_pmc(pmids):
#    response = []
#    for pmid in pmids:
#        raw_xml = _get_pmc_links_from_pmid(pmid)
#        response.append(_extract_num_pmc_citations_from_xml(raw_xml))
#        time.sleep(1/3)
#    return(response)
    
    

  
@fieldname("pmid")
def pubmed_id(pmids):
    """Returns a list of PubMed IDs"""
    return(pmids)

@fieldname("pubmed_authors")
def authors(pmids):
    response_author_lists = _filter_summary_for_pattern(pmids, "Author")
    response = [";".join(author_list) for author_list in response_author_lists]
    return(response)

@fieldname("pubmed_number_authors")
def number_authors(pmids):
    response_author_lists = _filter_summary_for_pattern(pmids, "Author")
    response = [len(author_list) for author_list in response_author_lists]
    return(response)
    
@fieldname("pubmed_year_published")    
def year_published(pmids):
    dates = date_published(pmids)
    years = [_get_year(date_str) for date_str in dates]
    return(years)

@fieldname("pubmed_date_published")
def date_published(pmids):
    response = flat_list(_filter_summary_for_pattern(pmids, "PubDate"))
    response = [str(date) for date in response]
    return(response)

@fieldname("pubmed_date_in_pubmed")
def date_in_pubmed(pmids):
    response = flat_list(_filter_summary_for_pattern(pmids, "medline"))
    return(response)

@fieldname("pubmed_journal")
def journal(pmids):
    response = flat_list(_filter_summary_for_pattern(pmids, "Source"))
    return(response)

@fieldname("pubmed_number_times_cited_in_pmc")
def number_times_cited_in_pmc(pmids):
    response = flat_list(_filter_summary_for_pattern(pmids, "PmcRefCount"))
    response_ints = [int(num) for num in response]
    return(response_ints)

@fieldname("pubmed_issn")
def issn(pmids):
    response = flat_list(_filter_summary_for_pattern(pmids, "ISSN"))
    return(response)

@fieldname("pubmed_essn")
def essn(pmids):
    response = flat_list(_filter_summary_for_pattern(pmids, "ESSN"))
    return(response)

@fieldname("pubmed_doi")
def doi(pmids):
    response = flat_list(_filter_summary_for_pattern(pmids, "DOI"))
    return(response)

@fieldname("pubmed_medline_status")
def medline_status(pmids):
    response_with_extra_text = flat_list(_filter_summary_for_pattern(pmids, "RecordStatus"))
    response = [item.replace("PubMed - ", "") for item in response_with_extra_text]
    return(response)
        
@fieldname("pubmed_corresponding_address")
def corresponding_address(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "Affiliation")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_subset")
def subset(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "CitationSubset")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_pubtype")
def pubtype(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "PublicationType")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_language")
def language(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "Language")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_volume")
def volume(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "Volume")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_issue")
def issue(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "Issue")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_pages")
def pages(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "MedlinePgn")
    response = [";".join(item) for item in response_list]
    return(response)

def get_first_names(pmids):
    def get_first_name(name_and_initials):
        return(name.split(" ")[0])
    response_list = _filter_medline_citation_for_pattern(pmids, "ForeName")
    first_names_only = [[get_first_name(name) for name in names_list] for names_list in response_list]
    return(first_names_only)

@fieldname("pubmed_first_names")
def first_names(pmids):
    first_names_only = get_first_names(pmids)
    joined_first_names = [";".join(first_names_list) for first_names_list in first_names_only]
    return(joined_first_names)

@fieldname("pubmed_first_authors_first_name")
def first_author_first_name(pmids):
    first_names_only = get_first_names(pmids)
    first_first_names = []
    for names in first_names_only:
        if names:
            first_first_name = names[0]
        else:
            first_first_name = ""
        first_first_names.append(first_first_name)
    return(first_first_names)

@fieldname("pubmed_last_author_first_name")
def last_author_first_name(pmids):
    first_names_only = get_first_names(pmids)
    last_first_names = []
    for names in first_names_only:
        if names:
            last_first_name = names[-1]
        else:
            last_first_name = ""
        last_first_names.append(last_first_name)
    return(last_first_names)

@fieldname("pubmed_grants")
def grants(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "GrantID")
    response = [";".join(item) for item in response_list]
    return(response)

year_pattern = re.compile("<Year>(.*?)</Year>")

# This one is from medline, so useful when already pulling medline rather than summary
@fieldname("pubmed_year")    
def year(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "PubDate")
    response = []
    for pubdate_hit in response_list:
        if pubdate_hit:
            response.append(";".join(year_pattern.findall(pubdate_hit[0])))
        else:
            response.append("")
    #response = [year_pattern.findall(pubdate_hit[0]) for pubdate_hit in response_list]
    return(response)

#http://www.nlm.nih.gov/bsd/mms/medlineelements.html#si
@fieldname("pubmed_in_genbank")    
def in_genbank(query_pmids):
    matching_pattern = "genbank[si]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
    
#http://www.nlm.nih.gov/bsd/mms/medlineelements.html#si
@fieldname("pubmed_in_pdb")    
def in_pdb(query_pmids):
    matching_pattern = "pdb[si]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

#http://www.nlm.nih.gov/bsd/mms/medlineelements.html#si
@fieldname("pubmed_in_swissprot")    
def in_swissprot(query_pmids):
    matching_pattern = "swissprot[si]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
              
@fieldname("pubmed_is_cancer")    
def is_cancer(query_pmids):
    matching_pattern = "cancer[sb]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_humans")    
def is_humans(query_pmids):
    matching_pattern = "humans[mesh]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_animals")    
def is_animals(query_pmids):
    matching_pattern = "animals[mesh:noexp]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_viruses")    
def is_viruses(query_pmids):
    matching_pattern = "viruses[mesh]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_plants")    
def is_plants(query_pmids):
    matching_pattern = "plants[mesh]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_fungi")    
def is_fungi(query_pmids):
    matching_pattern = "fungi[mesh]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_mice")    
def is_mice(query_pmids):
    matching_pattern = "mice[mesh]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
    
@fieldname("pubmed_is_bacteria")    
def is_bacteria(query_pmids):
    matching_pattern = "bacteria[mesh]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_cultured_cells")    
def is_cultured_cells(query_pmids):
    matching_pattern = '"cells,cultured"[mesh]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
                           
@fieldname("pubmed_is_ethics_sh")    
def is_ethics_sh(query_pmids):
    matching_pattern = '"ethics"[sh]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_ethics_mesh")    
def is_ethics_mesh(query_pmids):
    matching_pattern = '"ethics"[mesh]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_bioethics_sb")    
def is_bioethics_sb(query_pmids):
    matching_pattern = '"bioethics"[sb]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_jsubsete")    
def is_jsubsete(query_pmids):
    matching_pattern = 'jsubsete'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_review")    
def is_review(query_pmids):
    matching_pattern = 'review[pt]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_english")    
def is_english(query_pmids):
    matching_pattern = 'eng[la]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_open_access")    
def is_open_access(query_pmids):
    matching_pattern = 'pubmed_pmc_open_access[filter]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_effectiveness")    
def is_effectiveness(query_pmids):
    matching_pattern = 'effectiveness[filter]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_prognosis")    
def is_prognosis(query_pmids):
    matching_pattern = '"prognosis/broad"[filter]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_diagnosis")    
def is_diagnosis(query_pmids):
    matching_pattern = '"diagnosis/broad"[filter]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
    
@fieldname("pubmed_is_core_clinical_journal")    
def is_core_clinical_journal(query_pmids):
    matching_pattern = 'jsubsetaim[text]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_clinical_trial")    
def is_clinical_trial(query_pmids):
    matching_pattern = 'Clinical Trial[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
    
@fieldname("pubmed_is_randomized_controlled_trial")    
def is_randomized_controlled_trial(query_pmids):
    matching_pattern = 'Randomized Controlled Trial[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
    
@fieldname("pubmed_is_meta_analysis")    
def is_meta_analysis(query_pmids):
    matching_pattern = 'Meta-Analysis[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_comparative_study")    
def is_comparative_study(query_pmids):
    matching_pattern = 'Comparative Study[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_multicenter_study")    
def is_multicenter_study(query_pmids):
    matching_pattern = 'Multicenter Study[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_validation_study")    
def is_validation_study(query_pmids):
    matching_pattern = 'Validation Studies[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_funded_stimulus")    
def is_funded_stimulus(query_pmids):
    matching_pattern = 'Research Support, American Recovery and Reinvestment Act[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_funded_nih_extramural")    
def is_funded_nih_extramural(query_pmids):
    matching_pattern = 'Research Support, N I H, Extramural[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_funded_nih_intramural")    
def is_funded_nih_intramural(query_pmids):
    matching_pattern = 'Research Support, N I H, Intramural[ptyp]'
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_is_funded_non_us_govt")    
def is_funded_non_us_govt(query_pmids):
    matching_pattern = "Research Support, Non U S Gov't[ptyp]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_in_geo")    
def in_geo(query_pmids):
    matching_pattern = "pubmed_gds[filter]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2000")    
def pre_2000(query_pmids):
    matching_pattern = "1[PDAT]:1999/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2001")    
def pre_2001(query_pmids):
    matching_pattern = "1[PDAT]:2000/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
    
@fieldname("pubmed_pre_2002")    
def pre_2002(query_pmids):
    matching_pattern = "1[PDAT]:2001/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2003")    
def pre_2003(query_pmids):
    matching_pattern = "1[PDAT]:2002/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2004")    
def pre_2004(query_pmids):
    matching_pattern = "1[PDAT]:2003/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2005")    
def pre_2005(query_pmids):
    matching_pattern = "1[PDAT]:2004/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2006")    
def pre_2006(query_pmids):
    matching_pattern = "1[PDAT]:2005/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2007")    
def pre_2007(query_pmids):
    matching_pattern = "1[PDAT]:2006/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2008")    
def pre_2008(query_pmids):
    matching_pattern = "1[PDAT]:2007/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2009")    
def pre_2009(query_pmids):
    matching_pattern = "1[PDAT]:2008/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("pubmed_pre_2010")    
def pre_2010(query_pmids):
    matching_pattern = "1[PDAT]:2009/12/31[PDAT]"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

def get_year_groups(query_pmids, years):
    if VERBOSE:
        print "filter_pmids for %s" %query_pmids
        
    if not query_pmids:
        return([])
    (client, the_post) = get_history_client_post(pmids)
    flags = {}
    for year in years:
        pubmed_filter_string = "1[PDAT]:%d/12/31[PDAT]" %(year)
        try:
            time.sleep(1/3)
            filtered_pmid_records = the_post.search(
                        '#%s AND (%s)' %(the_post.query_key, pubmed_filter_string), 
                        db="pubmed") 
            filtered_pmids = filtered_pmid_records.dbids.ids
        except AttributeError:
            filtered_pmids = []
        except EUtils.EUtilsError, e:
            if e.args[0].strip() == "Empty result - nothing todo":
                filtered_pmids = []
            else:
                raise datasourcesError(e) 

        pmid_passes_filter = [(pmid in filtered_pmids) for pmid in query_pmids]   
        flags[year] = _map_booleans_to_flags(pmid_passes_filter)
        
    flag_pmid_passes_filter = [None for pmid in query_pmids]    
    for i in range(len(query_pmids)):
        flags_list = [flags[year][i] for year in years]
        flag_pmid_passes_filter[i] = ";".join(flags_list)
    return(flag_pmid_passes_filter)


@fieldname("pubmed_pre_2000to2010")    
def pre_2000to2010(query_pmids):
    flag_pmid_passes_filter = get_year_groups(query_pmids, range(1999,2010))
    return(flag_pmid_passes_filter)

@fieldname("pubmed_abstract")
def abstract(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "AbstractText")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_article_title")
def article_title(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "ArticleTitle")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_article_mesh_basic")
def mesh_basic(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "DescriptorName")
    response = [";".join(item) for item in response_list]
    return(response)

@fieldname("pubmed_article_mesh_qualifier")
def mesh_qualifier(pmids):
    response_list = _filter_medline_citation_for_pattern(pmids, "QualifierName")
    response_distinct = [list(set(items)) for items in response_list]
    response = [";".join(items) for items in response_distinct]
    return(response)

def get_mesh_xml(pmids):
    response = _filter_medline_citation_for_pattern(pmids, "MeshHeading")
    return(response)
    
def get_mesh_express(pmids, pattern):
    raw_xml_for_pmids = get_mesh_xml(pmids)
    response = []
    for (pmid, mesh_xml_list) in zip(pmids, raw_xml_for_pmids):
        pmid_response = []
        for mesh_xml in mesh_xml_list:
            matches = pattern.findall(mesh_xml)
            #print matches
            pmid_response.extend(matches)
        response.append(pmid_response)
    return(response)

mesh_major_pattern_string = """DescriptorName MajorTopicYN="Y">(?P<content>.+?)</DescriptorName"""
mesh_major_pattern = re.compile(mesh_major_pattern_string, re.DOTALL)

@fieldname("mesh_major")
def mesh_major(pmids):
    response_list = get_mesh_express(pmids, mesh_major_pattern)
    response = [";".join(items) for items in response_list]
    return(response)

mesh_major_qualifier_pattern_string = """QualifierName MajorTopicYN="Y">(?P<content>.+?)</QualifierName"""
mesh_major_qualifier_pattern = re.compile(mesh_major_qualifier_pattern_string, re.DOTALL)

@fieldname("mesh_major_qualifier")
def mesh_major_qualifier(pmids):
    response_list = get_mesh_express(pmids, mesh_major_qualifier_pattern)
    response_distinct = [list(set(items)) for items in response_list]
    response = [";".join(items) for items in response_distinct]
    return(response)
        