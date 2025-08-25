"""
Parse operation subsections
"""

import itertools as itt
from ._sass_util import SASS_Util as su

class SASS_Parser_Funit:
    def __init__(self, funit:dict):
        for param in funit.keys():
            setattr(self, param, funit[param])

    @staticmethod
    def parse(lines_iter:itt.islice, local_res:dict, tt:dict):
        lines = []
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif c == ';': break
            else: lines.append(c)
        xx = "".join(lines)

        # part with uC and issue slots
        uc = xx.strip()
        res = su.as_dict([x for x in ('name ' + uc.strip()).split()], su.try_convert)

        lines = []
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif c == ';': break
            else: lines.append(c)
        xx = "".join(lines)

        # part with the encoding width
        ew = xx.strip()
        ewn = 'ENCODING WIDTH'
        res[ewn.lower().replace(' ','_')] = su.try_convert(ew[(ew.find(ewn) + len(ewn)):])

        lines = []
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif c == ';': break
            else: lines.append(c)
        xx0 = "".join(lines)

        xx, nop = xx0.split('NOP_ENCODING')
        nop = 'NOP_ENCODING\n' + nop.strip()

        # part with the bit patterns
        xx1 = [x.strip().strip("'") for x in itt.chain.from_iterable([x.split() for x in [x.strip() for x in xx.split('\n') if x.strip()]])]
        
        instr_patterns = dict([(xx1[ind], "".join(["1" if x=='X' else "0" for x in xx1[ind+1]])) for ind in range(0,len(xx1),2)])
        nop_pattern = su.as_bits(res['encoding_width']*'.', 0, 0)

        res['encoding'] = instr_patterns
        res['encoding_ind'] = dict([(i[0],tuple(ind for ind,j in enumerate(i[1]) if j=='1')) for i in instr_patterns.items()])
        res['nop_encoding'] = nop_pattern

        return '', res
        
