import sys
import os
import re
import time
from collections import defaultdict
from utils.cache import TimedCache
import utils.dbimport
import datasources
from datasources import fieldname, datasourcesError, DataSource
from datasources import pubmed

@fieldname("grant_numbers")
def grant_numbers(pmids):
    grants = pubmed.grants(pmids)
    response = [grant_string.upper().replace(" ", "") for grant_string in grants]
    return(response)    

@fieldname("num_grant_numbers")
def num_grant_numbers(pmids):
    grants = grant_numbers(pmids)
    response = []
    for grant_string in grants:
        if grant_string:
            num_grants = 1 + grant_string.count(";")
        else:
            num_grants = 0
        response.append(num_grants)
    return(response)    
    
@fieldname("nih_is_nci")
def nih_is_nci(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("CA") for grant_string in grants]
    return(counts)    

@fieldname("nih_is_niehs")
def nih_is_niehs(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("ES") for grant_string in grants]
    return(counts)    

@fieldname("nih_is_nichd")
def nih_is_nichd(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("HD") for grant_string in grants]
    return(counts)    

@fieldname("nih_is_ninds")
def nih_is_ninds(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("NS") for grant_string in grants]
    return(counts)    

@fieldname("nih_is_niddk")
def nih_is_niddk(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("DK") for grant_string in grants]
    return(counts)    

@fieldname("nih_is_nigms")
def nih_is_nigms(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("GM") for grant_string in grants]
    return(counts)    

@fieldname("nih_is_niaid")
def nih_is_niaid(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("AI") for grant_string in grants]
    return(counts)    

@fieldname("nih_is_ncrr")
def nih_is_ncrr(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("RR") for grant_string in grants]
    return(counts)    

@fieldname("nih_is_nhlbi")
def nih_is_nhlbi(pmids):
    grants = grant_numbers(pmids)
    counts = [grant_string.count("HL") for grant_string in grants]
    return(counts)    

def get_grant_serial_number_from_pubmed(raw_grant_number_text):
    # break out award code like http://ocga3.ucsd.edu/Proposal_Preparation/Federal/NIH/Grants/Basics/NIH_Grants_Grant_Identification_Numbering_System.htm

    serial_number = Word(nums, min=5, max=6)
    addLeadingZeroIfShort = lambda tokens : tokens[0] if len(tokens[0])>5 else "0"+tokens[0]
    serial_number.setParseAction(addLeadingZeroIfShort)
    
    nih_application_type = Word(nums, exact=1)
    nih_activity_code = Word(alphanums, exact=3)
    nih_institute = Word(alphas, exact=2)
    grant_number_year = Word(nums, exact=2)
    is_amendment = Word(alphanums)
    serial_number_pattern = (Optional(nih_institute("grant_nih_institute")) + 
                            serial_number("grant_serial_number"))
           
    if raw_grant_number_text:
        try:
            grant_number_string = str(raw_grant_number_text)
            grant_serial_number_values = serial_number_pattern.searchString(grant_number_string)
            response =  grant_serial_number_values[0].asDict()
        except Exception, e:
            print e
            print "Couldn't parse grant serial number ", grant_number_text
            response = {}
            
    return(response)
    
    
from pyparsing import *    
import csv
import pprint

DASH = Suppress("-")
COMMA = Suppress(",")
joinTokens = lambda tokens : "".join(tokens)
joinWithSpace = lambda tokens : " ".join(tokens)
stripCommas = lambda tokens: tokens[0].replace(",","")
convertToFloat = lambda tokens: float(tokens[0])
convertToInt = lambda tokens: int(tokens[0])

decimalNumber = Suppress("$") + Word(nums+",")
decimalNumber.setParseAction( joinTokens, stripCommas, convertToFloat )
integerNumber = Word(nums)
integerNumber.setParseAction(convertToInt)

name_word = OneOrMore(Word(alphas+"'-", min=2)).setParseAction(joinWithSpace)  # + unicode?
name_initial = Word(alphas+"'-", max=2)   # + unicode?
pi_name = name_word("pi_last_name") + "," + name_word("pi_first_name") + Optional(name_initial)
pi_name_join = pi_name.copy()
pi_name_join.setParseAction(joinWithSpace)

fiscal_year_pattern = Suppress("fy") + integerNumber

# break out award code like 
# http://ocga.ucsd.edu/Proposals/NIH/Grants/Identification_Numbering_System.htm
serial_number = Word(nums, min=5, max=6)
nih_application_type = Word(nums, exact=1)
nih_activity_code = Word(alphanums, exact=3)
nih_institute = Word(alphas, exact=2)
grant_number_year = Word(nums, exact=2)
is_amendment = Word(alphanums)
grant_number = (Optional(nih_application_type("nih_application_type")) +
    Optional(nih_activity_code("nih_activity_code")) + 
    nih_institute("nih_institute") + 
    serial_number("serial_number") + 
    Optional("-" +
        Or ((grant_number_year("grant_number_year")) + 
                Optional(is_amendment("is_amendment")),
            Word(nums, exact=3)))  # some legacy number at the end of old grant numbers?
    )            
grant_number_join = grant_number.copy()
grant_number_join.setParseAction(joinTokens)

parse_list = [
    ("fiscal_year", fiscal_year_pattern),  
    ("organization_name", OneOrMore(Word(printables)).setParseAction(joinWithSpace)),
    ("grant_number", grant_number_join),
    ("nih_reference_number", integerNumber),        
    ("pi_name", pi_name_join),
    ("project_title", (OneOrMore(Word(printables))).setParseAction(joinWithSpace)),
    ("dept_name", (OneOrMore(Word(printables))).setParseAction(joinWithSpace)),
    ("dept_name2", (OneOrMore(Word(printables))).setParseAction(joinWithSpace)),
    ("dept_name3", (OneOrMore(Word(printables))).setParseAction(joinWithSpace)),        
    ("award_amount", decimalNumber),
    ("city", (OneOrMore(Word(printables))).setParseAction(joinWithSpace)),
    ("state_or_country", (OneOrMore(Word(alphas))).setParseAction(joinWithSpace)),
    ("zip_code", Word(nums+'-')),
    ("is_medical_school", Word(alphas)),
    ("medical_school_name", (OneOrMore(Word(printables))).setParseAction(joinWithSpace)),
    ("medical_school_location", (OneOrMore(Word(printables))).setParseAction(joinWithSpace)),
    ("ranking_category", (OneOrMore(Word(alphas))).setParseAction(joinWithSpace)),
    ("multi_campus", Word(alphas)),
    ("main_campus", (OneOrMore(Word(alphas))).setParseAction(joinWithSpace))
]
        
def get_parsedict(fiscal_year): 
    ordered_keys = [a for (a, b) in parse_list]
    # modifications for earlier versions        
    if (fiscal_year == 2003):
        ordered_keys.remove("nih_reference_number")
        ordered_keys.remove("dept_name")            
        ordered_keys.remove("is_medical_school")
        ordered_keys.remove("medical_school_name")
        ordered_keys.remove("medical_school_location")
        ordered_keys.remove("ranking_category")
        ordered_keys.remove("multi_campus")
        ordered_keys.remove("main_campus")                                                            
    elif (fiscal_year == 2004):
        ordered_keys.remove("dept_name")                        
        ordered_keys.remove("ranking_category")
        ordered_keys.remove("multi_campus")
        ordered_keys.remove("main_campus")                                                                
    elif (fiscal_year == 2008):
        ordered_keys.remove("nih_reference_number")
        ordered_keys.remove("dept_name3")                        
        ordered_keys.remove("main_campus")                                                                
    parse_dict = dict(parse_list)
    return (ordered_keys, parse_dict)

def get_detailed_fields(parsed_input):
    extra_items = {}
    #pprint.pprint(parsed_input)
    grant_number_text = parsed_input["grant_number"]
    if grant_number_text:
        grant_number_items = grant_number.parseString(grant_number_text)
        extra_items.update(grant_number_items.asDict())
    pi_name_text = parsed_input["pi_name"]
    if pi_name_text:
        pi_name_items = pi_name.parseString(pi_name_text)        
        extra_items.update(pi_name_items.asDict())            
    return(extra_items)


def parse_nih_grant_raw_data(filename, db_name=None, table_name=None):
    for t, s, e in fiscal_year_pattern.scanString(filename):
        fiscal_year = t[0]
                    
    (ordered_keys, parse_dict) = get_parsedict(fiscal_year)

    # skip the fiscal year entry... get that from the filename
    csvReader = csv.DictReader(open(filename, "rU"), fieldnames=ordered_keys[1:], delimiter=',', quotechar='"')   
    csvReader.next()  # skip header row
    #csvReader.next()  # skip 2 header rows
    
    count = 0
    if db_name:
        db = utils.dbimport.get_connection(db_name)

    for line in csvReader:
        parsed_output = {}
        parsed_output[ordered_keys[0]] = fiscal_year
        for field in ordered_keys[1:]:
            out = None  # default
            if line[field]:
                results = [t for (t,s,e) in parse_dict[field].scanString(line[field])]
                if results: 
                    out = results[0][0]
            parsed_output[field] = out
            #print "%s: %s" % (field, str(out))

        # Skip adding this entry if no grant number info
        if not parsed_output["grant_number"]:
            print "Skipping this row because no grant number:"
            print line["grant_number"]
            continue
        else:
            print count, parsed_output["grant_number"]
            count += 1
                            
        parsed_output.update(get_detailed_fields(parsed_output))
        parsed_output["timestamp"] = time.time()
        #pprint.pprint(parsed_output)
        if db_name:
            command = utils.dbimport.get_table_insert_command_from_dict(table_name, parsed_output)
            print command
            utils.dbimport.execute_python_db(db, command, verbose=False)
    if db_name:
        db.close()
    return(count)

def insert_into_db(db_name, table_name, insert_dict):
    db = utils.dbimport.get_connection(db_name)
    command = utils.dbimport.get_table_insert_command_from_dict(table_name, insert_dict)
    utils.dbimport.execute_python_db(db, command, verbose=False)
 
def get_pmid_grant_lists(db_name):
    db = utils.dbimport.get_connection(db_name)
    c = db.cursor()
    c.execute("SELECT * FROM aim3_pmid_grant_list;")
    rows = c.fetchall()
    return(rows)

def update_pmid_grant_lists(db_name):
    pmid_grant_lists = get_pmid_grant_lists(db_name)
    for (pmid, grant_list) in pmid_grant_lists:
        grants = grant_list.split(";")
        for grant in grants:
            print pmid, grant
            # insert this into database
            command = 'insert into aim3_pmid_grants (pmid, grant_id) values ("%s", "%s");' %(pmid, grant)
            db = utils.dbimport.get_connection(db_name)
            utils.dbimport.execute_python_db(db, command, verbose=False)

def update_grant_id(db_name, pmid, grant_raw, grant_id):
    command = 'update aim3_pmid_grants set grant_id="%s" where pmid="%s" and grant_raw="%s";' %(grant_id, pmid, grant_raw)
    db = utils.dbimport.get_connection(db_name)
    utils.dbimport.execute_python_db(db, command, verbose=False)
    
def get_pmid_grant_raw(db_name):
    db = utils.dbimport.get_connection(db_name)
    c = db.cursor()
    c.execute("SELECT pmid, grant_raw FROM aim3_pmid_grants;")
    rows = c.fetchall()
    return(rows)
        
def get_grant_serial_number_from_pubmed(raw_grant_number_text):
    # break out award code like http://ocga3.ucsd.edu/Proposal_Preparation/Federal/NIH/Grants/Basics/NIH_Grants_Grant_Identification_Numbering_System.htm

    serial_number = Word(nums, min=5, max=6)
    addLeadingZeroIfShort = lambda tokens : tokens[0] if len(tokens[0])>5 else "0"+tokens[0]
    serial_number.setParseAction(addLeadingZeroIfShort)
    
    nih_application_type = Word(nums, exact=1)
    nih_activity_code = Word(alphanums, exact=3)
    nih_institute = Word(alphas, exact=2)
    grant_number_year = Word(nums, exact=2)
    is_amendment = Word(alphanums)
    
    DASH = Suppress("-")

    serial_number_pattern = nih_institute("grant_nih_institute") + Optional(DASH) + serial_number("grant_serial_number")
           
    if raw_grant_number_text:
        try:
            grant_number_string = str(raw_grant_number_text)
            grant_serial_number_values = serial_number_pattern.searchString(grant_number_string)
            response_dict =  grant_serial_number_values[0].asDict()
            grant_id = response_dict["grant_nih_institute"] + response_dict["grant_serial_number"]         
        except Exception, e:
            print e
            print "!!!!!!!! Couldn't parse grant serial number ", raw_grant_number_text
            grant_id = ""
            
    return(grant_id)

