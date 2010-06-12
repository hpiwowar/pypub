import utils
import time
import sys
import os
import csv
import utils
from utils.cache import TimedCache

def get_callable(callable_name):
    """Takes a string and returns the runnable class/function/method/attribute.
    Imports methods.
    
    >>> a = get_callable("datetime.datetime")
    >>> a(2009, 4, 30)
    datetime.datetime(2009, 4, 30, 0, 0)
    """
    def get_name_without_most_specific_attribute(callable_name):
        parts = callable_name.split('.')
        module = ".".join(parts[:-1])
        return(module)

    def get_name_of_library(callable_name):
        module = get_name_without_most_specific_attribute(callable_name)
        return(module)

    def get_increasingly_specific_components(callable_name):
        parts = callable_name.split('.')    
        parts_without_top_level_module = parts[1:]
        return(parts_without_top_level_module)
    
    def get_most_specific_attribute(imported_module, callable_name):
        attribute = imported_module
        increasingly_specific_components = get_increasingly_specific_components(callable_name)
        for component in increasingly_specific_components:
            attribute = getattr(attribute, component)  
        return(attribute) 
    
    module = get_name_of_library(callable_name)
    m = __import__(module)
    callable = get_most_specific_attribute(m, callable_name)
    return callable

def csv_format(list_of_columns):
    list_of_rows = transpose(list_of_columns)
    return(list_of_rows)

def csv_write_to_file(file, input, dialect="excel"):
    # To make this a unittest, replace data_rows with canned data?
    for row in input:
        encoded_row = []
        for col in row:
            if col:
                try:
                    col = unicode(col).encode('utf-8', 'replace')
                except UnicodeDecodeError:
                    col = utils.unicode.clean_up_strange_unicode(col)
            encoded_row.append(col)
        csv.writer(file, dialect=dialect).writerow(encoded_row)
    return(file)

def collect_data_as_csv(ids, header_string):
    import StringIO 
    
    data = collect_data(ids, header_string)
    csv_data = csv_format(data)
    
    string_buffer = StringIO.StringIO()
    csv_write_to_file(string_buffer, csv_data)
    response = string_buffer.getvalue()
    string_buffer.close()
    return(response)

def get_getter(callable_name):
    callable_name = "datasources." + callable_name.strip()
    response = get_callable(callable_name)
    return response
    
def collect_data(ids, header_string):
    list_of_values = []
    populators = header_string.split(",")
    for populator in populators:
        print "\n*** Now working on " + populator.strip() + " ***"
        getter = get_getter(populator)
        getter_values = getter(ids)
        list_of_values.append([getter.fieldname] + getter_values)
    return(list_of_values)
    
def transpose(list_of_columns):
    rows = map(list, zip(*list_of_columns))
    return(rows)


def collect_data_batches_into_csv_file(query_pmids, 
                                            pubmed_request, 
                                            flat_file_to_put_it_in,
                                            start_number, 
                                            step_size=1000,
                                            max=None):                   
    if not max:
        max = len(query_pmids)

    write_to_file = True
    writer = None
    start = start_number

    start_time = time.asctime()       
    print "Now        ", start_time
    
    STEP = min(step_size, max)
    csv_data = ""
    failed_starts = []
    while (start < max): 
        print "\n_______PMID list from = %i to %i" %(start, start+STEP) 
        retry_count = 3
        while (retry_count > 0):
            try:
                new_csv_data = collect_data_as_csv(query_pmids[start:start+STEP], pubmed_request)                                      
                retry_count = 0
            except:
                print "\n" + "!"*20 + "FAILED on index %s" %(start) + "!"*20 + "\n\n"
                print "Unexpected error:", sys.exc_info()[0]
                new_csv_data = ""
                failed_starts.append(start)
                retry_count = retry_count - 1
        print "_________writing to file for PMID list from = %i to %i" %(start, start+STEP) 
        if write_to_file and new_csv_data:
            if not writer:
                writer = open(flat_file_to_put_it_in, "w")
            writer.write(new_csv_data)
            writer.flush()
        csv_data += new_csv_data
        start += STEP
        print "Started at ", start_time
        print "Now        ", time.asctime()
    
    #print "Storing cache"
    #TimedCache().store_cache()
    #print "Stored cache"
    
    if write_to_file:
        writer.close()

    print "Started at ", start_time
    print "Now ", time.asctime()
    
    print "Failed starts: ", failed_starts    
        
        
        
            