"""
Parse operation subsections
"""

import itertools as itt
from ._sass_util import SASS_Util as su

class SASS_Parser_Operation:
    def __init__(self, operation:dict):
        for param in operation.keys():
            setattr(self, param, operation[param])

    @staticmethod
    def parse(lines_iter:itt.islice, local_res:dict, tt:dict):
        xx = []
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif c == ';': break
            else: xx.append(c)

        pp = [su.try_convert(x) for x in "".join(xx).split('\n')]

        return '', {pp[0] : [p.strip() for p in pp[1:] if p.strip()]} # type: ignore
