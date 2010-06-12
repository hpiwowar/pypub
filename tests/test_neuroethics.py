import os
import time
import sys
from tests import slow, online, notimplemented, acceptance
import nose
from nose.tools import assert_equals
import dataset
import neuroethics
from neuroethics import neuroethics_all_union_pmids
 
def test_data_collection(max=None, write_to_file=False):
    query_pmids = neuroethics_all_union_pmids.union_pmid_list
    pubmed_request = """pubmed.pubmed_id, 
                           pubmed.is_humans, 
                           pubmed.is_animals, 
                           pubmed.year_published, 
                           pubmed.authors, 
                           pubmed.journal,
                           pubmed.affiliation,
                           pubmed.pubtype,
                           pubmed.subset,
                           pubmed.is_review,
                           pubmed.is_english,
                           pubmed.is_ethics_sh,
                           pubmed.is_ethics_mesh,
                           pubmed.is_bioethics_sb,
                           pubmed.is_jsubsete
                           """
                           
    csv_data = dataset.collect_data_as_csv(query_pmids[0:10], pubmed_request)
    gold_response = """pmid,pubmed_is_humans,pubmed_is_animals,pubmed_year_published,pubmed_authors,pubmed_journal,pubmed_affiliation,pubmed_pubtype,pubmed_subset,pubmed_is_review,pubmed_is_english,pubmed_is_ethics_sh,pubmed_is_ethics_mesh,pubmed_is_bioethics_sb,pubmed_is_jsubsete\r\n19949718,0,0,2009,Placentino A;Carletti F;Landi P;Allen P;Surguladze S;Benedetti F;Abbamonte M;Gasparotti R;Barale F;Perez J;McGuire P;Politi P,J Psychiatry Neurosci,"Fusar-Poli, Carletti, Allen, McGuire - Section of Neuroimaging, Department of Psychological Medicine, Institute of Psychiatry, King\'s College London, United Kingdom. p.fusar@libero.it",Journal Article,IM,0,1,0,0,0,0\r\n19949480,0,0,2009,Meunier D;Lambiotte R;Fornito A;Ersche KD;Bullmore ET,Front Neuroinformatics,"Brain Mapping Unit, Department of Psychiatry, University of Cambridge Cambridge, UK.",Journal Article,,0,1,0,0,0,0\r\n19949454,0,0,2009,Kopyciok RP;Richter S,Front Behav Neurosci,"Department of Neuropsychology, Otto-von-Guericke-University Magdeburg, Germany.",Journal Article,,0,1,0,0,0,0\r\n19949451,0,0,2009,Hodgins S;de Brito S;Simonoff E;Vloet T;Viding E,Front Behav Neurosci,"Department of Forensic Mental Health Science, Institute of Psychiatry, King\'s College London London, UK.",Journal Article,,0,1,0,0,0,0\r\n19936321,0,0,2009,Mell T;Wartenburger I;Marschner A;Villringer A;Reischies FM;Heekeren HR,Front Hum Neurosci,"Max-Planck-Institute for Human Development Berlin, Germany.",Journal Article,,0,1,0,0,0,0\r\n19936275,0,0,2009,Jung RE;Gasparovic C;Chavez RS;Caprihan A;Barrow R;Yeo RA,Intelligence,"The Mental Illness and Neuroscience Discovery (MIND) Research Network, Albuquerque, New Mexico, USA.",JOURNAL ARTICLE,,0,1,0,0,0,0\r\n19936244,0,0,2009,Meda SA;Stevens MC;Folley BS;Calhoun VD;Pearlson GD,PLoS One,"Olin Neuropsychiatry Research Center, Institute of Living at Hartford Hospital, Hartford, Connecticut, United States of America. smeda01@harthosp.org","Journal Article;Research Support, N.I.H., Extramural",IM,0,1,0,0,0,0\r\n19936235,0,0,2009,Vermeulen N;Godefroid J;Mermillod M,PLoS One,"Psychology Department, Universit\xc3\xa9 catholique de Louvain, Louvain-la-Neuve, Belgium. Nicolas.Vermeulen@uclouvain.be","Journal Article;Research Support, Non-U.S. Gov\'t",IM,0,1,0,0,0,0\r\n19936216,0,0,2009,Oliveri M;Turriziani P;Koch G;Lo Gerfo E;Torriero S;Vicario CM;Petrosini L;Caltagirone C,PLoS One,"Dipartimento di Psicologia, Universit\xc3\xa0 degli Studi di Palermo, Palermo, Italy. maxoliveri@unipa.it",Journal Article,IM,0,1,0,0,0,0\r\n19933818,0,0,2009,Rosenthal SM,CMAJ,,Comment;Letter,AIM;IM,0,1,0,0,0,0\r\n"""
    assert_equals(csv_data, gold_response)
    
        