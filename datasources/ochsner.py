import sys
import os
import re
import xlrd
from utils.cache import TimedCache
import datasources
from datasources import fieldname, datasourcesError, DataSource, GEO_ACCESSION_PATTERN, ARRAYEXPRESS_ACCESSION_PATTERN

class Ochsner(DataSource):
    def __init__(self, ids=[]):
        super(Ochsner, self).__init__(ids, "ochsner")

    def all_pmids(self):
        return(_get_ochsner_pmid_column())
        
    def all_accession_numbers(self, db):
        response = self.accession_numbers(db, self.all_pmids())
        return(response)

    def accession_numbers(self, db, pmids=None):
        if not pmids:
            pmids = self.ids
            
        data_ids_string = ";".join(list_data_ids(pmids))      
        if db=="geo":
            accession_pattern = GEO_ACCESSION_PATTERN
        elif db=="arrayexpress":
            accession_pattern = ARRAYEXPRESS_ACCESSION_PATTERN            
        else:
            raise NotImplementedError
        list_of_accessions = re.findall(accession_pattern, data_ids_string)
        return(list_of_accessions)        
        
    def pmid_for_data_location(self, id):
        if not id:
            return(None)
        combo = zip(_get_ochsner_pmid_column(), _get_ochsner_data_location_column())
        accession_pattern = r"\b" + id + r"\b"
        matching_pmid = None
        for (pmid, data_location_string) in combo:
            if re.search(accession_pattern, data_location_string):
                matching_pmid = pmid
        return(matching_pmid)

def _get_local_ochsner_filename():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    datafile = os.path.join(this_dir, '..', 'rawdata', 'ochsner', 'nmeth1208-991-S1.xls')
    return(datafile)

def _get_ochsner_pmid_column():
    ochsner_filename = _get_local_ochsner_filename()
    wb = xlrd.open_workbook(ochsner_filename)
    sh = wb.sheet_by_index(0)
    pmid_column = [str(cell)[:-2] for cell in sh.col_values(1)]
    return(pmid_column)

def _get_ochsner_data_location_column():
    ochsner_filename = _get_local_ochsner_filename()
    wb = xlrd.open_workbook(ochsner_filename)
    sh = wb.sheet_by_index(0)
    data_location_column = [cell for cell in sh.col_values(2)]
    return(data_location_column)
    
def _map_booleans_to_flags(list_of_True_False):
    mapping = {True:'1', False:'0'}
    list_of_flags = [mapping[i] for i in list_of_True_False]
    return(list_of_flags)

def _get_flags_for_pattern(query_pmids, data_location_query_string):
    if not query_pmids:
        return([])
    filtered_pmids = filter_pmids(query_pmids, data_location_query_string)
    pmid_passes_filter = [(pmid in filtered_pmids) for pmid in query_pmids]   
    flag_pmid_passes_filter = _map_booleans_to_flags(pmid_passes_filter)
    return(flag_pmid_passes_filter)

@fieldname("ochsner_found_smd_data")    
def found_smd_data_submission(query_pmids):
    matching_pattern = "SMD-"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("ochsner_found_arrayexpress_data")    
def found_arrayexpress_data_submission(query_pmids):
    matching_pattern = "E-"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)
    
@fieldname("ochsner_found_geo_data")    
def found_geo_data_submission(query_pmids):
    matching_pattern = "GSE"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("ochsner_found_other_data")    
def found_other_data_submission(query_pmids):
    matching_pattern = "www3.mdanderson.org|naturalvariation.org|\.edu\W|www.functionalglycomics.org|arrayconsortium.tgen.org|caarraydb.nci.nih.gov|UNC-MD-Experiment-Set|www.crukdmf.icr.ac.uk"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("ochsner_found_journal_data")    
def found_journal_data_submission(query_pmids):
    matching_pattern = "pnas.org|mcb.asm.org|jbc.org|aacrjournals.org|bloodjournal.hematologylibrary.org|ajp.amjpathol.org"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("ochsner_found_any_data")
def found_any_data_submission(query_pmids):
    """Returns a list of flags (0 or 1) indicating whether the PubMed IDs are listed as
    in the Ochsner dataset as having publicly available datasets
    """
    matching_pattern = "\S"
    flag_pmid_passes_filter = _get_flags_for_pattern(query_pmids, matching_pattern)
    return(flag_pmid_passes_filter)

@fieldname("ochsner_data_ids")
def list_data_ids(query_pmids):
    pmid_column = _get_ochsner_pmid_column()
    data_location_column = _get_ochsner_data_location_column()
    filtered_pmids = []
    for pmid in query_pmids:
        rownum = pmid_column.index(pmid)
        filtered_pmids.append(data_location_column[rownum])
    return(filtered_pmids)
             
def filter_pmids(query_pmids, data_location_query_string):
    pmid_column = _get_ochsner_pmid_column()    
    if data_location_query_string:
        data_location_column = _get_ochsner_data_location_column()    
        pmid_rownum_column = [(rownum, pmid) for rownum, pmid in enumerate(pmid_column)]
        filtered_pmid_column = [pmid for (rownum, pmid) in pmid_rownum_column if re.search(data_location_query_string, data_location_column[rownum])]
    else:
        filtered_pmid_column = pmid_column
    filtered_pmids = [pmid for pmid in filtered_pmid_column if pmid in query_pmids]        
    return(filtered_pmids)
    
def get_all_pmids():
    pmid_column_without_header = _get_ochsner_pmid_column()[1:]
    return(pmid_column_without_header)
