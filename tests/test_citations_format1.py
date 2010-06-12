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
from datasources import citations_format1
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
def get_this_dir():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    return(this_dir)
        
# Shared test data
gold_first_filename = os.path.join(get_this_dir(), 'testdata', 'citations_format1.csv')
gold_first_page = open(gold_first_filename, "r").read()
gold_first_citations = ['Acad Radiol|2002|9|S504|Kauczor|1', 'Acad Radiol|2002|9|513|Mikhelashvili-Browner|2', 'Acad Radiol|2002|9|1062|Burdette|3', 'Acta Biotheor|2002|50|281|Aubert|4', 'Acta Neurochir (Wien)|2002|144|279|Hoeller|5']

class TestCitationsFormat1(object):
    def test_get_citations_from_page(self):
        items_dict = citations_format1.get_citations_from_page(gold_first_page)
        lookup_lines = citations_format1.convert_items_to_lookup_strings(items_dict)
        assert_equals(lookup_lines[0:5], gold_first_citations)
    