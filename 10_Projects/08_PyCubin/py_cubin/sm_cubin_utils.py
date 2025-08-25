from py_sass_ext import SASS_Bits
from py_cubin import Instr_CuBin_Repr

class SM_CuBin_Utils:
    @staticmethod
    def overwrite_helper(val:tuple|int|bool, val_str:str, enc_vals:dict):
        if isinstance(val, tuple): v = val[-1]
        elif isinstance(val, int): v = val
        elif isinstance(val, bool): v = int(val)
        else: raise Exception("Illegal val type [{0}]".format(type(val)))
        v_old:SASS_Bits = enc_vals[val_str]
        v_new:SASS_Bits = SASS_Bits.from_int(v, bit_len=v_old.bit_len, signed=v_old.signed)
        enc_vals[val_str] = v_new
        return enc_vals

    @staticmethod
    def sass_bits_from_str(s:str):
        lead, bit_len_str = s.split(':')
        bit_len = int(bit_len_str[:-1])
        if lead.endswith('S'): signed = 1
        else: signed = 0
        val = int(lead[:-1])
        return SASS_Bits.from_int(val=val, bit_len=bit_len, signed=signed)
    
    @staticmethod
    def enc_vals_to_dict(instr:Instr_CuBin_Repr, u_index:int):
        return {k: SM_CuBin_Utils.sass_bits_from_str(str(v)) for k,v in instr.all_enc_vals[u_index].items()}
    
    @staticmethod
    def enc_vals_to_init(instr:Instr_CuBin_Repr, u_index:int):
        return ",\n".join("'" + k + "': SASS_Create_Utils.sass_bits_from_str('" + str(v) + "')" for k,v in instr.all_enc_vals[u_index].items())

    @staticmethod
    def enc_vals_dict_to_init(enc_vals:dict, joiner=',\n'):
        return joiner.join("'" + k + "': SASS_Create_Utils.sass_bits_from_str('" + str(v) + "')" for k,v in enc_vals.items())

if __name__ == '__main__':
    SM_CuBin_Utils.sass_bits_from_str(str(SASS_Bits.from_int(-1)))
