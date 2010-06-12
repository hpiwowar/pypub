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
import datasources.microarray_creating
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
    
class TestMicroarrayCreating(object):
    @online
    def test_microarray_creating_get_all_pmids(self):
        response = datasources.microarray_creating.get_all_pmids()
        assert_equals(len(response), 11602)

    @online
    def test_microarray_creating_is_microarray_data_creation(self):
        query_pmids = ['1234567', '19861542', '19863341', '10712937', '16418499']
        response = datasources.microarray_creating.is_microarray_data_creation(query_pmids)
        assert_equals(response, ['0', '1', '0', '0', '0'] )

