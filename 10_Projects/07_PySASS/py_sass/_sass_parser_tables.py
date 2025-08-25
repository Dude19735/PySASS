"""
Parses the tables
"""

import itertools as itt
from ._sass_util import SASS_Util as su

class SASS_Parser_Tables:
    def __init__(self, tables:dict):
        for param in tables.keys():
            setattr(self, param, tables[param])

    @staticmethod
    def parse_table(lines_iter:itt.islice, local_res:dict):
        result = {}
        entry = []
        xx = ''
        while True:
            i = next(lines_iter, False)
            if not i: break

            if i == ';':
                xx = "".join(entry).strip()
                entry = []
                break
            else:
                entry.append(i)

        xx2 = dict([
            (su.as_tuple([su.try_convert(ww, convert_hex=True, convert_bin=True, replace_quotes=True) for ww in w[0].split() if ww.strip()]), 
             su.try_convert(w[1], convert_bin=True, convert_hex=True)
             ) for w in [z.split('->') for z in [y.strip() for y in xx.split('\n')]]])
        return '', xx2

    @staticmethod
    def parse(lines_iter:itt.islice, outer_res:dict, tt:dict):
        result = {}
        entry = []
        while True:
            c = next(lines_iter, False)
            if not c: break

            if c in (' ', '\n'):
                nn = "".join(entry).strip()
                if nn in tt.keys():
                    return nn, result
                elif nn:
                    new_nn, res = SASS_Parser_Tables.parse_table(lines_iter, result)
                    result = su.update_dict({nn: res}, result)
                    nn = new_nn
                    entry = []
            else:
                entry.append(c)

        return '', result
        
