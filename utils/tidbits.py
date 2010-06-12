#import sys
#    module = sys.modules[__name__]
#    this_dir = os.path.dirname(os.path.abspath(module.__file__))
#    datafile = os.path.join(this_dir, 'data', 'myfile.txt')

#import cProfile
#import pstats
#import tests
#import tests.test_aim2b

#    cProfile.runctx('tests.test_aim2b.TestAcceptance().test_get_aim2b_part1_data(50)', globals(), locals(), filename="profout")
#    p = pstats.Stats('profout')
#    p.sort_stats('time').print_stats(10)
    # more examples:  http://docs.python.org/library/profile.html


def flat_list(lst):
    response = list(flatten(lst))
    return response
    
# From http://www.daniweb.com/code/snippet649.html#
def flatten(lst):
    for elem in lst:
        if type(elem) in (tuple, list):
            for i in flatten(elem):
                yield i
        else:
            yield elem
           
# docsum_iter = get_iter("<DocSum>.*?</DocSum>", summary_xml)
# for docsum in docsum_iter:
#        record_text = docsum.group()
def get_iter(pattern, text):
    # Then for i in iter, use i.group() as the zone
    docsum_pattern = re.compile(pattern, re.DOTALL)
    docsum_iter = docsum_pattern.finditer(text)
    return(docsum_iter)
