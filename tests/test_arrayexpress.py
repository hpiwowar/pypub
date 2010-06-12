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
import datasources.geo
import datasources.arrayexpress
import datasources.smd
import datasources.ochsner
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
# Shared test data
test_data_request = "pubmed.pubmed_id, geo.has_data_submission, arrayexpress.has_data_submission, smd.has_data_submission"
gold_pmids = ['16960149', '16973760', '17170127', '17404298']
test_data_arrayexpress_filtered_pmids = ['17170127']
test_data_arrayexpress_has_data = ['0', '0', '1', '0']
test_data_arrayexpress_accession_number = [None, None, u'E-TABM-133', None]
test_data_has_arrayexpress_data_submission = [['pmid'] + gold_pmids, ['has_arrayexpress_data'] + test_data_arrayexpress_has_data]


arrayexpress_ids = ['E-MEXP-854', 'E-MEXP-936', 'E-TABM-130', 'E-TABM-186', 'E-TABM-153', 'E-TABM-133', 'E-GEOD-7814', 'E-GEOD-8658', 'E-MEXP-560', 'E-MIMR-11']
test_data_arrayexpress_number_samples = ['20', '24', '35', '28', '9', '4', '64', '63', '6', '1']
test_data_arrayexpress_release_date = ['2007-01-22', '2007-12-07', '2006-10-13', '2007-01-04', '2006-11-29', '2006-08-22', '2008-06-14', '2008-06-15', '2006-02-15', '2005-09-07']
test_data_arrayexpress_submitter = ['Thomas Dittmar', 'Magnus Lundgren', 'Alexandre Gattiker', ' MacCallum', ' MacCallum', 'Philippe Dessen', 'Sina Gharib', None, 'Basem Abdallah', 'Ernesto Yague']
test_data_arrayexpress_array_design = ['A-MEXP-221: uwh_cDNA_human', 'A-MEXP-610: KTH Sulfolobus v10', 'A-AFFY-43: Affymetrix GeneChip  Rat Genome 230 2.0 [Rat230_2]', 'A-MEXP-225: EMBL A. gambiae MMC1 20k v1.0', 'A-MEXP-225: EMBL A. gambiae MMC1 20k v1.0', 'A-AGIL-11: Agilent Whole Human Genome Oligo Microarray 012391 G4112A', 'A-AFFY-36: Affymetrix GeneChip  Mouse Genome 430A 2.0 [Mouse430A_2]', 'A-AFFY-44: Affymetrix GeneChip  Human Genome U133 Plus 2.0 [HG-U133_Plus_2]', 'A-AFFY-37: Affymetrix GeneChip  Human Genome U133A 2.0 [HG-U133A_2]', 'A-AFFY-34: Affymetrix GeneChip  Human Genome HG-U133B [HG-U133B]']
test_data_arrayexpress_citation = [None, None, '<accession>17170127</accession><publication>Blood</publication><authors>Raslova, Hana; Kauffmann, Audrey; Sekkai, Dalila; Ripoche, Hugues; Larbret, Frederic; Robert, Thomas; Le Roux, Diana Tronik; Kroemer, Guido; Debili, Najet; Dessen, Philippe; Lazar, Vladimir; Vainchenker, William</authors><title>Interrelation between polyploidization and megakaryocyte differentiation: a gene profiling approach</title><year>2007</year><volume>109</volume><issue>8</issue><pages>3225</pages><uri>http://dx.doi.org/10.1182/blood-2006-07-037838</uri>', None]
test_data_arrayexpress_species = ['Homo sapiens', 'Sulfolobus acidocaldarius', 'Rattus norvegicus', 'Anopheles gambiae', 'Anopheles gambiae', 'Homo sapiens', 'Mus musculus', 'Homo sapiens', 'Homo sapiens', 'Homo sapiens']
test_data_arrayexpress_submission_date = [None, None, None, None, None, None, None, None, None, None]
test_data_arrayexpress_in_ochsner = [True, True, True, True, True, True, False, False, True, True]
test_data_arrayexpress_pmid_from_ochsner    = [['17372200'], ['17307872'], ['17483452'], ['17563388'], ['17563388'], ['17170127'], [], [], ['17182623'], ['17283147']]
test_data_arrayexpress_pmids_from_links     = [['17372200'], [], ['17483452'], ['17563388'], ['17563388'], ['17170127'], ['17991715'], ['17664351'], [], []]
test_data_arrayexpress_pmid_if_in_ochsner   = [['17372200'], [], ['17483452'], ['17563388'], ['17563388'], ['17170127'], ['17991715'], ['17664351'], [], []]
test_data_arrayexpress_pmid_from_link_or_ochsner = ['17372200', '17307872', '17483452', '17563388', '17563388', '17170127', '17991715', '17664351', '17182623', '17283147']


class TestArrayExpress(object):
    def setup(self):
        self.gold_arrayexpress_ids = arrayexpress_ids
        self.arrayexpress_source = datasources.arrayexpress.ArrayExpress()
        
    @online
    def test_arrayexpress_has_data_submission_no_hits(self):
        response = datasources.arrayexpress.has_data_submission([])
        assert_equals(response, [])
                
        pmids_that_do_not_pass_gold_filter = [pmid for pmid in gold_pmids if pmid not in test_data_arrayexpress_filtered_pmids]
        response = datasources.arrayexpress.has_data_submission(pmids_that_do_not_pass_gold_filter)
        all_zeros = ['0' for pmid in pmids_that_do_not_pass_gold_filter]
        assert_equals(response, all_zeros)
        
    @online
    def test_arrayexpress_has_data_submission(self):
        response = datasources.arrayexpress.has_data_submission(gold_pmids)
        assert_equals(response, test_data_arrayexpress_has_data)

    def test_arrayexpress_accession_number(self):
        response = [self.arrayexpress_source.accession_number(id) for id in self.gold_arrayexpress_ids]                
        assert_equals(response, arrayexpress_ids)

    def test_arrayexpress_number_samples(self):
        response = [self.arrayexpress_source.number_samples(id) for id in self.gold_arrayexpress_ids]                
        assert_equals(response, test_data_arrayexpress_number_samples)

    def test_arrayexpress_release_date(self):
        response = [self.arrayexpress_source.release_date(id) for id in self.gold_arrayexpress_ids]                
        assert_equals(response, test_data_arrayexpress_release_date)

    def test_arrayexpress_submitter(self):
        response = [self.arrayexpress_source.submitter(id) for id in self.gold_arrayexpress_ids]                
        assert_equals(response, test_data_arrayexpress_submitter)

    def test_arrayexpress_array_design(self):
        response = [self.arrayexpress_source.array_design(id) for id in self.gold_arrayexpress_ids]        
        assert_equals(response, test_data_arrayexpress_array_design)

    def test_arrayexpress_species(self):
        response = [self.arrayexpress_source.species(id) for id in self.gold_arrayexpress_ids]        
        assert_equals(response, test_data_arrayexpress_species)

    def test_arrayexpress_contributors(self):
        response = [self.arrayexpress_source.contributors(id) for id in self.gold_arrayexpress_ids]        
        assert_equals(response, test_data_arrayexpress_submitter)

    def test_arrayexpress_submission_date(self):
        response = [self.arrayexpress_source.submission_date(id) for id in self.gold_arrayexpress_ids]        
        assert_equals(response, test_data_arrayexpress_submission_date)

    def test_arrayexpress_in_ochsner(self):
        response = [self.arrayexpress_source.in_ochsner(id) for id in self.gold_arrayexpress_ids]        
        assert_equals(response, test_data_arrayexpress_in_ochsner)

    def test_arrayexpress_ochsner_pmid(self):
        response = [self.arrayexpress_source.pmid_from_ochsner(id) for id in self.gold_arrayexpress_ids]        
        assert_equals(response, test_data_arrayexpress_pmid_from_ochsner)

    def test_arrayexpress_linked_pmids_in_ochsner(self):
        response = [self.arrayexpress_source.pmids_from_links_in_ochsner_set(id) for id in self.gold_arrayexpress_ids]        
        assert_equals(response, test_data_arrayexpress_pmid_if_in_ochsner)

    def test_arrayexpress_linked_pmids(self):
        response = [self.arrayexpress_source.pmids_from_links(id) for id in self.gold_arrayexpress_ids]  
        assert_equals(response, test_data_arrayexpress_pmids_from_links)

#    def test_arrayexpress_multiple_linked_pmids(self):
#        response = self.arrayexpress_source.pmids_from_links('GSE2658')     
#        assert_equals(response, [u'16688228', u'16728703', u'17023574'])     
        
    def test_data_arrayexpress_pmid_from_links_or_ochsner(self):
        response = [self.arrayexpress_source.pmid_from_links_or_ochsner(id) for id in self.gold_arrayexpress_ids]        
        assert_equals(response, test_data_arrayexpress_pmid_from_link_or_ochsner)
        
