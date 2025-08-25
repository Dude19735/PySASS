from __future__ import annotations
import sys
import os
import typing
import datetime
import termcolor as tc
from multiprocessing import Process
from py_cubin import SM_CuBin_File
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
import _config as sp
from helpers import Helpers
from kernel_output import KernelOutput
from control_props import ControlProps
from binstr_base import BInstrBase
from kernel_w_loop import KernelWLoop
from benchmark_base import BenchmarkBase

class BInstrRandom(BInstrBase):
    def __init__(self, kk_sm:KK_SM, props:ControlProps):
        ww, enc_vals = kk_sm.get_enc_vals(self.class_name, {}, {})
        super().__init__(kk_sm, props, enc_vals)

    @staticmethod
    def create(kk_sm:KK_SM, num:int, props:ControlProps) -> typing.List[BInstrRandom]:
        results = []
        for i in range(num):
            results.append(BInstrRandom(kk_sm, props))
        return results

class BenchmarkEmpty(BenchmarkBase):
    def __init__(self, sm_nr:int):
        super().__init__(sm_nr)

        # Create 100 test benchmarking kernels
        tt = datetime.datetime.now()
        modified_location = '{0}/{1}test_{2}_{3}'.format(self.t_location, self.nogit_prefix, sm_nr, tt.strftime("%d-%m-%Y_%H-%M-%S"))
        os.mkdir(modified_location)
        Helpers.create_readme(
            location=modified_location,
            purpose="These benchmarks are to test the generation of the kernel and also to make sure that we subtract the correct clock measurement. The output cycle count should be 0 for all the measurements.",
            results="Holds up to expectation"
        )
        props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=True, loop_count=10)
        bInstrList = BInstrRandom.create(self.kk_sm, 100, props)
        exe_name_stem = '{0}/{1}'.format(modified_location, 'test')
        BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 16, exe_name_stem, props, KernelWLoop, bInstrList)

if __name__ == '__main__':
    b = BenchmarkEmpty(86)
    print("Finished")
    pass
