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

   
class TestSMD(object):
    @online
    def test_smd_has_data_submission_no_hits(self):
        response = datasources.smd.has_data_submission([])
        assert_equals(response, [])
                
        pmids_that_do_not_pass_gold_filter = [pmid for pmid in gold_pmids if pmid not in test_data_smd_filtered_pmids]
        response = datasources.smd.has_data_submission(pmids_that_do_not_pass_gold_filter)
        all_zeros = ['0' for pmid in pmids_that_do_not_pass_gold_filter]
        assert_equals(response, all_zeros)
        
    @online
    def test_smd_has_data_submission(self):
        response = datasources.smd.has_data_submission(gold_pmids)
        assert_equals(response, test_data_smd_has_data)
