"""
All kinds of expressions that yield some sort of result
"""

from __future__ import annotations
import termcolor
from . import _config as sp
from ._tt_terms import TT_Reg, TT_Func
from ._sass_expression_ops import *
# from ._sass_expression_domain_range import SASS_Expr_Domain_Range
from py_sass_ext import SASS_Bits
from py_sass_ext import BitVector

class SASS_Expr_Dec:
    TYPE__OPCODE = 'opcode'
    TYPE__CONST = 'const'
    TYPE__ALIAS = 'alias'

    ATTR__ALIAS = 'alias'
    ATTR__PARENT_REGISTER = 'parent_register'
    ATTR__REGISTER = 'register'
    ATTR__OP = 'op'

    CONST_TYPE__REGISTER = 0
    CONST_TYPE__INT = 1
    CONST_TYPE__CONSTANT = 2

    def __init__(self, type_:str, attr:dict, sb:SASS_Bits, d:int, h:str, b:str, enc_ind:tuple, code_name:str):
        if not isinstance(type_,str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(attr,dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sb,SASS_Bits): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(d,int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(h,str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(b,str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_ind,tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(code_name,str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        # if type_ == SASS_Expr_Dec.TYPE__ALIAS and not SASS_Expr_Dec.ATTR__ALIAS in attr: raise Exception(sp.CONST__ERROR_ILLEGAL)
        # if SASS_Expr_Dec.ATTR__REGISTER in attr and not len(attr[SASS_Expr_Dec.ATTR__REGISTER])==len(sb): raise Exception(sp.CONST__ERROR_ILLEGAL)
        # if SASS_Expr_Dec.ATTR__OP in attr and not len(attr[SASS_Expr_Dec.ATTR__OP])==len(sb): raise Exception(sp.CONST__ERROR_ILLEGAL)
        # if SASS_Expr_Dec.ATTR__REGISTER in attr and SASS_Expr_Dec.ATTR__OP in attr: raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        self.__type = type_
        self.__attr = attr
        self.__sb = sb
        self.__d = d
        self.__h = h
        self.__b = b
        self.__code_name = code_name
        self.__enc_ind = enc_ind
    
    @property
    def type_(self): return self.__type
    @property
    def attr(self): return self.__attr
    @property
    def sb(self): return self.__sb
    @property
    def d(self): return self.__d
    @property
    def h(self): return self.__h
    @property
    def b(self): return self.__b
    @property
    def code_name(self): return self.__code_name
    @property
    def enc_ind(self): return self.__enc_ind
    @property
    def bit_len(self): return self.__sb.bit_len
    @property
    def signed(self): return self.__sb.signed

    def has_parent_register(self):
        return SASS_Expr_Dec.ATTR__PARENT_REGISTER in self.__attr
    def parent_register(self):
        return self.__attr[SASS_Expr_Dec.ATTR__PARENT_REGISTER]
    def has_register(self):
        return SASS_Expr_Dec.ATTR__REGISTER in self.__attr
    def register(self):
        return self.__attr[SASS_Expr_Dec.ATTR__REGISTER]
    def is_alias(self):
        return self.__type == SASS_Expr_Dec.TYPE__ALIAS
    def alias(self):
        return self.__attr[SASS_Expr_Dec.ATTR__ALIAS]
    def is_const(self):
        return self.__type == SASS_Expr_Dec.TYPE__CONST
    def is_opcode(self):
        return self.__type == SASS_Expr_Dec.TYPE__OPCODE

    @staticmethod
    def val_to_reg(val_d:int, rr:TT_Reg):
        """Calculate the register names, for example:
        * 1 => R1, if it's a 'Register'
        * 1 => UR1, if it's a 'UniformRegister'
        * 1 => SP1, if it's a 'SpecialRegister'
        * etc...

        :param val_d: decimal value of the register
        :type val_d: int
        :param rr: TT_Reg generalized representation of the register.
        :type rr: TT_Reg
        :return: a set with all candidate names for this register
        :rtype: set
        """
        return [{str(ii[0]) for ii in reg.items() if val_d in ii[1] if not (isinstance(ii[0], str) and len(ii[0]) ==3 and ii[0].startswith('R0'))} for reg in rr.options.values()][0]

    @staticmethod
    def clean_reg_val(reg:set):
        """Take a set with all candidate names for a specific register, as calculated by SASS_Expr_Dec.val_to_reg and regurn
        a set with the best candidate name.

        * remove starting underscored, for example {'_64', '64'} => {'64'}
        * unify boolean names, for example {T, TRUE} => {'TRUE'}
        * select a good one for other kinds of synonyms, like {'P7', 'PT'} => {'PT'}

        :param reg: a set with all candidates. NOTE: candidates must be synonyms
        :type reg: set
        :return: the best name for the register
        :rtype: str
        """
        if len(reg) > 1:
            if any(r.startswith('INVALID') for r in reg):
                reg = {r for r in reg if not r.startswith('INVALID')}
        if len(reg) == 2 and ('PT' in reg and 'P7' in reg): return {'PT'}
        # if len(reg) == 2 and any(r.startswith('_') for r in reg): reg = {r for r in reg if not r.startswith('_')}
        if len(reg) >= 2 and any(r.startswith('_') for r in reg): 
            nr = {r[1:] if r.startswith('_') else r for r in reg}
            if len(nr) < len(reg): reg = nr
        if len(reg) == 2 and ('TRUE' in reg and 'T' in reg): return {'TRUE'}
        if len(reg) == 2 and ('FALSE' in reg and 'F' in reg): return {'FALSE'}
        if len(reg) > 1:
            pass
        return reg

    @staticmethod
    def reg_from_enc(rr:TT_Reg, instr_bits:BitVector, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        val = SASS_Expr_Dec.get_bdh(instr_bits, enc_ind)
        val_d = val['d']
        reg = SASS_Expr_Dec.val_to_reg(val_d, rr)
        if len(reg) > 1: reg = SASS_Expr_Dec.clean_reg_val(reg)
        attr = {SASS_Expr_Dec.ATTR__ALIAS:str(rr.alias), SASS_Expr_Dec.ATTR__PARENT_REGISTER:rr.value, SASS_Expr_Dec.ATTR__REGISTER:reg}
        sb = rr.sass_from_bits(BitVector([instr_bits[i] for i in enc_ind]))
        return SASS_Expr_Dec(
            type_=SASS_Expr_Dec.TYPE__ALIAS, 
            attr=attr,sb=sb, d=val_d, h=hex(val_d), b=bin(val_d), enc_ind=enc_ind, code_name=code_name)
    
    @staticmethod
    def reg_from_val(rr:TT_Reg, val_b:str, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        val_d = int(val_b,2)
        reg = SASS_Expr_Dec.val_to_reg(val_d, rr)
        if len(reg) > 1: reg = SASS_Expr_Dec.clean_reg_val(reg)
        bits = BitVector([int(i) for i in val_b])
        sb = rr.sass_from_bits(bits)
        attr = {SASS_Expr_Dec.ATTR__ALIAS:str(rr.alias), SASS_Expr_Dec.ATTR__PARENT_REGISTER:rr.value, SASS_Expr_Dec.ATTR__REGISTER:reg}
        return SASS_Expr_Dec(
            type_=SASS_Expr_Dec.TYPE__ALIAS, 
            attr=attr, sb=sb, d=val_d, h=hex(val_d), b=bin(val_d), enc_ind=enc_ind, code_name=code_name)
    
    @staticmethod
    def const_reg_from_enc(rr:Op_Register, instr_bits:BitVector, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        val = SASS_Expr_Dec.get_bdh(instr_bits, enc_ind)
        if val['d'] != rr.value(): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        sb = SASS_Bits.from_int(val['d'], bit_len=len(enc_ind), signed=0)
        attr = {SASS_Expr_Dec.ATTR__PARENT_REGISTER:rr.parent_register(), SASS_Expr_Dec.ATTR__REGISTER:rr.register()}
        return SASS_Expr_Dec(
            type_=SASS_Expr_Dec.TYPE__CONST, 
            attr=attr, sb=sb, d=val['d'], h=val['h'], b='0b'+val['b'], enc_ind=enc_ind, code_name=code_name)
    
    @staticmethod
    def const_int_from_enc(value:int, instr_bits:BitVector, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        val = SASS_Expr_Dec.get_bdh(instr_bits, enc_ind)
        # NOTE: this one also covers stuff like RD and WR bits. If they are not configured in the FORMAT
        # portion of the instruction class, we get an expression like
        #   BITS_3_115_113_src_rel_sb =* 7
        # If we decode such an instruction with adapted WR/RD barriers, we still parse that expression
        # with 7. Thus, we shouldn't compare the parsed value val['d'] to value (the actual hard-coded value in 
        # the epxression), which corresponds to the right side
        # of the expression above.
        # if value != val['d']: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if value != val['d']:
            # print a warning, though
            print("{0}: code_name {1} was parsed from bits with value [{2}] but is fixed to [{3}] in the ENCODING expression. If this isn't on purpose, it's probably a bug!"
                  .format(termcolor.colored("[WARNING]", 'red', attrs=['bold']), code_name, val['d'], int(value)))
        return SASS_Expr_Dec(
            type_=SASS_Expr_Dec.TYPE__CONST, 
            attr={},
            sb=SASS_Bits.from_int(val['d'], bit_len=len(enc_ind), signed=0), 
            d=val['d'], h=val['h'], b='0b'+val['b'], enc_ind=enc_ind, code_name=code_name
        )

    @staticmethod
    def func_from_enc(ff:TT_Func, instr_bits:BitVector, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        sb = ff.sass_from_bits(BitVector([instr_bits[i] for i in enc_ind]))
        return SASS_Expr_Dec.func_from_sb(ff, sb, enc_ind, code_name)
    
    @staticmethod
    def func_from_val(ff:TT_Func, val_b:str, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        bits = BitVector([int(i) for i in val_b])
        sb = ff.sass_from_bits(bits)
        return SASS_Expr_Dec.func_from_sb(ff, sb, enc_ind, code_name)

    @staticmethod
    def func_from_sb(ff:TT_Func, sb:SASS_Bits, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        attr = {SASS_Expr_Dec.ATTR__ALIAS:str(ff.alias)}
        val_d = int(sb)
        return SASS_Expr_Dec(
            type_=SASS_Expr_Dec.TYPE__ALIAS, 
            attr=attr, sb=sb, d=val_d, h=hex(val_d), b=bin(val_d), enc_ind=enc_ind, code_name=code_name)

    @staticmethod
    def op_from_enc(op, instr_bits:BitVector, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        if len(enc_ind) != 1: raise Exception(sp.CONST__ERROR_ILLEGAL)
        val = SASS_Expr_Dec.get_bdh(instr_bits, enc_ind)
        if val['d'] not in (0,1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if val['d'] == 1: op_str = str(op)
        else: op_str = ''
        return SASS_Expr_Dec(
            type_=SASS_Expr_Dec.TYPE__ALIAS, 
            attr={SASS_Expr_Dec.ATTR__ALIAS: op.alias, SASS_Expr_Dec.ATTR__OP:op_str},
            sb=SASS_Bits.from_int(val['d'], bit_len=1, signed=0), 
            d=val['d'], h=val['h'], b='0b'+val['b'], enc_ind=enc_ind, code_name=code_name
        )

    @staticmethod
    def op_from_val(op, val_b:str, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        if len(val_b) != 1: raise Exception(sp.CONST__ERROR_ILLEGAL)
        val_d = int(val_b)
        if val_d not in (0,1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if val_d == 1: op_str = str(op)
        else: op_str = ''
        return SASS_Expr_Dec(
            type_=SASS_Expr_Dec.TYPE__ALIAS, 
            attr={SASS_Expr_Dec.ATTR__ALIAS: op.alias, SASS_Expr_Dec.ATTR__OP:op_str},
            sb=SASS_Bits.from_int(val_d, bit_len=1, signed=0), 
            d=val_d, h=hex(val_d), b=bin(val_d), enc_ind=enc_ind, code_name=code_name
        )
    
    @staticmethod
    def opcode_from_enc(instr_bits:BitVector, enc_ind:tuple, code_name:str) -> SASS_Expr_Dec:
        sb = SASS_Bits(BitVector([instr_bits[i] for i in enc_ind]), bit_len=len(enc_ind), signed=False)
        val_d = int(sb)
        return SASS_Expr_Dec(
            type_=SASS_Expr_Dec.TYPE__OPCODE, 
            attr={}, sb=sb, d=val_d, h=hex(val_d), b=bin(val_d), enc_ind=enc_ind, code_name=code_name)

    @staticmethod
    def get_bdh(instr_bits:BitVector, enc_ind:tuple) -> dict:
        val_b = "".join(str(instr_bits[i]) for i in enc_ind)
        val_d = int(val_b,2)
        val_h = hex(val_d)
        return {'d':val_d, 'b':val_b, 'h':val_h}
