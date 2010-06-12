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
from datasources import affiliation
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
def get_this_dir():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    return(this_dir)
        
# Shared test data
gold_pmids = ['16960149', '16973760', '17170127', '17404298']

class TestGender(object):

    def test_get_country(self):
        response = affiliation.country(gold_pmids)
        assert_equals(response, ['Spain', 'Sweden', 'France', 'USA'])

    def test_get_institution(self):
        response = affiliation.institution(gold_pmids)
        assert_equals(response, ['University of Navarra', 'Karolinska Institutet', 'Institut Gustave Roussy', 'Stanford University School of Medicine'] )
