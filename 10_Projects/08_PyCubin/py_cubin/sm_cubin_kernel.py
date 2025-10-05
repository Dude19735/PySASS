from __future__ import annotations
import typing
import termcolor as tc
import itertools as itt
from py_sass import SM_SASS
from py_sass_ext import BitVector
from py_sass_ext import SASS_Bits
from . import _config as sp
from ._instr_cubin import Instr_CuBin, CubinDecodeException
from ._instr_cubin_repr import Instr_CuBin_Repr
from ._instr_cubin_repr_lib import Instr_CuBin_Repr_Lib
from ._instr_cubin_db_proxy import Db_Kernel_Proxy, Db_KernelMisc_Proxy, Db_KernelGraph_Proxy
from .sm_cubin_kernel_ht import SM_CuBin_Kernel_Head, SM_CuBin_Kernel_Tail
from .sm_cubin_lib import SM_CuBin_Lib
from .sm_cubin_elf import SM_Cubin_Elf
# from .sm_cubin_graph import Kernel_Graph

"""
This file contains abstraction class for one single Cuda kernel. NOTE that a Cuda binary
may contain multiple kernels.

Single instructions are refered to as 'universes' because each instruction can contain multiple
decoded possibilities.
"""

class SM_CuBin_Kernel:
    ARCH_NOP_BYTES = {
        50: b'\xe0\x07\x00\xfc\x00\x80\x1f\x00\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P', 
        52: b'\xe0\x07\x00\xfc\x00\x80\x1f\x00\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P', 
        53: b'\xe0\x07\x00\xfc\x00\x80\x1f\x00\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P', 
        60: b'\xe0\x07\x00\xfc\x00\x80\x1f\x00\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P', 
        61: b'\xe0\x07\x00\xfc\x00\x80\x1f\x00\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P', 
        62: b'\xe0\x07\x00\xfc\x00\x80\x1f\x00\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P\x00\x0f\x07\x00\x00\x00\xb0P', 
        70: b'\x18y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x0f\x00', 
        72: b'\x18y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x0f\x00', 
        75: b'\x18y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x0f\x00', 
        80: b'\x18y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x0f\x00', 
        86: b'\x18y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x0f\x00', 
        90: b'\x18y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x0f\x00', 
        100: b'\x18y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x0f\x00', 
        120: b'\x18y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x0f\x00'
    }

    ARCH_NOP_INSTR_BITS = {
        50: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
        52: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
        53: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
        60: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
        61: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
        62: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
        70: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0], 
        72: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0], 
        75: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0], 
        80: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0], 
        86: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0], 
        90: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0], 
        100: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0], 
        120: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0]
    }

    ARCH_NOP_WORDS = {
        50: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], 
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        52: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], 
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        53: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        60: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        61: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        62: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        70: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        72: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        75: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        80: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        86: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        90: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        100: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ], 
        120: [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ]
        }

    def __init__(self, id:str, arch:int, sass:SM_SASS, kk:dict, 
                 bin_offset_hex:str, kernel_offset_hex:str, 
                 head_only=False, wiped=False, verbose=False):
        
        if head_only: raise Exception(sp.CONST__ERROR_NOT_SUPPORTED)

        self.__id = id
        self.__arch = arch
        self.__head_only = head_only
        self.__kernel_offset_hex = kernel_offset_hex
        self.__bin_offset_hex = bin_offset_hex
        self.__used_regs = dict()
        self.__used_alias = dict()

        if not (wiped or kk['instr_bits']):
            # If we don't provide any instruction bits we need this one set to False.
            # This is for use in the decoder to lazily decode binaries with a giant amount of kernels in them
            self.__decoded = False
            # If we don't decode a kernel right away, we still store it's bits, so that we can decode it at a later time
            if not 'kernel_bits' in kk: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            self.__kernel_bits = kk['kernel_bits']
        else:
            # This is the regular case, if we want to fully decode a provided kernel
            self.__decoded = True
            self.__kernel_bits = None

        self.__kernel_name = kk['kernel_name']
        self.__offset = kk['offset']

        if wiped and not ('nop_us' in kk): 
            # If we went trough all the trouble of making kernels whipable very quickly, the least we can do is provide propper input XD.
            # nop_u is a finished instruction universe for the current SM's NOP instruction.
            raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        if wiped:
            # This is specifically to create a wiped kernel from a template
            self.__universes = kk['nop_us']
        elif self.__decoded:
            # print("[DEBUG...] Regular decoding", self.__kernel_name)
            # This is the regular case where we pass a kernel with arbitrary instructions and we want to decode it
            kernel_universe = SM_CuBin_Kernel.create_universe_heads(id, sass, kk, bin_offset_hex, kernel_offset_hex, verbose=verbose)
            self.__universes = kernel_universe['universes']

            used_regs_loc, used_alias_loc = self.compute_bodies(sass, verbose)
            self.__used_regs = SM_CuBin_Kernel.__contract_used_regs(used_regs_loc, dict())
            self.__used_alias = SM_CuBin_Kernel.__contract_used_regs(used_alias_loc, dict())
        else:
            # This must be the non-decoded state but with kernel_bits passed => check
            if not self.__kernel_bits: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            self.__universes = []

        # NOTE: also finish augmented_decode for this one to work!!!!
        if self.__decoded:
            self.__kernel_graph = None
        else:
            self.__kernel_graph = None

    @property
    def id(self) -> str: return self.__id
    @property
    def universes(self) -> list: return self.__universes
    @property
    def kernel_name(self) -> str: return self.__kernel_name
    @property
    def offset(self) -> str: return self.__offset
    @property
    def arch(self) -> int: return self.__arch
    @property
    def head_only(self) -> bool: return self.__head_only
    @property
    def kernel_offset_hex(self) -> str: return self.__kernel_offset_hex
    @property
    def bin_offset_hex(self) -> str: return self.__bin_offset_hex
    @property
    def used_regs(self) -> typing.Dict[str, SASS_Bits]: return self.__used_regs
    @property
    def used_alias(self) -> typing.Dict[str, set]: return self.__used_alias
    @property
    def decoded(self) -> bool: return self.__decoded
    @property
    def kernel_graph(self): 
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        return self.__kernel_graph

    def __len__(self) -> int:
        return len(self.universes)
    def __getitem__(self, index:int):
        return self.universes[index]
    def __copy__(self) -> SM_CuBin_Kernel:
        new = self.__new__(self.__class__)
        new.__id = self.__id
        new.__universes = list(self.__universes)
        new.__kernel_name = self.__kernel_name
        new.__offset = self.__offset
        new.__arch = self.__arch
        new.__decoded = self.__decoded
        new.__head_only = self.__head_only
        new.__kernel_offset_hex = self.__kernel_offset_hex
        new.__bin_offset_hex = self.__bin_offset_hex
        new.__used_regs = dict(self.__used_regs)
        new.__used_alias = dict(self.__used_alias)
        new.__kernel_bits = self.__kernel_bits
        return new
    
    def deferred_decoding(self, sass:SM_SASS):
        # print("[DEBUG...] Deferred decoding", self.__kernel_name)
        # If we have nothing to do: just stop
        if self.__decoded: 
            # print("[DEBUG...] Was already decoded:", self.__kernel_name, "Skip decoding again...")
            return
        
        # Invariant: if self.__decoded = False then self.__kernel_bits must exist
        if self.__kernel_bits is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        kk = SM_CuBin_Kernel.selective_decode_kernel(sass, self.__kernel_bits, self.__kernel_name, self.__kernel_offset_hex)
        kernel_universe = SM_CuBin_Kernel.create_universe_heads(id, sass, kk, self.__bin_offset_hex, self.__kernel_offset_hex, verbose=False)
        self.__universes = kernel_universe['universes']

        used_regs_loc, used_alias_loc = self.compute_bodies(sass, verbose=False)
        self.__used_regs = SM_CuBin_Kernel.__contract_used_regs(used_regs_loc, dict())
        self.__used_alias = SM_CuBin_Kernel.__contract_used_regs(used_alias_loc, dict())

        self.__decoded = True
        self.__kernel_bits = None
    
    def replace_instruction_by_bits(self, sass:SM_SASS, index:int, instr_bits:BitVector) -> Instr_CuBin_Repr:
        u = Instr_CuBin_Repr.create_from_bits(sass, index, self.bin_offset_hex, self.kernel_offset_hex, instr_bits)
        old = self.universes[index]
        self.universes[index] = u
        return old
    
    def replace_instruction_by_enc_vals(self, sass:SM_SASS, index:int, class_name:str, enc_vals:dict) -> Instr_CuBin_Repr:
        u = Instr_CuBin_Repr.create_from_enc_vals(sass, index, self.bin_offset_hex, self.kernel_offset_hex, class_name, enc_vals)
        old = self.universes[index]
        self.universes[index] = u
        return old

    # def replace_instruction_by_enc_vals_set_rdwr(self, sass:SM_SASS, index:int, class_name:str, enc_vals:dict, rd:SASS_Bits, wr:SASS_Bits) -> Instr_CuBin_Repr:
    #     u = Instr_CuBin_Repr.create_from_enc_vals_set_rdwr(sass, index, self.bin_offset_hex, self.kernel_offset_hex, class_name, enc_vals, rd, wr)
    #     old = self.universes[index]
    #     self.universes[index] = u
    #     return old

    def replace_instruction_by_universe(self, sass:SM_SASS, index:int, new_universe:Instr_CuBin_Repr) -> Instr_CuBin_Repr:
        if new_universe.instr_index == index:
            # if the new universe was created/contains the correct instruction index, use the universe directly...
            old = self.universes[index]
            self.universes[index] = new_universe
        else:
            # ...otherwise use the bits and create a new instruction universe with the correct index
            old = self.replace_instruction_by_bits(sass, index, new_universe.instr_bits)
        return old

    # def get_body_html(self, sass:SM_SASS, i_id:int):
    #     u:Instr_CuBin_Repr = self.universes[i_id]
    #     used_regs_loc = u.compute_instr_universes(sass, int(self.__kernel_offset_hex)+i_id)
    #     self.__used_regs = SM_CuBin_Kernel.__contract_used_regs(used_regs_loc, self.__used_regs)
    #     return u.to_html_body(sass, full=False)

    def compute_bodies(self, sass:SM_SASS, verbose=False):    
        return SM_CuBin_Kernel.compute_kernel_bodies(sass, self.__kernel_name, self.__universes, verbose=verbose)

    # def add_graph(self, kernel_graph:Kernel_Graph):
    #     if not isinstance(kernel_graph, Kernel_Graph): raise Exception(sp.CONST__ERROR_ILLEGAL)
    #     self.__kernel_graph = kernel_graph

    def to_db(self, sass:SM_SASS):
        instr_list = []
        instr_map = dict()
        u:Instr_CuBin_Repr
        for ind,u in enumerate(self.__universes):
            instr_list.append(u.to_db(sass))
            instr_map[u.instr_index] = instr_list[-1]
        
        # kernel_proxy:Db_KernelGraph_Proxy = None
        # if self.__kernel_graph is not None:
        #     print(tc.colored("Missing graph-to-db!!!"))
        #     # kernel_proxy = self.__kernel_graph.to_db(instr_map)

        # Invert things for nicer mapping
        # reg_map = {rr : dict(itt.chain.from_iterable([[(vv,k) for vv in v] for k,v in sass.sm.details.REGISTERS_DICT[rr].items()])) for rr in self.used_regs.keys()}
        # used_regs = {rr: {reg_map[rr][int(i)] for i in self.used_regs[rr]} for rr in self.used_regs.keys()}

        misc = [
            Db_KernelMisc_Proxy.create(Db_KernelMisc_Proxy.Type_KernelOffset, 0, self.__kernel_offset_hex, 'Offset of the kernel instructions relative to the start of the kernel'),
            Db_KernelMisc_Proxy.create(Db_KernelMisc_Proxy.Type_BinOffset, 1, self.__bin_offset_hex, 'Offset from the start of the binary to the start of the Cuda bits'),
            Db_KernelMisc_Proxy.create(Db_KernelMisc_Proxy.Type_WebId, 2, self.id, 'Some randomized, unique id'),
            Db_KernelMisc_Proxy.create(Db_KernelMisc_Proxy.Type_UsedAlias, 3, str(self.used_alias), 'All aliases used in the entire kernel'),
            Db_KernelMisc_Proxy.create(Db_KernelMisc_Proxy.Type_UsedRegs, 4, ", ".join(str(i) for i in itt.chain.from_iterable(self.used_regs.values())), 'All register values used in the entire kernel'),
            Db_KernelMisc_Proxy.create(Db_KernelMisc_Proxy.Type_UsedRegNames, 5, ", ".join(str(i) for i in self.used_regs.keys()), 'All register names used in the entire kernel'),
            Db_KernelMisc_Proxy.create(Db_KernelMisc_Proxy.Type_KernelDecoded, 6, '1' if self.__decoded else '0', 'This one is true if the kernel was decoded. It can be not decoded if the binary has a lot of kernels and the user chooses "single decode" mode. "single decode" mode is the default.'),
        ]

        return Db_Kernel_Proxy.create(0, self.kernel_name, instr_list, misc, '') #, [kernel_proxy], '')

    @staticmethod
    def __contract_used_regs(used_regs_loc:typing.List[dict], used_regs:dict) -> dict:
        for ur in used_regs_loc:
            for k,v in ur.items():
                if k in used_regs: used_regs[k] = used_regs[k].union(v)
                else: used_regs[k] = v
        return used_regs

    @staticmethod
    def create_universe_heads(id:str, sass:SM_SASS, kk:dict, bin_offset_hex:str, kernel_offset_hex:str, verbose=False):
        # kernel_res.append({'kernel_name': kernel_names[k], 'offset': kernel_offsets_hex[k], 'instr_bits':instr_bits, 'class_names':class_names})
        universes = []
        for instr_ind, (class_name, instr_bits) in enumerate(zip(kk['class_names'], kk['instr_bits'])):
            if verbose and instr_ind % 1000 == 0: print(100*" ", "\r", "  [H {0}: {1}/{2}]".format(kk['kernel_name'], instr_ind, len(kk['class_names'])), end='\r')
            u = Instr_CuBin_Repr("{0}-{1}".format(id, instr_ind), sass, instr_ind, bin_offset_hex, kernel_offset_hex, instr_bits, class_name)
            universes.append(u)
        if verbose: print(100*" ", "\r", "  [H {0}: {1}/{2}]".format(kk['kernel_name'], len(kk['class_names']), len(kk['class_names'])))
        return {'kernel_name': kk['kernel_name'], 'offset': kk['offset'], 'universes': universes}

    @staticmethod
    def compute_kernel_bodies(sass:SM_SASS, kernel_name:str, universes:list, verbose=False):
        u:Instr_CuBin_Repr
        # if verbose: print(100*" ", "\r", "  [{0}: {1}/{2}]".format(kk['kernel_name'], 0, len(kk['universes'])), end='\r')
        used_regs = []
        used_alias = []
        for ind,u in enumerate(universes): 
            if verbose and ind%1000 == 0: print(100*" ", "\r", "  [B {0}: {1}/{2}]".format(kernel_name, ind, len(universes)), end='\r')
            ur, ua = u.compute_instr_universes(sass)
            used_regs.append(ur)
            used_alias.append(ua)
        if verbose: print(100*" ", "\r", "  [B {0}: {1}/{2}]".format(kernel_name, ind+1, len(universes)))
        return used_regs, used_alias

    @staticmethod
    def selective_decode_kernel(sass:SM_SASS, kernel_bits:list, kernel_name:str, kernel_offset_hex:str) -> dict:
        instr_bits = Instr_CuBin.cubin_to_instr_bits(kernel_bits, sass)
        class_names = Instr_CuBin.instr_bits_to_class(instr_bits, sass, [])
        kernel_res = {'kernel_name': kernel_name, 'offset': kernel_offset_hex, 'instr_bits':instr_bits, 'class_names':class_names}
        return kernel_res

    @staticmethod
    def decode_kernel(sass:SM_SASS, kernel_bits:list, kernel_names:list, kernel_offsets_hex:list, target_classes:list=[]) -> typing.List[dict]:
        if not len(kernel_bits) == len(kernel_names): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        kernel_res = []
        for k,k_bits in enumerate(kernel_bits):
            instr_bits = Instr_CuBin.cubin_to_instr_bits(k_bits, sass)
            try:
                class_names = Instr_CuBin.instr_bits_to_class(instr_bits, sass, target_classes)
            except CubinDecodeException as error:
                raise CubinDecodeException(error.args)
            kernel_res.append({'kernel_name': kernel_names[k], 'offset': kernel_offsets_hex[k], 'instr_bits':instr_bits, 'class_names':class_names})
        return kernel_res

    @staticmethod
    def init_kernel_kk(sass:SM_SASS, 
                       arch:int, 
                       bin_start_offset_hex:str, 
                       bin_end_offset_hex:str, 
                       bits:bytes, 
                       head_only=False, 
                       wipe=False, 
                       selected_kernel='',
                       verbose=False) -> typing.Tuple[SM_Cubin_Elf, typing.List[str], typing.List[SM_CuBin_Kernel]]:
        """This one initializes the list of all kernels contained in a Cuda binary, passed as tripple
        * bin_start_offset_hex: this is the offset at which the Cuda part starts in the binary
        * bin_end_offset_hex: this is the offset at which the Cuda part ends in the binary
        * bits: these are all the bytes that contain all the Cuda instructions for ALL kernels in the binary

        :param sass: this is the regular py_sass.SM_SASS object, that must represent the architecture passed as [arch]
        :type sass: SM_SASS
        :param arch: this is the architecture number (50 to 120)
        :type arch: int
        :param bin_start_offset_hex: this is the offset at which the Cuda part starts in the binary
        :type bin_start_offset_hex: str
        :param bin_end_offset_hex: this is the offset at which the Cuda part ends in the binary
        :type bin_end_offset_hex: str
        :param bits: these are all the bytes that contain all the Cuda instructions for ALL kernels in the binary
        :type bits: bytes
        :param head_only: [DEPRECATED] this used to be a way to just decode the instruction class name of an instruction instead of all the universes too
        :type head_only: bool, optional
        :param wipe: set this to [True] to wipe all instructions in the [bits] whith fitting NOP instructions without decoding. NOTE: this is much faster than wipe=False
        :type wipe: bool, optional
        :param selected_kernel: set this to ['.'] to decode just the first kernel, set it to ['[existing-kernel-name]'] to decode that given kernel name, provided, it exists, defaults to '' to decode all kernels
        :type selected_kernel: str, optional
        :param verbose: provides some additional output with prints, NOTE: primarily a debug functionality and probably not complete, defaults to False
        :type verbose: bool, optional
        :return: SM_Cubin_Elf, all unique decoding IDs, all decoded kernels as SM_CuBin_Kernel list
        :rtype: typing.Tuple[SM_Cubin_Elf, typing.List[str], typing.List[SM_CuBin_Kernel]]
        """
        elf = SM_Cubin_Elf(arch, bits)        
        kernel_data = [(n, k.words(), k.offset_hex) for n,k in elf.kernel.items()]
        # kernel_data = sorted(kernel_data, key=lambda x: x[0])
        
        # The kernel inside of the binary are ordered in reverse to how they are defined in the .cu file.
        # i[2] is the offset of an individual kernel inside the binary.
        # Reversed sorting by i[2] will yield the desired outcome.
        # NOTE: if it doesn't on some architecture, this is the line to check.
        kernel_data = sorted(kernel_data, key=lambda x:x[2], reverse=True)
        kernel_names = [x[0] for x in kernel_data]
        kernel_bits = SM_CuBin_Lib.hex_words_to_bin(sass, [x[1] for x in kernel_data])
        kernel_offsets_hex = [x[2] for x in kernel_data]

        if wipe:
            # Create one for all
            nop_instr_bits:BitVector = BitVector(SM_CuBin_Kernel.ARCH_NOP_INSTR_BITS[sass.sm_nr])
            nop_class_name = Instr_CuBin.get_nop(sass)
            nop_u = Instr_CuBin_Repr.create_from_bits(sass, 0, bin_offset_hex=bin_start_offset_hex, kernel_offset_hex='0x0', bv=nop_instr_bits, class_name=nop_class_name)

            rep = [BitVector(i) for i in SM_CuBin_Kernel.ARCH_NOP_WORDS[arch]]
            len_rep = len(rep)
            kernel_res = []
            for bits, kernel_name, kernel_offset_hex in zip(kernel_bits, kernel_names, kernel_offsets_hex):
                len_bits = len(bits)
                if not (len_bits % len_rep == 0): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                for i in range(0, len_bits, len_rep):
                    bits[i:(i+len_rep)] = rep

                if sass.sm_nr < 70:
                    instr_count = int((len(bits)/4)*3)
                elif sass.sm_nr <= 120:
                    instr_count = int(len(bits)/2)
                else: raise Exception(sp.CONST__ERROR_NOT_SUPPORTED)

                kernel_res.append({
                    'kernel_name': kernel_name, 
                    'offset': kernel_offset_hex, 
                    'nop_us':[nop_u.new_with_instr_index(sass, i, bin_start_offset_hex, kernel_offset_hex) for i in range(0, instr_count)], 
                    'class_names':nop_class_name
                })

            all_kernel = []
            all_id = []
            for kk,koh in zip(kernel_res, kernel_offsets_hex):
                all_kernel.append(SM_CuBin_Kernel(id=Instr_CuBin_Repr_Lib.create_id('i'), 
                                                     arch=arch, sass=sass, kk=kk, 
                                                     bin_offset_hex=bin_start_offset_hex, kernel_offset_hex=koh, 
                                                     wiped=True, verbose=verbose))
                all_id.append(all_kernel[-1].id)
            return elf, all_id, all_kernel
        
        else:
            try:
                if selected_kernel == '.':
                    # only the first one
                    kernel_res = SM_CuBin_Kernel.selective_decode_kernel(sass, kernel_bits[0], kernel_names[0], kernel_offsets_hex[0])
                    # make this one be the same length as kernel_res by filling in dummies that SM_CuBin_Kernel will understand
                    kernel_res = [kernel_res] + [{'kernel_name': kernel_names[k], 'offset': kernel_offsets_hex[k], 'instr_bits':[], 'kernel_bits':kernel_bits[k], 'class_names':[]} for k in range(1, len(kernel_names))]
                elif selected_kernel == '':
                    # all of them
                    kernel_res = SM_CuBin_Kernel.decode_kernel(sass, kernel_bits, kernel_names, kernel_offsets_hex)
                elif selected_kernel in kernel_names:
                    # decode only the selected kernel
                    index = kernel_names.index(selected_kernel)
                    kernel_res = SM_CuBin_Kernel.selective_decode_kernel(sass, kernel_bits[index], kernel_names[index], kernel_offsets_hex[index])
                    kernel_res = \
                        [{'kernel_name': kernel_names[k], 'offset': kernel_offsets_hex[k], 'instr_bits':[], 'kernel_bits':kernel_bits[k], 'class_names':[]} for k in range(0, index)]\
                        + [kernel_res] \
                        + [{'kernel_name': kernel_names[k], 'offset': kernel_offsets_hex[k], 'instr_bits':[], 'kernel_bits':kernel_bits[k], 'class_names':[]} for k in range(index+1, len(kernel_names))]
                else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            except CubinDecodeException as error:
                raise CubinDecodeException(error.args)

            all_kernel = []
            all_id = []
            for kk,koh in zip(kernel_res, kernel_offsets_hex):
                if verbose: print(100*" ", "\r", "  [{0}: {1}/{2}]".format(kk['kernel_name'], 0, len(kk['class_names'])), end='\r')
                all_kernel.append(SM_CuBin_Kernel(Instr_CuBin_Repr_Lib.create_id('i'), arch, sass, kk, bin_start_offset_hex, koh, head_only, verbose))
                all_id.append(all_kernel[-1].id)
            if verbose: print(100*" ", "\r", "  [{0}: {1}/{2}]".format(kk['kernel_name'], len(all_kernel), len(kk['class_names'])))
            # return SM_CuBin_Kernel_Head(sass, head_words, bits, end_of_config, begin_of_sass), all_id, all_kernel, SM_CuBin_Kernel_Tail(sass, tail_words, bits)
            return elf, all_id, all_kernel
    
    # @staticmethod
    # def init_kernel(sass:SM_SASS, arch:int, bin_start_offset_hex:str, bin_end_offset_hex:str, bits:bytes, head_only=False, verbose=False) -> typing.Dict[str, SM_CuBin_Kernel]:
    #     elf, all_id, all_kernel = SM_CuBin_Kernel.init_kernel_kk(sass, arch, bin_start_offset_hex, bin_end_offset_hex, bits, head_only, verbose)
    #     return {id:kk for id,kk in zip(all_id, all_kernel)}
