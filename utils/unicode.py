#!/usr/bin/env python
# -*- coding: latin-1 -*-


def clean_up_strange_unicode(broken_string):
    # Some unicode for testing:  áéíóú
    
    # Todo look into unichar to solve this???
    
    new_string = ""
    try:
        for char in broken_string:
            if ord(char) < 128:
                new_string += char
            else:
                new_string += "?"
    except TypeError:
        new_string = str(broken_string)
    return(new_string)
