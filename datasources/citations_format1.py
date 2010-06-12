from utils.cache import TimedCache
from pyparsing import *
from collections import defaultdict

id_pattern = Word(nums)("id")
year_pattern = Word(nums, exact=4)("year") 
volume_pattern = Word(nums)("volume")
name_pattern = SkipTo(",")("first_author") + "," + Word(alphas, exact=1) + "." + SkipTo(year_pattern) 
journal_pattern = Or(SkipTo(volume_pattern), SkipTo(":"))("journal")
issue_pattern = Suppress("(") + Word(nums)("issue") + Suppress(")")
page_pattern = SkipTo(":") + ":" + Word(alphanums)("first_page") + SkipTo(",") #Optional("-") + Optional(Word(nums))
biblio_pattern = journal_pattern + Optional(volume_pattern) + Optional(issue_pattern) + SkipTo(":") + ":" + page_pattern
citation_pattern = id_pattern + "," + name_pattern + year_pattern + "," + biblio_pattern + ","

biblio_pattern2 = SkipTo(volume_pattern)("journal") + volume_pattern + Optional(issue_pattern) + Optional(page_pattern)
#citation_pattern2 = id_pattern + "," + Optional(name_pattern) + Optional(",") + year_pattern + "," + Or(biblio_pattern, biblio_pattern2) + ","
citation_pattern2 = id_pattern + "," + Optional(name_pattern) + Optional(",") + year_pattern + "," + biblio_pattern2 + ","


# A citation line looks like this
#  1,"Kauczor, H. U. ",2002, Acad Radiol 9 Suppl 2: S504-6.,Hyperpolarized 3helium gas as a novel contrast agent for functional MRI of ventilation.,,
#  2,"Mikhelashvili-Browner, N., D. M. Yousem, et al. ",2002, Acad Radiol 9(5): 513-9.,Correlation of reaction time in and out of the functional MR unit.,,
def get_citations_from_line(line):
    #print line
    items = get_dict_of_hits(citation_pattern2, line)
    return items
    
def get_citations_from_page(page):
    # Clean up stray characters in the citations
    page = page.replace('"', '')
    page = page.replace('\\', '')
    list_of_items = [get_citations_from_line(line) for line in page.splitlines()[1:]]
    return(list_of_items)

@TimedCache(timeout_in_seconds=1) # 60*60*24*7)            
def get_dict_of_hits(pattern, text):
    default_items = defaultdict(str)
    items = pattern.searchString(text)
    if items:
        for key in items[0].keys():
            default_items[key] = items[0][key]
    else:
        print "\n\nPARSING ERROR:\n" + text
        default_items['id'] = text.split(",")[0]
    return(default_items)
    
def convert_items_to_lookup_strings(items):
    lookup_strings = []
    for item in items:
        try:
            lookup_id = item['id']
            info_list = [item['journal'].strip(), item['year'], item['volume'], item['first_page'], item['first_author'], lookup_id]
        except KeyError:
            info_list = ["", "", "", "", "", "", "unparsed"]
        lookup_strings.append("|".join(info_list))
    for line in lookup_strings:
        print(line)
    return(lookup_strings)
             
    
