"""
All kinds of expressions that yield some sort of result
"""

from __future__ import annotations
import copy
import itertools as itt
import typing as typ
from . import _config as sp
from . import _sass_func
from ._tt_instruction import TT_Instruction
if not sp.SWITCH__USE_TT_EXT:
    from ._tt_terms import TT_Reg, TT_Func, AT_OP
else:
    from py_sass_ext import TT_Reg, TT_Func, TT_OpCashQuestion, TT_OpCashAnd, TT_OpCashAssign, TT_OpAtNegate, TT_OpAtNot, TT_OpAtInvert, TT_OpAtSign, TT_OpAtAbs, TT_AtOp
from ._sass_expression_utils import Op_Base
from ._sass_expression_utils import Op_Iter
from ._sass_expression_ops import *
# from ._sass_expression_domain_range import SASS_Expr_Domain_Range
from ._sass_expression_eval import SASS_Expr_Eval
from ._sass_expression_dec import SASS_Expr_Dec
from .sm_cu_details import SM_Cu_Details
from py_sass_ext import SASS_Bits
from py_sass_ext import BitVector

AT_OP = {'?':TT_OpCashQuestion, '&':TT_OpCashAnd, '=':TT_OpCashAssign, '-':TT_OpAtNegate, '!':TT_OpAtNot, '~':TT_OpAtInvert, '&&':TT_OpAtSign, '||':TT_OpAtAbs}

class SASS_Expr:
    def __init__(self, expr:str, tables:dict, constants:dict, registers:dict, parameters:dict, tables_inv:dict):
        # Make sure, the expression ends with exactly one whitespace. Otherwise the parser
        # won't work correctly with expressions with only one single character
        expr = expr.strip() + ' '

        # ` == REGISTERS
        # % == PARAMETERS
        # $ == CONSTANTS
        self.TABLES = tables
        expr = expr.strip()
        self.__expr =  expr
        self.__has_reg = False
        self.__has_func = False
        self.__has_large_func = False
        self.__convert_float_alias = None
        op:SASS_Op = SASS_Op()
        self.__split = []
        self.__print_outer_braces = [True]
        check_counter = 0
        self.__evaled = None
        splits = []
        self.__pattern = ()
        while expr:
            if check_counter > 5:
                # if we get more than 5 sub-expressions, there is a problem
                raise Exception("Too many sub expressions found")
            # if we have multiple expressions inside one right side, for example like this
            # DEFINED TABLES_opex_0(batch_t,usched_info)
            # where DEFINED and TABLES_opex_0 are not split by a valid expression splitter like a '(' or a '+'
            # we have to create multiple expressions. This is why we get a 2D array of expressions and not a 1D
            cc, split = op.split(expr, tables, constants, registers, parameters, tables_inv)
            expr = expr[cc:]
            splits.append(split)
            check_counter += 1
        self.__split = list(itt.chain.from_iterable(splits))
        if not (str(self).replace(' ','') == self.__expr.replace(' ','').replace('\n','').replace('"','')): raise Exception(sp.CONST__ERROR_UNEXPECTED)

    def __str__(self):
        res = []
        for ni,j in enumerate(self.__split):
            res.append(str(j))
        return "".join(res).strip()
    
    def __call__(self, enc_vals:dict) -> bool|SASS_Bits|list|int|set: #, bit_len:list=[], strict=False) -> typ.List[SASS_Bits] | SASS_Bits:
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        res = SASS_Expr_Eval.preorder_eval(self.__pre, enc_vals)
        if not (isinstance(res, bool|SASS_Bits|list|int|set) or res in (0,1)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        return res

    def __hash__(self):
        if not self.__pattern: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return self.__hash

    @property
    def has_reg(self): return self.__has_reg
    @property
    def has_func(self): return self.__has_func
    @property
    def has_large_func(self): return self.__has_large_func

    @property
    def expr(self): return self.__split
    @property
    def str(self): return str(self)
    @property
    def pattern(self): return self.__pattern
    @property
    def old_pattern(self): return self.__old_pattern

    @property
    def expr_embedded_str(self): return self.__embedded_str
    @property
    def expr_preorder(self): return self.__pre
    @property
    def preorder_str(self): return self.__pre_str

    def startswith_ConstBankAddressX(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_ConstBankAddress0) or isinstance(self.__split[0], Op_ConstBankAddress2)
    def startswith_convertFloat(self) -> bool: return isinstance(self.__split[0], Op_convertFloatType)
    def startswith_alias(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Alias)
    def startswith_tt_reg(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Alias) and isinstance(self.get_first_value(), TT_Reg)
    def startswith_tt_func(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Alias) and isinstance(self.get_first_value(), TT_Func)
    def startswith_opcode(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Opcode)
    def startswith_value(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Value)
    def startswith_defined(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Defined)
    def startswith_not_defined(self) -> bool: return len(self.__split) > 1 and isinstance(self.__split[0], Op_Not) and isinstance(self.__split[1], Op_Defined)
    def startswith_table(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Table)
    def startswith_int(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Int)
    def startswith_constant(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Constant)
    def startswith_register(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Register)
    def startswith_notEnc(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_NotEnc)
    def startswith_atOp(self) -> bool: return len(self.__split) > 0 and type(self.__split[0]) in EXPR_AT_OPS
    def startswith_identical(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_Identical)
    def startswith_lbrace(self) -> bool: return len(self.__split) > 0 and isinstance(self.__split[0], Op_LBrace)
    def is_int(self) -> bool: return self.startswith_int() and len(self.__split) == 1
    def is_constant(self) -> bool: return self.startswith_constant() and len(self.__split) == 1
    def is_register(self) -> bool: return self.startswith_register() and len(self.__split) == 1
    def is_scale(self) -> bool: return len(self.__split) > 2 and any(isinstance(i, Op_Scale) for i in self.__split)
    def is_fixed_val(self) -> bool: return not any(isinstance(i, Op_Alias) for i in self.__split)

    def get_first_value(self):
        if len(self.__split) == 0: return None
        return self.__split[0].value()

    def get_first_op(self):
        if len(self.__split) == 0: return None
        return self.__split[0]

    def get_alias_names(self) -> typ.List[str]:
        anames = set()
        if self.startswith_convertFloat():
            anames.add(self.__convert_float_alias)
        else:
            for i in self.__split:
                if isinstance(i, Op_Alias) or (type(i) in EXPR_AT_OPS):
                    anames.add(str(i))
        return list(anames)
    
    def get_alias_names_set(self) -> typ.Set[str]:
        anames = set()
        for i in self.__split:
            if isinstance(i, Op_Alias) or (type(i) in EXPR_AT_OPS):
                anames.add(str(i))
        return anames

    def get_sequenced_alias_names(self) -> typ.List[str]:
        anames = []
        for i in self.__split:
            if isinstance(i, Op_Alias) or (type(i) in EXPR_AT_OPS):
                var = str(i)
                if not var in anames:
                    anames.append(var)
        return anames
    
    def get_convertFloat_is_mufu(self) -> bool:
        if not self.startswith_convertFloat(): return False
        for i in self.__split:
            if isinstance(i, Op_Alias) and str(i.value()) == 'MUFU_OP': return True
        return False

    def get_table_args(self):
        if not self.startswith_table(): raise Exception(sp.CONST__ERROR_ILLEGAL)
        ee = self.expr
        args_all = [i.value() for i in ee[2:-1] if not isinstance(i, Op_Comma)]
        args_tt = [{'v':i, 's': str(i.value), 'n': str(i), 'a': str(i.alias),'i':ind} for ind,i in enumerate(args_all) if not isinstance(i, int)]
        return {'all': args_all, 'tt': args_tt}
    
    def get_alias(self) -> dict:
        aterms = dict()
        for i in self.__split:
            if isinstance(i, Op_Alias) or (type(i) in EXPR_AT_OPS) and not str(i) in aterms:
                aterms[str(i)] = i
        return aterms

    @staticmethod
    def create_notEnc_expr(code_name:str):
        expr = SASS_Expr('', {}, {}, {}, {}, {})
        if not code_name.startswith('!'): raise Exception("NotEnc must start with a '!'")
        expr.__split.append(Op_NotEnc(code_name[1:]))
        expr.__print_outer_braces.append(True)
        return expr
    
    def matches(self, pattern:typ.List[typ.List[Op_Base]]):
        if not len(pattern) == len(self.__split): return False
        for p,e in zip(pattern, self.__split): 
            if not len(p) == len(e): return False # type: ignore
            if not all([isinstance(ee, pp) for ee,pp in zip(e,p)]): return False # type: ignore
        return True

    def backwars_replace(self, alias_args:typ.List[typ.Dict], instr:TT_Instruction, instr_candidates:typ.List[TT_Instruction]):
        raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if len(self.__split) == 0: return
        # match up
        op_ii = Op_Iter(self.__split[0][0]) # type: ignore
        counter = 0
        while True:
            if counter > 1000: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            tt = op_ii.next()
            if not tt: break
            if isinstance(tt, Op_Alias):
                if not len(alias_args) == 1:
                    raise Exception("Unexpected behaviour exception")
                if not 'alias' in alias_args[0].keys():
                    raise Exception("Unexpected behaviour exception")
                if not tt.name == alias_args[0]['alias']: # type: ignore
                    raise Exception("Unexpected behaviour exception")
                tt(alias_args[0], instr, op_ii, instr_candidates) # type: ignore
            elif type(tt) in EXPR_AT_OPS_DIR.values():
                if not len(alias_args) == 1:
                    raise Exception("Unexpected behaviour exception")
                if not 'alias' in alias_args[0].keys():
                    raise Exception("Unexpected behaviour exception")
                if not tt.name == alias_args[0]['alias']: # type: ignore
                    raise Exception("Unexpected behaviour exception")
                tt(alias_args[0], instr, op_ii, instr_candidates) # type: ignore
            elif isinstance(tt, Op_Table):
                if not len(alias_args) == 1:
                    raise Exception("Unexpected behaviour exception")
                if not 'alias_n' in alias_args[0].keys():
                    raise Exception("Unexpected behaviour exception")
                if not tt.name in self.TABLES.keys(): # type: ignore
                    raise Exception("Unexpected behaviour exception")
                tt(alias_args[0], instr, op_ii, instr_candidates) # type: ignore
            else:
                tt(alias_args, instr, op_ii, instr_candidates) # type: ignore
            counter += 1

    def finalize(self, eval_alias:dict, eval_sets:dict = {}):
        split = []
        evaled = set()
        s_itt = iter(self.__split)
        # for i in self.__split:
        while True:
            i = next(s_itt, False)
            if i==False: break

            if isinstance(i, Op_LCBrace):
                split.append(SASS_Expr_Eval.isolate_set(s_itt))
            elif isinstance(i, Op_Value):
                i_value = i.value()
                if i_value.find('@') >= 0:
                    ii = i_value.split('@')
                    if ii[1] in EXPR_AT_OPS_DIR.keys() and ii[0] in eval_alias.keys():
                        split.append(EXPR_AT_OPS_DIR[ii[1]](ii[0], eval_alias[i_value]))
                        evaled.add(i_value)
                    else: raise Exception("Op_Value not found in alias list")    
                elif i_value in EXPR_SPECIALS_DICT:
                    split.append(EXPR_SPECIALS_DICT[i_value]())
                    evaled.add(i_value)
                elif i_value in _sass_func.CONVERT_FUNC.keys():
                    split.append(Op_TypeCast(_sass_func.CONVERT_FUNC[i_value]()))
                    evaled.add(i_value)
                elif i_value == 'Opcode':
                    split.append(Op_Opcode(i_value, eval_alias[i_value]))
                    evaled.add(i_value)
                elif i_value in eval_alias.keys():
                    split.append(Op_Alias(i_value, eval_alias[i_value]))
                    evaled.add(i_value)
                elif i_value in eval_sets:
                    # replace Op_Value that represents a set with the real set including sub operations, if need be
                    split.extend([Op_LBrace()] + eval_sets[i.value()].expr + [Op_RBrace()])
                else: raise Exception("Op_Value not found in alias list")
            else: split.append(i)

        for i in split:
            if isinstance(i, Op_Value): raise Exception("Expression finalization error: no terms should be Op_Value at this point")
            elif isinstance(i, Op_Alias) and isinstance(i.value(), TT_Func): 
                self.__has_func = True
                if i.value().arg_default.bit_len > 5: self.__has_large_func = True # type: ignore
            elif isinstance(i, Op_Alias) and isinstance(i.value(), TT_Reg): self.__has_reg = True

        if len(split) >= 2 and isinstance(split[1], Op_convertFloatType):
            self.__convert_float_alias = str(split[0])
            split = list(itt.chain.from_iterable([[i, Op_LBrace(), copy.copy(split[0]), Op_RBrace()] if isinstance(i, Op_TypeCast) else [i] for i in split[1:]]))

        self.__split = split
        self.__evaled = evaled

        self.__embedded = SASS_Expr_Eval.to_embedded_list(self.__split)
        self.__embedded_str = SASS_Expr_Eval.embedded_list_to_str(self.__embedded)
        self.__pre, self.__pre_str = SASS_Expr_Eval.SYAlgo(self.__embedded)
        if self.startswith_defined(): self.__pattern = tuple([type(self.__split[0]).__name__])
        elif self.startswith_not_defined(): self.__pattern = tuple([type(self.__split[0]).__name__, type(self.__split[1]).__name__])
        else: self.__pattern = tuple(type(i).__name__ for i in self.__split)

        self.__old_pattern = self.__pattern
        alias_enum = {i:"_"+str(ind) for ind,i in enumerate(self.get_sequenced_alias_names())}
        if (not (self.__pattern == (Op_Defined.__name__,) or self.__pattern == (Op_Not.__name__, Op_Defined.__name__))):
            self.__pattern = tuple(type(i).__name__ if not isinstance(i, Op_Alias) else type(i).__name__ + alias_enum[str(i.value().alias) if str(i.value().alias) in alias_enum else str(i.value().value)] for i in self.__split) # type: ignore

        self.__hash = self.__pattern.__hash__()

        return self, evaled

    def assemble(self, enc_vals:typ.Dict, enc_ind:typ.List[typ.Tuple], target_bits:BitVector, sm_nr:int) -> BitVector:
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_ind, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(e,tuple) for e in enc_ind): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(target_bits, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sm_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if len(self.__split) == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        if self.startswith_opcode():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            bits:SASS_Bits = self(enc_vals)  # type: ignore
            target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
        elif self.startswith_notEnc():
            pass # noting to encode
        elif self.startswith_alias():
            alias = self.get_alias_names()
            if len(alias) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # There is for example on SM86 instruction class hadd2_F32i_ that contains the following encoding line:
            #   BITS_0_Sb=Sb;
            # => skip such constructs. SASS_Bits will throw an exception just to make sure.
            if len(enc_ind[0]) != 0:
                bits:SASS_Bits = self(enc_vals) # type: ignore
                target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
        elif self.startswith_atOp():
            op = self.get_alias_names()
            if len(op) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if len(enc_ind[0]) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            bits:SASS_Bits = self(enc_vals) # type: ignore
            target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
        elif self.startswith_table():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            bits:SASS_Bits = self(enc_vals) # type: ignore
            target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
        elif self.startswith_int():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            bits:SASS_Bits = self(enc_vals) # type: ignore
            target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
        elif self.startswith_register():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            bits:SASS_Bits = self(enc_vals) # type: ignore
            target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
        elif self.startswith_constant():
            raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        elif self.startswith_convertFloat():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # here, we check:
            #  1. if the bits fit into the destination enc_inds, then do it
            #  2. if there are more bits than enc_inds, take the leading bits of the convertFloat result
            # => address the weird thing where an F64Imm goes into a 32 bit location after a convertFloat
            #    that then takes the upper 32 bits.
            # NOTE: this requires a test case. It may also be that we just read back-to-front and just stop if we
            # run out of space. In fact, this is much more likely than the other one.
            bits:SASS_Bits = self(enc_vals) # type: ignore
            if self.get_convertFloat_is_mufu():
                if bits.bit_len == 32:
                    target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
                else:
                    # or lower or whatever
                    upper32 = SASS_Bits(bits.bits[:32], bits.bit_len, bits.signed)
                    target_bits = upper32.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
            else:
                target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
        elif self.startswith_ConstBankAddressX():
            if len(enc_ind) != 2: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            constBank:SASS_Bits
            immConstOffset:SASS_Bits
            constBank, immConstOffset = self(enc_vals) # type: ignore
            target_bits = constBank.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
            target_bits = immConstOffset.assemble(target_bits, enc_ind[1], sm_nr) # type: ignore
        elif self.startswith_identical():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            bits:SASS_Bits = self(enc_vals) # type: ignore
            target_bits = bits.assemble(target_bits, enc_ind[0], sm_nr) # type: ignore
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        return target_bits

    def inv(self, details:SM_Cu_Details, instr_bits:BitVector, enc_ind:typ.List[typ.Tuple], enc_vals:typ.Dict, code_name:str) -> SASS_Expr_Dec|typ.List[SASS_Expr_Dec]:
        if not isinstance(details, SM_Cu_Details): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_bits, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_ind, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(e,tuple) for e in enc_ind): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(code_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if len(self.__split) == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        if self.startswith_opcode():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            return SASS_Expr_Dec.opcode_from_enc(instr_bits, enc_ind[0], code_name)
        elif self.startswith_notEnc():
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif self.is_scale():
            # NOTE: this one has to appear BEFORE startswith_alias() because it also startswith_alias() but requires
            # more work...
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            si = [ind for ind,i in enumerate(self.expr) if isinstance(i,Op_Scale)]
            if si != []: mult_val = self.expr[si[0]+1].value()
            else: mult_val = 0

            if isinstance(self.expr[0].value(), TT_Func):
                ff:TT_Func = self.expr[0].value()
                sb = ff.sass_from_bits(BitVector([instr_bits[i] for i in enc_ind[0]]))
                if mult_val > 0: sb = sb.multiply(mult_val)
                return SASS_Expr_Dec.func_from_sb(ff, sb, enc_ind[0], code_name)
            elif isinstance(self.expr[0].value(), TT_Reg): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif self.startswith_alias():
            alias = self.get_alias_names()
            if len(alias) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # There is for example on SM86 instruction class hadd2_F32i_ that contains the following encoding line:
            #   BITS_0_Sb=Sb;
            # => skip such constructs. SASS_Bits will throw an exception just to make sure.
            if isinstance(self.expr[0].value(), TT_Func):
                if len(enc_ind[0]) == 0:
                    ff:TT_Func = self.expr[0].value()
                    sb = ff.sass_from_bits(BitVector([0]))
                    return SASS_Expr_Dec.func_from_sb(self.expr[0].value(), sb, enc_ind[0], code_name)
                else:
                    return SASS_Expr_Dec.func_from_enc(self.expr[0].value(), instr_bits, enc_ind[0], code_name)
            elif isinstance(self.expr[0].value(), TT_Reg):
                if len(enc_ind[0]) == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                return SASS_Expr_Dec.reg_from_enc(self.expr[0].value(), instr_bits, enc_ind[0], code_name)
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif self.startswith_atOp():
            op = self.get_alias_names()
            if len(op) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if len(enc_ind[0]) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            return SASS_Expr_Dec.op_from_enc(self.expr[0].value(), instr_bits, enc_ind[0], code_name)
        elif self.startswith_table():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            val = SASS_Expr_Dec.get_bdh(instr_bits, enc_ind[0])
            inv_table = details.TABLES_INV_DICT[str(self.get_first_op())]
            # Get table values with bit precision
            # For example, there is one entry in table 'VarLatOperandEnc' ==
            #    {0: [(0,)], 1: [(1,)], 2: [(2,)], 3: [(3,)], 4: [(4,)], 5: [(5,)], 6: [(6,)], 7: [(7,), (65535,)]}
            # where the invers entry for 7 maps to 7 and 65535. With 3 encoding bits, 7 and 65535 are the same, though (0b111)
            # => make such entries be the same in the result => use sets and stuff
            t_val_variant = {tuple(bin(j)[2:][-len(enc_ind[0]):] for j in i) for i in inv_table[val['d']]}
            # Map values back to params of table call
            t_args = [(i['i'], i['a'], i['v']) for i in self.get_table_args()['tt']]
            res = []
            # if len(t_val_variant) > 1:
            #     pass
            for t_vals in t_val_variant:
                sub_res = []
                for arg in t_args:
                    val_b = t_vals[arg[0]]
                    if isinstance(arg[2], TT_Func):
                        sub_res.append(SASS_Expr_Dec.func_from_val(arg[2], val_b, enc_ind[0], code_name))
                    elif isinstance(arg[2], TT_Reg):
                        sub_res.append(SASS_Expr_Dec.reg_from_val(arg[2], val_b, enc_ind[0], code_name))
                    elif any(isinstance(arg[2], t) for t in AT_OP.values()):
                        sub_res.append(SASS_Expr_Dec.op_from_val(arg[2], val_b, enc_ind[0], code_name))
                    else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                res.append(sub_res)
            return res
        elif self.startswith_int():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            return SASS_Expr_Dec.const_int_from_enc(self.expr[0].value(), instr_bits, enc_ind[0], code_name)
        elif self.startswith_register():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            return SASS_Expr_Dec.const_reg_from_enc(self.expr[0], instr_bits, enc_ind[0], code_name) # type: ignore
        elif self.startswith_constant():
            raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        elif self.startswith_convertFloat():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # here, we check:
            #  1. if the bits fit into the destination enc_inds, then do it
            #  2. if there are more bits than enc_inds, take the leading bits of the convertFloat result
            # => address the weird thing where an F64Imm goes into a 32 bit location after a convertFloat
            #    that then takes the upper 32 bits.
            # NOTE: this requires a test case. It may also be that we just read back-to-front and just stop if we
            # run out of space. In fact, this is much more likely than the other one.

            bits = [instr_bits[i] for i in enc_ind[0]]
            arg = self.expr[-3]
            if not isinstance(arg.value(), TT_Func): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if self.get_convertFloat_is_mufu():
                # NOTE: this is the inverse of whatever is done in the SASS_Expr.assemble() for convertFloat.
                # It may be the opposite of what is being required, depending on what Nvidia means by msb and lsb
                # In this case, the assemble method removes the tail end of the vector => add it back here
                bb = BitVector(bits + 32*[0])
            else:
                # NOTE: if ever, we use real values, we have to really convert stuff here, not just fake it
                # But anyways, if we don't have a mufu, it's all 16 bit values anyways, so don't bother
                bb = BitVector(bits)
            ff:TT_Func = arg.value()
            # This one also checks bit length and stuff, expanding it if necessary. However, it is NOT a real cast!
            sb = ff.sass_from_bits(BitVector(bb))
            return SASS_Expr_Dec.func_from_sb(ff, sb, enc_ind[0], code_name)
        elif self.startswith_ConstBankAddressX():
            if len(enc_ind) != 2: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            arg1 = self.expr[2]
            arg2 = self.expr[4]
            if not isinstance(arg1.value(), TT_Func): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if not isinstance(arg2.value(), TT_Func): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            ff1:TT_Func = arg1.value()
            ff2:TT_Func = arg2.value()

            sb1 = ff1.sass_from_bits(BitVector([instr_bits[i] for i in enc_ind[0]]))            
            sb2 = ff2.sass_from_bits(BitVector([instr_bits[i] for i in enc_ind[1]]))

            # ConstBankAddress2 needs to reverse .scale(4) for arg2
            # ConstBankAddress0 and 2 need to reverse .to_unsigned() for arg2
            if isinstance(self.expr[0], Op_ConstBankAddress2): sb2 = sb2.multiply(4)
            sb2 = sb2.as_signed()
            sb1_val = int(sb1)
            sb2_val = int(sb2)
            return [SASS_Expr_Dec(
                type_=SASS_Expr_Dec.TYPE__ALIAS,
                attr={SASS_Expr_Dec.ATTR__ALIAS: arg1.value().alias},
                sb=sb1, d=sb1_val, h=hex(sb1_val), b=bin(sb1_val), enc_ind=enc_ind[0], code_name=code_name
            ), SASS_Expr_Dec(
                type_=SASS_Expr_Dec.TYPE__ALIAS,
                attr={SASS_Expr_Dec.ATTR__ALIAS: arg2.value().alias},
                sb=sb2, d=sb2_val, h=hex(sb2_val), b=bin(sb2_val), enc_ind=enc_ind[1], code_name=code_name
            )]
        elif self.startswith_identical():
            if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            arg1 = self.expr[2]
            arg2 = self.expr[4]

            if not isinstance(arg1.value(), TT_Reg): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if not isinstance(arg2.value(), TT_Reg): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            reg1:TT_Reg = arg1.value()
            reg2:TT_Reg = arg2.value()
            bits = reg1.sass_from_bits(BitVector([instr_bits[i] for i in enc_ind[0]]))            
            val_d = int(bits)
            val_h = hex(val_d)
            val_b = bin(val_d)
            return [SASS_Expr_Dec(
                type_=SASS_Expr_Dec.TYPE__ALIAS,
                attr={SASS_Expr_Dec.ATTR__ALIAS: reg1.alias.value, SASS_Expr_Dec.ATTR__PARENT_REGISTER:reg1.value, SASS_Expr_Dec.ATTR__REGISTER:SASS_Expr_Dec.val_to_reg(val_d, reg1)}, # type: ignore
                sb=bits, d=val_d, h=val_h, b=val_b, enc_ind=enc_ind[0], code_name=code_name
            ), SASS_Expr_Dec(
                type_=SASS_Expr_Dec.TYPE__ALIAS,
                attr={SASS_Expr_Dec.ATTR__ALIAS: reg2.alias.value, SASS_Expr_Dec.ATTR__PARENT_REGISTER:reg2.value, SASS_Expr_Dec.ATTR__REGISTER:SASS_Expr_Dec.val_to_reg(val_d, reg2)}, # type: ignore
                sb=bits, d=val_d, h=val_h, b=val_b, enc_ind=enc_ind[0], code_name=code_name
            )]
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
