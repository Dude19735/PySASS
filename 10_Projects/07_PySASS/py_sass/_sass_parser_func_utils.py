from py_sass_ext import SASS_Range

class SASS_Parser_Func_Utils:
    """
    This one contains utility methods for all the SASS_Parser_Func types.
    """
    FUNC_SIGNED_BIT = 1
    FUNC_UNSIGNED_BIT = 0
    
    @staticmethod
    def get_mock_addr_domain(bit_len, max_bit_len, signed) -> SASS_Range:
        if signed:
            max_val = (2**(bit_len-1))-1
        else:
            max_val = (2**bit_len)-1
        return SASS_Range(0, max_val, bit_len, signed=signed, bit_mask=0)

    @staticmethod
    def get_func_domain_signed(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len) -> SASS_Range:
        if is_address:
            return SASS_Parser_Func_Utils.get_mock_addr_domain(bit_len=bit_len, max_bit_len=max_bit_len, signed=1)
        else:
            if has_max_val:
                max_v = max_val
                min_v = -max_val
            else:
                max_v = (2**(bit_len-1))-1
                min_v = -(2**(bit_len-1))
            return SASS_Range(min_v, max_v, bit_len, signed=1, bit_mask=0)
        
    @staticmethod
    def get_func_domain_unsigned(is_address, bit_len, has_default, default_val, has_max_val, max_val, max_bit_len) -> SASS_Range:
        if is_address:
            return SASS_Parser_Func_Utils.get_mock_addr_domain(bit_len=bit_len, max_bit_len=max_bit_len, signed=0)
        else:
            if not has_max_val: 
                max_val = 2**(bit_len)-1
            return SASS_Range(0, max_val, bit_len, signed=0, bit_mask=0)

    @staticmethod
    def max_addr_bit_len(bit_len, signed) -> int:
        res:int
        if signed: res = bit_len - 3
        else: res = bit_len - 2
        if res <= 0: raise Exception("Invalid bit length")
        return res
