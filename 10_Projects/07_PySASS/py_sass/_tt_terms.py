"""
All different components of an instruction.

Initially an instruction class is parsed into a construct of TT_Term. Afterwards
the 'finalize' method will translate it into something that is more intuitively accessible.

All components for this translation and the final representation of an instruction class
are more or less in this file.

It could use some cleaning-up ^^
"""

import typing
import itertools as itt
from . import _config as sp
from . import _sass_func as sf
from ._sass_util import SASS_Util as su
from .sm_cu_details import SM_Cu_Details
from py_sass_ext import SASS_Bits
from py_sass_ext import BitVector
from py_sass_ext import IntVector
from py_sass_ext import OptionsDict, CashComponentsVector, ExtVector, ParamVector, OpsVector, ListVector
from py_sass_ext import TT_Alias as cTT_Alias
from py_sass_ext import TT_Reg as cTT_Reg
from py_sass_ext import TT_Pred as cTT_Pred
from py_sass_ext import TT_AtOp as cTT_AtOp
from py_sass_ext import TT_AttrParam as cTT_AttrParam
from py_sass_ext import TT_Param as cTT_Param
from py_sass_ext import TT_Cash as cTT_Cash
from py_sass_ext import TT_Default as cTT_Default
from py_sass_ext import TT_Ext as cTT_Ext
from py_sass_ext import TT_Func as cTT_Func
from py_sass_ext import TT_FuncArg as cTT_FuncArg
from py_sass_ext import TT_ICode as cTT_ICode
from py_sass_ext import TT_List as cTT_List
from py_sass_ext import TT_Opcode as cTT_Opcode
from py_sass_ext import TT_OpAtAbs as cTT_OpAtAbs
from py_sass_ext import TT_OpAtSign as cTT_OpAtSign
from py_sass_ext import TT_OpAtNot as cTT_OpAtNot
from py_sass_ext import TT_OpAtInvert as cTT_OpAtInvert
from py_sass_ext import TT_OpAtNegate as cTT_OpAtNegate
from py_sass_ext import TT_OpCashQuestion as cTT_OpCashQuestion
from py_sass_ext import TT_OpCashAssign as cTT_OpCashAssign
from py_sass_ext import TT_OpCashAnd as cTT_OpCashAnd

class TT_OverrideError(Exception):
    def __init__(self, message): super().__init__(message)

class TT_ValueOptions:
    def __init__(self):
        self.__values = []
    def add_set(self, value_set:set):
        if not isinstance(value_set, set): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__values.append(value_set)

class TT_Base: pass

class TTs_Utils:
    @staticmethod
    def call_checksBinaryAtOp(args:typing.Dict, format_eval:typing.Dict, e_ptr) -> SASS_Bits:
        if not isinstance(args, dict): raise Exception("Error evaluating")
        if not ('arg' in args.keys() and isinstance(args['arg'], SASS_Bits)): raise Exception("Error evaluating")
        if not args['arg'].bit_len == 1: raise Exception("Error evaluating")
        if not int(args['arg']) in (0,1): raise Exception("Unsupported value")
        return args['arg']

class TT_Alias:
    def __init__(self, class_name:str, alias:str, is_at_alias:bool):
        self.value = alias
        self.class_name = class_name
        self.is_at_alias = is_at_alias

    def __str__(self): return self.value
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception("Illegal")
    def get_decode_value(self) -> None: raise Exception("Illegal")
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_Alias: return cTT_Alias(self.value, self.is_at_alias)

class TT_Op:
    """
    This one is an initializer for all the cash and at ops. Otherwise, it does nothing.
    """
    def __init__(self): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    @staticmethod
    def call(eval_value_:str, args:typing.Dict, format_eval:typing.Dict, e_ptr) -> SASS_Bits:
        if eval_value_: raise Exception("Override forbidden")
        return TTs_Utils.call_checksBinaryAtOp(args, format_eval, e_ptr)
    @staticmethod
    def as_str(op_sign:str): return op_sign
    @staticmethod
    def eval_str(op_sign, eval_value_) -> str: return op_sign if eval_value_ > 0 else ''
    @staticmethod
    def get_domain(): return {SASS_Bits.from_int(0, bit_len=1, signed=0), SASS_Bits.from_int(1, bit_len=1, signed=0)}
    @staticmethod
    def space_size(): return 2
    @staticmethod
    def contextual_decode(encode_input:SASS_Bits) -> typing.Tuple[bool, SASS_Bits|None]:
        if not (int(encode_input) in [0,1]): return False, None
        return True, encode_input
    @staticmethod
    def tt(): return 'op'
class TT_OpAtNot(TT_Base):
    """
    This one represents [!]

    AtOps are the things in front of operands, like the [-] before [-]Register:Ra.
    The eval_value for this one is {1,0} where 1==operation_is_there, 0==no_operation
    """
    def __init__(self, class_name:str):
        self.class_name = class_name
        self.__decode_value = None
        self.__op_name = '@not'
        self.__op_sign = '!'
        self.__min_bit_len = 1
        self.__reg_alias = None
    @property
    def value(self): return 'AtOp'
    @property
    def alias(self):
        if self.__reg_alias is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return TT_Alias(self.class_name, self.__reg_alias + self.__op_name, False)
    def set_alias(self, reg_alias:str): self.__reg_alias = reg_alias
    def min_bit_len(self): return self.__min_bit_len
    def __str__(self): return TT_Op.as_str(self.__op_sign)
    def op_name(self): return self.__op_name
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__decode_value = decode_value
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def contextual_decode(self, encode_input:SASS_Bits) -> typing.Tuple[bool, SASS_Bits|None]: return TT_Op.contextual_decode(encode_input)
    def eval_str(self) -> str: return TT_Op.eval_str(self.__op_sign, self.__decode_value)
    def has_func(self): return False
    def space_size(self): return TT_Op.space_size()
    def get_domain(self, to_limit:dict): return TT_Op.get_domain()
    def to_cpp(self) -> cTT_OpAtNot: return cTT_OpAtNot(self.__reg_alias if self.__reg_alias is not None else "")
class TT_OpAtNegate(TT_Base):
    """
    This one represents [-]
    
    AtOps are the things in front of operands, like the [-] before [-]Register:Ra.
    The eval_value for this one is {1,0} where 1==operation_is_there, 0==no_operation
    """
    def __init__(self, class_name:str):
        self.class_name = class_name
        self.__decode_value = None
        self.__op_name = '@negate'
        self.__op_sign = '-'
        self.__min_bit_len = 1
        self.__reg_alias = None
    @property
    def value(self): return 'AtOp'
    @property
    def alias(self):
        if self.__reg_alias is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return TT_Alias(self.class_name, self.__reg_alias + self.__op_name, False)
    def set_alias(self, reg_alias:str): self.__reg_alias = reg_alias
    def min_bit_len(self): return self.__min_bit_len
    # def __call__(self, args:typing.Dict, format_eval:typing.Dict, e_ptr) -> SASS_Bits:
    #     return TT_Op.call(self.__decode_value, args, format_eval, e_ptr)
    def __str__(self): return TT_Op.as_str(self.__op_sign)
    def op_name(self): return self.__op_name
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__decode_value = decode_value
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def contextual_decode(self, encode_input:SASS_Bits) -> typing.Tuple[bool, SASS_Bits|None]: return TT_Op.contextual_decode(encode_input)
    def eval_str(self) -> str: return TT_Op.eval_str(self.__op_sign, self.__decode_value)
    def has_func(self): return False
    def space_size(self): return TT_Op.space_size()
    def get_domain(self, to_limit:dict): return TT_Op.get_domain()
    def to_cpp(self) -> cTT_OpAtNegate: return cTT_OpAtNegate(self.__reg_alias if self.__reg_alias is not None else "")
class TT_OpAtAbs(TT_Base):
    """
    This one represents [!!]
    
    AtOps are the things in front of operands, like the [-] before [-]Register:Ra.
    The eval_value for this one is {1,0} where 1==operation_is_there, 0==no_operation
    """
    def __init__(self, class_name:str):
        self.class_name = class_name
        self.__decode_value = None
        self.__op_name = '@absolute'
        self.__op_sign = '||'
        self.__min_bit_len = 1
        self.__reg_alias = None
    @property
    def value(self): return 'AtOp'
    @property
    def alias(self):
        if self.__reg_alias is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return TT_Alias(self.class_name, self.__reg_alias + self.__op_name, False)
    def set_alias(self, reg_alias:str): self.__reg_alias = reg_alias
    def min_bit_len(self): return self.__min_bit_len
    # def __call__(self, args:typing.Dict, format_eval:typing.Dict, e_ptr) -> SASS_Bits:
    #     return TT_Op.call(self.__decode_value, args, format_eval, e_ptr)
    def __str__(self): return TT_Op.as_str(self.__op_sign)
    def op_name(self): return self.__op_name
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__decode_value = decode_value
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def contextual_decode(self, encode_input:SASS_Bits) -> typing.Tuple[bool, SASS_Bits|None]: return TT_Op.contextual_decode(encode_input)
    def eval_str(self) -> str: return TT_Op.eval_str(self.__op_sign, self.__decode_value)
    def has_func(self): return False
    def space_size(self): return TT_Op.space_size()
    def get_domain(self, to_limit:dict): return TT_Op.get_domain()
    def to_cpp(self) -> cTT_OpAtAbs: return cTT_OpAtAbs(self.__reg_alias if self.__reg_alias is not None else "")
class TT_OpAtSign(TT_Base):
    """
    This one represents [&&] (somehow I can't find it anymore XD)

    @sign exists for uImm, sImm, etc.
    
    AtOps are the things in front of operands, like the [-] before [-]Register:Ra.
    The eval_value for this one is {1,0} where 1==operation_is_there, 0==no_operation
    """
    def __init__(self, class_name:str):
        self.class_name = class_name
        self.__decode_value = None
        self.__op_name = '@sign'
        self.__op_sign = '&&'
        self.__func:sf.RSImm|sf.UImm|sf.F16Imm|sf.SImm|sf.SSImm|sf.F64Imm|sf.F32Imm|sf.BITSET|sf.E8M7Imm|sf.E6M9Imm|None
        self.__func = None
        self.__min_bit_len = 1
        self.__reg_alias = None
    @property
    def value(self): return 'AtOp'
    @property
    def alias(self):
        if self.__reg_alias is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return TT_Alias(self.class_name, self.__reg_alias + self.__op_name, False)
    def set_alias(self, reg_alias:str): self.__reg_alias = reg_alias
    def min_bit_len(self): return self.__min_bit_len
    # def __call__(self, args:typing.Dict, format_eval:typing.Dict, e_ptr) -> SASS_Bits:
    #     return TT_Op.call(self.__decode_value, args, format_eval, e_ptr)
    def __str__(self): return TT_Op.as_str(self.__op_sign)
    def op_name(self): return self.__op_name
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__decode_value = decode_value
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def contextual_decode(self, encode_input:SASS_Bits) -> typing.Tuple[bool, SASS_Bits|None]: return TT_Op.contextual_decode(encode_input)
    def eval_str(self) -> str: return TT_Op.eval_str(self.__op_sign, self.__decode_value)
    def has_func(self): return self.__func is not None
    def add_func(self, func:sf.RSImm|sf.UImm|sf.F16Imm|sf.SImm|sf.SSImm|sf.F64Imm|sf.F32Imm|sf.BITSET|sf.E8M7Imm|sf.E6M9Imm):
        # generate the func types: "|".join(["sf." + i.__name__ for i in _sass_func.FUNC.values()])
        self.__func = func
    def space_size(self): return TT_Op.space_size()
    def get_domain(self, to_limit:dict): return TT_Op.get_domain()
    def to_cpp(self) -> cTT_OpAtSign: return cTT_OpAtSign(self.__reg_alias if self.__reg_alias is not None else "")
class TT_OpAtInvert(TT_Base):
    """
    This one represents [~]
    
    AtOps are the things in front of operands, like the [-] before [-]Register:Ra.
    The eval_value for this one is {1,0} where 1==operation_is_there, 0==no_operation
    """
    def __init__(self, class_name:str):
        self.class_name = class_name
        self.__decode_value = None
        self.__op_name = '@invert'
        self.__op_sign = '~'
        self.__min_bit_len = 1
        self.__reg_alias = None
    @property
    def value(self): return 'AtOp'
    @property
    def alias(self):
        if self.__reg_alias is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return TT_Alias(self.class_name, self.__reg_alias + self.__op_name, False)
    def set_alias(self, reg_alias:str): self.__reg_alias = reg_alias
    def min_bit_len(self): return self.__min_bit_len
    # def __call__(self, args:typing.Dict, format_eval:typing.Dict, e_ptr) -> SASS_Bits:
    #     return TT_Op.call(self.__decode_value, args, format_eval, e_ptr)
    def __str__(self): return TT_Op.as_str(self.__op_sign)
    def op_name(self): return self.__op_name
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__decode_value = decode_value
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def contextual_decode(self, encode_input:SASS_Bits) -> typing.Tuple[bool, SASS_Bits|None]: return TT_Op.contextual_decode(encode_input)
    def eval_str(self) -> str: return TT_Op.eval_str(self.__op_sign, self.__decode_value)
    def has_func(self): return False
    def space_size(self): return TT_Op.space_size()
    def get_domain(self, to_limit:dict): return TT_Op.get_domain()
    def to_cpp(self) -> cTT_OpAtInvert: return cTT_OpAtInvert(self.__reg_alias if self.__reg_alias is not None else "")
class TT_OpCashQuestion:
    """
    This one represents '?'

    Cash ops are the ones in the scheduling assignments like in 
    $( { '&' RD:rd '=' UImm(3/0x7):src_rel_sb } )$.
    They don't hold a value. They are just there.
    """
    def __init__(self, class_name:str): self.class_name = class_name
    # def __call__(self, args:typing.Dict, format_eval:typing.Dict, e_ptr): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def __str__(self): return '?'
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def get_decode_value(self) -> None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_OpCashQuestion: return cTT_OpCashQuestion()
class TT_OpCashAnd:
    """
    This one represents '&'

    Cash ops are the ones in the scheduling assignments like in 
    $( { '&' RD:rd '=' UImm(3/0x7):src_rel_sb } )$.
    They don't hold a value. They are just there.
    """
    def __init__(self, class_name:str): self.class_name = class_name
    # def __call__(self, args:typing.Dict, format_eval:typing.Dict, e_ptr): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def __str__(self): return '&'
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception("Illegal")
    def get_decode_value(self) -> None: raise Exception("Illegal")
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_OpCashAnd: return cTT_OpCashAnd()
class TT_OpCashAssign:
    """
    This one represents '='

    Cash ops are the ones in the scheduling assignments like in 
    $( { '&' RD:rd '=' UImm(3/0x7):src_rel_sb } )$.
    They don't hold a value. They are just there.
    """
    def __init__(self, class_name:str): self.class_name = class_name
    # def __call__(self, args:typing.Dict, format_eval:typing.Dict, e_ptr): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def __str__(self): return '='
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def get_decode_value(self) -> None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_OpCashAssign: return cTT_OpCashAssign()
class TT_Default(TT_Base):
    def __init__(self, class_name:str, def_name, has_print, options):
        self.class_name = class_name
        self.options = options
        if not isinstance(def_name, int|str): raise Exception(sp.CONST__ERROR_NOT_TESTED)
        val = su.try_convert(def_name, convert_hex=True, convert_bin=True)
        if not isinstance(val, int|str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.value:str|int =  val
        self.has_print = has_print
        if not self.value in self.options:
            raise Exception("TT_Default for class {0} has a value {1} not contained in options {2}".format(class_name, self.value, options))
    def __str__(self):
        res = str(self.value)
        if self.has_print: res += '/PRINT'
        return res
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def get_decode_value(self) -> None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def space_size(self): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_Default: return cTT_Default(self.value, self.has_print, self.options)
    @staticmethod
    def tt(): return 'default'
class TT_FuncArg:
    def __init__(self, class_name, arg_val):
        self.class_name = class_name
        self.arg_val = arg_val
        self.has_star = False
        self.has_print = False
        self.bit_len = 0
        self.default_val:int = 0
        self.has_default = False
        self.has_max_val = False
        self.max_val = 0
        if isinstance(self.arg_val, str):
            # If we have a string, we always have something '/' divided, for example 5/0*
            # The star is optional.
            arg_val = self.arg_val
            if arg_val.endswith('*'):
                self.has_star = True
                arg_val = arg_val[:-1]
            if arg_val.endswith('/PRINT'):
                arg_val = arg_val[:-6]
                self.has_print = True
            bb,dd = arg_val.split('/')
            self.bit_len = int(bb)
            default_val = su.try_convert(dd, convert_bin=True, convert_hex=True)
            if not isinstance(default_val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
            self.default_val = default_val
            self.has_default = True
        else:
            self.bit_len = self.arg_val
    def __str__(self): return str(self.arg_val)
    def space_size(self):
        if self.has_max_val: return self.max_val
        else: return 2**self.bit_len
    def contextual_decode(self, encode_input:SASS_Bits) -> typing.Tuple[bool, SASS_Bits|None]:
        val = int(encode_input)
        if self.has_max_val and val > self.max_val: return False, None
        if encode_input.bit_len > self.bit_len: return False, None
        return True, SASS_Bits.from_int(val, bit_len=self.bit_len, signed=encode_input.signed)
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def get_decode_value(self) -> None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def set_max_val(self, max_val):
        self.max_val = max_val
        self.has_max_val = True
    def to_cpp(self) -> cTT_FuncArg: return cTT_FuncArg(self.arg_val, self.has_star, self.has_print, self.bit_len, self.has_default, self.default_val, self.has_max_val, self.max_val)
class TT_Reg(TT_Base):
    def __init__(self, class_name:str, reg_name:str, arg_default:TT_Default|None, options):
        if not isinstance(class_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(reg_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if arg_default and not isinstance(arg_default, TT_Default): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(options, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        self.class_name = class_name
        self.value = reg_name
        self.options = options
        self.alias:TT_Alias|None = None
        self.__decode_value = None
        self.arg_default = arg_default
        if not self.value in options:
            raise Exception("TT_Reg for class {0} has a value {1} not contained in options".format(class_name, self.value))
        
        mm_val = max(max(max(v for v in j) for j in opt.values()) for opt in options.values())
        if not isinstance(mm_val, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__min_bit_len = len(bin(mm_val)[2:])
    def min_bit_len(self): return self.__min_bit_len
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        if not isinstance(bits, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)
        bit_len = max(len(bits), self.__min_bit_len)
        return SASS_Bits(bits, bit_len=bit_len, signed=False)
    def __str__(self):
        res = self.value
        if self.alias is None: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if self.arg_default: res += "(" + str(self.arg_default) + ")"
        res += ("@" if self.alias.is_at_alias else "") + ((":" + str(self.alias)) if self.alias is not None else "")
        return res
    def get_domain(self, to_limit:dict, filter_invalid:bool=False):
        if self.value in to_limit.keys():
            if filter_invalid: 
                # Don't allow mixing to_limit and filter_invalid, too close to the deadline...
                raise Exception(sp.CONST__ERROR_ILLEGAL)
            vals = set(itt.chain.from_iterable([list(i) for i in self.options[self.value].values()]))
            if not all(isinstance(i,int) for i in vals): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            m_vals = max(vals)
            vals2 = to_limit[self.value](vals, m_vals)
            ret = set([SASS_Bits.from_int(i, bit_len=self.__min_bit_len, signed=0) for i in vals2])
        else:
            if filter_invalid:
                vals = set(itt.chain.from_iterable([list(i) for n,i in self.options[self.value].items() if isinstance(n, int) or not (n.lower().startswith('invalid'))]))
            else:
                vals = set(itt.chain.from_iterable([list(i) for i in self.options[self.value].values()]))
            if not all(isinstance(i,int) for i in vals): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            ret = set([SASS_Bits.from_int(i,bit_len=self.__min_bit_len, signed=0) for i in vals])
        return ret
    def set_alias(self, alias:TT_Alias):
        """
        Because of the dualism between registers and their aliases, the register needs to know
        it's own alias!
        """
        if not isinstance(alias, TT_Alias): raise Exception("Invalid")
        self.alias = alias
    def contextual_decode(self, encode_input:SASS_Bits) -> SASS_Bits:
        raise Exception(sp.CONST__ERROR_NOT_TESTED)
        if not (int(encode_input) in self.options[self.value].values()): return False, None
        return True, encode_input
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_NOT_TESTED)
        self.__decode_value = decode_value
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def eval_str(self) -> str: raise Exception("Unexpected behaviour exception")
    def space_size(self): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_Reg: 
        if self.alias is None: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if self.arg_default is None: return cTT_Reg(self.value, cTT_Default(-1, False, OptionsDict({})), self.alias.to_cpp())
        else: return cTT_Reg(self.value, self.arg_default.to_cpp(), self.alias.to_cpp())
    @staticmethod
    def tt(): return 'reg'
class TT_ICode(TT_Base):
    def __init__(self, class_name:str):
        self.class_name = class_name
        self.bin_str:str|None = None
        self.bin_ind:list = []
        self.bin_tup:tuple = ()
        self.__decode_value = None
        self.__min_bit_len = None
    @property
    def value(self): return 'Opcode'
    @property
    def alias(self): return ''
    def min_bit_len(self): return self.__min_bit_len
    def set_opcode_bin(self, bin_str:str, bin_ind:list):
        self.bin_str = bin_str
        self.bin_ind = bin_ind
        self.bin_tup = tuple(int(i) for i in self.bin_str.replace('_',''))
    def __str__(self): return 'Opcode'
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__decode_value = decode_value
        if not decode_value.bits == self.bin_tup: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if self.bin_tup is None: raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__min_bit_len = len(self.bin_tup)
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def eval_str(self) -> str: raise Exception("Illegal")
    def space_size(self): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_ICode: 
        if self.bin_str is None: raise Exception(sp.CONST__ERROR_ILLEGAL)
        return cTT_ICode(self.bin_str, self.bin_ind[0], IntVector(self.bin_tup))
class TT_Func(TT_Base):
    def __init__(self, class_name:str, func_name:str, alias:TT_Alias, arg_default:TT_FuncArg, options:set, star:bool):
        if not isinstance(options, set): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.class_name = class_name
        self.value = func_name
        if not self.value in sf.FUNC.keys():
            raise Exception("Class {0}: unknown function {1}".format(class_name, self.value))
        self.options = options
        self.arg_default:TT_FuncArg = arg_default
        self.star = star
        self.is_address = False
        self.alias:TT_Alias = alias # this is the same as one level up, but it's needed here too
        if self.value not in sf.FIXED_BIT_FUNC: self.func = sf.FUNC[self.value](self.arg_default.bit_len)
        else: self.func = sf.FUNC[self.value]()
    def min_bit_len(self): return self.arg_default.bit_len
    def __str__(self):
        res = self.value + "(" + str(self.arg_default) + ")"
        if self.star: res += '*'
        if self.alias.is_at_alias: res += "@"
        res += ":" + str(self.alias)
        return res
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        if not isinstance(bits, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)
        ff:sf.Imm = self.func
        bl = ff.get_bit_len()
        # Sometimes we write function values into larger bit places. In that case, though, all leading bits are 0
        # on decode
        if sum(bits[:-bl]) != 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return ff.sass_from_bits(bits[-bl:])
    def get_domain(self, to_limit:dict):
        if self.arg_default is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        bl = self.arg_default.bit_len
        ff:sf.Imm
        ff = self.func
        domain = ff.get_domain(self.is_address, self.arg_default.bit_len, self.arg_default.has_default, self.arg_default.default_val, self.arg_default.has_max_val, self.arg_default.max_val, bl)
        # if bl > 5:
        #     # print(expr)
        #     # sp.GLOBAL__LARGE_FUNC_EXPRESSIONS.append(expr)
        #     return SASS_Range(2**ll, 2**(bit_len-1)-1, bit_len, sign, bit_mask=int_1)
        # # return set([SASS_Bits.from_int(i) for i in range(0, 2**bl)])
        if bl <= 5:
            # this value is in conjunction with SASS_Expr large_func flag
            return set(domain)
        else:
            return domain
    def contextual_decode(self, encode_input:SASS_Bits) -> typing.Tuple[bool, SASS_Bits|None]:
        if self.is_address:
            # Assume we have an address. Sometimes the address is right-shifted by 2 if we don't
            # have space in the target bits. Then the encode_input.bit_len is 2 less than the actual
            # self.arg_default.bit_len-1 (-1 because it's a signed function). If we have that situation
            # we can left-shift the input by 2 to get the original number
            if self.arg_default.bit_len-1 >= encode_input.bit_len+2: ff1 = encode_input << 2
            else: ff1 = encode_input
        else: ff1 = encode_input
        rr,ff2 = self.func.contextual_decode(ff1)
        if not rr: return rr, None
        if self.func not in set({sf.E6M9Imm, sf.E8M7Imm, sf.F16Imm, sf.F32Imm, sf.F64Imm}):
            return self.arg_default.contextual_decode(ff2)
        return True, ff2
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__decode_value = decode_value
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def space_size(self):
        return self.arg_default.space_size()
    def eval_str(self) -> str: raise Exception("Unexpected behaviour exception")
    def set_for_constBank(self, sm_details:SM_Cu_Details): self.arg_default.set_max_val(sm_details.PARAMETERS.MAX_CONST_BANK) # type: ignore
    def set_for_addr(self): self.is_address = True
    def to_cpp(self) -> cTT_Func: return cTT_Func(self.value, self.options, self.arg_default.to_cpp(), self.star, self.is_address, cTT_Alias(self.alias.value, self.alias.is_at_alias))
    @staticmethod
    def tt(): return 'func'
###########################################################################################
AT_OP = {'?':TT_OpCashQuestion, '&':TT_OpCashAnd, '=':TT_OpCashAssign, '-':TT_OpAtNegate, '!':TT_OpAtNot, '~':TT_OpAtInvert, '&&':TT_OpAtSign, '||':TT_OpAtAbs}
###########################################################################################
###########################################################################################
###########################################################################################
###########################################################################################
###########################################################################################
class TT_Pred:
    def __init__(self, class_name:str, tt_term, cu_sm_details:SM_Cu_Details):
        self.class_name = class_name
        self.eval = {}
        self.eval_alias = {}
        self.operand_index = []
        self.is_at_alias:bool = tt_term.is_at_alias

        term = tt_term.val

        op_start = term.find('[')
        op_end = term.find(']')
        self.op = AT_OP[term[(op_start+1):op_end]](self.class_name)
        
        reg_end = term.find('(')
        # arg_options = {}
        val_possibilities = ['Predicate']
        # arg_options.update(cu_sm_details.REGISTERS.Predicate)
        if 'UniformPredicate' in cu_sm_details.REGISTERS_DICT.keys():
            val_possibilities.append('UniformPredicate')
            # arg_options.update(cu_sm_details.REGISTERS.UniformPredicate)
        
        reg = term[(op_end+1):reg_end]
        if reg not in val_possibilities:
            raise Exception("TT_Pred {0} for class {1} has an invalid register name {2}".format(str(tt_term), self.class_name, reg))

        arg_options = getattr(cu_sm_details.REGISTERS, reg)
        def_end = term.find(')')
        default = term[(reg_end+1):def_end]
        arg_default = TT_Default(class_name, default, False, arg_options)

        self.value = TT_Reg(class_name, reg, arg_default, {reg: arg_options})
        # self.eval[self.value.value] = self

        if not term[(def_end+1)] == ':':
            raise Exception("TT_Pred {0} for class {1}: format error".format(str(tt_term), self.class_name))

        alias = term[(def_end+2):]
        if alias == '':
            raise Exception("TT_Pred {0} for class {1}: format error".format(str(tt_term), self.class_name))
        self.alias = TT_Alias(class_name, alias, self.is_at_alias)
        self.value.set_alias(self.alias) # the register has to know it's own alias
        self.op.set_alias(str(self.alias)) # the atop has to know the alias as well
        self.eval[self.alias.value] = self.value
        self.eval[self.alias.value + self.op.op_name()] = self.op
        self.eval_alias[self.alias.value] = self
        self.operand_index = [self.alias.value]

        self.__decode_value = None
        old = str(tt_term)
        new = str(self)
        if not old == new:
            raise Exception("Class {0}: TT_Pred {1} benchmark compare error".format(self.class_name, old))

        self.enc_alias = [self.alias.value] + [str(self.op.alias)]

    def get_enc_alias(self):
        return self.enc_alias
    def __str__(self):
        res = '@[' + str(self.op).strip() + "]"
        res += str(self.value)
        # res += ":" + str(self.alias)
        return res
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def get_decode_value(self) -> SASS_Bits: raise Exception(sp.CONST__ERROR_ILLEGAL)
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def space_size(self): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def to_cpp(self) -> cTT_Pred: return cTT_Pred(self.value.to_cpp(), self.op.to_cpp())
    @staticmethod
    def tt(): return 'pred'
class TT_Ext(TT_Base):
    def __init__(self, class_name:str, tt_term, cu_sm_details:SM_Cu_Details):
        self.class_name = class_name
        self.eval = {}
        self.eval_alias = {}
        self.operand_index = []
        """
        tt_term.alias or tt_term.attr or tt_term.attr_args or tt_term.default or 
        tt_term.ext or tt_term.ops or tt_term.star or tt_term.unknown_def or tt_term.val
        """

        if not tt_term.alias:
            raise Exception("TT_Ext {0} for class {1} has no alias".format(str(tt_term), self.class_name))                        

        self.alias = TT_Alias(class_name, tt_term.alias, tt_term.is_at_alias)
        self.eval_alias[self.alias.value] = self
        self.operand_index = [self.alias.value]
        self.__decode_value = None

        if tt_term.access_func:
            raise Exception("TT_Ext {0} for class {1} has access func".format(str(tt_term), self.class_name))

        if tt_term.attr:
            raise Exception("TT_Ext {0} for class {1} has attr".format(str(tt_term), self.class_name))

        if not tt_term.val in cu_sm_details.REGISTERS_DICT:
            raise Exception("TT_Ext {0} for class {1} is not valid".format(str(tt_term), class_name))
        options = {tt_term.val: getattr(cu_sm_details.REGISTERS, tt_term.val)}

        if tt_term.default:
            arg_options = getattr(cu_sm_details.REGISTERS, tt_term.val)
            if len(tt_term.default) != 1:
                raise Exception("TT_Ext {0} for class {1} has unknown default value".format(str(tt_term), self.class_name))
            if not tt_term.default[0].val in arg_options:
                raise Exception("TT_Ext {0} for class {1} has more than one default value".format(str(tt_term), self.class_name))
            arg_default = TT_Default(class_name, tt_term.default[0].val, tt_term.default[0].default_has_print, arg_options)
        else:
            arg_default = None

        self.value = TT_Reg(class_name, tt_term.val, arg_default, options)
        self.value.set_alias(self.alias)
        self.eval[self.value.value] = self.value
        self.eval[self.alias.value] = self.value

        if tt_term.ext:
            raise Exception("TT_Ext {0} for class {1} has extensions".format(str(tt_term), self.class_name))
        
        if tt_term.ops:
            raise Exception("TT_Ext {0} for class {1} has operations".format(str(tt_term), self.class_name))            

        if tt_term.star:
            raise Exception("TT_Ext {0} for class {1} has star".format(str(tt_term), self.class_name))            

        # this one means, the alias doesn't show up in the encodings
        self.is_at_alias = tt_term.is_at_alias

        if tt_term.unknown_def:
            raise Exception("TT_Ext {0} for class {1} has unknown_def".format(str(tt_term), self.class_name))            

        old = str(tt_term)
        new = str(self)
        if not old == new:
            raise Exception("TT_Ext {0} for class {1} has unknown_def".format(str(tt_term), self.class_name))            
        
    def __str__(self):
        res = '/'
        res += str(self.value)
        # if self.alias.is_at_alias: res += '@'
        # res += ":" + str(self.alias)
        return res
    def contextual_decode(self, encode_input:SASS_Bits) -> SASS_Bits:
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def set_decode_value(self, decode_value:SASS_Bits) -> None:
        if self.__decode_value is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__decode_value = decode_value
    def get_decode_value(self) -> SASS_Bits:
        if self.__decode_value is None: raise Exception("Unassigned value")
        return self.__decode_value
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def space_size(self): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_Ext: return cTT_Ext(self.value.to_cpp())
    @staticmethod
    def tt(): return 'ext'
class TT_Opcode:
    def __init__(self, class_name:str, tt_term, cu_sm_details:SM_Cu_Details):
        self.class_name = class_name
        self.bin_str = ''
        self.bin_ind = ()
        self.eval = {}
        self.eval_alias = {}
        self.operand_index = []
        """
        tt_term.alias or tt_term.attr or tt_term.attr_args or tt_term.default or 
        tt_term.ext or tt_term.ops or tt_term.star or tt_term.unknown_def or tt_term.val
        """
        if tt_term.alias:
            raise Exception("TT_Opcode {0} for class {1} has distinct alias (supposed to be 'Opcode')".format(str(tt_term), self.class_name))                        

        self.alias = TT_Alias(class_name, tt_term.val, tt_term.is_at_alias)
        self.is_at_alias = False

        if tt_term.access_func:
            raise Exception("TT_Opcode {0} for class {1} has access func".format(str(tt_term), self.class_name))

        if tt_term.attr:
            raise Exception("TT_Opcode {0} for class {1} has attr".format(str(tt_term), self.class_name))

        if tt_term.default:
            raise Exception("TT_Opcode {0} for class {1} has default".format(str(tt_term), self.class_name))

        self.extensions = []
        for ext in tt_term.ext:
            self.extensions.append(TT_Ext(class_name, ext, cu_sm_details))
            self.eval.update(self.extensions[-1].eval)
            self.eval_alias.update(self.extensions[-1].eval_alias)
            self.operand_index.extend(self.extensions[-1].operand_index)
        
        old = "".join([str(i) for i in tt_term.ext])
        new = "".join([str(i) for i in self.extensions])
        if not old == new:
            raise Exception("TT_Opcode {0} for class {1}: extension parsing error".format(str(tt_term), self.class_name))            

        if not (tt_term.val == 'Opcode'):
            raise Exception("TT_Opcode {0} for class {1} has weird opcode {2}".format(str(tt_term), self.class_name, tt_term.val))            

        self.value = TT_ICode(class_name)
        self.eval[self.alias.value] = self.value
        self.eval_alias[self.alias.value] = self.value

        if tt_term.ops:
            raise Exception("TT_Opcode {0} for class {1} has operations".format(str(tt_term), self.class_name))            

        if tt_term.star:
            raise Exception("TT_Opcode {0} for class {1} has star".format(str(tt_term), self.class_name))            

        if tt_term.unknown_def:
            raise Exception("TT_Opcode {0} for class {1} has unknown_def".format(str(tt_term), self.class_name))            

        self.__decode_value = None
        old = str(tt_term)
        new = str(self).replace(' ','')
        if not old == new:
            raise Exception("Class {0}: TT_Opcode {1} benchmark compare error".format(self.class_name, old))

        self.enc_alias = list(itt.chain.from_iterable((i.value.value, i.value.alias.value) for i in self.extensions))

    def __str__(self):
        val = str(self.value)
        for ext in self.extensions:
            val += ' ' + str(ext)
        return val
    def get_enc_alias(self): return self.enc_alias
    def set_opcode_bin(self, bin_str, bin_ind):
        self.value.set_opcode_bin(bin_str, bin_ind)
    def get_opcode_bin(self):
        return self.value.bin_tup
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def get_decode_value(self) -> SASS_Bits: raise Exception("Unassigned value")
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def space_size(self): raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def to_cpp(self) -> cTT_Opcode: return cTT_Opcode(self.alias.to_cpp(), self.value.to_cpp(), ExtVector([ext.to_cpp() for ext in self.extensions]))
    @staticmethod
    def tt(): return 'Opcode'
class TT_List:
    def __init__(self, class_name, ll:typing.List, extensions:typing.List[TT_Ext]|None, cu_sm_details:SM_Cu_Details):
        self.eval = {}
        self.eval_alias = {}
        self.operand_index = []

        self.class_name = class_name
        self.value = ll
        for v in self.value:
            self.eval.update(v.eval)
            self.operand_index.extend(v.operand_index)
        self.extensions = []
        if extensions:
            for e in extensions:
                self.extensions.append(TT_Ext(class_name, e, cu_sm_details))
                self.eval.update(self.extensions[-1].eval)
                self.eval_alias.update(self.extensions[-1].eval_alias)
                self.operand_index.extend(self.extensions[-1].operand_index)

        self.enc_alias = list(itt.chain.from_iterable(t.get_enc_alias() for t in self.value)) + \
            list(itt.chain.from_iterable((i.value.value, i.value.alias.value) for i in self.extensions))

    def __str__(self):
        res = '['
        for ind, i in enumerate(self.value):
            res += str(i)
            if ind < len(self.value)-1:
                res += '+'
        res += ']'
        if self.extensions:
            for e in self.extensions:
                res += " " + str(e)
        return res
    def get_enc_alias(self): return self.enc_alias
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception("Unexpected behaviour exception")
    def get_decode_value(self) -> None: raise Exception("Unexpected behavour exception")
    def eval_str(self) -> str:
        res = '['
        for ind, i in enumerate(self.value):
            res += i.eval_str()
            if ind < len(self.value)-1:
                res += '+'
        res += ']'
        if self.extensions:
            for e in self.extensions:
                res += " " + e.eval_str()
        return res
    def to_cpp(self) -> cTT_List: return cTT_List(ParamVector([p.to_cpp() for p in self.value]), ExtVector([ext.to_cpp() for ext in self.extensions]))
    @staticmethod
    def tt(): return 'list'
class TT_Accessor:
    def __init__(self, class_name:str, access_func_name:str, attr:typing.List[TT_List], extensions:typing.List[TT_Ext], options, has_star):
        self.class_name = class_name
        self.value = access_func_name
        self.operand_index = [access_func_name]
        
        self.options = options
        if len(attr) > 2:
            raise Exception("Class {0} has more than two attributes".format(self.class_name))
        self.attr = attr
        self.has_star = has_star
        self.extensions = extensions
    def __str__(self):
        res = self.value
        for ind, a in enumerate(self.attr):
            res += str(a)
            if self.has_star and ind < len(self.attr)-1: res += '*'
        for e in self.extensions:
            res += " " + str(e)
        return res
    def get_enc_alias(self):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def get_decode_value(self) -> SASS_Bits: raise Exception("Unassigned value")
    def eval_str(self) -> str:
        res = self.value
        for ind, a in enumerate(self.attr):
            res += a.eval_str()
            if self.has_star and ind < len(self.attr)-1: res += '*'
        for e in self.extensions:
            res += " " + e.eval_str()
        return res
    @staticmethod
    def tt(): return 'accs'
class TT_Func_Accessor:
    @staticmethod
    def tt(): return 'accs'
class TT_Param:
    def __init__(self, class_name:str, tt_term, cu_sm_details:SM_Cu_Details):
        self.class_name = class_name
        self.is_at_alias = False
        self.attr = []
        self.has_attr_star = False
        self.extensions = []
        self.eval = {}
        self.eval_alias = {}
        self.operand_index = []
        """
        tt_term.alias or tt_term.attr or tt_term.attr_args or tt_term.default or 
        tt_term.ext or tt_term.ops or tt_term.star or tt_term.unknown_def or tt_term.val
        """
        # if we have an access function, like 'srcConst' in
        # [-][||]C:srcConst[UImm(5/0*):constBank]* [SImm(17)*:immConstOffset]
        # then we can't have an alias for the term
        if tt_term.access_func and tt_term.alias:
            raise Exception("TT_Param {0} for class {1} has alias and access func".format(str(tt_term), class_name))                                    
        elif not tt_term.access_func and not tt_term.alias:
            raise Exception("TT_Param {0} for class {1} has no alias".format(str(tt_term), class_name))                        

        self.ops = []
        if tt_term.alias:
            # self.access_func = None
            self.alias = TT_Alias(class_name, tt_term.alias, tt_term.is_at_alias)
            self.operand_index.append(tt_term.alias)

            if tt_term.tt == TT_Reg.tt():
                self.value = self.add_reg(class_name, tt_term, cu_sm_details)
                self.value.set_alias(self.alias)
                self.eval[self.value.value] = self.value

                if tt_term.ops:
                    for op in tt_term.ops:
                        self.ops.append(AT_OP[op.val](class_name))
                        self.ops[-1].set_alias(str(self.alias))

                # this one means, the alias doesn't show up in the encodings
                self.is_at_alias = tt_term.is_at_alias
            
            elif tt_term.tt == TT_Func.tt():
                self.value = self.add_func(class_name, tt_term, cu_sm_details)
                # self.value.value are things like BITSET, F64Imm, F32Imm, etc.
                # They are often not unique in a class format => they are never used
                # as alias in the encodings => don't add function names to the evals
                #    self.eval[self.value.value] = self            
                # this one means, the alias doesn't show up in the encodings
                self.is_at_alias = tt_term.is_at_alias

                if tt_term.ops:
                    for op in tt_term.ops:
                        self.ops.append(AT_OP[op.val](class_name))
                        self.ops[-1].set_alias(str(self.alias))

                if int(cu_sm_details.SM_XX.split('_')[-1]) < 70:
                    # NOTE: this is only relevant for **SM 50 to 62** (so not really...)
                    # There are instances where these functions need to access their sign, for example
                    #   AVGMode3 = PSignMAD(PO,Ra@negate,uImm@sign,Rc@negate);
                    # uses uImm@sign where
                    #   SSImm(17):uImm
                    # The usecase is for example with following format:
                    # FORMAT PREDICATE @[!]Predicate(PT):Pg Opcode
                    #     /Integer16:safmt /SIntegerNo32No64:sbfmt
                    #     /PO(noPO):po /VMadScale(PASS):vscale /SAT(noSAT):sat
                    #     $( Register:Rd /optCC(noCC):writeCC )$
                    #     ',' $( [-] Register:Ra /H1H0(H0):asel {/REUSE(noreuse):reuse_src_a} )$
                    #     ',' SSImm(16):sImm
                    #     ',' $( [-] Register:Rc {/REUSE(noreuse):reuse_src_c} )$
                    # Here SSImm(16) gets the operator @sign that probably returns if a value inside of
                    # SImm(16) is positive or negative.
                    # In get_domain() these return {0,1}.
                    # They show up in CONDITIONS and ENCODINGS:
                    #   ILLEGAL_INSTR_ENCODING_ERROR
                    #       (PO -> (!Ra@negate && !sImm@sign && !Rc@negate)) :
                    #           ".PO cannot be used with '-' on either input"
                    # or in table lookups like the following:
                    #   AVGMode3 = PSignMAD(PO,Ra@negate,uImm@sign,Rc@negate);
                    self.ops.append(AT_OP['&&'](class_name))
                    self.ops[-1].add_func(self.value.func)
                    self.ops[-1].set_alias(str(self.alias))

            for ext in tt_term.ext:
                self.extensions.append(TT_Ext(class_name, ext, cu_sm_details))
                self.eval.update(self.extensions[-1].eval)
                self.eval_alias.update(self.extensions[-1].eval_alias)
                self.operand_index.extend(self.extensions[-1].operand_index)

            for op in self.ops:
                self.eval[self.alias.value + op.op_name()] = op

            self.eval[self.alias.value] = self.value
            self.eval_alias[self.alias.value] = self

        elif tt_term.access_func:
            if tt_term.star:
                raise Exception("TT_Param {0} for class {1} has star".format(str(tt_term), class_name))
            if tt_term.is_at_alias:
                raise Exception("TT_Param {0} for class {1} has @ alias for accessor".format(str(tt_term), class_name))
            
            self.value = self.add_reg(class_name, tt_term, cu_sm_details, no_default=True)
            # new: TT_Param with an accessor has an alias now too
            # self.alias = None
            self.eval[self.value.value] = self.value

            if tt_term.ops:
                for op in tt_term.ops:
                    self.ops.append(AT_OP[op.val](class_name))
            
            access_func = tt_term.access_func
            if access_func.tt == TT_Accessor.tt():
                # This one stays here for reference:
                # ==================================
                # It use to be that for things like
                # [-]C:srcConst[UImm(5/0*):constBank]* [SImm(17)*:immConstOffset]
                # C == TT_Reg, srcConst == TT_Accessor and the rest inside the [] were accessor attributes
                # The new world is: srcConst is the alias of the register C => TT_Param will get a direct
                # alias in this case too.

                if access_func.alias:
                    raise Exception("TT_Param {0} for class {1} has register access func with an alias".format(str(tt_term), class_name))
                if not access_func.attr:
                    raise Exception("TT_Param {0} for class {1} has register access func but no attr".format(str(tt_term), class_name))
                if tt_term.ext:
                    raise Exception("TT_Param {0} for class {1} has register access func but reg has extensions".format(str(tt_term), class_name))

                # this is how it used to be (just with self. instead of s_)
                s_access_func:TT_Accessor = self.add_accessor(class_name, access_func, cu_sm_details)
                # There are essentially two types of accessors:
                #  - with only one attr: A:srcAttr[ZeroRegister(RZ):Ra + UImm(10/0)*:uImm]
                #  - with two attr: [-] C:Sb[UImm(5/0*):constBank]* [SImm(17)*:immConstOffset]
                # All the ones with two attr are memory accesses with the weird quirks that they come with
                # and we have to set some flag to make sure we generate "address"-bits and not generalized bits
                if len(s_access_func.attr) == 2:
                    # if we have a const memory access, we have a max number of memory banks
                    # that exist => set that number in the TT_FuncArg argument
                    for i in s_access_func.attr[0].value:
                        if i.alias.value == 'constBank': i.value.set_for_constBank(cu_sm_details)
                    # we also address the memory with 4 byte granularity
                    # => we only need 14 out of 17 bits if signed and 15 out of 17 bits if unsigned
                    for i in s_access_func.attr[1].value:
                        if i.alias.value == 'immConstOffset': i.value.set_for_addr()
                        else:
                            funcs = [i.value for i in s_access_func.attr[1].value if isinstance(i.value, TT_Func)]
                            if any(funcs):
                                for f in funcs: f.set_for_addr()
                                
                # this is new
                self.alias = TT_Alias(class_name, s_access_func.value, tt_term.is_at_alias)
                self.attr = s_access_func.attr
                self.has_attr_star = access_func.has_star
                self.extensions = s_access_func.extensions
                self.eval[self.alias.value] = self.value
                if isinstance(self.value, TT_Reg):
                    self.value.set_alias(self.alias)
                    
                self.eval_alias[self.alias.value] = self
                self.operand_index.append(self.alias.value)
                for a in self.attr:
                    self.eval.update(a.eval)
                    self.eval_alias.update(a.eval_alias)
                    self.operand_index.extend(a.operand_index)
                for e in self.extensions:
                    self.eval.update(e.eval)
                    self.eval_alias.update(e.eval_alias)
                    self.operand_index.extend(e.operand_index)
                for op in self.ops:
                    self.eval[self.alias.value + op.op_name()] = op
                    op.set_alias(str(self.alias))

                # get the operand aliases out of the attributes
                self.operand_index.extend(list(itt.chain.from_iterable([[j.alias.value for j in i.value] for i in self.attr])))
            else: raise Exception("TT_Param {0} for class {1} invalid access func format".format(str(tt_term), class_name))

        if tt_term.unknown_def:
            raise Exception("TT_Param {0} for class {1} has unknown_def".format(str(tt_term), class_name))            

        old = str(tt_term)
        new = str(self).replace(' ','')
        if not old == new:
            raise Exception("Class {0}: TT_Param {1} benchmark compare error".format(class_name, old))

        self.enc_alias = [self.alias.value] + list(itt.chain.from_iterable((i.value.value, i.value.alias.value) for i in self.extensions)) + [str(o.alias) for o in self.ops] + list(itt.chain.from_iterable(i.get_enc_alias() for i in self.attr)) # type: ignore

    def add_accessor(self, class_name, tt_term, cu_sm_details):
        accessors = set([i for i in dir(cu_sm_details.ACCESSORS) if not (i.startswith('__') and i.endswith('__'))])
        if not tt_term.val in accessors:
            raise Exception("TT_Param {0} for class {1} has invalid accessor name".format(str(tt_term), class_name))

        attr = []
        for a in tt_term.attr:
            ll = []
            for i in a.val:
                ll.append(TT_Param(class_name, i, cu_sm_details))
            attr.append(TT_List(class_name, ll, None, cu_sm_details))
        ext = []
        if tt_term.ext:
            for e in tt_term.ext:
                ext.append(TT_Ext(class_name, e, cu_sm_details))
        
        return TT_Accessor(class_name, tt_term.val, attr, ext, accessors, tt_term.has_star)

    def add_reg(self, class_name, tt_term, cu_sm_details, no_default=False):
        if tt_term.default:
            if no_default:
                raise Exception("TT_Param {0} for class {1} is not allowed to have default value".format(str(tt_term), class_name))
            if len(tt_term.default) != 1:
                raise Exception("TT_Param {0} for class {1} has more than one default value".format(str(tt_term), class_name))
            arg_options = getattr(cu_sm_details.REGISTERS, tt_term.val)
            arg_default = TT_Default(class_name, tt_term.default[0].val, tt_term.default[0].default_has_print, arg_options)
        else:
            arg_default = None

        if tt_term.star:
            raise Exception("TT_Param {0} for class {1} has star".format(str(tt_term), class_name))
        # This used to be all registers, but that is pretty much useless. It's much more valuable to have
        # all possible values for a register at the disposal, no matter what. Registers are never just generic. They always have a name
        # and assigned possible values.
        if not tt_term.val in cu_sm_details.REGISTERS_DICT:
            raise Exception("TT_Param {0} for class {1} is not valid".format(str(tt_term), class_name))
        options = {tt_term.val: getattr(cu_sm_details.REGISTERS, tt_term.val)}
        return TT_Reg(class_name, tt_term.val, arg_default, options)

    def add_func(self, class_name, tt_term, cu_sm_details):
        if tt_term.default:
            if len(tt_term.default) != 1:
                raise Exception("TT_Param {0} for class {1} has more than one default value".format(str(tt_term), class_name))
            arg_default = TT_FuncArg(class_name, tt_term.default[0].val)
        else:
            arg_default = None
        if tt_term.ops:
            raise Exception("TT_Param {0} for class {1} has operations".format(str(tt_term), class_name))            
        options = set([i for i in dir(cu_sm_details.FUNCTIONS) if not (i.startswith('__') and i.endswith('__'))])
        if not tt_term.val in options:
            raise Exception("TT_Param {0} for class {1} has invalid function name".format(str(tt_term), class_name))
        if not arg_default:
            raise Exception("TT_Param {0} for class {1} has function without arguments".format(str(tt_term), class_name))
        # if tt_term.is_at_alias:
        #     raise Exception("TT_Param {0} for class {1} has @ alias for function".format(str(tt_term), class_name))
        
        return TT_Func(class_name, tt_term.val, TT_Alias(class_name, tt_term.alias, tt_term.is_at_alias), arg_default, options, tt_term.has_star)
        
    def __str__(self):
        res = ""
        i:TT_OpAtAbs|TT_OpAtInvert|TT_OpAtNegate|TT_OpAtNot|TT_OpAtSign
        for i in self.ops:
            if i.has_func(): continue
            res += "[" + str(i) + "]"
        res += str(self.value)
        # if self.is_at_alias: res += '@'
        # res += ":" + str(self.alias)
        for ind, a in enumerate(self.attr):
            res += str(a)
            if self.has_attr_star and ind < len(self.attr)-1: res += '*'
        for ext in self.extensions:
            res += " " + str(ext)
        return res
    def get_enc_alias(self): return self.enc_alias
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def get_decode_value(self) -> SASS_Bits: raise Exception(sp.CONST__ERROR_ILLEGAL)
    def eval_str(self) -> str: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def space_size(self): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def to_cpp(self) -> cTT_AttrParam|cTT_Param:
        if self.attr:
            return cTT_AttrParam(OpsVector([o.to_cpp() for o in self.ops]), self.value.to_cpp(), ListVector([a.to_cpp() for a in self.attr]), ExtVector([ext.to_cpp() for ext in self.extensions]), self.has_attr_star)
        else:
            return cTT_Param(OpsVector([o.to_cpp() for o in self.ops]), self.value.to_cpp(), ExtVector([ext.to_cpp() for ext in self.extensions]))
    @staticmethod
    def tt(): return 'param'
class TT_Cash:
    def __init__(self, class_name:str, tt_term, cu_sm_details:SM_Cu_Details, added_later=False):
        self.class_name = class_name
        self.eval = {}
        self.eval_alias = {}
        self.operand_index = []
        self.added_later = added_later

        vals = []
        for i in tt_term.val:
            if i.tt == TT_Op.tt():
                vals.append(AT_OP[i.val](class_name))
            elif i.tt == TT_Reg.tt():
                vals.append(self.add_reg(class_name, i, cu_sm_details))
                self.eval.update(vals[-1].eval)
                self.eval_alias.update(vals[-1].eval_alias)
                self.operand_index.extend(vals[-1].operand_index)
            elif i.tt == TT_Func.tt():
                vals.append(self.add_func(class_name, i, cu_sm_details))
                self.eval.update(vals[-1].eval)
                self.eval_alias.update(vals[-1].eval_alias)
                self.operand_index.extend(vals[-1].operand_index)
            else:
                raise Exception("Class {0} cash {1} has unknown komponent".format(self.class_name, "$( { " + " ".join([str(i) for i in tt_term.val]) + " } )$"))
        
        self.values = vals

        old = str(tt_term)
        new = str(self)
        if not old == new:
            raise Exception("Class {0}: TT_Cash {1} benchmark compare error".format(self.class_name, old))
        
        self.enc_alias = list(itt.chain.from_iterable(v.get_enc_alias() for v in self.values if isinstance(v, TT_Param)))

    def add_reg(self, class_name, tt_term, cu_sm_details:SM_Cu_Details):
        if tt_term.star:
            raise Exception("TT_Cash {0} for class {1} has star".format(str(tt_term), self.class_name))
        if tt_term.access_func:
            raise Exception("TT_Cash {0} for class {1} has access func".format(str(tt_term), self.class_name))                                    
        if not tt_term.alias:
            raise Exception("TT_Cash {0} for class {1} has no alias".format(str(tt_term), self.class_name))                        
        if tt_term.unknown_def:
            raise Exception("TT_Cash {0} for class {1} has unknown_def".format(str(tt_term), self.class_name))            
        if tt_term.ops:
            raise Exception("TT_Cash {0} for class {1} has leading operations".format(str(tt_term), self.class_name))
        if tt_term.attr:
            raise Exception("TT_Cash {0} for class {1} has attr".format(str(tt_term), self.class_name))
        
        return TT_Param(class_name, tt_term, cu_sm_details)

    def add_func(self, class_name, tt_term, cu_sm_details:SM_Cu_Details):
        if not tt_term.default:
            raise Exception("TT_Cash {0} for class {1} has no default value".format(str(tt_term), self.class_name))
        if tt_term.star:
            raise Exception("TT_Cash {0} for class {1} has star".format(str(tt_term), self.class_name))
        if tt_term.access_func:
            raise Exception("TT_Cash {0} for class {1} has access func".format(str(tt_term), self.class_name))                                    
        if not tt_term.alias:
            raise Exception("TT_Cash {0} for class {1} has no alias".format(str(tt_term), self.class_name))                        
        if tt_term.unknown_def:
            raise Exception("TT_Cash {0} for class {1} has unknown_def".format(str(tt_term), self.class_name))            
        if tt_term.ops:
            raise Exception("TT_Cash {0} for class {1} has leading operations".format(str(tt_term), self.class_name))
        if tt_term.attr:
            raise Exception("TT_Cash {0} for class {1} has attr".format(str(tt_term), self.class_name))
        
        return TT_Param(class_name, tt_term, cu_sm_details)
        
    def __str__(self):
        res = '$( { '
        for i in self.values:
            res += str(i) + " "
        res += '} )$'
        return res
    def get_enc_alias(self): return self.enc_alias
    def set_decode_value(self, decode_value:SASS_Bits) -> None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def get_decode_value(self) -> SASS_Bits: raise Exception(sp.CONST__ERROR_ILLEGAL)
    def space_size(self): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def eval_str(self) -> str:
        res = '$( { '
        for i in self.values:
            res += i.eval_str() + " "
        res += '} )$'
        return res
    def to_cpp(self) -> cTT_Cash: return cTT_Cash(CashComponentsVector([v.to_cpp() for v in self.values]), self.added_later)
    @staticmethod
    def tt(): return '$'
