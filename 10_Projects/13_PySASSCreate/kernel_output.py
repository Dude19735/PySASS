import sys
import os
import typing
from py_cubin import SM_CuBin_File
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
import _config as sp

class KernelOutput:
    def __init__(self, file:SM_CuBin_File, benchmark_ind:int, prequel_inds:typing.List[int], sequel_inds:typing.List[int]):
        if not isinstance(file, SM_CuBin_File): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(benchmark_ind, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(prequel_inds, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, int) for i in prequel_inds): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sequel_inds, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, int) for i in sequel_inds): raise Exception(sp.CONST__ERROR_ILLEGAL)

        self.file = file
        self.benchmark_ind = benchmark_ind
        self.prequel_inds = prequel_inds
        self.sequel_inds = sequel_inds
