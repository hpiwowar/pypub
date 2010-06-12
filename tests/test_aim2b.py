#!/usr/bin/env python
# encoding: utf-8
"""
Snappy documentation goes here
@author: Heather Piwowar
@contact:  hpiwowar@gmail.com
@status:  playing around
"""

from __future__ import with_statement
import sys
import os
import nose
from nose.tools import assert_equals
import fudge
from fudge.inspector import arg
from fudge import patched_context
from tests import slow, online, notimplemented, acceptance
import dataset
import datasources
import datasources.geo
import datasources.arrayexpress
import datasources.smd
import datasources.ochsner
import utils
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
# Shared test data
test_data_request = "pubmed.pubmed_id, geo.has_data_submission, arrayexpress.has_data_submission, smd.has_data_submission"
gold_pmids = ['16960149', '16973760', '17170127', '17404298']
test_data_geo_filter = "pubmed_gds[filter]"
test_data_geo_filtered_pmids = ['16960149', '17404298']
test_data_arrayexpress_filtered_pmids = ['17170127']
test_data_smd_filtered_pmids = ['17404298']
test_data_geo_has_data = ['1', '0', '0', '1']
test_data_arrayexpress_has_data = ['0', '0', '1', '0']
test_data_smd_has_data = ['0', '0', '0', '1']
test_data_pubmed_is_humans = ['1', '1', '1', '1']
test_data_pubmed_is_animals = ['0', '1', '0', '1']
test_data_pubmed_is_mice = ['0', '1', '0', '0']
test_data_pubmed_is_bacteria = ['0', '0', '0', '0']
test_data_pubmed_is_fungi = ['0', '0', '0', '0']
test_data_pubmed_is_cultured_cells = ['1', '0', '1', '0']
test_data_pubmed_is_cancer = ['1', '0', '0', '0']
test_data_has_geo_data_submission = [['pmid'] + gold_pmids, ['has_geo_data'] + test_data_geo_has_data]
test_data_collect_response = [['pmid'] + gold_pmids, 
                              ['has_geo_data'] + test_data_geo_has_data, 
                              ['has_arrayexpress_data'] + test_data_arrayexpress_has_data,
                              ['has_smd_data'] + test_data_smd_has_data] 
test_data_csv_format = [['pmid', 'has_geo_data'], ['16960149', '1'], ['16973760', '0'], ['17170127', '0'], ['17404298', '1']]
test_data_csv_string = 'pmid,has_geo_data\r\n16960149,1\r\n16973760,0\r\n17170127,0\r\n17404298,1\r\n'
test_data_soup_to_nuts = 'pmid,has_geo_data,has_arrayexpress_data,has_smd_data\r\n16960149,1,0,0\r\n16973760,0,0,0\r\n17170127,0,1,0\r\n17404298,1,0,1\r\n'
test_data_ochsner_found_geo_data = ['0', '0', '0', '0']
test_data_ochsner_found_arrayexpress_data = ['0', '0', '1', '0']
test_data_ochsner_found_smd_data = ['0', '0', '0', '1']
test_data_ochsner_other_gold_pmids = ['17510434', '17409432', '17308088', '18172295', '17200196', '17200196']
test_data_ochsner_found_journal_data = ['1', '0', '0', '0', '1', '1']
test_data_ochsner_found_other_data = ['0', '1', '1', '0', '0', '0']
test_data_ochsner_found_any_data = ['0', '0', '1', '1', '1', '1', '1', '0', '1', '1']
test_data_list_data_ids = ['', '', u'E-TABM-133', u'SMD-Experiment-Set-No_3827']
            
class TestInterface(object):
    def test_get_back_pmid(self):
        response = dataset.collect_data(gold_pmids, "pubmed.pubmed_id")
        assert_equals(response, [['pmid'] + gold_pmids])

    def test_csv_format(self):
        input = test_data_has_geo_data_submission
        response = dataset.csv_format(input)
        assert_equals(response, test_data_csv_format)

    def test_csv_file(self):
        import StringIO
        string_buffer = StringIO.StringIO()

        input = test_data_csv_format
        
        response = dataset.csv_write_to_file(string_buffer, input)
        response = string_buffer.getvalue()
        string_buffer.close()

        assert_equals(response, test_data_csv_string)

    @online
    def test_collect_data(self):
        response = dataset.collect_data(gold_pmids, test_data_request)
        assert_equals(response, test_data_collect_response)


class TestAcceptance(object):
    @acceptance
    @online
    def test_soup_to_nuts(self):
        response = dataset.collect_data_as_csv(gold_pmids, test_data_request)
        assert_equals(response, test_data_soup_to_nuts)
        
    @acceptance
    @online        
    def test_get_aim2b_part1_data(self, max=None):
        all_pmids = datasources.ochsner.get_all_pmids()
        if not max:
            max = len(all_pmids)
        large_data_request = """pubmed.pubmed_id, 
                               geo.has_data_submission, 
                               arrayexpress.has_data_submission, 
                               smd.has_data_submission,
                               ochsner.found_any_data_submission,
                               ochsner.found_geo_data_submission,                               
                               ochsner.found_arrayexpress_data_submission,                               
                               ochsner.found_smd_data_submission,
                               ochsner.found_journal_data_submission,
                               ochsner.found_other_data_submission,                               
                               ochsner.list_data_ids
                               """
        response = dataset.collect_data_as_csv(all_pmids[0:max], large_data_request)
        #print response
        FILENAME = "../results/aim2b_overview.csv"
        writer = open(FILENAME, "w")
        writer.write(response)
        writer.close()
        #assert_equals(len(response), 398)

    @acceptance
    def get_pubmed_data(self, max=None, pmids=None):
        if pmids:
            query_pmids = pmids
        else:
            all_pmids = datasources.ochsner.get_all_pmids()
            if not max:
                max = len(all_pmids)            
            query_pmids = all_pmids[0:max]

        pubmed_request = """pubmed.pubmed_id, 
                               ochsner.found_geo_data_submission,                               
                               ochsner.found_arrayexpress_data_submission,                               
                               ochsner.found_smd_data_submission,                                                                                             
                               ochsner.found_any_data_submission,                                                                                                                            
                               ochsner.list_data_ids,
                               pubmed.is_humans, 
                               pubmed.is_animals, 
                               pubmed.is_mice,                                
                               pubmed.is_fungi,
                               pubmed.is_bacteria, 
                               pubmed.is_plants, 
                               pubmed.is_viruses,                                
                               pubmed.is_cultured_cells,                                                               
                               pubmed.is_cancer,
                               pubmed.date_published, 
                               pubmed.authors, 
                               pubmed.journal,
                               pubmed.number_times_cited_in_pmc,
                               isi.impact_factor                              
                               """

        data = dataset.collect_data(query_pmids, pubmed_request)
        csv_data = dataset.csv_format(data)

        if False:
            FILENAME = "../../results/aim2b_part2_pubmed.txt"
            writer = open(FILENAME, "w")
            for row in csv_data:
                writer.write("\t".join([str(col) for col in row]))
                writer.write("\r\n")
            writer.close()
        assert_equals(len(csv_data), 1+len(query_pmids))
        return(csv_data)

    @acceptance    
    def get_arrayexpress_data(self, max=None, pmids=None):
        data = self.get_database_data("arrayexpress", max, pmids)
        return(data)

    @acceptance
    def get_geo_data(self, max=None, pmids=None):
        data = self.get_database_data("geo", max, pmids)
        return(data)

    @acceptance        
    def get_database_data(self, db, max=None, pmids=None, verbose=True):
        if pmids:
            query_pmids = pmids
        else:
            all_pmids = datasources.ochsner.get_all_pmids()
            if not max:
                max = len(all_pmids)            
            query_pmids = all_pmids[0:max]
        
        from_ochsner = datasources.ochsner.Ochsner(query_pmids).accession_numbers(db)
        if verbose:
            print from_ochsner
        
        if (db == "arrayexpress"):
            from_centralized_db = datasources.arrayexpress.accessions_from_pmids(query_pmids)
        elif (db == "geo"):
            from_centralized_db = datasources.pubmed.PubMed(query_pmids).geo_accession_numbers()
        if verbose:
            print from_centralized_db

        all_accessions = set(from_ochsner)
        all_accessions.update(from_centralized_db)

        if (db == "arrayexpress"):
            instances = datasources.arrayexpress.ArrayExpress(all_accessions)
        elif (db == "geo"):
            instances = datasources.geo.GEO(all_accessions)

        data_header = """accession_number,
                        pmids_from_links, 
                        pmids_from_links_in_ochsner_set,
                        in_ochsner,
                        pmid_from_ochsner,
                        pmid_from_links_or_ochsner,
                        release_date,
                        submission_date,
                        submitter, 
                        contributors,
                        species,
                        number_samples, 
                        array_design
                        """
                    
        data = instances.collect_data_transposed(data_header)
        print data

        return(data)

    @acceptance
    def test_merge_subset_data(self):
        PUBMED_TABLE = "pubmed_table"
        GEO_TABLE = "geo_table"        
        ARRAYEXPRESS_TABLE = "ae_table"                
        VERBOSE = True
        
        pmids = ['17975066', '17105813']
        
        pubmed_data = self.get_pubmed_data(pmids=pmids)
        print pubmed_data
        
        geo_data = self.get_geo_data(pmids=pmids)        
        print geo_data

        arrayexpress_data = self.get_arrayexpress_data(pmids=pmids)        
        print arrayexpress_data
        

    #@acceptance
    def test_merge_data(self):
        mymax = None
        DB_NAME = "temp.db"
        PUBMED_TABLE = "pubmed_table"
        GEO_TABLE = "geo_table"        
        ARRAYEXPRESS_TABLE = "ae_table"                
        VERBOSE = True

        TimedCache().store_cache()
        
        pubmed_data = self.get_pubmed_data(max=mymax)
        assert(len(pubmed_data) > 3)
        table_create_command = utils.dbimport.get_table_insert_command(PUBMED_TABLE, pubmed_data)
        print table_create_command
        
        if False:
            utils.dbimport.drop_table(DB_NAME, PUBMED_TABLE, VERBOSE)
            utils.dbimport.write_to_db(DB_NAME, PUBMED_TABLE, pubmed_data, VERBOSE)
            db_response = utils.shell.run_in_sqlite(DB_NAME, "select count(pmid) from " + PUBMED_TABLE)
            assert_equals(db_response, "%s\n" %(len(pubmed_data) - 1))

            TimedCache().store_cache()
        
            geo_data = self.get_geo_data(max=mymax)        
            utils.dbimport.drop_table(DB_NAME, GEO_TABLE, VERBOSE)        
            utils.dbimport.write_to_db(DB_NAME, GEO_TABLE, geo_data, VERBOSE)
            db_response = utils.shell.run_in_sqlite(DB_NAME, "select count(geo_pmid_from_links_or_ochsner) from " + GEO_TABLE)
            assert_equals(db_response, "%s\n" %(len(geo_data) - 1))

            TimedCache().store_cache()
        
            arrayexpress_data = self.get_arrayexpress_data(max=mymax)        
            utils.dbimport.drop_table(DB_NAME, ARRAYEXPRESS_TABLE, VERBOSE)        
            utils.dbimport.write_to_db(DB_NAME, ARRAYEXPRESS_TABLE, arrayexpress_data, VERBOSE)
            db_response = utils.shell.run_in_sqlite(DB_NAME, "select count(arrayexpress_pmid_from_links_or_ochsner) from " + ARRAYEXPRESS_TABLE)
            assert_equals(db_response, "%s\n" %(len(arrayexpress_data) - 1))
        
            TimedCache().store_cache()
        
            # Join the tables on the fields named pmid
            #execute ("join ...")
            join_command = """.headers ON; SELECT * FROM %s pubmed, %s geo  %s ae WHERE pubmed.pmid = geo.geo_pmid_from_links_or_ochsner AND pubmed.pmid = ae.arrayexpress_pmid_from_links_or_ochsner;""" %(PUBMED_TABLE, GEO_TABLE, ARRAYEXPRESS_TABLE)
            join_results = utils.shell.run_in_sqlite(DB_NAME, join_command, VERBOSE)
    #SELECT * FROM pubmed_table pubmed 
    #LEFT OUTER JOIN geo_table geo ON pubmed.pmid = geo.geo_pmid_from_links_or_ochsner 
    #LEFT OUTER JOIN ae_table ae ON pubmed.pmid = ae.arrayexpress_pmid_from_links_or_ochsner
        
            print "******** Join results *************"
            print join_results
        
        
        #rm temp.db ???
        
                  
            
    def write_to_file(self, data, filename):
        file = open(filename, "w")
        csv_data = dataset.csv_format(data)
        for row in csv_data:
            joined_row_contents = []
            for col in row:
                if col is None:
                    col = u""
                if col==True:
                    col = u"1"
                if col==False:
                    col = u"0"

                try:
                    file.write(str(col))
                except UnicodeEncodeError:
                    new_string = utils.unicode.clean_up_strange_unicode(col)
                    file.write(new_string)                    

                file.write(u"\t")

            file.write(u"\r\n")        
        file.close()
        return(csv_data)
                        
    
