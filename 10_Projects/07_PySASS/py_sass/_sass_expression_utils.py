
from __future__ import annotations
import typing as typ
import operator as oo
from . import _config as sp
from py_sass_ext import SASS_Bits
from ._sass_util import SASS_Util as su
from ._tt_terms import TT_OpAtAbs, TT_OpAtNot, TT_OpAtInvert, TT_OpAtNegate, TT_OpAtSign

class Op_Base:
    TT_CONVERTIBLE = set([oo.mul, oo.add, oo.sub, oo.eq, oo.le, oo.ge, oo.lt, oo.gt, oo.floordiv, oo.ne])
    def __init__(self, op_f:typ.Callable|None, op_str:str, op_checks:typ.Callable|None=None):
        self.__NEXT:Op_Base|None
        self.__OP_F:typ.Callable|None
        self.__OP_STR:str
        self.__op_checks:typ.Callable|None=None
        if not (callable(op_f) or op_f is None): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(op_str, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not ((op_checks is None) or (callable(op_checks) and op_checks.__name__ == '<lambda>' and op_checks.__code__.co_argcount == 2)): 
            raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__NEXT = None
        self.__OP_F = op_f
        self.__OP_STR = op_str
        self.__OP_CHECKS = op_checks
        self.__op_set = set(i for i in dir(oo) if not i.startswith('__') and i.endswith('__'))
    def __str__(self): return self.__OP_STR
    def v_str(self): return type(self).__name__ + "[{0}]".format(self.__OP_STR)
    def signature(self): return type(self)
    def set_next(self, nn:Op_Base): self.__NEXT = nn
    def get_next(self) -> Op_Base|None: return self.__NEXT
    def is_op(self): return True
    def op(self, *args) -> typ.Callable:
        if self.__OP_CHECKS is not None and not self.__OP_CHECKS(*args): raise Exception(sp.CONST__ERROR_ILLEGAL) 
        if self.__OP_F is None: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if len(args) == 2:
            if isinstance(args[0], list) and isinstance(args[1], dict):
                # this is an Op_Function => no need to check SASS_Bits stuff
                # but maybe unpack some arguments...
                # if any(isinstance(a,set) for a in args[0]):
                #     args0 = []
                #     for a in args[0]:
                #         if not isinstance(a,set) or len(a) > 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                #         args0.append(next(iter(a)))
                #     args = (args0, args[1])
                pass
            elif not isinstance(args[0], SASS_Bits) and isinstance(args[1], SASS_Bits):
                # This can happen if we at some point have args[0] True and args[1] some SASS_Bits
                if not self.__OP_F in self.TT_CONVERTIBLE and self.__OP_F.__name__ in self.__op_set:
                    raise Exception(sp.CONST__ERROR_UNEXPECTED)
                args = (args[0], int(args[1]))
        return self.__OP_F(*args)
    def value(self): raise Exception(sp.CONST__ERROR_ILLEGAL)

class Op_DualOperator(Op_Base):
    def __init__(self, op_f:typ.Callable, op_str:str, op_checks:typ.Callable|None=None):
        super().__init__(op_f, op_str, op_checks)
    def __str__(self): 
        return ' ' + Op_Base.__str__(self) + ' '
    def op(self, arg1, arg2): # type: ignore
        return super().op(arg1, arg2)
    
class Op_UnaryOperator(Op_Base):
    def __init__(self, op_f:typ.Callable, op_str:str, op_checks:typ.Callable|None=None): super().__init__(op_f, op_str, op_checks)
    def __str__(self): return ' ' + Op_Base.__str__(self)
    def op(self, arg1): # type: ignore
        return super().op(arg1)

class Op_Function(Op_Base):
    def __init__(self, op_f:typ.Callable, op_str:str, op_checks:typ.Callable|None=None): super().__init__(op_f, op_str, op_checks)
    def op(self, args, enc_vals:dict): # type: ignore
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(args, list): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return super().op(args, enc_vals)
    def set_arg_num(self, num:int): self.arg_num = num
    def get_arg_num(self): return self.arg_num

class Op_Operand(Op_Base):
    def __init__(self, op_f:typ.Callable|None, name:str, value):
        if not isinstance(name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        super().__init__(op_f, name, None)
        self.__VALUE:object
        self.__VALUE = su.try_convert(value, convert_bin=True, convert_hex=True, convert_split_bin=True)
    def value(self): return self.__VALUE # type: ignore

class Op_Control(Op_Base):
    def __init__(self, op_f:typ.Callable, op_str:str): super().__init__(op_f, op_str, op_checks=None)

class Op_ParamSplit(Op_Base):
    def __init__(self): super().__init__(None, ',', None)

class Op_AtOperand(Op_Operand):
    """This one corresponds to all @bla operands"""
    __tt_types = {
        'TT_OpAtAbs': TT_OpAtAbs, 
        'TT_OpAtNot': TT_OpAtNot, 
        'TT_OpAtInvert': TT_OpAtInvert, 
        'TT_OpAtNegate': TT_OpAtNegate, 
        'TT_OpAtSign': TT_OpAtSign
    }
    def operation_at(self, enc_vals:dict):
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not str(self) in enc_vals.keys(): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return enc_vals[str(self)]
    def __init__(self, name:str, term:object, tt_type:str, op_name:str):
        if not isinstance(term, TT_OpAtAbs|TT_OpAtNot|TT_OpAtInvert|TT_OpAtNegate|TT_OpAtSign):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        super().__init__(self.operation_at, name + op_name, term)
        self.__TT_TYPE:str
        self.__OP_NAME:str
        # This workaround with a semi-static dictionary with the TT_.. types is to avoid having to
        # from . import _tt_terms into _sass_expression_ops.py. That makes it easier to use all the Op_... classes
        # elsewhere without causing a circular import problem
        if not tt_type in Op_AtOperand.__tt_types: raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__TT_TYPE = Op_AtOperand.__tt_types[tt_type]
        self.__OP_NAME = op_name

class Op_Iter:
    def __init__(self, start:Op_Base, skip_undef_first=False):
        if not isinstance(start, Op_Base): raise Exception("Illegal")
        self.__start:Op_Base
        self.__start = start
        self.__cur:Op_Base|int|None
        self.__cur = start if skip_undef_first else 0
    def current(self) -> Op_Base|bool|None|int:
        if self.__cur == 0: return None
        elif self.__cur is not None: return self.__cur
        else: return False
    def next(self) -> Op_Base|bool|None|int:
        if self.__cur == 0: self.__cur = self.__start
        elif self.__cur is None: return False
        else: self.__cur = self.__cur.get_next() # type: ignore
        return self.__cur
    def peek(self) -> Op_Base|bool|None|int:
        if self.__cur == 0: return self.__start
        elif self.__cur is not None: return self.__cur.get_next() # type: ignore
        else: return False
