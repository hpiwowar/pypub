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
from datasources import author
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
            
# Shared test data
gold_pmids = ['16960149', '16973760', '17170127', '17404298']
gold_aim3_pmids = ['10894146', '19843711', '18996570', '17997859']

#                       author.first_author_first_name,
#                       author.first_author_female,
#                       author.first_author_male,
#                       author.first_author_gender_not_found,
#                       author.first_author_num_prev_pubs,
#                       author.first_author_num_prev_microarray_creation,

#                       author.first_author_prev_oa,
#                       author.first_author_prev_genbank_sharing,
#                       author.first_author_prev_pdb_sharing,
#                       author.first_author_prev_swissprot_sharing,
#                       author.first_author_prev_geoae_sharing,
#                       author.first_author_prev_geo_reuse,
#                       author.first_author_year_first_pub,
#                       author.first_author_num_prev_pmc_cites,
                       
class TestAuthor(object):

    def test_first_author_first_name(self):
        response = author.first_author_first_name(gold_pmids)
        assert_equals(response, ['Cinta', 'Maria', 'Hana', 'Seon-Kyeong'])

    def test_last_author_first_name(self):
        response = author.last_author_first_name(gold_pmids)
        assert_equals(response, ['Jose', 'Knut', 'William', 'John'])

    def test_first_author_female(self):
        response = author.first_author_female(gold_pmids)
        assert_equals(response, ['0', '1', '1', '0'])

    def test_last_author_female(self):
        response = author.last_author_female(gold_pmids)
        assert_equals(response, ['0', '0', '0', '0'])
        
    def test_first_author_male(self):
        response = author.first_author_male(gold_pmids)
        assert_equals(response, ['1', '0', '0', '0'])

    def test_last_author_male(self):
        response = author.last_author_male(gold_pmids)
        assert_equals(response, ['1', '1', '1', '1'])

    def test_first_author_gender_not_found(self):
        response = author.first_author_gender_not_found(gold_pmids)
        assert_equals(response, ['0', '0', '0', '1'])

    def test_last_author_gender_not_found(self):
        response = author.last_author_gender_not_found(gold_pmids)
        assert_equals(response, ['0', '0', '0', '0'])

    def test_first_author_prev_pubs(self):
        response = author.first_author_prev_pubs(gold_aim3_pmids)
        #gold_aim3_pmids = ['10894146', '19843711', '18996570', '17997859'
        gold_first_prev_pubs = [[], [], ['15247401', '15247401'], ['17581960', '17360646', '17121828', '15620361', '15342915', '12391155', '11390640', '11106735', '10623806', '9702189', '9584134', '17581960', '17360646', '17121828', '15620361', '15342915', '12391155', '11390640', '11106735', '10623806', '9702189', '9584134']]
        assert_equals(response, gold_first_prev_pubs)

    def test_last_author_prev_pubs(self):
        response = author.last_author_prev_pubs(gold_aim3_pmids)
        assert_equals(response[0][0:5], ['10634393', '10508171', '10090587', '10087437', '10067863'])

    def test_first_author_num_all_pubs(self):
        response = author.first_author_num_all_pubs(gold_aim3_pmids)
        assert_equals(response, [18, 0, 6, 26])

    def test_first_author_num_prev_pubs(self):
        response = author.first_author_num_prev_pubs(gold_aim3_pmids)
        assert_equals(response, [0, 0, 2, 22])

    def test_last_author_num_all_pubs(self):
        response = author.last_author_num_all_pubs(gold_aim3_pmids)
        assert_equals(response, [162, 0, 44, 27])

    def test_last_author_num_prev_pubs(self):
        response = author.last_author_num_prev_pubs(gold_aim3_pmids)
        assert_equals(response, [98, 0, 36, 22])

    def test_first_author_num_prev_microarray_creation(self):
        response = author.first_author_num_prev_microarray_creation(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 1])

    def test_last_author_num_prev_microarray_creation(self):
        response = author.last_author_num_prev_microarray_creation(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 6])


#                       author.first_author_year_first_pub,
#                       author.first_author_num_prev_pmc_cites,


    def test_first_author_num_prev_oa(self):
        response = author.first_author_num_prev_oa(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_last_author_num_prev_oa(self):
        response = author.last_author_num_prev_oa(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_first_author_num_prev_genbank_sharing(self):
        response = author.first_author_num_prev_genbank_sharing(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 1])

    def test_last_author_num_prev_genbank_sharing(self):
        response = author.last_author_num_prev_genbank_sharing(gold_aim3_pmids)
        assert_equals(response, [1, 0, 0, 0])

    def test_first_author_num_prev_pdb_sharing(self):
        response = author.first_author_num_prev_pdb_sharing(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 1])

    def test_last_author_num_prev_pdb_sharing(self):
        response = author.last_author_num_prev_pdb_sharing(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_first_author_num_prev_swissprot_sharing(self):
        response = author.first_author_num_prev_swissprot_sharing(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_last_author_num_prev_swissprot_sharing(self):
        response = author.last_author_num_prev_swissprot_sharing(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_first_author_num_prev_geoae_sharing(self):
        response = author.first_author_num_prev_geoae_sharing(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 1])

    def test_last_author_num_prev_geoae_sharing(self):
        response = author.last_author_num_prev_geoae_sharing(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 3])

    def test_first_author_num_prev_geo_reuse(self):
        response = author.first_author_num_prev_geo_reuse(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_last_author_num_prev_geo_reuse(self):
        response = author.last_author_num_prev_geo_reuse(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_first_author_num_prev_multi_center(self):
        response = author.first_author_num_prev_multi_center(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_last_author_num_prev_multi_center(self):
        response = author.last_author_num_prev_multi_center(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_first_author_num_prev_meta_analysis(self):
        response = author.first_author_num_prev_meta_analysis(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_last_author_num_prev_meta_analysis(self):
        response = author.last_author_num_prev_meta_analysis(gold_aim3_pmids)
        assert_equals(response, [0, 0, 0, 0])

    def test_first_author_num_prev_pmc_cites(self):
        response = author.first_author_num_prev_pmc_cites(gold_aim3_pmids)
        assert_equals(response, [0, 0, 10, 518])

    def test_last_author_num_prev_pmc_cites(self):
        response = author.last_author_num_prev_pmc_cites(gold_aim3_pmids)
        assert_equals(response, [440, 0, 80, 233])

    def test_first_author_year_first_pub(self):
        response = author.first_author_year_first_pub(gold_aim3_pmids)
        assert_equals(response, [None, None, u'2004', u'1998'])

    def test_last_author_year_first_pub(self):
        response = author.last_author_year_first_pub(gold_aim3_pmids)
        assert_equals(response, [u'1977', None, u'1988', u'2002'])
