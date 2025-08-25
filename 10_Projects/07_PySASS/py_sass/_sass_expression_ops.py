from __future__ import annotations
import operator
import inspect
import sys
import typing as typ
import itertools as itt
from . import _config as sp
from . import _sass_func
from ._sass_util import SASS_Util as su
from ._sass_func import F16Imm, F32Imm, F64Imm, E6M9Imm, E8M7Imm
from py_sass_ext import SASS_Bits
from py_sass_ext import BitVector
from ._sass_expression_utils import Op_ParamSplit, Op_Base, Op_Function, Op_UnaryOperator
from ._sass_expression_utils import Op_Operand, Op_DualOperator, Op_Control, Op_AtOperand
from ._tt_terms import TT_ICode

class Op_NotEnc(Op_Operand):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_NONE
    P=sp.EXPR_OP_PRECEDENCE_NR_NONE
    def __init__(self, code_name:str): super().__init__(None, code_name, 0)
    def __str__(self): return "!_(" + Op_Base.__str__(self) + ")_"
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
# The following classes have strings as args like 'TT_OpAtNot'. This is to avoid an import of 
# _tt_terms into this file to make it easier to use all the Op_... classes somewhere else (avoid circular imports)
class Op_AtNot(Op_AtOperand):
    """This one corresponds to @not (not the logical '!')"""
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def __init__(self, name:str, term): super().__init__(name, term, 'TT_OpAtNot', '@not')
class Op_AtNegate(Op_AtOperand):
    """This one corresponds to @negate (not the unary '-')"""
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def __init__(self, name:str, term): super().__init__(name, term, 'TT_OpAtNegate', '@negate')
class Op_AtAbs(Op_AtOperand):
    """This one corresponds to @absolute which is the [||] in front of some instructions"""
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def __init__(self, name:str, term): super().__init__(name, term, 'TT_OpAtAbs', '@absolute')
class Op_AtSign(Op_AtOperand):
    """This one corresponds to @sign"""
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def __init__(self, name:str, term): super().__init__(name, term, 'TT_OpAtSign', '@sign')
class Op_AtInvert(Op_AtOperand):
    """This one corresponds to @invert that corresponds to the [~] that is sometimes present in front of instructions"""
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def __init__(self, name:str, term): super().__init__(name, term, 'TT_OpAtInvert', '@invert')
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_TypeCast(Op_Function):
    """If we have a convertFloatType, this one will be the first argument, containing the type things get typecasted to."""
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_cast(self, args, enc_vals:dict) -> SASS_Bits:
        if not len(args) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return self.__TC_FF(args[0])
    def __init__(self, tc_ff:F16Imm|F32Imm|F64Imm|E6M9Imm|E8M7Imm): 
        if not (type(tc_ff) in _sass_func.CONVERT_FUNC.values()): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        super().__init__(self.operation_cast, str(tc_ff))
        self.__TC_FF:typ.Callable
        self.__TC_FF = tc_ff
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_ConstBankAddress2(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_p(self, args, enc_vals:dict) -> typ.List[SASS_Bits]:
        if not len(args) == 2: raise Exception(sp.CONST__ERROR_ILLEGAL)
        arg1:SASS_Bits = args[0]
        arg2:SASS_Bits = args[1]
        # 1st arg is UImm => unsigned
        if arg1.signed: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # 2nd arg is SImm => signed
        if not arg2.signed: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # we are going to shave off the trailing 2 bits with SCALE => they both have to be 0
        if not (arg2 & SASS_Bits(BitVector([1,1]), bit_len=3, signed=False) == 0): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # With constBankAddress2 we want to assign a full immediate value for an address, like in
        #   [-] C:srcConst[UImm(5/0*):constBank]* [SImm(17)*:immConstOffset]
        # But in the encoding portion
        #   Bcbank,Bcaddr =  ConstBankAddress2(constBank,immConstOffset);
        # Bcaddr usually has 3 fewer bits (immConstOffset has 17 bits, Bcaddr only 14 bits)
        # Since arg2 is an address, it's rightmost bits are 0. It also has to be a signed value.
        #  => apply "SCALE 4" (shave off trailing 2 bits)
        #  => apply "to_unsigned" (shave off leading bit)
        arg2_a = arg2.scale(4).to_unsigned()
        return [arg1, arg2_a]
    def __init__(self): super().__init__(self.operation_p, 'ConstBankAddress2')
class Op_ConstBankAddress0(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_p(self, args, enc_vals:dict) -> typ.List[SASS_Bits]:
        if not len(args) == 2: raise Exception(sp.CONST__ERROR_ILLEGAL)
        arg1:SASS_Bits = args[0]
        arg2:SASS_Bits = args[1]
        # 1st arg is UImm => unsigned
        if arg1.signed: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # 2nd arg is SImm => signed
        if not arg2.signed: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # With constBankAddress0 we want to assign a full immediate value for an address, like in
        #   [-] C:srcConst[UImm(5/0*):constBank]* [SImm(17)*:immConstOffset]
        # But in the encoding portion
        #   Bcbank,Bcaddr =  ConstBankAddress2(constBank,immConstOffset);
        # Bcaddr usually has 1 fewer bits (immConstOffset has 17 bits, Imm16 only 16 bits)
        #  => apply "to_unsigned" (shave off leading bit)
        arg2_a = arg2.to_unsigned()
        return [arg1, arg2_a]
    def __init__(self): super().__init__(self.operation_p, 'ConstBankAddress0')
class Op_Identical(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_p(self, args, enc_vals:dict) -> SASS_Bits:
        if not len(args) == 2: raise Exception(sp.CONST__ERROR_ILLEGAL)
        # Dest = IDENTICAL(Rd,Rc); means, we select one of them and assign it to both.
        # Both args must be the same
        if not args[0] == args[1]: raise Exception(sp.CONST__ERROR_ILLEGAL)
        # Pick the first one and return it.
        return args[0]
    def __init__(self): super().__init__(self.operation_p, 'IDENTICAL')
class Op_convertFloatType(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_convert(self, args, enc_vals:dict) -> SASS_Bits:
        for ind,p in enumerate(args[:-1][::2]):
            if p: return args[2*ind+1]
        return args[-1]
    def __init__(self): super().__init__(self.operation_convert, 'convertFloatType')
class Op_Reduce(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_reduce(self, args, enc_vals:dict) -> SASS_Bits|int|bool:
        if not len(args) >= 2: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(self.reduce_op, Op_DualOperator): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        op:Op_DualOperator = self.reduce_op
        cur:SASS_Bits|int|bool = args[0]
        for p in args[1:]:
            cur = op.op(cur, p) # type: ignore
        return cur
    def __init__(self): 
        super().__init__(self.operation_reduce, 'Reduce')
        self.reduce_op = None
    def set_reduce_op(self, op): self.reduce_op = op
    def __str__(self): return Op_Function.__str__(self) + (('(' + str(self.reduce_op) + ')') if self.reduce_op is not None else '')
class Op_Table(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_table(self, args, enc_vals:dict):
        if not len(args) == len(list(self.table.keys())[0]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        vals = tuple(int(i) for i in args)
        # If we don't find the vals in the table, it's not an exception. In the cases
        # where this could be from the assembling perspective, we make sure that the mock
        # functions only generate valid bits. Thus, this check is redundant
        #    if not vals in self.table.keys(): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # From the evaluation perspective, from SM70++ we have things like this
        # ILLEGAL_INSTR_ENCODING_SASS_ONLY_ERROR
        #   DEFINED TABLES_opex_0(batch_t,usched_info) :
        #   "Invalid combination of batch_t, usched_info" 
        # where DEFINED stands for 'check if the value exists in the table'. For this we need
        # a propper return value on the stack
        if not vals in self.table.keys(): return False # this is for the DEFINED operator
        res = self.table[vals]
        res = su.try_convert(res, convert_bin=True, convert_hex=True, convert_split_bin=True)
        if not isinstance(res, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return SASS_Bits.from_int(res, signed=0)
    def __init__(self, name:str, table:dict, table_inv:dict):
        super().__init__(self.operation_table, name)
        self.table:dict = table
        self.table_inv:dict = table_inv
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_RBrace(Op_Base):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_NONE
    P=sp.EXPR_OP_PRECEDENCE_NR_NONE
    def operation_brace(self): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def __init__(self): super().__init__(op_f=self.operation_brace, op_str=')')
class Op_LBrace(Op_Base):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_NONE
    P=sp.EXPR_OP_PRECEDENCE_NR_NONE
    def operation_brace(self): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def __init__(self): super().__init__(op_f=self.operation_brace, op_str='(')
class Op_RCBrace(Op_Base):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_NONE
    P=sp.EXPR_OP_PRECEDENCE_NR_NONE
    def operation_cbrace(self): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def __init__(self): super().__init__(op_f=self.operation_cbrace, op_str='}')
class Op_LCBrace(Op_Base):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_NONE
    P=sp.EXPR_OP_PRECEDENCE_NR_NONE
    def operation_cbrace(self): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def __init__(self): super().__init__(op_f=self.operation_cbrace, op_str='{')
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_Index(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_index(self, args, enc_vals:dict) -> SASS_Bits:
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def __init__(self): super().__init__(op_f=self.operation_index, op_str='INDEX')
    # def evaluate(self, args:typ.Dict, tt_format:TT_Instruction, op_ii:Op_Iter, instr_candidates:typ.List[TT_Instruction], parent_nr:int): 
    #     # Assume that this one only occurs in the PROPERTIES section that we don't really care about
    #     if not parent_nr == sp.CONST_INT__PROPERTIES: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     stack, enc_vals, tt = Ops_Utils.eval_checkStartFunc(EXPR_1ARG_PACKAGE_DICT, args, op_ii)
    #     stack.append('s')
    #     tt.evaluate(args, tt_format, op_ii, instr_candidates, parent_nr)
    #     if not len(stack) >= 1 and isinstance(stack[-1], str): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     alias_name = stack.pop()
    #     stack.append(SASS_Bits.from_int(tt_format.operand_index.index(alias_name)))
class Op_IsEven(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_is_even(self, args, enc_vals:dict):
        if not len(args) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return (int(args[0])%2)==0
    def __init__(self): super().__init__(op_f=self.operation_is_even, op_str='IsEven')
class Op_IsOdd(Op_Function):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
    P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
    def operation_is_odd(self, args, enc_vals:dict):
        if not len(args) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return (int(args[0])%2)==1
    def __init__(self): super().__init__(op_f=self.operation_is_odd, op_str='IsOdd')
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
# if isinstance(self.__VALUE, TT_ICode): self.__BITS = SASS_Bits(self.__VALUE.bin_tup, bit_len=len(self.__VALUE.bin_tup), signed=False)
# elif isinstance(self.__VALUE, TT_Reg): self.__BITS = SASS_Bits.from_int(self.__VALUE.value(), signed=0) 
# elif isinstance(self.__VALUE, int): self.__BITS = SASS_Bits.from_int(self.__VALUE)
# elif isinstance(self.__VALUE, str): self.__BITS = SASS_Bits.from_int(su.try_convert(value, convert_bin=True, convert_hex=True, convert_split_bin=True))
# else: raise Exception(sp.CONST__ERROR_ILLEGAL)
class Op_Parameter(Op_Operand):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def parameter_operation(self, enc_vals:dict): 
        val = self.value()
        if not isinstance(val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return SASS_Bits.from_int(val, signed=0)
    def __init__(self, name:str, value): 
        super().__init__(self.parameter_operation, name, value)
    def __str__(self): return '%'+ Op_Operand.__str__(self)
    def v_str(self): return type(self).__name__ + "[{0}]".format('%'+str(self))
class Op_Constant(Op_Operand):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def constant_operation(self, enc_vals:dict): 
        val = self.value()
        if not isinstance(val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return SASS_Bits.from_int(val, signed=0)
    def __init__(self, name:str, value): 
        super().__init__(self.constant_operation, name, value)
class Op_Register(Op_Operand):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def register_operation(self, enc_vals:dict): 
        val = self.value()
        if not isinstance(val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return SASS_Bits.from_int(val, signed=0)
    def __init__(self, parent:str, name:str, value): 
        if not isinstance(parent, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not type(name) in [str, int]: raise Exception(sp.CONST__ERROR_ILLEGAL)
        # because the register values are not as unique as originally assumed, do some differentiation here
        if not isinstance(value, int):
            if not isinstance(value, set): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if len(value) != 1: 
                # SIDL_NAMES is special...
                # All it's children only appear in the PROPERTIES and it's not clear yet what criterias need to work for them
                if parent == 'SIDL_NAMES':
                    value = min(value)
                else:
                    raise Exception(sp.CONST__ERROR_UNEXPECTED)
            else:
                value = next(iter(value))
            if not isinstance(value, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        super().__init__(self.register_operation, parent + '@' + str(name), value)
        self.__PARENT:str
        self.__REGISTER:str
        self.__PARENT = parent
        self.__REGISTER = name
    def __str__(self): return '`'+Op_Operand.__str__(self)
    def v_str(self): return type(self).__name__ + "[{0}]".format('`'+str(self))
    def parent_register(self): return self.__PARENT
    def register(self): return self.__REGISTER
#######################################################################################################################################
class Op_Int(Op_Operand):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def int_operation(self, enc_vals:dict): 
        val = self.value()
        if not isinstance(val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return SASS_Bits.from_int(val)
    def __init__(self, val_str:str, val:int): 
        super().__init__(self.int_operation, val_str, val)
class Op_Opcode(Op_Operand):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def opcode_operation(self, enc_vals:dict): 
        val = self.term()
        if not isinstance(val, TT_ICode): raise Exception(sp.CONST__ERROR_ILLEGAL)
        bin_tup:tuple = val.bin_tup # type: ignore
        return SASS_Bits(BitVector(bin_tup), bit_len=len(bin_tup), signed=False)
    def __init__(self, name:str, term): 
        super().__init__(self.opcode_operation, name, str(term))
        self.__term = term
    def term(self): return self.__term
class Op_Alias(Op_Operand):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_OPERAND
    P=sp.EXPR_OP_PRECEDENCE_NR_OPERAND
    def alias_operation(self, enc_vals:dict):
        if not str(self) in enc_vals.keys(): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return enc_vals[str(self)]
    def __init__(self, name:str, term): 
        super().__init__(self.alias_operation, name, term)
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_Comma(Op_ParamSplit):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_COMMA
    P=sp.EXPR_OP_PRECEDENCE_NR_COMMA
    def __init__(self): super().__init__()
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_Value(Op_Base):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_NONE
    P=sp.EXPR_OP_PRECEDENCE_NR_NONE
    def operation_value(self, arg): return arg
    def __init__(self, val:str): 
        super().__init__(op_f=self.operation_value, op_str=val)
        if not isinstance(val, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if val.find(' ') >= 0: raise Exception("Token '{0}' contains illegal whitespace".format(val))
    def value(self): return Op_Base.__str__(self) # type: ignore
    def __hash__(self): return self.value().__hash__()
class Op_Set(Op_Operand):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_NONE
    P=sp.EXPR_OP_PRECEDENCE_NR_NONE
    def operation_set(self, arg): return self.value()
    def __init__(self, val:set): 
        if not isinstance(val, set): raise Exception(sp.CONST__ERROR_ILLEGAL)
        super().__init__(self.operation_set, "{...}", {v.value() for v in val})
    def __str__(self):
        return "{{{0}}}".format(", ".join(str(i) for i in self.value())) # type: ignore
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_IfElse(Op_Control):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_CTRL
    P=sp.EXPR_OP_PRECEDENCE_NR_CTRL
    def operation_ifelse(self): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def __init__(self): super().__init__(op_f=self.operation_ifelse, op_str=':')
    def __str__(self): return ' ' + Op_Control.__str__(self) + ' '
class Op_If(Op_Control):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_CTRL
    P=sp.EXPR_OP_PRECEDENCE_NR_CTRL
    def operation_if(self, args:typ.List, enc_vals:dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def __init__(self): super().__init__(op_f=self.operation_if, op_str='?')
    def __str__(self): return ' ' + Op_Control.__str__(self) + ' '
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_Not(Op_UnaryOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_0
    P=sp.EXPR_OP_PRECEDENCE_NR_0
    def __init__(self): super().__init__(op_f=operator.not_, op_str='!')
class Op_BNot(Op_UnaryOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_0
    P=sp.EXPR_OP_PRECEDENCE_NR_0
    def __init__(self): super().__init__(op_f=operator.inv, op_str='~')
#######################################################################################################################################
class Op_Mod(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_1
    P=sp.EXPR_OP_PRECEDENCE_NR_1
    def __init__(self): super().__init__(op_f=operator.mod, op_str='%')
class Op_Div(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_1
    P=sp.EXPR_OP_PRECEDENCE_NR_1
    def __init__(self): super().__init__(op_f=operator.floordiv, op_str='/')
class Op_Mult(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_1
    P=sp.EXPR_OP_PRECEDENCE_NR_1
    def __init__(self): super().__init__(op_f=operator.mul, op_str='*')
#######################################################################################################################################
class Op_Plus(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_2
    P=sp.EXPR_OP_PRECEDENCE_NR_2
    def operation_add(self, arg1, arg2): 
        if isinstance(arg1, set) and isinstance(arg2, set): return arg1.union(arg2)
        else: return arg1 + arg2
    def __init__(self): super().__init__(op_f=self.operation_add, op_str='+')
class Op_Minus(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_2
    P=sp.EXPR_OP_PRECEDENCE_NR_2
    def operation_sub(self, arg1, arg2):
        if isinstance(arg1, set) and isinstance(arg2, set): 
            return arg1.difference(arg2)
        else: return arg1 - arg2
    def __init__(self): super().__init__(op_f=self.operation_sub, op_str='-')
#######################################################################################################################################
class Op_LShift(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_3
    P=sp.EXPR_OP_PRECEDENCE_NR_3
    def __init__(self): super().__init__(op_f=operator.lshift, op_str='<<')
class Op_RShift(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_3
    P=sp.EXPR_OP_PRECEDENCE_NR_3
    def __init__(self): super().__init__(op_f=operator.rshift, op_str='>>')
#######################################################################################################################################
class Op_Smaller(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_4
    P=sp.EXPR_OP_PRECEDENCE_NR_4
    def __init__(self): super().__init__(op_f=operator.lt, op_str='<')
class Op_Greater(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_4
    P=sp.EXPR_OP_PRECEDENCE_NR_4
    def __init__(self): super().__init__(op_f=operator.gt, op_str='>')
class Op_SmallerOrEqual(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_4
    P=sp.EXPR_OP_PRECEDENCE_NR_4
    def __init__(self): super().__init__(op_f=operator.le, op_str='<=')
class Op_GreaterOrEqual(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_4
    P=sp.EXPR_OP_PRECEDENCE_NR_4
    def __init__(self): super().__init__(op_f=operator.ge, op_str='>=')
#######################################################################################################################################
class Op_Equal(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_5
    P=sp.EXPR_OP_PRECEDENCE_NR_5
    def __init__(self): super().__init__(op_f=operator.eq, op_str='==')
class Op_NotEqual(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_5
    P=sp.EXPR_OP_PRECEDENCE_NR_5
    def __init__(self): super().__init__(op_f=operator.ne, op_str='!=')
#######################################################################################################################################
class Op_BAnd(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_6
    P=sp.EXPR_OP_PRECEDENCE_NR_6
    def __init__(self): super().__init__(op_f=operator.and_, op_str='&')
#######################################################################################################################################
class Op_BXor(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_7
    P=sp.EXPR_OP_PRECEDENCE_NR_7
    def __init__(self): super().__init__(op_f=operator.xor, op_str='^')
#######################################################################################################################################
class Op_BOr(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_8
    P=sp.EXPR_OP_PRECEDENCE_NR_8
    def __init__(self): super().__init__(op_f=operator.or_, op_str='|')
#######################################################################################################################################
class Op_And(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_9
    P=sp.EXPR_OP_PRECEDENCE_NR_9
    def operator_and(self, a, b): return a and b
    def __init__(self): super().__init__(op_f=self.operator_and, op_str='&&')
#######################################################################################################################################
class Op_Or(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_10
    P=sp.EXPR_OP_PRECEDENCE_NR_10
    def operator_or(self, a, b): return a or b
    def __init__(self): super().__init__(op_f=self.operator_or, op_str='||')
#######################################################################################################################################
class Op_Implication(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_11
    P=sp.EXPR_OP_PRECEDENCE_NR_11
    def operator_imp(self, a, b): return (not a) or b
    def __init__(self): super().__init__(op_f=self.operator_imp, op_str='->')
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class Op_Defined(Op_UnaryOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_12
    P=sp.EXPR_OP_PRECEDENCE_NR_12
    def operation_defined(self, arg1): 
        if not isinstance(arg1, SASS_Bits) and not arg1: return False
        return True
    def __init__(self): super().__init__(op_f=self.operation_defined, op_str='DEFINED')
    def __str__(self): return Op_UnaryOperator.__str__(self).strip() + ' '
#######################################################################################################################################
class Op_Scale(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_13
    P=sp.EXPR_OP_PRECEDENCE_NR_13
    def operation_scale(self, bits:SASS_Bits, val:SASS_Bits):
        if not isinstance(bits, SASS_Bits): raise Exception(sp.CONST__ERROR_UNEXPECTED) 
        if not isinstance(val, SASS_Bits): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return bits.scale(int(val))
    def __init__(self): super().__init__(op_f=self.operation_scale, op_str='SCALE')
class Op_Multiply(Op_DualOperator):
    A=sp.EXPR_OP_ASSOCIATIV_GROUP_13
    P=sp.EXPR_OP_PRECEDENCE_NR_13
    def operation_multiply(self, bits:typ.List[SASS_Bits], val:typ.List[SASS_Bits]):
        if not isinstance(bits, SASS_Bits): raise Exception(sp.CONST__ERROR_UNEXPECTED) 
        if not isinstance(val, SASS_Bits): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return bits.multiply(int(val))
    def __init__(self): super().__init__(op_f=self.operation_multiply, op_str='MULTIPLY')
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
if not 'EXPR_AT_OPS' in locals(): EXPR_AT_OPS = set({Op_AtAbs, Op_AtInvert, Op_AtNegate, Op_AtNot, Op_AtSign})
if not 'EXPR_AT_OPS_DIR' in locals(): EXPR_AT_OPS_DIR = {'negate': Op_AtNegate, 'not' : Op_AtNot, 'absolute': Op_AtAbs, 'sign': Op_AtSign,'invert': Op_AtInvert}
if not 'EXPR_ALIAS_CONVERT_FOLLOWUP' in locals(): EXPR_ALIAS_CONVERT_FOLLOWUP = set({Op_convertFloatType})
if not 'EXPR_1ARG_PACKAGE_DICT' in locals(): EXPR_1ARG_PACKAGE_DICT = {1:Op_LBrace, 2:set({Op_Alias}), 3:Op_RBrace}
if not 'EXPR_2ARG_PACKAGE_DICT' in locals(): EXPR_2ARG_PACKAGE_DICT = {1:Op_LBrace, 2:Op_Alias, 3:Op_Comma, 4:Op_Alias, 5:Op_RBrace}
if not 'EXPR_NARG_PACKAGE_DICT' in locals(): EXPR_NARG_PACKAGE_DICT = {1:Op_LBrace, 2:set({Op_Alias, Op_Int, Op_Register}).union(EXPR_AT_OPS), 3:Op_Comma, 4:Op_RBrace} # type: ignore
if not 'EXPR_ALIAS_SPECIALS_FOLLOWUP' in locals(): EXPR_ALIAS_SPECIALS_FOLLOWUP = set({Op_Scale, Op_Multiply})
if not 'EXPR_SPECIALS' in locals(): EXPR_SPECIALS = set({Op_Defined, Op_Scale, Op_Index, Op_Multiply})
if not 'EXPR_SPECIALS_DICT' in locals(): EXPR_SPECIALS_DICT = {'DEFINED' : Op_Defined, 'SCALE' : Op_Scale, 'INDEX' : Op_Index, 'MULTIPLY' : Op_Multiply}

if not 'OP_OPERAND' in locals(): 
    OP_OPERAND = tuple(i[1] for i in inspect.getmembers(sys.modules[__name__], inspect.isclass) if (i[1].__bases__[0] == Op_Operand and not i[1]==Op_AtOperand or i[1].__bases__[0] == Op_AtOperand))
    assert(all('P' in dir(i) and 'A' in dir(i) for i in OP_OPERAND))
if not 'OP_FUNCTION' in locals(): 
    OP_FUNCTION = tuple(i[1] for i in inspect.getmembers(sys.modules[__name__], inspect.isclass) if (i[1].__bases__[0] == Op_Function))
    assert(all('P' in dir(i) and 'A' in dir(i) for i in OP_FUNCTION))
if not 'OP_OPERATOR' in locals(): 
    OP_OPERATOR = tuple(i[1] for i in inspect.getmembers(sys.modules[__name__], inspect.isclass) if (i[1].__bases__[0] in (Op_DualOperator, Op_UnaryOperator)))
    assert(all('P' in dir(i) and 'A' in dir(i) for i in OP_OPERATOR))
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
class SASS_Op:
    CASH_OP = set({'=', '?', '&'})
    OP = set({'+', '-', '!', '~', '*', '/', '%', '>>', '<<', '<', '>', '<=', '>=', '==', '!=', '&', '^', '|', '&&', '||'})
    AN = set(itt.chain.from_iterable([(i.upper(), i) for i in {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}]))

    def __init__(self): 
        self.state = 0
        self.specials = {
            'ConstBankAddress0': Op_ConstBankAddress0,
            'ConstBankAddress2': Op_ConstBankAddress2,
            'IDENTICAL' : Op_Identical,
            'convertFloatType': Op_convertFloatType,
            'IsEven': Op_IsEven,
            'IsOdd': Op_IsOdd,
            'Reduce': Op_Reduce
        }

    def parse_next(self, c:str) -> list:
        if self.state == 0:
            if c == '(' : return  [[Op_LBrace()], '']
            elif c == '{' : return  [[Op_LCBrace()], '']
            elif c == '}' : return  [[Op_RCBrace()], '']
            elif c == ')' : return  [[Op_RBrace()], '']
            elif c == '+' : return  [[Op_Plus()], ''] 
            elif c == '-' :
                self.state = 14
                return [None, ''] 
            elif c == '!' :
                self.state = 1 
                return [None, ''] 
            elif c == '~' : return  [[Op_BNot()], ''] 
            elif c == '*' : return  [[Op_Mult()], ''] 
            elif c == '/' : return  [[Op_Div()], ''] 
            elif c == '%' :
                self.state = 15
                return [None, ''] 
            elif c == '<' :
                self.state = 3 
                return [None, ''] 
            elif c == '>' :
                self.state = 6 
                return [None, ''] 
            elif c == '&' :
                self.state = 9 
                return [None, ''] 
            elif c == '^' : return  [[Op_BXor()], '']
            elif c == '|' :
                self.state = 11 
                return [None, '']
            elif c == '=' :
                self.state = 13 
                return [None, '']
            elif c == '?' : return  [[Op_If()], ''] # ? ... => eval bool term
            elif c == ':' : return  [[Op_IfElse()], ''] # : ... => if not last bool term, eval this one
            # elif c == '@' : return  [[Op_At()], '']
            else: return [None, c]
        else:
            state = self.state
            self.state = 0
            if state == 1:
                if c == '=' : return  [[Op_NotEqual()], ''] # !=,
                elif c == '(' : return  [[Op_Not(), Op_LBrace()], '']
                else: return  [[Op_Not()], c] # !
            elif state == 3:
                if c == '<' : return  [[Op_LShift()], ''] # <<,
                elif c == '=' : return  [[Op_SmallerOrEqual()], ''] # <=,
                elif c == '(' : return  [[Op_Smaller(), Op_LBrace()], '']
                else: return  [[Op_Smaller()], c] # <
            elif state == 6:
                if c == '>' : return  [[Op_RShift()], ''] # >>,
                elif c == '=' : return  [[Op_GreaterOrEqual()], ''] # >=,
                elif c == '(' : return  [[Op_Greater(), Op_LBrace()], '']
                else: return  [[Op_Greater()], c] # >
            elif state == 9:
                if c == '&' : return  [[Op_And()], ''] # &&,
                elif c == '(' : return  [[Op_BAnd(), Op_LBrace()], '']
                else: return  [[Op_BAnd()], c] # &
            elif state == 11:
                if c == '|' : return  [[Op_Or()], ''] # ||,
                elif c == '(' : return  [[Op_BOr(), Op_LBrace()], '']
                else: return  [[Op_BOr()], c] # |
            elif state == 13:
                if c == '=' : return  [[Op_Equal()], ''] # ==
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
                if c == '(' : return  [[Op_Assign(), Op_LBrace()], '']
                else: return  [[Op_Assign()], c]
            elif state == 14:
                if c == '>' : return  [[Op_Implication()], '']
                elif c == '(' : return  [[Op_Minus(), Op_LBrace()], '']
                else: return  [[Op_Minus()], c]
            elif state == 15:
                # this one has to be more nuanced:
                #  this one '%SHADER_TYPE' means, we have a parameter SHADER_TYPE somewhere
                #  this one '%2' or '% 2' means the actual modulo operator
                if c == ' ': return  [[Op_Mod()], '']
                elif c == '(': return  [[Op_Mod(), Op_LBrace()], '']
                else:
                    # vv = su.try_convert(c, convert_hex=True, convert_bin=True)
                    if c in self.AN:
                        return [None, '%' + c]
                    else: return  [[Op_Mod()], c]
            
            raise Exception('Op parser trouble...')

    def split(self, t:str, tables, constants, registers, parameters, tables_inv):
        def sub_2(e:str, res:typ.List):
            val = su.try_convert(e, convert_bin=True, convert_hex=True)
            if isinstance(val, int):
                res.append(Op_Int(e.strip(), val))
            elif val in self.specials.keys():
                res.append(self.specials[val]()) # type: ignore
            elif val in tables.keys():
                res.append(Op_Table(val, tables[val], tables_inv[val])) # type: ignore
            elif val.startswith('$'): # type: ignore
                vv = val[1:] # type: ignore
                if vv in constants.keys():
                    res.append(Op_Constant(val, constants[vv])) # type: ignore
                else:
                    raise Exception("Expression evaluation: term {0} starting with '$' does not represent a constant".format(val))
            elif val.startswith('%'): # type: ignore
                vv = val[1:] # type: ignore
                if vv in parameters.keys():
                    res.append(Op_Parameter(vv, parameters[vv]))
                else:
                    raise Exception("Expression evaluation: term {0} starting with '%' does not represent a parameter".format(val))
            elif val.startswith('`'): # type: ignore
                acc,reg = val[1:].split('@') # type: ignore
                r = su.try_convert(reg)
                reg = r
                reg_val = None
                if not acc in registers.keys():
                    # Some registers are misspelled
                    if acc == 'Chkmode': 
                        print("ERROR: {0} not found in REGISTERS. Rename {0} to {1} in instructions.txt".format('Chkmode', 'ChkMode'))
                    elif acc == 'RedOP':
                        print("ERROR: {0} not found in REGISTERS. Rename {0} to {1} in instructions.txt".format('RedOP', 'RedOp'))
                    else: raise Exception("Expression evaluation: term {0} starting with '`' does not represent a register".format(val))
                elif not reg in registers[acc].keys():
                    # # Some register values are used but never defined. This seems to be an Nvidia bug. Since there is sometimes such a thing as
                    # # INVALIDMUFUOPCODE8 with enum value 8, we set this one to 9
                    # if reg == 'INVALIDMUFUOPCODE9':
                    #     reg_val = 9
                    #     print("WARNING: {0} not found in {1}. Set value to 9 because it seems like the most apparent fix".format(reg, acc))
                    raise Exception("Expression evaluation: term {0} starting with '`' does not represent a register".format(val))

                if not reg_val: reg_val = registers[acc][reg]
                res.append(Op_Register(acc, reg, reg_val)) # type: ignore
            elif val in constants.keys():
                # these are the properties that have constants that don't start with a ($ => giant mess again)
                res.append(Op_Constant(val, constants[val])) # type: ignore
            else:
                res.append(Op_Value(val)) # type: ignore

        def sub(ee:str, res:typ.List):
            ees = ee.split(',')
            rem = ''
            if len(ees) == 1:
                ees = [i for i in ees[0].split(' ',1) if i.strip()]
                if len(ees) == 2:
                    rem = ees[1]
                    ees = [ees[0]]
            for ind,e in enumerate(ees):
                if ind > 0 and ind < len(ees):
                    res.append(Op_Comma())
                if e.strip():
                    sub_2(e.strip(), res)
            return len(ee) - len(rem)

        ii = itt.islice(t, 0, None)
        res = []
        entry = []
        cc = 0
        stop = False
        counter = 0
        while True:
            if counter > 70000: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            c = next(ii, False)
            if stop: break
            if not c:
                # use this to get everything out of the parser that is still in there
                c = ' '
                stop = True
            else: cc += 1
            if c == '\n': continue

            obj, c = self.parse_next(c) # type: ignore
            if c:
                entry.append(c)
            else: 
                if entry: 
                    ee = "".join(entry).strip()
                    # ee = "".join([i for i in entry if i.strip()]).strip()
                    # if ee == 'Sb convertFloatType':
                    #     pass
                    passed = sub(ee, res)
                    entry = []
                    if passed != len(ee):
                        # if we don't parse the entire thing, for example, if we have something like this
                        # DEFINED TABLES_opex_0(batch_t,usched_info)
                        # where DEFINED is separate and then we have the table entry, we need to split the expression
                        # into two parts => return one with DEFINES and one with the rest
                        ll_obj = 0
                        if obj:
                            ll_obj = sum([len(str(o)) for o in obj])
                        cc = cc - len(ee) + passed - ll_obj
                        break
            if obj:
                res.extend(obj)
                obj = []
            counter += 1

        if entry: 
            ee = "".join(entry).strip()
            passed = sub(ee, res)
            if passed != len(ee):
                cc = cc - len(ee) + passed
        return cc, res
