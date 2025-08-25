"""
Architecture parser for the instructions.txt
"""

import itertools as itt
from ._sass_util import SASS_Util as su
from ._sass_parser_list import SASS_Parser_List
from ._sass_parser_condition import SASS_Parser_Condition

class SASS_Parser_Arch:
    def __init__(self, arch:dict):
        for param in arch.keys():
            setattr(self, param, arch[param])

    @staticmethod
    def parse_addr_base(lines_iter:itt.islice, local_res:dict):
        xx = []
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif c == ';': break
            else: xx.append(c)

        rr = "".join(xx)
        if rr.find('+'):
            res = [su.try_convert(x) for x in rr.split('+')]
            return '', {'base': res[0], 'op': '+', 'offset': res[1]}
        elif rr.find('-'):
            res = [su.try_convert(x) for x in rr.split('-')]
            return '', {'base': res[0], 'op': '-', 'offset': res[1]}

    @staticmethod
    def parse_empty(lines_iter:itt.islice, local_res:dict):
        xx:str = ''
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif xx.endswith('";'): break
            else: xx += str(c)

        rr = "".join(xx).split('"')
        if len(rr) != 3:
            raise ValueError("EMPTY_INSTRUCTION is not as expected")
        
        return '', rr[1]

    @staticmethod
    def parse_options(lines_iter:itt.islice, local_res:dict):
        xx = []
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif c == ';': break
            else: xx.append(c)

        return '', [su.try_convert(x) for x in "".join(xx).split(',')]

    @staticmethod
    def parse_var(lines_iter:itt.islice, local_res:dict):
        xx = []
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif c == ';': break
            else: xx.append(c)

        return '', su.try_convert("".join(xx))
    
    @staticmethod
    def parse_reloc(lines_iter:itt.islice, local_res:dict):
        result = []
        while True:
            c = next(lines_iter, False)
            if not c: break
            elif c == ';': break
            elif c =='{': 
                res = SASS_Parser_List.parse(lines_iter)
                result.append(res)
        return '', result

    @staticmethod
    def parse(lines_iter:itt.islice, outside_res:dict, tt:dict):
        local_tt = {
            'PROCESSOR_ID': SASS_Parser_Arch.parse_var,
            'ISSUE_SLOTS': SASS_Parser_Arch.parse_var,
            'WORD_SIZE': SASS_Parser_Arch.parse_var,
            'BRANCH_DELAY': SASS_Parser_Arch.parse_var,
            'ELF_ID': SASS_Parser_Arch.parse_var,
            'ELF_ABI': SASS_Parser_Arch.parse_var,
            'ELF_ABI_VERSION': SASS_Parser_Arch.parse_var,
            'ELF_VERSION': SASS_Parser_Arch.parse_var,            
            'RELOCATORS': SASS_Parser_Arch.parse_reloc,
            'OPTIONS': SASS_Parser_Arch.parse_options,
            'RELATIVE_ADDRESS_BASE': SASS_Parser_Arch.parse_addr_base,
            'EMPTY_INSTRUCTION': SASS_Parser_Arch.parse_empty,
            'CONDITION': SASS_Parser_Condition.parse
        }

        local_result = {}
        entry = []
        ff = None
        nn = ''
        next_nn = ''
        class_type = 'ARCHITECTURE'
        class_name = ''
        while True:
            c = next(lines_iter, False)
            if not c: break

            elif c in (' ', '\n', '='):
                nn = "".join(entry).strip()
                while nn:
                    if nn.startswith('"') and nn.endswith('"'):
                       class_name = nn.strip('"')
                       nn = ''
                    elif nn in local_tt.keys():
                        ff = local_tt[nn]
                        if ff:
                            new_nn, res = ff(lines_iter, local_result)
                            local_result = su.update_dict({nn: res}, local_result)
                            nn = new_nn
                        else:
                            nn = ''
                    # this one should be 'PARAMETERS'
                    else: 
                        next_nn = nn
                        nn = ''
                        break

                    entry = []
            else:
                entry.append(c)

            if next_nn:
                break
        
        local_result = su.update_dict({class_type: class_name}, local_result)
        return next_nn, local_result
