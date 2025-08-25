"""
This one iterates over one giant sass config string. It is a core part of the instructions.txt parser.
"""

from collections import defaultdict
from . import _config as sp
from ._sass_util import SASS_Util as su
from ._sass_parser_registers import SASS_Parser_Registers
from ._sass_parser_assignment import SASS_Parser_Assignment
from ._sass_parser_arch import SASS_Parser_Arch
from ._sass_parser_tables import SASS_Parser_Tables
from ._sass_parser_operation import SASS_Parser_Operation
from ._sass_parser_funit import SASS_Parser_Funit
from .sass_class import SASS_Class
from .sass_class import Iterator

class SASS_Parser_Iter:
    def __init__(self):
        pass

    @staticmethod
    def parse(sm_xx:int, instructions_txt:str):
        sm90_reg_jumbo = {
            'SIZE_64x8x16_64x16x16_64x24x16_64x32x16_64x40x16_64x48x16_64x56x16_64x64x16_64x72x16_64x80x16_64x88x16_64x96x16_64x104x16_64x112x16_64x120x16_64x128x16_64x136x16_64x144x16_64x152x16_64x160x16_64x168x16_64x176x16_64x184x16_64x192x16_64x200x16_64x208x16_64x216x16_64x224x16_64x232x16_64x240x16_64x248x16_64x256x16_64x8x32_64x16x32_64x24x32_64x32x32_64x40x32_64x48x32_64x56x32_64x64x32_64x72x32_64x80x32_64x88x32_64x96x32_64x104x32_64x112x32_64x120x32_64x128x32_64x136x32_64x144x32_64x152x32_64x160x32_64x168x32_64x176x32_64x184x32_64x192x32_64x200x32_64x208x32_64x216x32_64x224x32_64x232x32_64x240x32_64x248x32_64x256x32' : 'SIZE_64..1',
            'SIZE_64x8x16_64x16x16_64x24x16_64x32x16_64x40x16_64x48x16_64x56x16_64x64x16_64x72x16_64x80x16_64x88x16_64x96x16_64x104x16_64x112x16_64x120x16_64x128x16_64x136x16_64x144x16_64x152x16_64x160x16_64x168x16_64x176x16_64x184x16_64x192x16_64x200x16_64x208x16_64x216x16_64x224x16_64x232x16_64x240x16_64x248x16_64x256x16_64x8x8_64x16x8_64x24x8_64x32x8_64x40x8_64x48x8_64x56x8_64x64x8_64x72x8_64x80x8_64x88x8_64x96x8_64x104x8_64x112x8_64x120x8_64x128x8_64x136x8_64x144x8_64x152x8_64x160x8_64x168x8_64x176x8_64x184x8_64x192x8_64x200x8_64x208x8_64x216x8_64x224x8_64x232x8_64x240x8_64x248x8_64x256x8' : 'SIZE_64..2',
            'SIZE_64x8x32_64x16x32_64x24x32_64x32x32_64x40x32_64x48x32_64x56x32_64x64x32_64x72x32_64x80x32_64x88x32_64x96x32_64x104x32_64x112x32_64x120x32_64x128x32_64x136x32_64x144x32_64x152x32_64x160x32_64x168x32_64x176x32_64x184x32_64x192x32_64x200x32_64x208x32_64x216x32_64x224x32_64x232x32_64x240x32_64x248x32_64x256x32' : 'SIZE_64..3',
            'SIZE_64x8x32_64x16x32_64x24x32_64x32x32_64x48x32_64x64x32_64x80x32_64x96x32_64x112x32_64x128x32_64x144x32_64x160x32_64x176x32_64x192x32_64x208x32_64x224x32_64x240x32_64x256x32' : 'SIZE_64..4',
            'SIZE_64x8x64_64x16x64_64x24x64_64x32x64_64x40x64_64x48x64_64x56x64_64x64x64_64x72x64_64x80x64_64x88x64_64x96x64_64x104x64_64x112x64_64x120x64_64x128x64_64x136x64_64x144x64_64x152x64_64x160x64_64x168x64_64x176x64_64x184x64_64x192x64_64x200x64_64x208x64_64x216x64_64x224x64_64x232x64_64x240x64_64x248x64_64x256x64' : 'SIZE_64..5',
            'SIZE_64x8x64_64x16x64_64x24x64_64x32x64_64x48x64_64x64x64_64x80x64_64x96x64_64x112x64_64x128x64_64x144x64_64x160x64_64x176x64_64x192x64_64x208x64_64x224x64_64x240x64_64x256x64' : 'SIZE_64..6'
        }

        tt = {
            "ARCHITECTURE": SASS_Parser_Arch.parse, 
            "PARAMETERS": SASS_Parser_Assignment.parse, 
            "CONSTANTS": SASS_Parser_Assignment.parse, 
            "STRING_MAP": None,
            "REGISTERS": SASS_Parser_Registers.parse,
            "TABLES": SASS_Parser_Tables.parse,
            "OPERATION": SASS_Parser_Operation.parse,
            "FUNIT": SASS_Parser_Funit.parse, 
            "CLASS": SASS_Class.parse,
            "ALTERNATE": SASS_Class.parse
        }

        # milestones = [
        #     "ARCHITECTURE\n", 
        #     "PARAMETERS\n", 
        #     "CONSTANTS\n", 
        #     "STRING_MAP\n",
        #     "REGISTERS\n",
        #     "TABLES\n",
        #     "OPERATION PROPERTIES\n",
        #     "OPERATION PREDICATES\n",
        #     "FUNIT ",
        #     'CLASS "'
        # ]

        instr = ''
        with open(instructions_txt,'r') as f:
            instr = f.read()
            if instr == '':
                raise Exception(instructions_txt + " not found!")
            # apply some bugfixes to the file
            # instr.replace('Chkmode', 'ChkMode')

        # [(m.start(0), m.end(0), m.group(0)) for m in re.finditer("|".join(milestones), instr)]
        # mstones = [m.end(0) for m in re.finditer("|".join(milestones), instr)]    
        # mstones.append(len(instr))
        msg = "Parse {0}...".format(instructions_txt.split('/')[-1])
        print('\n|' + msg + (100-len(msg)-2)*' ' + '|')

        if sm_xx == 90:
            jumbos = sorted([i for i in sm90_reg_jumbo.keys()], key=lambda x: len(x), reverse=True)
            for i in jumbos:
                instr = instr.replace(i, sm90_reg_jumbo[i])

        progr_v = len(instr) / 10
        progr_n = 0
        def pb(lines_iter:Iterator, progr_v, progr_n):
            pn = lines_iter.chr_counter // progr_v
            if pn > progr_n: 
                while progr_n < pn:
                    print(10*'=',end='', flush=True)
                    progr_n += 1
            return progr_n

        lines_iter = Iterator(instr)
        result = {}
        entry = []
        ff = None
        sp.GLOBAL__ALL_NON_REGS = []
        while True:
            c = next(lines_iter, False)
            if not c: break

            if c in (' ', '\n'):
                nn = "".join(entry).strip()
                while nn:
                    entry = []
                    if nn == 'CLASS' or nn == 'ALTERNATE':
                        pass
                    if nn in tt.keys():
                        ff = tt[nn]
                        if ff:
                            is_alternate = False
                            if nn == 'ALTERNATE':
                                is_alternate = True
                                while next(lines_iter, False) != ' ':
                                    pass
                                nn = 'CLASS'
                            if nn == 'CLASS':
                                new_nn, res = ff(lines_iter, result, tt, is_alternate)
                            else:
                                new_nn, res = ff(lines_iter, result, tt)

                            if nn in result:
                                result[nn] = su.update_dict(res, result[nn])
                            else:
                                result = su.update_dict({nn: res}, result)
                            
                            if nn == 'TABLES':
                                # NOTE: evaluating the table must be done AFTER inverting it. The inversion
                                # needs the verbose output! => Nope!!! The other way around
                                # In the real tables, we may have stuff like this:
                                #   Register@R0 Register@R1 CASInteger@"32" -> 0b0_00000000
                                # But if we forwards insert, we will have numbers. Thus we need a
                                # forwards table that also has numbers as args
                                regs = result['REGISTERS']
                                table_dec = {}
                                for table in result[nn]:
                                    old_tt = result[nn][table]
                                    new_tt = []
                                    for i in old_tt.items():
                                        kk = i[0]
                                        new_kk = []
                                        for k in kk:
                                            if isinstance(k,str):
                                                if k.find('@') >= 0:
                                                    r1,r2t = k.split('@')
                                                    r2 = su.try_convert(r2t)
                                                    if not r2 in regs[r1]:
                                                        if r1 == 'DC' and r2 == 'noDC':
                                                            raise Exception("{0} not found in {1}: rename all instances of 'nodc' to 'noDC'!".format(r2, r1))
                                                        if r1 == 'MS' and r2 == 'noMS':
                                                            raise Exception("{0} not found in {1}: rename all instances of 'noms' to 'noMS'!".format(r2, r1))
                                                        else:
                                                            raise Exception("{0} not found in {1}".format(r2, r1))
                                                    v = regs[r1][r2]
                                                    new_kk.append(v)
                                                else:
                                                    # this is stuff like ("'&'", 0) => let's see if this is necessary too
                                                    new_kk.append(k)
                                            else:
                                                if not isinstance(k,int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                                                new_kk.append(k)
                                        # we now have sets for register values
                                        if any(isinstance(v,set) for v in new_kk):
                                            inter1 = sorted([(len(x) if isinstance(x,set) else 1,x) for x in new_kk], key=lambda x:x[0], reverse=True)
                                            if all(x[0]==1 for x in inter1): new_kk = [next(iter(x[1])) if isinstance(x[1], set) else x[1] for x in inter1]
                                            else:
                                                # This would be the case where we can have multiple values for a specific register.
                                                # We don't know if we need this case yet, though...
                                                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
                                        new_tt.append((tuple(new_kk), su.try_convert(i[1], convert_bin=True, convert_hex=True, convert_split_bin=True)))
                                    table_dec[table] = dict(new_tt)
                                # just replace it...
                                result[nn] = table_dec

                                # In tables, we may have things like
                                # Integer@U8 -> 0b0_00
                                # In the forward parsing, we can't remove those because we need the '_' to generate
                                # bit codes (the '_' signify jumps in the bit pattern). In the inverse, we match integers.
                                # For that, we have to convert the 0b0_00 and the likes to numbers as well. 
                                inv_i = dict([(i[0], [(su.try_convert(j[1], convert_bin=True, convert_hex=True, convert_split_bin=True),j[0]) for j in i[1].items()]) for i in result[nn].items()])
                                inv = dict([(i,defaultdict(list)) for i in inv_i.keys()])
                                for i in inv.items():
                                    for j in inv_i[i[0]]:
                                        i[1][j[0]].append(j[1])
                                result = su.update_dict({nn + "_INV":inv}, result)
                            nn = new_nn
                        else:
                            nn = ''
                    else:
                        nn = ''

                    # progress bar        
                    progr_n = pb(lines_iter, progr_v, progr_n)
            else:
                entry.append(c)

            # progress bar
            progr_n = pb(lines_iter, progr_v, progr_n)
        print()

        # result['FUNCS'] = dict([(i, None) for i in set(sp.GLOBAL__ALL_NON_REGS)])
        result['FUNCTIONS'] = dict([(i, None) for i in set(sp.GLOBAL__ALL_FUNCTIONS)])
        result['ACCESSORS'] = dict([(i, None) for i in set(sp.GLOBAL__ALL_ACCESSORS)])

        if sm_xx == 90:
            sm90_reg_jumbo_inv = {}
            for i in sm90_reg_jumbo.items():
                sm90_reg_jumbo_inv[i[1]] = i[0]
            result['SM90_JUMBO_INV'] = sm90_reg_jumbo_inv
        
        return result

if __name__ == '__main__':
    results = {}
    instructions = {}

    sm = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90]
    for s in sm:
        instructions_txt = 'DocumentSASS/sm_' + str(s) + '_instructions.txt.in'
        print(instructions_txt)
        result = SASS_Parser_Iter.parse(s, instructions_txt)
