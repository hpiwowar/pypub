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
from datasources import gender
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
def get_this_dir():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    return(this_dir)
        
# Shared test data
gold_query = ["Heather", "John", "Kira"]

class TestGender(object):

    def test_get_female_factors(self):
        response = gender.get_female_factors(gold_query)
        assert_equals(response, [9.3759999999999994, 0.026014568158168577, 2.6240000000000001])

    def test_is_female(self):
        response = gender.is_female(gold_query)
        assert_equals(response, ['1', '0', '1'])

    def test_is_male(self):
        response = gender.is_male(gold_query)
        assert_equals(response, ['0', '1', '0'])

  