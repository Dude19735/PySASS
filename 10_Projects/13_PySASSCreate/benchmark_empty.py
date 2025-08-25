from __future__ import annotations
import sys
import os
import typing
import datetime
import shutil
import termcolor as tc
from multiprocessing import Process
from py_cubin import SM_CuBin_File
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
import _config as sp
from helpers import Helpers
from kernel_output import KernelOutput
from binstr_base import BInstrBase
from kernel_w_loop import KernelWLoop
from kernel_w_loop_control_props import KernelWLoopControlProps
from benchmark_base import BenchmarkBase

class BInstrEmpty(BInstrBase):
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps):
        if not props.empty_instr: raise Exception(sp.CONST__ERROR_ILLEGAL)
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

    @staticmethod
    def create(kk_sm:KK_SM, num:int, props:KernelWLoopControlProps) -> typing.List[BInstrEmpty]:
        results = []
        for i in range(num):
            results.append(BInstrEmpty(kk_sm, props))
        return results

class BenchmarkEmpty(BenchmarkBase):
    def __init__(self, sm_nr:int):
        super().__init__(sm_nr, 
                         name='empty',
                         purpose="These benchmarks are to test the generation of the kernel and also to make sure that we subtract the correct clock measurement. The output cycle count should be 0 for all the measurements.",
                        implicit_replace=True)

        template = '{0}/template_projects/template_1k/benchmark_binaries/template_1k_{1}.bin'.format(self.t_location, self.sm_nr)
        props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=True, loop_count=10, template=template)
        bInstrList = BInstrEmpty.create(self.kk_sm, 100, props)
        exe_name_stem = '{0}/{1}'.format(self.modified_location, 'test')
        BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 16, exe_name_stem, props, KernelWLoop, bInstrList)

if __name__ == '__main__':
    b = BenchmarkEmpty(86)
    print("Finished")
    pass
