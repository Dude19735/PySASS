import itertools as itt
from ._sass_util import SASS_Util as su

class SASS_Parser_Assignment:
    """
    This one is part of the instruction.txt parser.

    It covers stuff like
    PARAMETERS
        MAX_REG_COUNT = 255
        SHADER_TYPE = 0
        MAX_CONST_BANK = 17
    """

    @staticmethod
    def parse(lines_iter:itt.islice, local_res:dict, tt:dict={}):
        entry = []
        result = {}
        ee = ''
        while True:
            i = next(lines_iter, False)
            if not i: break

            if i == '\n':
                ee = "".join(entry)
                ind = ee.find('=')
                if ind >= 0:
                    d = {ee[:ind].strip(): su.try_convert(ee[(ind+1):].strip())}
                    result = su.update_dict(d, result)
                else:
                    break
                entry = []
            else:
                entry.append(i)
        return ee, result
