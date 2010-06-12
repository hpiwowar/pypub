
import time
import pickle
import sys

class TimedCache(object):
    """Memoize With Timeout"""
    # Based on http://code.activestate.com/recipes/325905/
    _caches = {}
    _timeouts = {}
    _hits_and_misses = {}
    _is_bypass_cache = {}
    PICKLE_FILENAME = "/tmp/cache.pkl"
        
    def __new__(type, timeout_in_seconds=60*60*2):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type, timeout_in_seconds)
        return type._the_instance

    def __init__(self, timeout_in_seconds=60*60*2):
        self.timeout = timeout_in_seconds
        if not self._caches:
            try:
                self.load_cache()
                print "Loaded cache"
            except EOFError, e:
                print "Couldn't load cache"
                pass
    
    # To do
    #def delete_cache(self):
    #    pass
        #rm /tmp/cache.pkl
        
    def load_cache(self):
        try:
            pkl_file = open(self.PICKLE_FILENAME, 'rb')
            [self._caches, self._timeouts] = pickle.load(pkl_file)            
            pkl_file.close()  
            for func_key in self._caches:
                self._set_hits_and_misses(func_key)
                self._is_bypass_cache[func_key] = False
                self._timeouts[func_key] = self.timeout

        except IOError, EOFError:
            # No pickle file, so set to defaults
            pass
            
    def store_cache(self):
        try:
            pkl_file = open(self.PICKLE_FILENAME, 'wb')
            pickle.dump([self._caches, self._timeouts], pkl_file)
            pkl_file.close()
            print "\nStored cache"
        except RuntimeError, e:
            print "Failed to store cache!  Runtime Error:", e
            # might need to delete cache file to recover?  see delete_cache
        
    def collect(self):
        """Clear cache of results which have timed out"""
        for func_key in self._caches:
            cache = {}
            for key in self._caches[func_key]:
                if (time.time() - self._caches[func_key][key][1]) < self._timeouts[func_key]:
                    cache[key] = self._caches[func_key][key]
            self._caches[func_key] = cache

    def clear_cache(self):
        """Clear all caches of all results"""
        print "\nclearing caches"
        for func_key in self._caches:
            self._caches[func_key] = {}

    def is_bypass_cache(self, is_bypass_on):
        """Bypasses the cache for all functions when set to True"""
        #print "setting bypass to", is_bypass_on
        for func_key in self._caches:
            self._is_bypass_cache[func_key] = is_bypass_on

    def print_hits_and_misses_for_func(self, func_key):
        try:
            print "\n%60s:  Hits=%d, Misses=%d" %(func_key, self._hits_and_misses[func_key]['hits'], self._hits_and_misses[func_key]['misses'])
        except KeyError:
            # cache for this function was loaded by not accessed
            pass
            
    def print_hits_and_misses(self):
        """Clear cache of all results"""
        for func_key in self._caches:   
            self.print_hits_and_misses_for_func(func_key)    
    
    def get_func_key(self, f):
        return(f.__module__ + "." + f.func_name)

    def _set_hits_and_misses(self, func_key):
        self._hits_and_misses[func_key] = {'hits':0, 'misses':0}
                
    def __call__(self, f):
        # Add a check if time to call collect.  Maybe every 100 calls, or something?
        
        func_key = self.get_func_key(f)
        if not func_key in self._caches:
            self._caches[func_key] = {}
            self._timeouts[func_key] = self.timeout
        self._is_bypass_cache[func_key] = False
        self._set_hits_and_misses(func_key)
        
        def func(*args, **kwargs):
            kw = kwargs.items()
            kw.sort()
            key = (args, tuple(kw))
            func_key = self.get_func_key(f)
            try:
                (func_value, timestamp) = self._caches[func_key][str(key)]
                #print (time.time() - timestamp)
                #print self._timeouts[func_key]
                #print ((time.time() - timestamp) > self._timeouts[func_key])
                if (self._is_bypass_cache[func_key] or 
                    ((time.time() - timestamp) > self._timeouts[func_key])):
                    raise KeyError
                print "+",
                sys.stdout.flush()
                #print "+", func_key + " hits cache" #, " with args ", str(key)
                self._hits_and_misses[func_key]['hits'] += 1
            except KeyError:
                print "-",
                sys.stdout.flush()
                #print "-", func_key + " misses cache" #, " with args ", str(key)
                self._hits_and_misses[func_key]['misses'] += 1 
                func_value = f(*args,**kwargs)             
                self._caches[func_key][str(key)] = func_value, time.time()
            return func_value
        func.func_name = f.func_name
        return func


#@TimedCache(timeout_in_seconds=10)
#def hi(a=2):
#    print "hi heather"
#    return(a)