import os
import sys
import re
import typing
import subprocess
from py_sass import SM_SASS
from py_sass import SASS_Class
from py_sass import SASS_Class_Props
from py_sass_ext import SASS_Bits
from py_cubin import SM_CuBin_File
from py_sass import TT_List, TT_Param, TT_Reg, TT_Instruction, TT_Func
from py_cubin import Instr_CuBin_Repr, Instr_CuBin_Param_RF, Instr_CuBin_Param_Attr, Instr_CuBin_Param_L
from py_sass import SM_Cu_Props
from py_sass import SM_Cu_Details
from py_sass import SASS_Class, SASS_Class_Props
from py_cubin import SM_CuBin_Regs
from py_cubin import SM_CuBin_File
from py_cubin import SM_CuBin_Utils
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from sass_create_utils import SASS_Create_Utils
from kk_sm import KK_SM
import _config as sp
from helpers import Helpers
from benchmark_base import BenchmarkBase
from kernel_w_loop_control_props import KernelWLoopControlProps
from kernel_w_loop import KernelWLoop
from binstr_base import BInstrBase
import sass_create as sc

class BInstr(BInstrBase):

    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps, kernel_index:int):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        PT = kk_sm.regs.Predicate__PT__7
        RZ = kk_sm.regs.Register__RZ__255
        R30 = kk_sm.regs.Register__R30__30
        R31 = kk_sm.regs.Register__R31__31
        R32 = kk_sm.regs.Register__R32__32
        R34 = kk_sm.regs.Register__R34__34
        R36 = kk_sm.regs.Register__R36__36
        R38 = kk_sm.regs.Register__R38__38

        result = sc.SASS_KK__MOVImm(kk_sm, exec_pred_inv=False, exec_pred=PT, target_reg=R31, imm_val=0, usched_info_reg=wait15)
        self.add_post_clock_sequels(result.class_name, result.enc_vals)

        main = sc.SASS_KK__MOVImm(kk_sm, exec_pred_inv=False, exec_pred=PT, target_reg=R30, imm_val=kernel_index, usched_info_reg=wait15)
        self.add_main(main.class_name, main.enc_vals)

        move = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.control_base_ureg, offset=0x20, 
                                   source_reg=R30, 
                                   usched_info_reg=wait15,
                                   rd=0x7,
                                   size=64)
        self.add_pre_clock_sequels(move.class_name, move.enc_vals)

class Benchmark(BenchmarkBase):
    def __init__(self, sm_nr:int):
        super().__init__(sm_nr, 
                         name='kernel_sequence',
                         purpose="This one aims at testing the sequence of kernels in memory relative to their decoded indices",
                        implicit_replace=True)

        print("Load template")
        template = "{0}/{1}".format(self.t_location, "template_projects/template_3600k/benchmark_binaries/template_3600k_{0}.bin".format(self.sm_nr))
        props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)

        instr = []
        enc_vals_str = []
        for kernel_index in range(props.nr_kernels):
            print("[{0}/{1}] Create kernels...".format(kernel_index, props.nr_kernels), end='')
            ii = BInstr(self.kk_sm, props, kernel_index)
            enc_vals_str.append(BenchmarkBase.normatized_class_and_enc_vals_to_str(kernel_index, ii.class_name, ii.enc_vals))
            instr.append(ii)
            print("Ok")

        print("Create modified binaries...")
        exe_name_stem = '{0}/{1}'.format(self.modified_location, self.name)
        generated_bins = BenchmarkBase.create_modified_binaries_per_k_instructions(self.kk_sm, 16, exe_name_stem, props, KernelWLoop, instr, enc_vals_str)
        print("Ok")

        print("Run all binaries...")
        results = Helpers.run_bin_loop(1, 2, generated_bins, True)
        Helpers.process_output_multi_kernel_w_loop_results(results, 100)
        
        print("[Finished]")

if __name__ == '__main__':
    shortcut = True

    if shortcut:
        # Shortcut
        # generated_bins = ['/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/nogit__non_mem_86/non_mem.0.bin']
        generated_bins = [
            '/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/variable_latency_benchmark/benchmark_results/nogit__kernel_sequence_86/kernel_sequence.0.0.bin',
        ]
        results = Helpers.run_bin_loop(1, 2, generated_bins, True)
        with open("log.ansi", 'w') as f:
            Helpers.process_output_multi_kernel_w_loop_results(results, 100, file_obj=f)
    else:
        # Generator
        Benchmark(86)
