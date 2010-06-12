create table cluster_maxes as 
select cluster_name, 
sum(is_microarray_data_creation) as is_microarray_data_creation, 
max(pubmed_in_genbank) as in_genbank, 
max(pubmed_in_pdb) as in_pdb, 
max(pubmed_in_swissprot) as in_swissprot, 
sum(in_ae_or_geo) as in_ae_or_geo, 
max(is_geo_reuse) as is_geo_reuse, 
max(pubmed_is_meta_analysis) as is_meta_analysis, 
max(pubmed_is_multicenter_study) as is_multicenter_study, 
max(pubmed_is_open_access) as is_open_access 
from authority_attributes a, clusters c 
where a.pmid=c.pmid group by cluster_name;



create table first_last_author_clusters as
select distinct(a.pmid) as pmid, 
a.cluster_name as first_author_cluster,
b.cluster_name as last_author_cluster
from clusters a, clusters b
where a.pmid = b.pmid
and a.author_order_int = 1
and b.author_order_int = (select max(c.author_order_int) from clusters c where c.pmid=b.pmid);

select pmids
from clusters
where cluster_name = (select first_author_cluster from
    first_last_author_clusters where pmid=query_pmid)

delete from first_last_author_clusters where not exists (select 1 from vars v where pmid=v.mid);
delete from first_last_author_clusters where pmid not in (select pmid from vars);

select count(*) from first_last_author_clusters, aim3_vars where
first_last_author_clusters.pmid = aim3_vars.pmid;

    
CREATE TABLE pmid_years (pmid, year)
import into it

CREATE TABLE cluster_min_year as    
select distinct(cluster_name) as cluster_name, c.pmid as pmid, year as min_year 
from clusters c, pmid_years
where c.pmid_int = (select min(pmid_int) from clusters cc where cc.cluster_name=c.cluster_name)
and pmid_years.pmid = c.pmid;
    
    


delete all lines that are not pmids in my cohort

then:  write code to get maxes for first author etc?
then:  see if papers are sequential, and figure out pmid year breaks
then:  write code to collect number of papers for first and last
then:  write code to collect number of citations for first and last

then:  set grants up and running

first:  neuroethics


then:  import impact factor and journal data policy
then:  affiliation sector and rank
then:  need to run affiliation and clean it up a little bit, 
create a dirty->clean lookup table?

some point (could be on the weekend):  look at other papers
etc
