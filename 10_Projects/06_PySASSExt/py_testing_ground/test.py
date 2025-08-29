import pickle
from py_sass_ext import TT_Alias
from py_sass_ext import TT_AtOp, TT_OpAtAbs, TT_OpAtInvert, TT_OpAtNegate, TT_OpAtNot, TT_OpAtSign
from py_sass_ext import TT_OpCashAnd, TT_OpCashAssign, TT_OpCashQuestion
from py_sass_ext import TT_Default, TT_NoDefault 
from py_sass_ext import TT_FuncArg, TT_Func
from py_sass_ext import TT_Reg
from py_sass_ext import TT_ICode
from py_sass_ext import TT_Ext
from py_sass_ext import TT_Param
from py_sass_ext import TT_CashComponent, TT_OpCashQuestion, TT_OpCashAnd, TT_OpCashAssign
from py_sass_ext import TT_Cash
from py_sass_ext import CashVector

import time

a = TT_Alias("hello")

x = pickle.dumps(a)
print("===")
aa = pickle.loads(x)
print(a, aa)

op1 = TT_OpAtAbs("Pg")
op1x = pickle.dumps(op1)
op1r = pickle.loads(op1x)
print(op1, op1r)
c1 = TT_OpCashQuestion()
c2 = TT_OpCashAnd()
c3 = TT_OpCashAssign()

c1x = pickle.dumps(c1)
c1r = pickle.loads(c1x)
print(c1, c1r)

# Op_Register: value == integer
# Op_Int: value = integer
# Op_Parameter: value = integer
# Op_Constant: value = integer|string
# Op_NotEnc: value = integer (fixed in call to super())
# Op_Alias: value = TT_Reg, TT_Func
# Op_Opcode: value = TT_ICode
# Op_Set: value = Python set of strings

# print(c1, c2, c3)

# print(pickle.loads(pickle.dumps(c1)))
# print(pickle.loads(pickle.dumps(c2)))
# print(pickle.loads(pickle.dumps(c3)))

default = TT_Default(0, False, {'R0': {0}, 'R1':{1}, 'R2':{2}, 'R3':{3}, 'R4':{4}, 'R5':{5}, 'R6':{6}, 'R7':{7}})
dx = pickle.dumps(default)
dr = pickle.loads(dx)
print(default, dr)

no_default = TT_NoDefault()
dx = pickle.dumps(no_default)
dr = pickle.loads(dx)
print(no_default, dr)

func_arg = TT_FuncArg("func_arg", False, False, 5, False, 0, False, 0)
dx = pickle.dumps(func_arg)
dr = pickle.loads(dx)
print(func_arg, dr)

func = TT_Func("hello world", "SImm", {"SImm", "UImm"}, func_arg, False, False, a)
dx = pickle.dumps(func)
dr = pickle.loads(dx)
print(func, dr)

reg = TT_Reg("class_name", "reg_name", default, {}, TT_Alias("alias"))
dx = pickle.dumps(reg)
dr = pickle.loads(dx)
print(reg, dr)

# default2 = TT_Default(0, False, {'R0': {0}})
# reg2 = TT_Reg("class_nameXXX", "reg_nameXXX", default2, {}, TT_Alias("aliasXXX"))
# regp2 = pickle.dumps(reg2)
# regl2 = pickle.loads(regp2)

# tt = TT_Test(0, a, reg, [TT_OpAtInvert("p1"), TT_OpAtNegate("p2")])

# print(tt)
# ttp = pickle.dumps(tt)
# print(pickle.loads(ttp))

icode = TT_ICode("1010", [12, 13, 14, 15], [1,0,1,0])
dx = pickle.dumps(icode)
dr = pickle.loads(dx)
print(icode, dr)

ext = TT_Ext("test_class", a, reg, default, False)
dx = pickle.dumps(ext)
dr = pickle.loads(dx)
print(ext, dr)

param = TT_Param("test_class", a, [op1], reg, [ext], False, False)
dx = pickle.dumps(param)
dr = pickle.loads(dx)
print(param, dr)

cash = TT_Cash("bla_class", [c1, c2, param, c3], False)
dx = pickle.dumps(cash)
dr = pickle.loads(dx)
print(cash, dr)

pass
