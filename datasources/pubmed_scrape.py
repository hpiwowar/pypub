import re
import cPickle
from collections import defaultdict
from pyparsing import *
import EUtils

def query_pubmed_for_summary_xml(unique_pmids):
    history_client = EUtils.HistoryClient.HistoryClient()
    pmids_dbids = EUtils.DBIds("pubmed", unique_pmids)
    the_post = history_client.from_dbids(pmids_dbids)
    the_esummary = the_post.esummary()
    summary_xml = the_esummary.read()
    return(summary_xml)
    
def write_summary_xml(summary_xml, pubmed_medline_filename = "miamescore/results/cited_pubmed_medline.xml"):
    fh = open(pubmed_medline_filename, "w")
    fh.write(summary_xml)
    fh.close()

def read_summary_xml(pubmed_medline_filename = "miamescore/results/cited_pubmed_medline.xml"): 
    summary_xml = open(pubmed_medline_filename, "r").read()
    return(summary_xml)

DocSum_start, DocSum_end = makeXMLTags("DocSum")
Id_start, Id_end = makeXMLTags("Id")
Item_start, Item_end = makeXMLTags("Item")

pmid_pattern = Id_start + SkipTo(Id_end)("pmid") + Id_end
date_pattern = Item_start + Word(nums, exact=4)("year") + SkipTo(Item_end).suppress() + Item_end
edate_pattern = Item_start + SkipTo(Item_end)("edate") + Item_end
journal_pattern = Item_start + SkipTo(Item_end)("journal") + Item_end
record_pattern = DocSum_start.suppress() + pmid_pattern + date_pattern + edate_pattern + journal_pattern + SkipTo(DocSum_end).suppress() + DocSum_end.suppress()

def get_iter(pattern, text):
    # Then for i in iter, use i.group() as the zone
    docsum_pattern = re.compile(pattern, re.DOTALL)
    docsum_iter = docsum_pattern.finditer(text)
    return(docsum_iter)

def get_year_journal_dicts_from_xml(summary_xml):
    year_dict = defaultdict(str)
    journal_dict = defaultdict(str)
    docsum_iter = get_iter("<DocSum>.*?</DocSum>", summary_xml)
    count = 0
    for docsum in docsum_iter:
        print count
        count += 1
        record_text = docsum.group()
        record_fields = record_pattern.searchString(record_text)
        for hit in record_fields:
            pmid = hit["pmid"]
            journal_dict[pmid] = hit["journal"]
            year_dict[pmid] = hit["year"] 
    return(year_dict, journal_dict)       
        

def get_year_journal_dicts_from_reading_file():
    #summary_xml = read_summary_xml()
    #(year_dict, journal_dict) = get_year_journal_dicts_from_xml(summary_xml)
    year_dict = cPickle.load(open("miamescore/results/year_dict.pkl", "r"))
    journal_dict = cPickle.load(open("miamescore/results/journal_dict.pkl", "r"))
    return(year_dict, journal_dict)
    