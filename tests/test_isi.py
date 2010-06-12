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
import datasources.isi
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
# Shared test data
gold_pmids = ['16960149', '16973760', '17170127', '17404298']
test_data_impact_factors = [10.896000000000001, 5.3369999999999997, 10.896000000000001, 6.0679999999999996]


class TestISI(object):
    def test_impact_factor(self):
        response = datasources.isi.impact_factor([])
        assert_equals(response, [])

        response = datasources.isi.impact_factor(['dummy_pmid1', 'dummy_pmid2'])
        assert_equals(response, [None, None])

        response = datasources.isi.impact_factor(gold_pmids)
        assert_equals(response, test_data_impact_factors)
