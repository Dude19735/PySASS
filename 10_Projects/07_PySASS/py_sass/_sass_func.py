from . import _config as sp
from ._sass_parser_func_utils import SASS_Parser_Func_Utils
from py_sass_ext import SASS_Bits
from py_sass_ext import BitVector

class SASS_Func:
    def __init__(self, func:dict):
        for param in func.keys():
            setattr(self, param, func[param])

class Imm:
    __SIGNED:int
    __BIT_LEN:int
    def __init__(self, signed:bool, bit_len:int):
        if not isinstance(bit_len, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(signed, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if bit_len == 0: raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__SIGNED = signed
        self.__BIT_LEN = bit_len
    def __call__(self, input:SASS_Bits):
        if not isinstance(input, SASS_Bits): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return input.cast(self.__BIT_LEN)
    def __str__(self): return type(self).__name__
    def v_str(self): return type(self).__name__
    def get_bit_len(self): return self.__BIT_LEN
    def max_addr_bit_len(self, bit_len) -> int: return SASS_Parser_Func_Utils.max_addr_bit_len(bit_len, signed=True)
    def sign(self): return SASS_Bits.from_int(SASS_Parser_Func_Utils.FUNC_SIGNED_BIT if self.__SIGNED else SASS_Parser_Func_Utils.FUNC_UNSIGNED_BIT, bit_len=1, signed=0)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): raise Exception(sp.CONST__ERROR_ILLEGAL)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

class RSImm(Imm):
    def __init__(self, bit_len): super().__init__(signed=True, bit_len=bit_len)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0: raise Exception("bit_len required")
        return SASS_Parser_Func_Utils.get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=True)
class UImm(Imm):
    def __init__(self, bit_len): super().__init__(signed=False, bit_len=bit_len)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0: raise Exception("bit_len required")
        if max_bit_len > 0 and bit_len > max_bit_len: bit_len = max_bit_len
        return SASS_Parser_Func_Utils.get_func_domain_unsigned(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=False)
class F16Imm(Imm):
    def __init__(self): super().__init__(signed=True, bit_len=16)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0 or bit_len > self.get_bit_len(): bit_len = self.get_bit_len()
        if bit_len > max_bit_len: bit_len = max_bit_len
        return SASS_Parser_Func_Utils.get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=True)
class SImm(Imm):
    def __init__(self, bit_len): super().__init__(signed=True, bit_len=bit_len)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0: raise Exception("bit_len required")
        return SASS_Parser_Func_Utils.get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=True)
class SSImm(Imm):
    def __init__(self, bit_len): super().__init__(signed=True, bit_len=bit_len)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0: raise Exception("bit_len required")
        return SASS_Parser_Func_Utils.get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=True)
class F64Imm(Imm):
    def __init__(self): super().__init__(signed=True, bit_len=64)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0 or bit_len > self.get_bit_len(): bit_len = self.get_bit_len()
        if bit_len > max_bit_len: bit_len = max_bit_len
        return SASS_Parser_Func_Utils.get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=True)
class F32Imm(Imm):
    def __init__(self): super().__init__(signed=True, bit_len=32)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0 or bit_len > self.get_bit_len(): bit_len = self.get_bit_len()
        if bit_len > max_bit_len: bit_len = max_bit_len
        return SASS_Parser_Func_Utils.get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=True)
class BITSET(Imm):
    def __init__(self, bit_len): super().__init__(signed=False, bit_len=bit_len)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0:raise Exception("bit_len required")
        return SASS_Parser_Func_Utils.get_func_domain_unsigned(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=False)
class E8M7Imm(Imm):
    def __init__(self): super().__init__(signed=True, bit_len=16)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0 or bit_len > self.get_bit_len(): bit_len = self.get_bit_len()
        return SASS_Parser_Func_Utils.get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=True)
class E6M9Imm(Imm):
    def __init__(self): super().__init__(signed=True, bit_len=16)
    def get_domain(self, is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len): # type: ignore
        if bit_len == 0 or bit_len > self.get_bit_len(): bit_len = self.get_bit_len()
        return SASS_Parser_Func_Utils.get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len)
    def sass_from_bits(self, bits:BitVector) -> SASS_Bits:
        return SASS_Bits(bits, bit_len=self.get_bit_len(), signed=True)

CONVERT_FUNC = {
    F16Imm.__name__: F16Imm, 
    F32Imm.__name__: F32Imm, 
    F64Imm.__name__: F64Imm, 
    E6M9Imm.__name__: E6M9Imm, 
    E8M7Imm.__name__: E8M7Imm
}
FIXED_BIT_FUNC = {
    F16Imm.__name__: F16Imm, 
    F32Imm.__name__: F32Imm, 
    F64Imm.__name__: F64Imm, 
    E6M9Imm.__name__: E6M9Imm, 
    E8M7Imm.__name__: E8M7Imm
}
FUNC = {
    RSImm.__name__ : RSImm,
    UImm.__name__ : UImm,
    F16Imm.__name__ : F16Imm,
    SImm.__name__ : SImm,
    SSImm.__name__ : SSImm,
    F64Imm.__name__ : F64Imm,
    F32Imm.__name__ : F32Imm,
    BITSET.__name__ : BITSET,
    E8M7Imm.__name__ : E8M7Imm, 
    E6M9Imm.__name__ : E6M9Imm
}