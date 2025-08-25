from py_sass_ext import SASS_Bits
from py_cubin import Instr_CuBin_Repr
import _config as sp

class SASS_Create_Utils:
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
        return {k: SASS_Create_Utils.sass_bits_from_str(str(v)) for k,v in instr.all_enc_vals[u_index].items()}
    
    @staticmethod
    def enc_vals_to_init(instr:Instr_CuBin_Repr, u_index:int):
        return ",\n".join("'" + k + "': SASS_Create_Utils.sass_bits_from_str('" + str(v) + "')" for k,v in instr.all_enc_vals[u_index].items())

    @staticmethod
    def enc_vals_dict_to_init(enc_vals:dict):
        return ",\n".join("'" + k + "': SASS_Create_Utils.sass_bits_from_str('" + str(v) + "')" for k,v in enc_vals.items())

if __name__ == '__main__':
    SASS_Create_Utils.sass_bits_from_str(str(SASS_Bits.from_int(-1)))
