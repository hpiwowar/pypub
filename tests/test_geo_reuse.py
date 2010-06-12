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
from tests import slow, online, notimplemented, acceptance
import dataset
import datasources
from datasources import geo_reuse
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()

gold_pmids = ['19629191', '19545436', '19432952', '19619298', '17601345', '19597778', '19447789', '18229690', '19594909', '19662677', '19014681', '19594911', '19096132', '19703314', '19657382', '18538735', '18603568', '19640299', '19235922', '19690572', '19571305', '19712474', '19736252', '19671526', '19509081', '19584098', '19622796', '19718279', '19351846', '19756046', '19698124', '19728865', '19737418', '19209693', '19723343', '19244110', '19732433', '12805549']
query_pmids = ['19432952', '19619298', '17170127', '17404298']
    
def _get_test_filename():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    datafile = os.path.join(this_dir, 'testdata', 'geo_usage_citations_sample.html')
    return(datafile)
    
class TestGeo_Reuse(object):
    def setup(self):
        self.filename = _get_test_filename()
        self.test_instance = geo_reuse.GeoReuse(filename=self.filename)
        
    def test_geo_reuse_get_pmids(self):
        pmids = self.test_instance.get_pmids()
        assert_equals(pmids, gold_pmids)

    def test_geo_reuse_is_reuse(self):
        test_data_arrayexpress_has_data = ['1', '1', '0', '0']
        response = datasources.geo_reuse.is_geo_reuse(query_pmids, filename=self.filename)
        assert_equals(response, test_data_arrayexpress_has_data)

        # Will use default location
        response = datasources.geo_reuse.is_geo_reuse(query_pmids)
        assert_equals(response, test_data_arrayexpress_has_data)
