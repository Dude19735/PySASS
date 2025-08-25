import termcolor
import typing
import itertools as itt
from py_sass import SASS_Expr
from py_sass import SM_SASS
from py_sass import SASS_Class
from py_sass import Instr_EncDec_Lookup
from py_sass_ext import BitVector
from . import _config as sp

"""
This file contains all methods necessary to create instructions, assemble them to
bits, create one ficticious kernel, decode that kernel and go back to class_names and
Instr_CuBin_Repr.

Check out _instr_cubin_test.py for use case sample methods.
"""

class CubinDecodeException(Exception):
    pass

class Instr_CuBin:
    @staticmethod
    def get_nop(sass:SM_SASS):
        sm_nr:int = sass.sm_nr
        if sm_nr < 70: return 'NOP'
        elif sm_nr <= 120: return 'nop_'
        else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

    @staticmethod
    def __instr_to_words_50pp(sass:SM_SASS, i1:BitVector, i2:BitVector, i3:BitVector):
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i1, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i2, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i3, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)

        ws:int = sass.sm.details.ARCHITECTURE.WORD_SIZE # type: ignore # always 64 up to this point
        if not ws == 64: raise Exception(sp.CONST__ERROR_UNEXPECTED) #...to say the least
        
        # distribute full-length instructions onto word sized chunks
        se = BitVector(ws*[0])
        b1 = BitVector(ws*[0])
        b2 = BitVector(ws*[0])
        b3 = BitVector(ws*[0])
        # encode scheduler bits
        se[-21:] = i1[3:24]
        se[-42:-21] = i2[3:24]
        se[-63:-42] = i3[3:24]
        b1 = i1[-64:]
        b2 = i2[-64:]
        b3 = i3[-64:]
        
        return [se,b1,b2,b3]

    @staticmethod
    def __instr_to_words_70pp(sass:SM_SASS, i1:BitVector):
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i1, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)

        ws:int = sass.sm.details.ARCHITECTURE.WORD_SIZE # type: ignore # always 64 up to this point
        if not ws == 64: raise Exception(sp.CONST__ERROR_UNEXPECTED) #...to say the least
        
        bb_cash = BitVector(i1[:ws])
        bb_inst = BitVector(i1[ws:])
        return [bb_inst, bb_cash]
    
    @staticmethod
    def instr_bv_list_to_bwords(sass:SM_SASS, instr_list:typing.List[BitVector]) -> typing.List[BitVector]:
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_list, list): raise Exception(sp.CONST__ERROR_ILLEGAL)

        sm_nr:int = sass.sm_nr
        words_list = []
        if sm_nr < 70:
            if not len(instr_list)%3 == 0: raise Exception("SM {0} to {1} require instr_list length to be a multiple of 3".format(50, 62))
            for i in range(0, len(instr_list), 3):
                words_list.extend(Instr_CuBin.__instr_to_words_50pp(sass, instr_list[i+0], instr_list[i+1], instr_list[i+2]))
        elif sm_nr <= 120:
            for i in range(0, len(instr_list)):
                words_list.extend(Instr_CuBin.__instr_to_words_70pp(sass, instr_list[i]))
        else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        return words_list
    
    @staticmethod
    def instr_bwords_to_bytes(bvl:typing.List[BitVector]):
        bits = [[hex(int(i,2))[2:].zfill(2) for i in 
                 reversed(['0b' + "".join(str(b) for b in bv[i:(i+8)]) for i in range(0,len(bv),8)])]
                    for bv in bvl]
        return b''.join([bytearray.fromhex("".join(bv)) for bv in bits])

    @staticmethod
    def check_expr_conditions(class_:SASS_Class, enc_vals:dict, throw:bool=False):
        # augment enc_vals with default values if they are not present
        enc_vals = class_.default_enc_vals | enc_vals
        
        # Check conditions
        conds = class_.CONDITIONS

        # get all required variables for all conditions
        required_alias = [c['expr'].get_alias() for c in conds]
        # conditions that have some sort of problem
        problematic = [ind for ind,a in enumerate(required_alias) if not all(k in enc_vals for k in a)]
        if problematic:
            required = [conds[i]['expr'].get_alias() for i in problematic]
            translate = [[(dd, str(required[ind][dd].value().value)) for dd in d] for ind,d in enumerate([set(r.keys()).difference(enc_vals) for r in required])]

            # make a copy...
            enc_vals = dict(enc_vals)
            for r,o in itt.chain.from_iterable(translate): enc_vals[r] = enc_vals[o]
            check_again = [ind for ind,a in enumerate(required_alias) if not all(k in enc_vals for k in a)]
            if check_again:
                required = [conds[i]['expr'].get_alias() for i in check_again]
                missing = ["Missing alias {0} in [{1}]".format([dd for dd in d], conds[ei]['expr']) for ei,d in [(ei, set(r.keys()).difference(enc_vals)) for r,ei in zip(required, check_again)]]
                raise Exception("Missing alias for expression:\n{0}".format("\n".join(missing)))

        err1 = [(i['code'], i['msg']) for i in conds if i['expr'](enc_vals) is False]
        if err1:
            for i in err1:
                print(termcolor.colored(i[0], 'red', attrs=['bold']), termcolor.colored(i[1], 'yellow'))

        # Not all table keys are checked by the CONDITIONS. Make sure all required table keys exist if
        # the instruction contains tables in the ENCODING stage.
        # NOTE: up to this point, all tables in the ENCODING stage are in the first spot of the expression
        tables = [i['alias'] for i in class_.ENCODING if i['alias'].startswith_table()]
        err2 = [str(t) for t in tables if t(enc_vals) is False]
        if err2:
            for i in err2:
                print(termcolor.colored("Invalid Table key", 'red', attrs=['bold']), termcolor.colored(i, 'yellow'))
        
        if err1 or err2:
            for k,v in enc_vals.items(): print("{0} = {1}".format(termcolor.colored(k,'red'), termcolor.colored(v,'yellow')))
            if throw:
                raise Exception("Tried to assemble SASS instruction [{}] with illegal encoding values!".format(class_.class_name))
            return False
        return True

    @staticmethod
    def instr_assemble_to_bv(sass:SM_SASS, class_name:str, enc_vals:dict, check_conditions=True) -> BitVector:
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)

        sm_nr:int = int(sass.sm.details.SM_XX.split('_')[-1])
        encw:int = sass.sm.details.FUNIT.encoding_width # type: ignore
        if not encw in [128,88]: raise Exception(sp.CONST__ERROR_UNEXPECTED) #...alternate reality

        class_:SASS_Class = sass.sm.classes_dict[class_name]
        if check_conditions:
            Instr_CuBin.check_expr_conditions(class_, enc_vals, throw=True)
            
        # Add default values that are not present yet in enc_vals. Some instructions (or most of them)
        # don't actually have a full set of cash bits. In the parsing and finalizing step, those instructions
        # get those bits (appropriate for their SM version) added to them for consistency. In here, we like to encode
        # a new instruction based on passed "enc_vals". Since the instruction generator doesn't include the augmented instructions
        # (probably) we have to add the default encoding values for them to the enc_vals we will encode, manually.
        # This one will take all the values in default_enc_vals and extend/override it with the values in enc_vals.
        enc_vals = class_.default_enc_vals | enc_vals

        enc_expr_ = [(e['alias'], e['code_ind']) for e in class_.ENCODING]

        # allocate space for each instruction
        bv = BitVector(encw*[0]) # 1st instr in pack

        # assemble the bits for each instruction based on the expressions in the ENCODING stage
        expr:SASS_Expr
        for expr, enc in enc_expr_: bv = expr.assemble(enc_vals, enc, bv, sm_nr)

        # make sure that no assembled instruction violates its allowed bitmask
        if not [m or b for m,b in zip(class_.funit_mask, bv)] == class_.funit_mask: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return bv
    
    @staticmethod
    def cubin_to_instr_bits(cubin_bits:list, sass:SM_SASS):
        if not isinstance(cubin_bits, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)

        sm_nr = int(sass.sm.details.SM_XX.split('_')[1])
        if sm_nr in [50, 52, 53, 60, 61, 62]: return Instr_CuBin.__cubin_to_instr_bits_50pp(cubin_bits, sass)
        elif sm_nr in [70, 72, 75, 80, 86, 90, 100, 120]: return Instr_CuBin.__cubin_to_instr_bits_70pp(cubin_bits, sass)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

    @staticmethod
    def __cubin_to_instr_bits_50pp(cubin_bits:list, sass:SM_SASS):
        if not isinstance(cubin_bits, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not len(cubin_bits) % 4 == 0: raise Exception(sp.CONST__ERROR_ILLEGAL)
        encw = sass.sm.details.FUNIT.encoding_width # type: ignore
        
        unused = 3*[0]
        schedule_prefix = [[],[],[]] # must contain three entries
        if not len(schedule_prefix) == 3: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        instruction_bits = []

        for ind,sb_bv in enumerate(cubin_bits):
            sb = list(sb_bv)
            if ind%4==0:
                schedule_prefix[0] = sb[-21:]
                schedule_prefix[1] = sb[-42:-21]
                schedule_prefix[2] = sb[-63:-42]
            else:
                instruction_bits.append(BitVector(unused + schedule_prefix[ind%4-1] + sb))
                if not len(instruction_bits[-1]) == encw: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return instruction_bits
    
    @staticmethod
    def __cubin_to_instr_bits_70pp(cubin_bits:list, sass:SM_SASS):
        if not isinstance(cubin_bits, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        encw = sass.sm.details.FUNIT.encoding_width # type: ignore
        
        instruction_bits = []
        tail = []
        for ind,sb_bv in enumerate(cubin_bits):
            if ind%2==0: tail = list(sb_bv)
            else: instruction_bits.append(BitVector(list(sb_bv) + tail))
            
        if not all(len(sb)==encw for sb in instruction_bits): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return instruction_bits
    
    @staticmethod
    def instr_bits_to_class(instr_bits_l:list, sass:SM_SASS, target_classes:list=[]) -> typing.List[str]:
        if not isinstance(instr_bits_l, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(target_classes, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if target_classes and len(target_classes) != len(instr_bits_l): raise Exception(sp.CONST__ERROR_ILLEGAL)

        encw = sass.sm.details.FUNIT.encoding_width # type: ignore
        sm = int(sass.sm.details.SM_XX.split('_')[1])
        res = []
        for i_ind, instr_bits in enumerate(instr_bits_l):
            if target_classes and i_ind%1000 == 0: print(100*" ",'\r', "[SM {0}]: Decode [{1}/{2}]".format(sm, i_ind, len(instr_bits_l)), end='\r', flush=True)
            if len(instr_bits) != encw: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            m_found = False
            for m_ind, enc_ref in sass.sm.opcode_ref.items():
                mask_check = all(instr_bits[i]==0 for i in m_ind)
                if not mask_check: continue

                found = False
                for enc_ind, enc_bin in enc_ref.items():
                    opc_bin = tuple(instr_bits[i] for i in enc_ind)
                    if not opc_bin in enc_bin: continue
                    if target_classes: tcn = target_classes[i_ind]
                    else: tcn = None

                    instr_match, msg = Instr_EncDec_Lookup.get(sass.lu[opc_bin], instr_bits, tcn)
                    if msg:
                        raise CubinDecodeException("Instruction class matching failed with the following message: {0}".format(msg))
                    res.append(instr_match)
                    found = True
                    break
                if found: 
                    m_found = True
                    break
            if not m_found: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if target_classes: print(100*" ",'\r', "[SM {0}]: Decode [{1}/{2}]".format(sm, len(instr_bits_l), len(instr_bits_l)))
        return res
