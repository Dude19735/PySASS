import os
import sys
import typing
import _config as sp
from py_cubin import SM_CuBin_File
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
from binstr_base import BInstrBase
from control_props import ControlProps
from kernel_output import KernelOutput

class KernelBase:
    @staticmethod
    def get_kernel_control_props(kk_sm:KK_SM, 
                                 benchmark_class_name:str, 
                                 benchmark_barrier_type:str, 
                                 benchmark_barrier_num_to_set:int,
                                 empty_instr:bool, 
                                 json_file:str|None,
                                 kernel_arg:int) -> ControlProps:
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        
    @staticmethod
    def create(kk_sm:KK_SM, props:ControlProps, binstr:BInstrBase) -> KernelOutput:
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)