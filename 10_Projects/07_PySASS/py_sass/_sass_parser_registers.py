"""
Parses the registers
"""

import itertools as itt
from . import _config as sp
from ._sass_util import SASS_Util as su
from ._sass_parser_enum import SASS_Parser_Enum

class SASS_Parser_Registers:
    def __init__(self, registers:dict):
        for param in registers.keys():
            setattr(self, param, registers[param])

    @staticmethod
    def final_check(result:dict):
        if any([any([isinstance(sv, dict) for sk, sv in v.items()]) for k,v in result.items()]):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

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
                    SASS_Parser_Registers.final_check(result)        
                    return nn, result
                elif nn:
                    # if nn == 'NonZeroRegisterFAU':
                    #     pass
                    # if nn == 'F2FRound1':
                    #     pass
                    # if nn == 'NAN':
                    #     pass
                    new_nn, res = SASS_Parser_Enum.parse(lines_iter, result) # type: ignore
                    # if nn == 'NonZeroRegisterFAU':
                    #     pass
                    # if nn == 'F2FRound1':
                    #     pass
                    # if nn == nn == 'F32ONLY_i2fp':
                    #     pass
                    # if nn == 'RegisterFAU':
                    #     pass
                    # if nn == 'Register':
                    #     pass
                    # if nn == 'GRF':
                    #     pass
                    # if nn == 'Scoreboard':
                    #     pass
                    # if nn == 'Predicate':
                    #     pass
                    # if nn == 'SpecialRegister':
                    #     pass
                    # if nn == 'Integer':
                    #     pass
                    # if nn == 'SQInteger':
                    #     pass
                    # if nn == 'MufuOp':
                    #     pass
                    # if nn == 'CCTLTOp':
                    #     pass
                    # if nn == 'RGBA':
                    #     pass
                    # if nn == 'REQ':
                    #     pass

                    result = su.update_dict({nn: res}, result)
                    nn = new_nn
                    entry = []
            else:
                entry.append(c)

        SASS_Parser_Registers.final_check(result)
        return '', result
        
