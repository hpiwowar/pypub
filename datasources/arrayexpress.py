import re
import time
from BeautifulSoup import BeautifulStoneSoup
from utils.cache import TimedCache
from utils.tidbits import flatten
from datasources import ochsner, DataSource, fieldname, datasourcesError, ARRAYEXPRESS_ACCESSION_PATTERN
from datasources import urlopener


class ArrayExpress(DataSource):
    
    def __init__(self, ids=[]):
        self._arrayexpress_soups = {}
        super(ArrayExpress, self).__init__(ids, "arrayexpress")

    @fieldname("arrayexpress_accession")
    def accession_number(self, id):
        return(id)
  
    @fieldname("arrayexpress_accession_numbers")
    def accession_numbers(self):
        return(self.ids)  

    @fieldname("arrayexpress_pmids_from_links")
    def pmids_from_links(self, accession):
        pmids = self.pmids(accession)
        if not pmids[0]:
            pmids = []
        return(pmids)
        
    @fieldname("arrayexpress_pmids_from_links_in_ochsner_set")
    def pmids_from_links_in_ochsner_set(self, accession):
        pmids = self.pmids(accession)
        ochsner_pmids = ochsner.Ochsner().all_pmids()
        pmids_in_ochsner = set(ochsner_pmids).intersection(pmids)
        return(list(pmids_in_ochsner))

    @fieldname("arrayexpress_dataset_in_ochsner")
    def in_ochsner(self, id):
        ochsner_arrayexpress_accessions = ochsner.Ochsner().all_accession_numbers("arrayexpress")
        response = id in ochsner_arrayexpress_accessions
        return(response)

    @fieldname("arrayexpress_pmid_from_links_or_ochsner")
    def pmid_from_links_or_ochsner(self, id):
        pmids = self.pmids_from_links_in_ochsner_set(id)
        if not pmids:
            pmids = self.pmid_from_ochsner(id)
        try:
            pmid = pmids[0]
        except IndexError:
            pmid = None
        return(pmid)

    @fieldname("arrayexpress_pmid_from_ochsner")
    def pmid_from_ochsner(self, id):
        ochsner_pmid = ochsner.Ochsner().pmid_for_data_location(id)
        if ochsner_pmid:
            return([ochsner_pmid])
        else:
            return([])
                    
    @fieldname("arrayexpress_accession")
    def accession_number(self, id):
        accession_list = self.query_arrayexpress(id, ["experiment", "accession"])
        return(accession_list)

    @fieldname("arrayexpress_submitter")
    def submitter(self, id):
        response = self.query_arrayexpress(id, ["provider", "contact"])   
        return(response)

    @fieldname("arrayexpress_contributor")
    def contributors(self, id):
        return(self.submitter(id))

    @fieldname("arrayexpress_submission_date")
    def submission_date(self, id):
        return(None)
                
    @fieldname("arrayexpress_release_date")
    def release_date(self, id):
        response = self.query_arrayexpress(id, ["releasedate"])    
        return(response)

    @fieldname("arrayexpress_number_samples")
    def number_samples(self, id):
        response = self.query_arrayexpress(id, ["experiment", "samples"])  
        return(response)

    @fieldname("arrayexpress_species")
    def species(self, id):
        response = self.query_arrayexpress(id, ["experiment", "species"])   
        return(response)

    @fieldname("arrayexpress_array_design")
    def array_design(self, id):
        response_accession = self.query_arrayexpress(id, ["arraydesign", "accession"])    
        response_name = self.query_arrayexpress(id, ["arraydesign", "name"])
        response = response_accession + ": " + response_name
        return(response)

    @fieldname("arrayexpress_citation")
    def citation(self, id):
        response = self.query_arrayexpress(id, ["bibliography"])    
        return(response)

    @fieldname("arrayexpress_pmids")
    def pmids(self, id):
        pmid = self.query_arrayexpress(id, ["bibliography", "accession"])
        return([pmid])
       
    def get_soup(self, query_string):
        if not query_string:
            return(None)
        try:
            return(self._arrayexpress_soups[query_string])
        except KeyError:
            raw_xml = get_arrayexpress_page(query_string)
            soup = BeautifulStoneSoup(raw_xml)
            # Verify we got a valid page
            try:
                assert(soup.find("experiments")) 
            except:
                #print query_string
                #print soup.prettify()
                raise Exception("Page not retrieved.  Perhaps server down or no internet connection?")
            self._arrayexpress_soups = soup
            return(soup)
           
    def _extract_from_soup(self, soup, soup_funcs):
        try:
            for func in soup_funcs:
                soup = soup.find(func)
            response = soup.renderContents()
        except AttributeError:
            # No links found
            response = None
        return(response)

    def query_arrayexpress(self, id, tags):
        soup = self.get_soup(id)
        accessions = self._extract_from_soup(soup, tags)
        return(accessions)

         
#http://www.ebi.ac.uk/microarray-as/ae/xml/experiments?keywords=17170127

@fieldname("has_arrayexpress_data")
def has_data_submission(query_pmids):
    """Returns a list of flags (0 or 1) indicating whether the PubMed IDs are listed as
    a citation in ArrayExpress.  
    """
    found_in_arrayexpress = [query_arrayexpress_for_pmid(pmid) for pmid in query_pmids]
    return(found_in_arrayexpress)

@TimedCache(timeout_in_seconds=60*60*24*7)
def get_arrayexpress_page(query_string, verbose=True):
    base_url = "http://www.ebi.ac.uk/microarray-as/ae/xml/experiments?keywords="
    query_url = base_url + query_string
    if verbose:
        print "Getting ArrayExpress page for " + query_string + "...",
    page = urlopener.open(query_url).read()
    if verbose:
        print "done"
    return(page)

def accessions_from_pmids(pmids):
    accessions = [accessions_from_pmid(pmid) for pmid in pmids]
    accessions_set = set(flatten(accessions))
    # Remove None if it is in there
    try:
        accessions_set.remove(None)
    except KeyError:
        pass 
    return(list(accessions_set))
    
def accessions_from_pmid(pmid):
    page = get_arrayexpress_page(pmid, 1)
    pmid_search_pattern = r"<bibliography><accession>" + pmid + r"</accession>"
    if re.search(pmid_search_pattern, page):
        accessions = re.findall(r"<accession>" + ARRAYEXPRESS_ACCESSION_PATTERN + r"</accession>", page)
    else:
        accessions = None
    return(accessions)
        
def query_arrayexpress_for_pmid(pmid):
    if accessions_from_pmid(pmid):
        search_found_pmid = '1'
    else:
        search_found_pmid = '0'
    return(search_found_pmid)



