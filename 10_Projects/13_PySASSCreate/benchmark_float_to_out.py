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
from kernel_w_loop_control_props import KernelWLoopControlProps
from binstr_base import BInstrBase
from kernel_w_loop import KernelWLoop
from benchmark_base import BenchmarkBase
import sass_create as sc

class BInstr___Float32ToOut(BInstrBase):
    """This experiment is inteded to find out how many cycles exactly that FFMA takes.

    It uses F32 floats.
    FFMA has a fixed latency.
    """
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        PT = kk_sm.regs.Predicate__PT__7
        R30 = kk_sm.regs.Register__R30__30

        ########################################################################################
        # Preparations: create some 32 bit floats in R32, 34, 36
        f32_32 = sc.SASS_KK__i2f__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R30, Sb=10, dst_format=32, usched_info_reg=wait15, wr=0x0, rd=0x7)
        
        # Read the values into the operand registers
        self.add_pre_clock_prequels(f32_32.class_name, f32_32.enc_vals)

        ########################################################################################
        # This is the instruction that is benchmarked
        # Get the usched_info appropriate for the currently required wait_cycles
        main = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.f_output_base_ureg, offset=0x0,
                                   source_reg=R30, 
                                   usched_info_reg=wait15,
                                   rd=0x0,
                                   size=32)
        self.add_main(main.class_name, main.enc_vals)

class BenchmarkFloatToOut(BenchmarkBase):
    def __init__(self, sm_nr:int, experiment_nr:int=0):
        super().__init__(sm_nr, 
                         name='f2o',
                         purpose="\n".join([
                            "This benchmark tests how to write a 32 bit float to a 32 bit output. It's not really a benchmark.",
                            "",
                            "NOTE how SASS_KK__STG_RaRZ requires the correct size=32 for a 32 bit float. This size must",
                            "match the uniform register loaded using ULDC that can also take a size=32. ",
                            "",
                            "If the sizes don't match, there will be some sort of Cuda error to do with memory accesses",
                            "* missaligned memory",
                            "* invalid memory access",
                            "*  ..."]),
                        implicit_replace=True)

        expected_result:float = 10.0
        template = '{0}/binaries/template_{1}.bin'.format(self.t_location, self.sm_nr)

        if experiment_nr in (0,1):
            # Experiment 1: find out how long FFMA takes exactly
            ####################################################
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            bInstrList = [BInstr___Float32ToOut(self.kk_sm, props)]
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'Float32ToOut')
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, bInstrList)
            results = Helpers.run_single_kernel_bin(exe_name=generated_bins[0].format(exe_name_stem), exe_arg=str(props.loop_count))
            print()
            Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__FOutput)
        else: 
            print("Pick an existing experiment")
            raise Exception(sp.CONST__ERROR_ILLEGAL)

if __name__ == '__main__':
    b = BenchmarkFloatToOut(86, experiment_nr=0)
    print("Finished")
    pass
