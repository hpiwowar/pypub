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
test_data_geo_filter = "pubmed_gds[filter]"
test_data_geo_filtered_pmids = ['16960149', '17404298']
test_data_arrayexpress_filtered_pmids = ['17170127']
test_data_smd_filtered_pmids = ['17404298']
test_data_geo_has_data = ['1', '0', '0', '1']
test_data_arrayexpress_has_data = ['0', '0', '1', '0']
test_data_smd_has_data = ['0', '0', '0', '1']
test_data_pubmed_is_humans = ['1', '1', '1', '1']
test_data_pubmed_is_animals = ['0', '1', '0', '1']
test_data_pubmed_is_mice = ['0', '1', '0', '0']
test_data_pubmed_is_bacteria = ['0', '0', '0', '0']
test_data_pubmed_is_fungi = ['0', '0', '0', '0']
test_data_pubmed_is_cultured_cells = ['1', '0', '1', '0']
test_data_pubmed_is_cancer = ['1', '0', '0', '0']
test_data_has_geo_data_submission = [['pmid'] + gold_pmids, ['has_geo_data'] + test_data_geo_has_data]
test_data_collect_response = [['pmid'] + gold_pmids, 
                              ['has_geo_data'] + test_data_geo_has_data, 
                              ['has_arrayexpress_data'] + test_data_arrayexpress_has_data,
                              ['has_smd_data'] + test_data_smd_has_data] 
test_data_csv_format = [['pmid', 'has_geo_data'], ['16960149', '1'], ['16973760', '0'], ['17170127', '0'], ['17404298', '1']]
test_data_csv_string = 'pmid,has_geo_data\r\n16960149,1\r\n16973760,0\r\n17170127,0\r\n17404298,1\r\n'
test_data_soup_to_nuts = 'pmid,has_geo_data,has_arrayexpress_data,has_smd_data\r\n16960149,1,0,0\r\n16973760,0,0,0\r\n17170127,0,1,0\r\n17404298,1,0,1\r\n'
test_data_ochsner_found_geo_data = ['0', '0', '0', '0']
test_data_ochsner_found_arrayexpress_data = ['0', '0', '1', '0']
test_data_ochsner_found_smd_data = ['0', '0', '0', '1']
test_data_ochsner_other_gold_pmids = ['17510434', '17409432', '17308088', '18172295', '17200196', '17200196']
test_data_ochsner_found_journal_data = ['1', '0', '0', '0', '1', '1']
test_data_ochsner_found_other_data = ['0', '1', '1', '0', '0', '0']
test_data_ochsner_found_any_data = ['0', '0', '1', '1', '1', '1', '1', '0', '1', '1']
test_data_list_data_ids = ['', '', u'E-TABM-133', u'SMD-Experiment-Set-No_3827']
test_data_pubmed_date_published = ['2007 Jan 1', '2007 Jan', '2007 Apr 15', '2007 Apr 15']
test_data_pubmed_year_published = ['2007', '2007', '2007', '2007']
test_data_pubmed_journal = ['Blood', 'Mol Endocrinol', 'Blood', 'J Immunol']
test_data_pubmed_authors = ['Mestre-Escorihuela C;Rubio-Moscardo F;Richter JA;Siebert R;Climent J;Fresquet V;Beltran E;Agirre X;Marugan I;Mar\xc3\xadn M;Rosenwald A;Sugimoto KJ;Wheat LM;Karran EL;Garc\xc3\xada JF;Sanchez L;Prosper F;Staudt LM;Pinkel D;Dyer MJ;Martinez-Climent JA', 'Nilsson M;Stulnig TM;Lin CY;Yeo AL;Nowotny P;Liu ET;Steffensen KR', 'Raslova H;Kauffmann A;Sekka\xc3\xaf D;Ripoche H;Larbret F;Robert T;Le Roux DT;Kroemer G;Debili N;Dessen P;Lazar V;Vainchenker W', 'Kim SK;Fouts AE;Boothroyd JC']
test_data_pubmed_number_times_cited_in_pmc = ['6', '0', '4', '9']
test_citation_pmids = ['17375194', '18767901']


class TestPubMed(object):
    @online
    def test_pubmed_filter_no_hits(self):
        response = datasources.pubmed.is_humans([])
        assert_equals(response, [])

    @online
    def test_pubmed_date_published(self):
        response = datasources.pubmed.date_published(gold_pmids)
        assert_equals(response, test_data_pubmed_date_published)

    @online
    def test_pubmed_year_published(self):
        response = datasources.pubmed.year_published(gold_pmids)
        assert_equals(response, test_data_pubmed_year_published)

    @online
    def test_pubmed_pubmed_year(self):
        response = datasources.pubmed.year(gold_pmids)
        assert_equals(response, test_data_pubmed_year_published)

    @online
    def test_pubmed_journal(self):
        response = datasources.pubmed.journal(gold_pmids)
        assert_equals(response, test_data_pubmed_journal)

    @online
    def test_pubmed_authors(self):
        response = datasources.pubmed.authors(gold_pmids)
        assert_equals(response, test_data_pubmed_authors)

    @online
    def test_pubmed_number_times_cited_in_pmc(self):
        response = datasources.pubmed.number_times_cited_in_pmc(gold_pmids)
        assert_equals(response, test_data_pubmed_number_times_cited_in_pmc)

    @online
    def test_pubmed_get_express_pmc_citations(self):
        response = datasources.pubmed.get_express_pmc_citations(gold_pmids)
        assert_equals(response, test_data_pubmed_number_times_cited_in_pmc)
        
    @online
    def test_pubmed_is_humans(self):
        response = datasources.pubmed.is_humans(gold_pmids)
        assert_equals(response, test_data_pubmed_is_humans)

    @online
    def test_pubmed_is_animals(self):
        response = datasources.pubmed.is_animals(gold_pmids)
        assert_equals(response, test_data_pubmed_is_animals)

    @online
    def test_pubmed_is_mice(self):
        response = datasources.pubmed.is_mice(gold_pmids)
        assert_equals(response, test_data_pubmed_is_mice)

    @online
    def test_pubmed_is_bacteria(self):
        response = datasources.pubmed.is_bacteria(gold_pmids)
        assert_equals(response, test_data_pubmed_is_bacteria)

    @online
    def test_pubmed_is_fungi(self):
        response = datasources.pubmed.is_fungi(gold_pmids)
        assert_equals(response, test_data_pubmed_is_fungi)

    @online
    def test_pubmed_is_cultured_cells(self):
        response = datasources.pubmed.is_cultured_cells(gold_pmids)
        assert_equals(response, test_data_pubmed_is_cultured_cells)
        
    @online
    def test_pubmed_is_cancer(self):
        response = datasources.pubmed.is_cancer(gold_pmids)
        assert_equals(response, test_data_pubmed_is_cancer)

    @online
    def test_pubmed_corresponding_address(self):
        response = datasources.pubmed.corresponding_address(gold_pmids)
        assert_equals(response, ['Center for Applied Medical Research (CIMA), University of Navarra, Avda Pio XII, 55, Pamplona 31008, Spain. jamcliment@unav.es.', 'Department of Biosciences and Nutrition, Karolinska Institutet, S-14157 Huddinge, Sweden.', 'INSERM Unit\xc3\xa9 790, Institut Gustave Roussy, 1 rue Camille Desmoulins, 94805 Villejuif, France. hraslova@igr.fr', 'Department of Microbiology and Immunology, Stanford University School of Medicine, Stanford, CA 94305, USA.'])

    @online
    def test_pubmed_pubtype(self):
        response = datasources.pubmed.pubtype(gold_pmids)
        assert_equals(response, [u"Journal Article;Research Support, Non-U.S. Gov't", u"Journal Article;Research Support, Non-U.S. Gov't", u"Clinical Trial;Comparative Study;Journal Article;Research Support, Non-U.S. Gov't", u'Journal Article;Research Support, N.I.H., Extramural'])

    @online
    def test_pubmed_subset(self):
        response = datasources.pubmed.subset(gold_pmids)
        assert_equals(response, [u'AIM;IM', u'IM', u'AIM;IM', u'AIM;IM'] )

    @online
    def test_pubmed_language(self):
        response = datasources.pubmed.language(gold_pmids)
        assert_equals(response, [u'eng', u'eng', u'eng', u'eng'])

    @online
    def test_pubmed_issn(self):
        response = datasources.pubmed.issn(gold_pmids)
        assert_equals(response, ['0006-4971', '0888-8809', '0006-4971', '0022-1767'])

    @online
    def test_pubmed_volume(self):
        response = datasources.pubmed.volume(gold_pmids)
        assert_equals(response, ['109', '21', '109', '178'])

    @online
    def test_pubmed_issue(self):
        response = datasources.pubmed.issue(gold_pmids)
        assert_equals(response, ['1', '1', '8', '8'])

    @online
    def test_pubmed_pages(self):
        response = datasources.pubmed.pages(gold_pmids)
        assert_equals(response, ['271-80', '126-37', '3225-34', '5154-65'])
                
    @online
    def test_pubmed_get_pmid_from_citation(self):
        test_line = "Proc Natl Acad Sci U S A|2007|||Young DW|googlescholar;fmeasure35_not"
        test_vars = test_line.split("|")        
        response = datasources.pubmed.get_pmid_from_citation(*test_vars)
        assert_equals(response, ["17360627"])

        response = datasources.pubmed.get_pmid_from_citation(journal=test_vars[0], 
                                                            year=test_vars[1], 
                                                            firstauthor=test_vars[4])
        assert_equals(response, ["17360627"])

    @online
    def test_pubmed_get_what_cites_this_tuples(self):
        response = datasources.pubmed.get_what_cites_this_tuples(test_citation_pmids)
        gold_cites = [u'19296844', u'18998887', u'18767902', u'18767901', u'18594519']
        assert_equals(response[0][1][0:5], gold_cites)
        
        response1 = datasources.pubmed.number_times_cited_in_pmc(gold_pmids)
        assert_equals(response1, test_data_pubmed_number_times_cited_in_pmc)

        response2 = datasources.pubmed.get_what_cites_this_tuples(gold_pmids)
        assert_equals([len(b) for (a, b) in response2], response1)


    @online
    def test_pubmed_get_what_this_cites_tuples(self):
        response = datasources.pubmed.get_what_this_cites_tuples(test_citation_pmids)
        assert_equals(response, [('17375194', [u'16683865', u'16368950', u'16340990', u'16319137', u'16106022', u'16030302', u'15900006', u'15879210', u'15713967', u'15661852', u'15608265', u'15608260', u'15340487', u'15175721', u'15169549', u'15141061', u'15068665', u'14983930', u'14744116', u'14602436', u'12698183', u'12225585', u'11752295', u'11726920', u'11125075', u'10693778', u'9056804']), ('18767901', [u'18259695', u'17917124', u'17687342', u'17660804', u'17657230', u'17607307', u'17493285', u'17465717', u'17375194', u'17330011', u'17077452', u'16704733', u'16436574', u'15923720', u'15340487', u'15141061', u'15046250', u'15017960', u'12525262', u'11228147', u'8837534', u'8054076'])])
        

    @online
    def test_pubmed_journal(self):
        query_pmid = ['19727677']
        response = datasources.pubmed.journal(query_pmid)
        assert_equals(response, ['Psychopharmacology (Berl)'])

    @online
    def test_pubmed_in_genbank(self):
        query_pmids = ['20080736', '19861542', '19952139']
        response = datasources.pubmed.in_genbank(query_pmids)
        assert_equals(response, ['0', '0', '1'])
     
    @online
    def test_pubmed_in_pdb(self):
        query_pmids = ['20080736', '19861542', '19952139']
        response = datasources.pubmed.in_pdb(query_pmids)
        assert_equals(response, ['1', '0', '0'])

    def test_pubmed_abstract(self):
        response = datasources.pubmed.abstract(gold_pmids)
        assert_equals(response[0][0:100], 'Integrative genomic and gene-expression analyses have identified amplified oncogenes in B-cell non-H')

    def test_pubmed_article_title(self):
        response = datasources.pubmed.article_title(gold_pmids)
        gold_titles = ['Homozygous deletions localize novel tumor suppressor genes in B-cell lymphomas.', 'Liver X receptors regulate adrenal steroidogenesis and hypothalamic-pituitary-adrenal feedback.', 'Interrelation between polyploidization and megakaryocyte differentiation: a gene profiling approach.', 'Toxoplasma gondii dysregulates IFN-gamma-inducible gene expression in human fibroblasts: insights from a genome-wide transcriptional profiling.']
        assert_equals(response, gold_titles)

    def test_pubmed_mesh_major(self):
        response = datasources.pubmed.mesh_major(gold_pmids)
        assert_equals(response, ['Genes, Tumor Suppressor;Sequence Deletion', 'Feedback, Physiological', '', 'Gene Expression Profiling;Gene Expression Regulation'])

    def test_pubmed_mesh_basic(self):
        response = datasources.pubmed.mesh_basic(gold_pmids)
        gold_basic_mesh = ['Apoptosis;Apoptosis Regulatory Proteins;Biopsy;Carrier Proteins;Cell Line, Tumor;Chromosome Mapping;Chromosomes, Human;Cyclin-Dependent Kinase Inhibitor p18;DNA Methylation;DNA Mutational Analysis;DNA, Neoplasm;Epigenesis, Genetic;Gene Dosage;Gene Expression Regulation, Neoplastic;Gene Silencing;Genes, Tumor Suppressor;Homeodomain Proteins;Homozygote;Humans;Lymphoma, B-Cell;Membrane Proteins;Nuclear Proteins;Nucleic Acid Hybridization;Oligonucleotide Array Sequence Analysis;Point Mutation;Promoter Regions, Genetic;Proto-Oncogene Proteins;Proto-Oncogene Proteins c-bcl-2;Sequence Deletion;Transcription Factors;Vesicular Transport Proteins', 'Adrenal Glands;Animals;DNA-Binding Proteins;Feedback, Physiological;Gene Expression Profiling;Glucocorticoids;Humans;Hypothalamus;Mice;Mice, Inbred C57BL;Mice, Knockout;Models, Biological;Orphan Nuclear Receptors;Pituitary Gland;Receptors, Cytoplasmic and Nuclear;Steroids', 'Antigens, CD34;Blood Platelets;Cell Differentiation;Cells, Cultured;Female;Gene Expression Profiling;Gene Expression Regulation;Humans;Male;Megakaryocytes;Oligonucleotide Array Sequence Analysis;Ploidies;Thrombopoietin', 'Active Transport, Cell Nucleus;Animals;Cell Nucleus;Fibroblasts;Gene Expression Profiling;Gene Expression Regulation;Gene Regulatory Networks;Histocompatibility Antigens Class II;Humans;Interferon Regulatory Factor-1;Interferon-gamma;Oligonucleotide Array Sequence Analysis;Phosphorylation;STAT1 Transcription Factor;Toxoplasma']
        assert_equals(response, gold_basic_mesh)

    def test_pubmed_mesh_qualifiers(self):
        response = datasources.pubmed.mesh_qualifier(gold_pmids)
        assert_equals(response, ['immunology;pathology;genetics;classification;ultrastructure', 'metabolism', 'drug effects;cytology;physiology;pharmacology', 'genetics;pharmacology;analysis;physiology;metabolism;pathogenicity'])

    def test_pubmed_mesh_major_qualifiers(self):
        response = datasources.pubmed.mesh_major_qualifier(gold_pmids)
        assert_equals(response, ['genetics', 'metabolism', 'physiology', 'pharmacology;pathogenicity'])

