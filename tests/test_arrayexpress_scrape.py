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
from datasources import arrayexpress_scrape
from utils.cache import TimedCache

if __name__ == '__main__':
    nose.runmodule()
    
# Shared test data
gold_record = 'E-MEXP-1219\n\t\nComparative genomic hybridization of human osteosarcomas\n\t\n36\n\t\nHomo sapiens\n\t\n2009-06-24\n\t\nClick to download processed data\n\t\nClick to download raw data\n\t\n-\nDescription\n\t\nProfiling of DNA copy number changes in human osteosarcomas using array CGH\nMIAME score\n\t\nArray designs\tProtocols\tFactors\tProcessed data\tRaw data\n-\t*\t*\t*\t*\nCitations\n\t\nLSAMP, a novel candidate tumor suppressor gene in human osteosarcomas, identified by array comparative genomic hybridization. Kresse SH, Ohnstad HO, Paulsen EB, Bjerkehagen B, Szuhai K, Serra M, Schaefer KL, Myklebost O, Meza-Zepeda LA. Genes Chromosomes Cancer 48(8):679-93 (2009), PubMed 19441093\nLinks\n\t\nArray design A-MEXP-253 - NMC Human Genomic Array 20K v1\nArray design A-MEXP-341 - NMC Human Genomic Array 20k v2\nExperimental protocols\nArrayExpress Advanced Interface\nFiles\n\t\nData Archives\tE-MEXP-1219.processed.zip, E-MEXP-1219.raw.zip\nInvestigation Description\tE-MEXP-1219.idf.txt\nSample and Data Relationship\tE-MEXP-1219.sdrf.txt\nExperiment Design Images\tE-MEXP-1219.biosamples.png, E-MEXP-1219.biosamples.svg\nArray Design\tA-MEXP-253.adf.txt, A-MEXP-341.adf.txt\nBrowse all available files\nExperiment types\n\t\ncomparative genome hybridization, disease state, in vivo\nExperimental factors\n\t\nFactor name\tFactor values\nDiseaseState\tnormal, Osteosarcoma\nSample attributes\n\t\nAttribute name\tAttribute values\nAge\t11 years, 12 years, 13 years, 14 years, 15 years, 16 years, 17 years, 18 years, 19 years, 24 years, 26 years, 27 years, 31 years, 34 years, 41 years, 49 years, 50 years, 58 years, 67 years, 7 years, 8 years\nBioSourceType\tfrozen_sample\nDiseaseState\tnormal, Osteosarcoma\nOrganism\tHomo sapiens\nOrganismPart\tfemur, femur/tibia, humerus, lung, pelvis, rib, tibia\nSex\tfemale, male\n\t\n'

def _get_test_filename():
    module = sys.modules[__name__]
    this_dir = os.path.dirname(os.path.abspath(module.__file__))
    datafile = os.path.join(this_dir, 'testdata', 'arrayexpress_scrape_sample.txt')
    return(datafile)
    
class TestArrayExpress_Scrape(object):
    def setup(self):
        self.filename = _get_test_filename()
        self.test_scrape = arrayexpress_scrape.ArrayExpressScrape(filename=self.filename)
        
    def test_get_pmids(self):
        pmids = self.test_scrape.get_pmids()
        gold_pmids = ['19441093', '19490115', '19402892', '19465600', '19494812', '19471018', '19421193', '19526060', '19353763', '19491391', '19260470', '19419536', '16731744', '16581911', '17152010', '19464103', '19468298', '19318562', '19470167', '19376812', '19001005', '18578861', '19435925', '19403659', '19409979', '19465579', '19416906', '19062086', '19396863', '19396863', '18804535', '17713630', '19401422', '19282476', '19411072', '19429403', '19305503', '19362239', '15955062', '16431368', '17925015', '18509161', '19088304', '18794119', '19399471', '19404404']
        assert_equals(pmids, gold_pmids)

    def test_get_unique_pmids(self):
        pmids = self.test_scrape.get_unique_pmids()
        gold_unique_pmids = ['19062086', '17152010', '19411072', '16431368', '19318562', '19282476', '19088304', '18578861', '18509161', '19403659', '19490115', '15955062', '19421193', '19441093', '16581911', '19404404', '18794119', '19465600', '19409979', '19260470', '19494812', '19468298', '19435925', '19471018', '19416906', '19402892', '18804535', '17713630', '16731744', '19429403', '19362239', '19464103', '19376812', '19399471', '19526060', '19353763', '19401422', '19305503', '19419536', '19470167', '19396863', '19465579', '19491391', '19001005', '17925015']
        assert_equals(pmids, gold_unique_pmids)
        
    def test_get_record_generator(self):
        gen = self.test_scrape.get_record_generator()
        assert_equals(gen.next(), gold_record)

        gen = self.test_scrape.get_record_generator()
        gold_num_records = 227
        assert_equals(len(list(gen)), gold_num_records)

    def test_get_match(self):
        hit = arrayexpress_scrape.get_match("date", "abcd\n2009-12-01\nabcd")
        assert_equals(hit, "2009-12-01")

        hit = arrayexpress_scrape.get_match("date", "No date here!")
        assert_equals(hit, None)
        
    def test_get_date_from_record(self):
        match = arrayexpress_scrape.get_date_from_record(gold_record)
        assert_equals(match, '2009-06-24')

    def test_get_description_from_record(self):
        match = arrayexpress_scrape.get_description_from_record(gold_record)
        assert_equals(match, 'Profiling of DNA copy number changes in human osteosarcomas using array CGH')

    def test_get_pmid_from_record(self):
        match = arrayexpress_scrape.get_pmid_from_record(gold_record)
        assert_equals(match, "19441093")

    def test_get_accession_from_record(self):
        match = arrayexpress_scrape.get_accession_from_record(gold_record)
        assert_equals(match, 'E-MEXP-1219')
        
    def test_get_num_samples_from_record(self):
        match = arrayexpress_scrape.get_num_samples_from_record(gold_record)
        assert_equals(match, 36)

    def test_get_species_from_record(self):
        match = arrayexpress_scrape.get_species_from_record(gold_record)
        assert_equals(match, "Homo sapiens")

    def test_get_num_factors_from_record(self):
        match = arrayexpress_scrape.get_num_factors_from_record(gold_record)
        assert_equals(match, 1)

    def test_get_factors_dict_from_record(self):
        match = arrayexpress_scrape.get_factors_dict_from_record(gold_record)
        assert_equals(match, {'DiseaseState': 'normal, Osteosarcoma'})

    def test_get_num_attributes_from_record(self):
        match = arrayexpress_scrape.get_num_attributes_from_record(gold_record)
        assert_equals(match, 6)

    def test_get_attributes_dict_from_record(self):
        match = arrayexpress_scrape.get_attributes_dict_from_record(gold_record)
        assert_equals(match, {'BioSourceType': 'frozen_sample', 'Age': '11 years, 12 years, 13 years, 14 years, 15 years, 16 years, 17 years, 18 years, 19 years, 24 years, 26 years, 27 years, 31 years, 34 years, 41 years, 49 years, 50 years, 58 years, 67 years, 7 years, 8 years', 'Sex': 'female, male', 'OrganismPart': 'femur, femur/tibia, humerus, lung, pelvis, rib, tibia', 'Organism': 'Homo sapiens', 'DiseaseState': 'normal, Osteosarcoma'})

    def test_get_platform_accession_from_record(self):
        match = arrayexpress_scrape.get_platform_accession_from_record(gold_record)
        assert_equals(match, 'A-MEXP-253')

    def test_get_is_affy_from_record(self):
        match = arrayexpress_scrape.get_is_affy_from_record(gold_record)
        assert_equals(match, 0)

    def test_get_is_agilent_from_record(self):
        match = arrayexpress_scrape.get_is_agilent_from_record(gold_record)
        assert_equals(match, 0)
        
    def test_get_has_experiment_type_from_record(self):
        match = arrayexpress_scrape.get_has_experiment_type_from_record(gold_record)
        assert_equals(match, 1)
                
    def test_get_miame_score_from_record(self):
        score = arrayexpress_scrape.get_miame_score_from_record(gold_record)
        assert_equals(score, 4)
        
    def test_get_record_dict(self):
        record_dict = arrayexpress_scrape.get_record_dict(gold_record)
        assert_equals(len(record_dict), 25)
        
        
