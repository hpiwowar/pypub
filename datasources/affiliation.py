import re
import time
import urllib2
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from utils import world
from utils.cache import TimedCache
from datasources import fieldname, datasourcesError
from datasources import pubmed
from datasources import DataSource
from datasources import urlopener

# Affiliation algorithm, email pattern, and evaluation from paper:
# Yu et al. An automatic method to generate domain-specific investigator networks using PubMed abstracts. BMC medical informatics and decision making (2007) vol. 7 pp. 17

EMAIL_PATTERN = """[a-z0-9.\-_+]+@([a-z0-9\_]+\.)+(com|net|org|edu|int|mil|gov|arpa|biz|tr|jp|pl|tr|fr|cz|cn|au|aero|name|coop|info|pro|museum|tv|([a-z]{2}))"""
INSTITUTION_PATTERN = """univ|institu|hospital|college|cent|foundat|school|acad|facul|labora|clin|infirm|agenc"""

def is_email_address(string):
    if re.search(EMAIL_PATTERN, string.lower()):
        return True
    else:
        return False
    
def get_country_from_address(address):
    if not address:
        return None
    
    address_clean = address.replace("&lt;", "").replace("&gt;", "")    
    address_split = address_clean.strip(".").split(". ")    
    email_part = address_split[-1]
    if is_email_address(email_part):
        country = resolve_country(email_part)
    else:
        country_raw = address.split(",")[-1]
        country = country_raw.strip(".").strip()
        
    return(country)

def get_institutions_from_address(address):
    if not address:
        return None
    address_split = address.split(",")
    for address_part in reversed(address_split):
        if re.search(INSTITUTION_PATTERN, address_part.lower()):
            return address_part.strip()
    return None

@fieldname("address")
def address(pmids):
    addresses = pubmed.corresponding_address(pmids)
    return(addresses)
        
@fieldname("country")
def country(pmids):
    addresses = pubmed.corresponding_address(pmids)
    countries = [get_country_from_address(address) for address in addresses]
    return(countries)

@fieldname("institution")
def institution(pmids):
    addresses = pubmed.corresponding_address(pmids)
    institutions = [get_institutions_from_address(address) for address in addresses]
    return(institutions)

def resolve_country(rawaddr):
    parts = rawaddr.split('.')
    if not len(parts):
        # no top level domain found, bounce it to the next step
        return rawaddr
    addr = parts[-1]
    if world.nameorgs.has_key(addr):
        return "USA"
    elif world.countries.has_key(addr):
        return world.countries[addr]
    else:
        # Not resolved
        return None




