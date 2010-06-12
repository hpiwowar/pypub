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
import re
from nose.tools import assert_equals
from tests import slow, online, notimplemented, acceptance
import dataset
import datasources
from datasources import grants
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
# Shared test data
gold_aim3_pmids = ['20031609', '19843711', '11027315', '10737792']

def _get_test_filename():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    datafile = os.path.join(this_dir, 'testdata', 'nih_grant_allorgs_fy2008_sample.csv')
    return(datafile)
    
class TestGrants(object):
    def setup(self):
        #filename = _get_test_filename()
        #db_name = ":memory:"
        #self.test_instance = authority_excerpt.AuthorityExcerpt(db_name=db_name, filename=filename, do_import=True)
        pass
        
    def test_setup(self):
        #number_of_rows = self.test_instance.get_number_of_rows()
        #sample = open(_get_test_filename(), "r").read()
        #gold_pattern = "[^_\d]\d+_\d+"
        #gold_number_of_rows = len(re.findall(gold_pattern, sample))
        #assert_equals(number_of_rows, gold_number_of_rows)
        pass
        
#                       grants.num_grant_numbers,
#                       grants.nih_is_nichd,
#                       grants.nih_is_niehs,
#                       grants.nih_is_ninds,
#                       grants.nih_is_niddk,
#                       grants.nih_is_nigms,
#                       grants.nih_is_nci,
#                       grants.nih_is_niaid,
#                       grants.nih_is_nccr,
#                       grants.nih_is_nhlbi,
        
    def test_grant_numbers(self):
        response = grants.grant_numbers(gold_aim3_pmids)
        assert_equals(response, ['HL072488;P01HL077180;R33HL087345;T32HL007227', '', 'GM08295-11;GM09738;HG00983', 'CA20525;CA75125'])

    def test_num_grant_numbers(self):
        response = grants.num_grant_numbers(gold_aim3_pmids)
        assert_equals(response, [4, 0, 3, 2])

    def test_nih_is_nci(self):
        response = grants.nih_is_nci(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 2])

    def test_nih_is_niehs(self):
        response = grants.nih_is_niehs(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_nih_is_nichd(self):
        response = grants.nih_is_nichd(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_nih_is_niddk(self):
        response = grants.nih_is_niddk(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_nih_is_nigms(self):
        response = grants.nih_is_nigms(gold_aim3_pmids)
        assert_equals(response, [0, 0, 2, 0])

    def test_nih_is_niaid(self):
        response = grants.nih_is_niaid(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_nih_is_ncrr(self):
        response = grants.nih_is_ncrr(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_nih_is_nhlbi(self):
        response = grants.nih_is_nhlbi(gold_aim3_pmids)
        assert_equals(response, [4, 0, 0, 0])

    def test_nih_is_ninds(self):
        response = grants.nih_is_ninds(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])
        
    def test_parse_nih_grant_raw_data(self):
        filename = _get_test_filename()
        response = grants.parse_nih_grant_raw_data(filename)
        gold_response = {'serial_number': '023770', 'pi_first_name': 'Roberto', 'fiscal_year': 2008, 'medical_school_name': None, 'state_or_country': 'NORTH CAROLINA', 'nih_activity_code': 'R01', 'multi_campus': 'No', 'medical_school_location': None, 'dept_name2': 'EARTH SCIENCES/RESOURCES', 'pi_last_name': 'Cabeza', 'city': 'DURHAM', 'project_title': 'Relational Memory and Aging: Role of Prefrontal Lobe', 'is_medical_school': 'Yes', 'dept_name': 'NONE', 'grant_number': 'R01AG023770-04', 'organization_name': 'DUKE UNIVERSITY', 'nih_institute': 'AG', 'ranking_category': 'Domestic Higher Education', 'pi_name': 'Cabeza , Roberto', 'grant_number_year': '04', 'award_amount': 293353.0, 'zip_code': '27705'}
        assert_equals(response[1], gold_response)

