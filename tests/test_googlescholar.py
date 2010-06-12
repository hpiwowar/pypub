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
from datasources import googlescholar
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
def get_this_dir():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    return(this_dir)
        
# Shared test data
gold_first_filename = os.path.join(get_this_dir(), 'testdata', 'scholar_gold_results.html')
gold_first_page = open(gold_first_filename, "r").read()
gold_first_citations = ['Cell|2007|||Takahashi K|test', 'Cell|2007|||Siepka SM|test', 'Cell|2007|||Zhao Y|test', 'Cell|2007|||Guenther MG|test', 'Cell|2007|||Camblong J|test']

class TestGoogleScholar(object):
    def test_get_citations_from_page(self):
        items_dict = googlescholar.get_citations_from_page(gold_first_page)
        lookup_lines = googlescholar.convert_items_to_lookup_strings(items_dict)
        assert_equals(lookup_lines[0:5], gold_first_citations)
    
    def test_get_citation_file_from_pages_in_directory(self):
        glob_pattern = os.path.join(get_this_dir(), 'testdata', 'google_scholar', "*", "*.html")
        list_of_citation_strings = googlescholar.get_citations_from_directories(glob_pattern, "googlescholar;")
        for str in list_of_citation_strings[0:10]:
            print str
        assert_equals(len(list_of_citation_strings), 616)
        assert_equals(list_of_citation_strings[0:5], ['Cell|2007|||Takahashi K|googlescholar;fmeasure35_not', 'Cell|2007|||Siepka SM|googlescholar;fmeasure35_not', 'Cell|2007|||Zhao Y|googlescholar;fmeasure35_not', 'Cell|2007|||Guenther MG|googlescholar;fmeasure35_not', 'Cell|2007|||Camblong J|googlescholar;fmeasure35_not'])
        
        
    