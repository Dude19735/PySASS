import pickle
from py_sass_ext import TT_Alias
from py_sass_ext import TT_AtOp, TT_OpAtAbs, TT_OpAtInvert, TT_OpAtNegate, TT_OpAtNot, TT_OpAtSign
from py_sass_ext import TT_OpCashAnd, TT_OpCashAssign, TT_OpCashQuestion
from py_sass_ext import TT_Default, TT_NoDefault 
from py_sass_ext import TT_FuncArg, TT_Func
from py_sass_ext import TT_Reg
from py_sass_ext import TT_ICode
from py_sass_ext import CPP

import time

print()
print()
t1 = time.time()
a = []
for i in range(0,100000):
    a.append(i)
print("Regular Python loop: ", time.time() - t1, "len(a): ", len(a))

t1 = time.time()
b = [i for i in range(0, 100000)]
print("Python list comprehension (assignment): ", time.time() - t1, "len(b): ",  len(b))

t1 = time.time()
d = []
[d.append(i) for i in range(0, 100000)]
print("Python list comprehension (implicit): ", time.time() - t1, "len(d): ", len(d))

t1 = time.time()
c = []
CPP.create(c, 0, 100000)
print("CPP extension: ", time.time() - t1, "len(c): ", len(c), "c==a: ", c==a, "c==b: ", c==b, "c==d: ", c==d)

t1 = time.time()
e = []
CPP.create(e, 0, 100000)
print("CPP extension: ", time.time() - t1, "len(e): ", len(e))

t1 = time.time()
f = [float(i) for i in range(0, 100000)]
print("Python list comprehension (assignment, float): ", time.time() - t1, "len(f): ",  len(f), "f==e", f==e)