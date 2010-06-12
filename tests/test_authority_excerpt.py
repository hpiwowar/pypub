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
from datasources import authority_excerpt
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
# Shared test data
gold_aim3_pmids = ['10894146', '19843711', '18996570', '17997859']

def _get_test_filename():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    datafile = os.path.join(this_dir, 'testdata', 'authority_excerpt_sample.txt')
    return(datafile)
    
class TestAuthority_Excerpt(object):
    def setup(self):
        filename = _get_test_filename()
        db_name = ":memory:"
        self.test_instance = authority_excerpt.AuthorityExcerpt(db_name=db_name, filename=filename, do_import=True)

    def test_setup(self):
        number_of_rows = self.test_instance.get_number_of_rows()
        sample = open(_get_test_filename(), "r").read()
        gold_pattern = "[^_\d]\d+_\d+"
        gold_number_of_rows = len(re.findall(gold_pattern, sample))
        assert_equals(number_of_rows, gold_number_of_rows)

    def test_get_pmids(self):
        pmids = self.test_instance.get_all_pmids()
        assert_equals(len(pmids), 15167)

    def test_first_author_all_pubs(self):
        all_pubs = authority_excerpt.first_author_all_pubs(gold_aim3_pmids)
        gold_first_all_pubs = [['17638889', '16442701', '12776178', '12591240', '12527389', '12094606', '11518802', '11328825', '10894146', '17638889', '16442701', '12776178', '12591240', '12527389', '12094606', '11518802', '11328825', '10894146'], [], ['19013643', '18996570', '15247401', '19013643', '18996570', '15247401'], ['18852287', '17997859', '17581960', '17360646', '17121828', '15620361', '15342915', '12391155', '11390640', '11106735', '10623806', '9702189', '9584134', '18852287', '17997859', '17581960', '17360646', '17121828', '15620361', '15342915', '12391155', '11390640', '11106735', '10623806', '9702189', '9584134']]
        assert_equals(all_pubs, gold_first_all_pubs)

    def test_last_author_all_pubs(self):
        all_pubs = authority_excerpt.last_author_all_pubs(gold_aim3_pmids)
        gold_last_all_pubs = [['19196836', '19074847', '18514727', '17574003', '17218414', '16543378', '16442701', '16254015', '15784681', '15699542', '15625236', '15650365', '14767065', '14669837', '12946875', '12776178', '12591240', '12506123', '12354788', '12094606', '11838736', '11701737', '11701667', '11518802', '11427693', '11407657', '11328825', '11266502', '11152480', '11704987', '10894146', '10634393', '10508171', '10090587', '10087437', '10067863', '9837884', '9751500', '9705285', '9564863', '9440808', '9401716', '9357766', '9328341', '9143002', '9013763', '8901626', '8828512', '8796370', '8754792', '8631908', '8593780', '7895689', '7835274', '7789309', '7593433', '7488874', '8288596', '8276832', '8175681', '8119145', '8033801', '7956930', '7956917', '7904604', '7877614', '18407190', '9831479', '8396023', '7683671', '7511545', '1740410', '1537303', '1430208', '1331079', '1954909', '1843207', '2710132', '2564808', '7238401', '908269', '19196836', '19074847', '18514727', '17574003', '17218414', '16543378', '16442701', '16254015', '15784681', '15699542', '15625236', '15650365', '14767065', '14669837', '12946875', '12776178', '12591240', '12506123', '12354788', '12094606', '11838736', '11701737', '11701667', '11518802', '11427693', '11407657', '11328825', '11266502', '11152480', '11704987', '10894146', '10634393', '10508171', '10090587', '10087437', '10067863', '9837884', '9751500', '9705285', '9564863', '9440808', '9401716', '9357766', '9328341', '9143002', '9013763', '8901626', '8828512', '8796370', '8754792', '8631908', '8593780', '7895689', '7835274', '7789309', '7593433', '7488874', '8288596', '8276832', '8175681', '8119145', '8033801', '7956930', '7956917', '7904604', '7877614', '18407190', '9831479', '8396023', '7683671', '7511545', '1740410', '1537303', '1430208', '1331079', '1954909', '1843207', '2710132', '2564808', '7238401', '908269'], [], ['19559768', '19428707', '19356740', '19337736', '19253323', '19031367', '19013643', '18996570', '18723134', '18534845', '18320194', '18312497', '18061225', '18061221', '17879227', '17827764', '17704015', '17470060', '17324374', '17306392', '17293176', '16956635', '16844831', '16843564', '16324763', '16293277', '16131718', '16038998', '16014367', '15587265', '11500561', '11355633', '11218821', '11035946', '10948424', '10712536', '9352086', '8002013', '2844961', '6128288', '6117254', '6115380', '6111293', '6108785'], ['19465643', '19052728', '18752282', '18513787', '17696997', '17174450', '17997859', '17895273', '17762873', '17761679', '17411399', '17360646', '17356705', '17121828', '16573589', '16547175', '16480787', '16157420', '16205371', '16002521', '15914554', '15620361', '15597075', '15115763', '12368860', '12086925', '11752262']]
        assert_equals(all_pubs, gold_last_all_pubs)
    
    def test_get_aggregate_attributes(self):
        all_author_pubs = authority_excerpt.first_author_all_pubs([gold_aim3_pmids[0]])
        response = authority_excerpt.get_aggregate_attributes(all_author_pubs[0])
        gold_response = {'is_open_access': 0, 'is_microarray_data_creation': 4, 'is_meta_analysis': 0, 'in_ae_or_geo': 0, 'is_multicenter_study': 0, 'in_swissprot': 0, 'in_pdb': 0, 'in_genbank': 0, 'is_geo_reuse': 0}
        assert_equals(response, gold_response)

    def test_get_min_year(self):
        pmid_years = [None, None, '15247401', '9584134']
        response = authority_excerpt.get_min_year(pmid_years)
        assert_equals(response, [None, None, u'2004', u'1998'])
        
        
