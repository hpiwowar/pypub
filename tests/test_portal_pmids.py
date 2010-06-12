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
import datasources.portal_pmids
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
# Shared test data
test_sourcedata_filename = "/Users/hpiwowar/Documents/Code/hpiwowar/pypub/trunk/src/tests/testdata/portal_pmids_sample.xls"
test_data_request = "portal_pmids.pmid, portal_pmids.found_by_highwire, portal_pmids.found_by_googlescholar, portal_pmids.found_by_scirus"
test_data_response = [['pmid', '19861542', '19863341', '10712937', '16418499', '1234567'], ['found_by_highwire', '1', '0', '0', '0', '0'], ['found_by_googlescholar', '0', '1', '0', '0', '0'], ['found_by_scirus', '0', '0', '1', '0', '0']]
gold_pmids = ['19861542', '19863341', '10712937', '16418499', '1234567']
test_data_found_by_highwire = ['1', '0', '0', '0', '0']
test_data_found_by_googlescholar = ['0', '1', '0', '0', '0']
test_data_found_by_scirus = ['0', '0', '1', '0', '0']
    
class TestPortalPMIDs(object):
    def test_portal_pmids_get_all_ids(self):
        response = datasources.portal_pmids.get_all_pmids(test_sourcedata_filename)
        assert_equals(len(response), 528)
        assert_equals(len(set(response)), 451)

    def test_portal_pmids_found_by_highwire(self):
        response = datasources.portal_pmids.found_by_highwire(gold_pmids, test_sourcedata_filename)
        assert_equals(response, test_data_found_by_highwire)

    def test_portal_pmids_found_by_scirus(self):
        response = datasources.portal_pmids.found_by_scirus(gold_pmids, test_sourcedata_filename)
        assert_equals(response, test_data_found_by_scirus)

    def test_portal_pmids_found_by_googlescholar(self):
        response = datasources.portal_pmids.found_by_googlescholar(gold_pmids, test_sourcedata_filename)
        assert_equals(response, test_data_found_by_googlescholar)

    def test_collect_data(self):
        # gold_pmids = datasources.portal_pmids.get_all_pmids()
        response = dataset.collect_data(gold_pmids, test_data_request)                                      
        assert_equals(response, test_data_response)
        