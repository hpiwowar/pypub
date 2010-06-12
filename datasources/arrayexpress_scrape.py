import sys
import os
import re
from utils.cache import TimedCache
import datasources
from datasources import fieldname, datasourcesError, DataSource
from collections import defaultdict

pattern = {}
accession_pattern_text = "(?P<accession>E-[A-Z]{4}-[0-9]+)"
pattern["record_start"] = re.compile("^\s*" + accession_pattern_text + "\s*$")
pattern["pmid"] = re.compile("PubMed (?P<pmid>[0-9]+)")
pattern["accession"] = re.compile(accession_pattern_text)
pattern["from_geo"] = re.compile("(?P<from_geo>-GEOD-)")
pattern["date"] = re.compile(r"\n\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\n", re.DOTALL)
pattern["description"] = re.compile(r"\nDescription\s*(?P<description>.*?)\nMIAME score", re.DOTALL)
score_pattern_text = "MIAME score.*?(?P<design>.)\t(?P<protocol>.)\t(?P<factors>.)\t(?P<processed>.)\t(?P<raw>.)\s*"
pattern["design"] = re.compile(score_pattern_text, re.DOTALL)
pattern["protocol"] = re.compile(score_pattern_text, re.DOTALL)
pattern["factors"] = re.compile(score_pattern_text, re.DOTALL)
pattern["processed"] = re.compile(score_pattern_text, re.DOTALL)
pattern["raw"] = re.compile(score_pattern_text, re.DOTALL)

pattern["num_samples"] = re.compile("\n\s*(?P<num_samples>\d{1,6})\s*\n", re.DOTALL)
pattern["species"] = re.compile(r"\d\s*\n\s*(?P<species>[A-Za-z]+ [A-Za-z]+)\s*\n\s*\d", re.DOTALL)
pattern["factor_list"] = re.compile(r"Factor name	Factor values\s*(?P<factor_list>.*?)\s*Sample attributes", re.DOTALL)
pattern["attribute_list"] = re.compile(r"Attribute name	Attribute values\s*(?P<attribute_list>.*?)\s*$", re.DOTALL)
pattern["platform_accession"] = re.compile("(?P<platform_accession>A-[A-Z]{4}-[0-9]+)")
pattern["is_affy"] = re.compile("(?P<is_affy>Affymetrix)")
pattern["is_agilent"] = re.compile("(?P<is_agilent>Agilent)")
pattern["experiment_type"] = re.compile("Experiment type.\s*(?P<experiment_type>.*?)\s*(Experimental factor|Sample attribute)", re.DOTALL)


class ArrayExpressScrape(DataSource):
    def __init__(self, ids=[], filename=""):
        super(ArrayExpressScrape, self).__init__(ids, "arrayexpress_scrape")
        self.scrape_filename = filename
            
    def get_pmids(self):
        pmids = []
        scrape_file = open(self.scrape_filename, "r")
        for line in scrape_file:
            pmid_match = pattern["pmid"].search(line)
            if pmid_match:
                pmid = pmid_match.group("pmid")
                pmids.append(pmid)
        scrape_file.close()
        return(pmids)
        
    def get_unique_pmids(self):
        unique_pmids = list(set(self.get_pmids()))
        return(unique_pmids)
        
    def get_record_generator(self):
        scrape_file = open(self.scrape_filename, "r")
        record_text = ""
        is_in_header = True
        for line in scrape_file:
            record_start_match = pattern["record_start"].search(line)
            if record_start_match:
                if is_in_header:
                    is_in_header = False
                else:  
                    yield record_text
                record_text = line
            else:
                record_text += line
        scrape_file.close()
        yield record_text

@TimedCache(timeout_in_seconds=60*60*24*7)
def get_ae_pmids(source_filename=None):    
    ae_filename = "/Users/hpiwowar/Documents/Projects/Thesis/Data/ArrayExpress/scrape.txt"
    if not source_filename:
        source_filename = ae_filename
    scrape = ArrayExpressScrape(filename = source_filename)
    all_pmids = scrape.get_pmids()
    return(all_pmids)
    
@fieldname("in_arrayexpress")    
def in_arrayexpress(query_pmids, source_filename=None):
    all_pmids = get_ae_pmids(source_filename)
    in_ae_flags = ['1' if (pmid in all_pmids) else '0' for pmid in query_pmids]
    return(in_ae_flags)

from datasources import pubmed

@fieldname("in_ae_or_geo")    
def in_ae_or_geo(query_pmids, source_filename=None):
    in_ae_flags = in_arrayexpress(query_pmids, source_filename)
    in_geo_flags = pubmed.in_geo(query_pmids)
    in_either_flags = ['1' if (in_ae=='1' or in_geo=='1') else '0' for (in_ae, in_geo) in zip(in_ae_flags, in_geo_flags)]
    return(in_either_flags)
                
def get_record_dict(record):
    record_dict = defaultdict(str)
    record_dict['pmid']         = get_pmid_from_record(record)
    record_dict['date']         = get_date_from_record(record)
    record_dict['accession']    = get_accession_from_record(record)
    #record_dict['description']  = get_description_from_record(record)
    record_dict['description_length']  = get_description_length_from_record(record)
    record_dict['miame_score']  = get_miame_score_from_record(record)
    record_dict['design']       = get_design_from_record(record)
    record_dict['protocol']     = get_protocol_from_record(record)
    record_dict['factors']      = get_factors_from_record(record)
    record_dict['processed']    = get_processed_from_record(record)
    record_dict['raw']          = get_raw_from_record(record)    
    record_dict['species']      = get_species_from_record(record)
    record_dict['platform_accession'] = get_platform_accession_from_record(record)
    record_dict['is_affy']      = get_is_affy_from_record(record)
    record_dict['is_agilent']   = get_is_agilent_from_record(record)
    record_dict['has_experiment_type']= get_has_experiment_type_from_record(record)
    record_dict['num_samples']  = get_num_samples_from_record(record)
    record_dict['num_factors']  = get_num_factors_from_record(record)
    record_dict['num_attributes']   = get_num_attributes_from_record(record)
    record_dict['from_geo']     = get_from_geo_from_record(record)
    #record_dict.update(get_factors_dict_from_record(record))
    #record_dict.update(get_attributes_dict_from_record(record))
    #print record_dict
    return(record_dict)
    
def get_match(fieldname, text):
    re_pattern = pattern[fieldname]
    a_match = re_pattern.search(text)
    try:
        hit = a_match.group(fieldname)
    except AttributeError:
        hit = None
    return(hit)

def get_binary_from_bool(bool):
    if bool:
        return 1
    else:
        return 0

def get_int_from_string(str):
    try:
        return(int(str))
    except TypeError:
        return(None)
                    
def get_date_from_record(record):
    match = get_match("date", record)
    return(match)

def get_description_from_record(record):
    match = get_match("description", record)
    return(match)            

def get_description_length_from_record(record):
    match = get_match("description", record)
    try:
        field_length = len(match)
    except TypeError:
        field_length = 0
    return(field_length)            

def get_pmid_from_record(record):
    match = get_match("pmid", record)
    return(match)       

def get_accession_from_record(record):
    match = get_match("accession", record)
    return(match)       

def get_from_geo_from_record(record):
    match = get_match("from_geo", record)
    return(get_binary_from_bool(match))   
    
def get_num_samples_from_record(record):
    match = get_match("num_samples", record)
    return(get_int_from_string(match))

def get_species_from_record(record):
    match = get_match("species", record)
    return(match)  

def get_platform_accession_from_record(record):
    match = get_match("platform_accession", record)
    return(match)       
        
def get_is_affy_from_record(record):
    match = get_match("is_affy", record)
    return(get_binary_from_bool(match))       

def get_is_agilent_from_record(record):
    match = get_match("is_agilent", record)
    return(get_binary_from_bool(match))       

def get_has_experiment_type_from_record(record):
    match = get_match("experiment_type", record)
    has_info = match not in ["unknown experiment type", "transcription profiling, unknown experiment type"]
    return(get_binary_from_bool(has_info))       
            
def get_design_from_record(record):
    match = star_to_flag(get_match("design", record))
    return(match)  
    
def get_protocol_from_record(record):
    match = star_to_flag(get_match("protocol", record))
    return(match)  
    
def get_factors_from_record(record):
    match = star_to_flag(get_match("factors", record))
    return(match)  
    
def get_processed_from_record(record):
    match = star_to_flag(get_match("processed", record))
    return(match)  

def get_raw_from_record(record):
    match = star_to_flag(get_match("raw", record))
    return(match)  
    
def get_miame_score_from_record(record):
    score = get_design_from_record(record) + get_protocol_from_record(record) + \
        get_factors_from_record(record) + get_processed_from_record(record) + \
        get_raw_from_record(record)
    return(score)           
            
def star_to_flag(star):
    if star=="*":
        return 1
    else:
        return 0

def _split_list(list_text):
    try:
        split_list = list_text.split("\n")
    except AttributeError:
        split_list = []
    return(split_list)
    
def get_num_factors_from_record(record):
    factor_list_text = get_match("factor_list", record)
    factor_list = _split_list(factor_list_text)
    num_factors = len(factor_list)
    return(num_factors)  
                    
def get_factors_dict_from_record(record):
    factor_list_text = get_match("factor_list", record)
    factor_list = _split_list(factor_list_text)
    factors_dict = {}
    for factor_line in factor_list:
        try:
            factor_name, factor_value = factor_line.split("\t")
            factors_dict[factor_name.upper()] = 1
            #factors_dict[factor_name] = factor_value        
        except ValueError:
            pass
    return(factors_dict)        

def get_num_attributes_from_record(record):
    attribute_list_text = get_match("attribute_list", record)
    attribute_list = _split_list(attribute_list_text)
    num_attributes = len(attribute_list)
    return(num_attributes)  
                    
def get_attributes_dict_from_record(record):
    attribute_list_text = get_match("attribute_list", record)
    attribute_list = _split_list(attribute_list_text)
    attributes_dict = {}
    for attribute_line in attribute_list:
        try:
            attribute_name, attribute_value = attribute_line.split("\t")
            attributes_dict[attribute_name.upper()] = 1
            #attributes_dict[attribute_name] = attribute_value   
        except ValueError:
            pass     
    return(attributes_dict)        
    