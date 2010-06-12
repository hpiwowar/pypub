import sys
import os
import re
from utils.cache import TimedCache
import utils.dbimport
import datasources
from datasources import fieldname, datasourcesError, DataSource
from collections import defaultdict


CLUSTERS_TABLE_NAME = "clusters"
CLUSTERS_COLUMNS = ["cluster_name", "pmid", "author_order"]

class AuthorityExcerpt(DataSource):
    def __init__(self, ids=[], db_name=":memory:", filename="", do_import=False):
        super(AuthorityExcerpt, self).__init__(ids, "authority_excerpt")
        self.db = utils.dbimport.get_connection(db_name)

        if do_import:
            self.create_table(CLUSTERS_TABLE_NAME, CLUSTERS_COLUMNS)        
            number_of_lines_imported = self.import_from_file_to_db(filename)
            #print number_of_lines_imported

    def create_table(self, table_name, column_names):
        command = utils.dbimport.get_table_create_command(table_name, [column_names])
        utils.dbimport.execute_python_db(self.db, command)
    
    def write_to_table(self, table_name, lines):
        data = [table_name, lines]
        command = utils.dbimport.get_table_insert_command(table_name, lines)
        utils.dbimport.execute_python_db(self.db, command, verbose=False)
    
    def parse_authority_excerpt_line(self, line):
        columns = line.split("\t")
        cluster_name = columns[1]
        cluster_size = columns[2]
        cluster_contents = columns[5].strip()
        cluster_pmid_authornum_tuples = [author_string.split("_") for author_string in cluster_contents.split("|")]
        return(cluster_name, cluster_pmid_authornum_tuples)
    
    def import_from_file_to_db(self, filename):
        file = open(filename, "r")
        number_of_lines = 0
        counter = 0
        for line in file:
            (cluster_name, cluster_pmid_authornum_tuples) = self.parse_authority_excerpt_line(line)
            clusters = [[CLUSTERS_COLUMNS]]
            for (pmid,num) in cluster_pmid_authornum_tuples:
                clusters.append([cluster_name, int(pmid),int(num)])
            self.write_to_table(CLUSTERS_TABLE_NAME, clusters)
            #print len(clusters)
            number_of_lines += len(clusters)
            counter += 1
            #print counter
            #print clusters
        file.close()
        return number_of_lines
        
    def get_number_of_rows(self):
        c = self.db.cursor()
        c.execute("SELECT COUNT(*) FROM clusters;")
        (number_of_lines,) = c.fetchone()
        return(number_of_lines)

    def get_all_pmids(self):
        c = self.db.cursor()
        c.execute("SELECT DISTINCT(pmid) FROM clusters;")
        pmid_rows = c.fetchall()
        pmids = [pmid for (pmid,) in pmid_rows]
        return(pmids)

    def get_earliest_pmid_per_cluster(self):
        cur = self.db.cursor().execute("SELECT MIN(pmid_int) FROM clusters GROUP BY cluster_name;")
        pmid_rows = cur.fetchall()
        pmids = [str(pmid) for (pmid,) in pmid_rows]
        return(pmids)

AIM3_DB = "/Users/hpiwowar/Documents/Code/hpiwowar/pypub/trunk/src/pypub.db"

def first_author_all_pubs(pmids):
    authoritydb = AuthorityExcerpt(db_name=AIM3_DB)
    response = []
    for query_pmid in pmids:
        select_string = """select pmid from clusters
            where cluster_name = (select first_author_cluster 
            from first_last_author_clusters 
            where pmid='%s')""" %query_pmid
        cur = authoritydb.db.cursor().execute(select_string)
        cluster_pmid_rows = cur.fetchall()
        #print cluster_pmid_rows
        cluster_pmids = [str(pmid) for (pmid,) in cluster_pmid_rows]
        response.append(cluster_pmids)
    return(response)

def last_author_all_pubs(pmids):
    authoritydb = AuthorityExcerpt(db_name=AIM3_DB)
    response = []
    for query_pmid in pmids:
        select_string = """select pmid from clusters
            where cluster_name = (select last_author_cluster 
            from first_last_author_clusters 
            where pmid='%s')""" %query_pmid
        cur = authoritydb.db.cursor().execute(select_string)
        cluster_pmid_rows = cur.fetchall()
        #print cluster_pmid_rows
        cluster_pmids = [str(pmid) for (pmid,) in cluster_pmid_rows]
        response.append(cluster_pmids)
    return(response)

@TimedCache(timeout_in_seconds=60*60*24*7)            
def get_aggregate_attributes(pmids):
    pmids_string = ",".join(["'"+pmid+"'" for pmid in pmids])
    authoritydb = AuthorityExcerpt(db_name=AIM3_DB)
    select_string = """select sum(pubmed_in_genbank), 
        sum(pubmed_in_pdb), 
        sum(pubmed_in_swissprot), 
        sum(is_microarray_data_creation), 
        sum(in_ae_or_geo), 
        sum(is_geo_reuse), 
        sum(pubmed_is_meta_analysis), 
        sum(pubmed_is_multicenter_study), 
        sum(pubmed_is_open_access) 
        from authority_attributes where pmid in (%s);""" %pmids_string
    cur = authoritydb.db.cursor().execute(select_string)
    cluster_pmid_row = cur.fetchone()
    #print cluster_pmid_row
    attribute_names = ('in_genbank', 'in_pdb', 'in_swissprot', 'is_microarray_data_creation', 'in_ae_or_geo', 'is_geo_reuse', 'is_meta_analysis', 'is_multicenter_study', 'is_open_access')
    response = {}
    for i in range(len(attribute_names)):
        if cluster_pmid_row[i]:
            value = cluster_pmid_row[i]
        else:
            value = 0
        response[attribute_names[i]] = value
    return(response)
    
@TimedCache(timeout_in_seconds=60*60*24*7)            
def get_min_year(pmids):
    authoritydb = AuthorityExcerpt(db_name=AIM3_DB)
    response = []
    for query_pmid in pmids:
        if query_pmid:
            select_string = """select year from pmid_years where pmid='%s';""" %query_pmid
            cur = authoritydb.db.cursor().execute(select_string)
            cluster_pmid_row = cur.fetchone()
            (year,) = cluster_pmid_row
        else:
            year = None
        response.append(year)
    return(response)



