#!/usr/bin/env python
# encoding: utf-8
"""
Snappy documentation goes here
@author: Heather Piwowar
@contact:  hpiwowar@gmail.com
@status:  playing around
"""

import sys
import os
import nose
from nose.tools import assert_equals
from tests import slow, online, notimplemented, acceptance
import dataset
import datasources
import datasources.geo
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
# Shared test data
gold_pmids = ['16960149', '16973760', '17170127', '17404298', '17579077']
test_data_geo_filter = "pubmed_gds[filter]"
test_data_geo_filtered_pmids = ['16960149', '17404298', '17579077']
test_data_geo_has_data = ['1', '0', '0', '1', '1']
test_data_has_geo_data_submission = [['pmid'] + gold_pmids, ['has_geo_data'] + test_data_geo_has_data]
test_data_geo_accession_number = ['GSE5316', None, None, 'GSE8521', 'GSE7586']
test_data_geo_number_samples = [u'48', None, None, u'16', u'20']
test_data_geo_release_date = [u'Feb 05, 2007', None, None, u'Jul 19, 2007', u'Jul 01, 2007']
test_data_geo_submitter = [u'Jose Angel Martinez Climent', None, None, None, 'Atis Muehlenbachs']
test_data_geo_array_design = [u'GPL3789: UCSF HUMAN 1.14', None, None, u'GPL5620: SHGS', u'GPL570: [HG-U133_Plus_2] Affymetrix Human Genome U133 Plus 2.0 Array']
test_data_geo_species = [u"Homo sapiens", None, None, u"Homo sapiens", u'Homo sapiens']
test_data_geo_contributors = [None, None, None, u'Kim S', u'Muehlenbachs A']
test_data_geo_submission_date = [u'Jul 14, 2006', None, None, u'Jul 18, 2007', u'Apr 23, 2007']
test_data_geo_in_ochsner = [False, False, False, False, True]
test_data_geo_pmids = [[u'16960149'], [], [], [u'17404298'], [u'17579077']]
test_data_geo_pmid_if_in_ochsner = [[u'16960149'], [], [], [u'17404298'], [u'17579077']]
test_data_geo_ochsner_pmid = [[], [], [], [], ['17579077']]
test_data_geo_pmid_from_link_or_ochsner = ['16960149', None, None, '17404298', '17579077']

class TestGEO(object):
    def setup(self):
        self.gold_geo_ids = datasources.pubmed.PubMed(gold_pmids).geo_accession_numbers()
        self.geo_source = datasources.geo.GEO()
        
    @online
    def test_geo_has_data_submission_no_hits(self):
        response = datasources.geo.has_data_submission([])
        assert_equals([], response)
                
        pmids_that_do_not_pass_gold_filter = [pmid for pmid in gold_pmids if pmid not in test_data_geo_filtered_pmids]
        response = datasources.geo.has_data_submission(pmids_that_do_not_pass_gold_filter)
        all_zeros = ['0' for pmid in pmids_that_do_not_pass_gold_filter]
        assert_equals(response, all_zeros)
        
    @online
    def test_geo_has_data_submission(self):
        response = datasources.geo.has_data_submission(gold_pmids)
        assert_equals(response, test_data_geo_has_data)

    def test_geo_accession_number(self):
        response = [self.geo_source.accession_number(id) for id in self.gold_geo_ids]                
        assert_equals(response, test_data_geo_accession_number)

    def test_geo_number_samples(self):
        response = [self.geo_source.number_samples(id) for id in self.gold_geo_ids]                
        assert_equals(response, test_data_geo_number_samples)

    def test_geo_release_date(self):
        response = [self.geo_source.release_date(id) for id in self.gold_geo_ids]                
        assert_equals(response, test_data_geo_release_date)

    def test_geo_submitter(self):
        response = [self.geo_source.submitter(id) for id in self.gold_geo_ids]                
        assert_equals(response, test_data_geo_submitter)

    def test_geo_array_design(self):
        response = [self.geo_source.array_design(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_array_design)

    def test_geo_species(self):
        response = [self.geo_source.species(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_species)

    def test_geo_contributors(self):
        response = [self.geo_source.contributors(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_contributors)

    def test_geo_submission_date(self):
        response = [self.geo_source.submission_date(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_submission_date)
       
    def test_geo_in_ochsner(self):
        response = [self.geo_source.in_ochsner(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_in_ochsner)

    def test_geo_ochsner_pmid(self):
        response = [self.geo_source.pmid_from_ochsner(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_ochsner_pmid)

    def test_geo_linked_pmids_in_ochsner(self):
        response = [self.geo_source.pmids_from_links_in_ochsner_set(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_pmid_if_in_ochsner)

    def test_geo_linked_pmids(self):
        response = [self.geo_source.pmids_from_links(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_pmids)

    def test_geo_multiple_linked_pmids(self):
        response = self.geo_source.pmids_from_links('GSE2658')     
        assert_equals(response, [u'16688228', u'16728703', u'17023574'])     
        
    def test_data_geo_pmid_from_links_or_ochsner(self):
        response = [self.geo_source.pmid_from_links_or_ochsner(id) for id in self.gold_geo_ids]        
        assert_equals(response, test_data_geo_pmid_from_link_or_ochsner)


        
       
        
               

       

