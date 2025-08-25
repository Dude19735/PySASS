from py_sass_ext import SASS_Bits
from . import _config as sp

class Instr_Reg:
    def __init__(self, index:int, value_name:str, alias:str, parent_name:str, value_d:int, sass_bits:SASS_Bits):
        if not isinstance(index, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(value_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(alias, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(value_d, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sass_bits, SASS_Bits): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        self.__index = index
        self.__value_name = value_name
        self.__alias = alias
        self.__parent_name = parent_name
        self.__value_d = value_d
        self.__sass_bits = sass_bits

    @property
    def index(self): return self.__index
    @property
    def value_name(self): return self.__value_name
    @property
    def alias(self): return self.__alias
    @property
    def parent_name(self): return self.__parent_name
    @property
    def value_d(self): return self.__value_d
    @property
    def sass_bits(self): return self.__sass_bits

    def __str__(self):
        return "i[{0}] - p[{1}].n[{2}]:a[{3}](v[{4}],sb[{5}])".format(self.__index, self.__parent_name, self.__value_name, self.__alias, self.__value_d, str(self.__sass_bits))
