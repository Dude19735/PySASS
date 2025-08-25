from __future__ import annotations
import requests
import typing
import struct
from py_sass_ext import BitVector
from py_cubin import SM_CuBin_Lib
from . import _config as sp

class SM_CuBin_Service_Lib:
    @staticmethod
    def get_instr_bits(sm_nr:int, class_name:str, ankers:dict, exceptions:dict, url:str) -> typing.Tuple[typing.List[BitVector, BitVector], dict]:
        if not isinstance(sm_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ankers, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(exceptions, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(url, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        data = b'\x64' + struct.pack('!i',sm_nr)
        class_name_b = class_name.encode('utf-8')
        data += struct.pack('!i',len(class_name_b)) + class_name_b
        ankers_b = SM_CuBin_Lib.args_to_bytes(ankers)
        data += struct.pack('!i',len(ankers_b)) + ankers_b
        exceptions_b = SM_CuBin_Lib.args_to_bytes(exceptions)
        data += struct.pack('!i',len(exceptions_b)) + exceptions_b
        response = requests.post(url, data=data)
        
        split = response.content.find(b':')
        bits = response.content[:split]
        enc_vals_b = response.content[(split+1):]

        # TODO: there may be a bug somewhere with bytes_to_args for the current instruction class...
        # print("Before: ", enc_vals_b)
        enc_vals:dict = {k:next(iter(v)) for k,v in SM_CuBin_Lib.bytes_to_args(enc_vals_b).items()}
        # print("After: ", enc_vals)
        w1 = BitVector(bits[:64].decode('utf-8'))
        w0 = BitVector(bits[-64:].decode('utf-8'))
        return [w1,w0], enc_vals