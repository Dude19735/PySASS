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

class BInstr___fadd__RRR_RR___WAITX(BInstrBase):
    """This experiment is inteded to find out how many cycles exactly that FADD takes.

    It uses F32 floats.
    FADD has a fixed latency.
    """
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps, wait_cycles:int):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        PT = kk_sm.regs.Predicate__PT__7
        RZ = kk_sm.regs.Register__RZ__255
        R30 = kk_sm.regs.Register__R30__30
        R32 = kk_sm.regs.Register__R32__32
        R34 = kk_sm.regs.Register__R34__34
        R36 = kk_sm.regs.Register__R36__36
        R38 = kk_sm.regs.Register__R38__38

        ########################################################################################
        # Preparations: create some 32 bit floats in R32, 34, 36
        f32_32 = sc.SASS_KK__i2f__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R32, Sb=10, dst_format=32, usched_info_reg=wait15, wr=0x0, rd=0x7)
        f32_34 = sc.SASS_KK__i2f__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R34, Sb=15, dst_format=32, usched_info_reg=wait15, wr=0x0, rd=0x7)
        
        # Read the values into the operand registers
        self.add_pre_clock_prequels(f32_32.class_name, f32_32.enc_vals)
        self.add_pre_clock_prequels(f32_34.class_name, f32_34.enc_vals)

        ########################################################################################
        # Put a well defined number in the FFMA target register that is not 10*15+20
        move1 = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R30, imm_val=0, 
                                   usched_info_reg=wait15)
        self.add_post_clock_prequels(move1.class_name, move1.enc_vals)

        # This is the instruction that is benchmarked
        # Get the usched_info appropriate for the currently required wait_cycles
        main_usched_info = getattr(kk_sm.regs, 'USCHED_INFO__WAIT{0}_END_GROUP__{0}'.format(min(15, wait_cycles)))
        main = sc.SASS_KK__fadd__RRR_RR(kk_sm,
                           Pg_negate=False, Pg=PT, Rd=R30,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=R32,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=R34,
                           usched_info_reg=main_usched_info, 
                           req=0x0
                        )
        self.add_main(main.class_name, main.enc_vals)
        
        # Add NOP instructions that wait for a given number of cycles. NOTE that with WAIT1, the actual wait is 2 cycles.
        # This is consistent accross all Nvidia GPUs.
        # NOTE: this particular example takes about 4 cycles, so all of the following are for nothing. They serve as reference.
        # NOTE: in the i2f_f2i benchmark, they are not there for nothing.
        if wait_cycles > 15:
            nop = sc.SASS_KK__NOP(kk_sm, usched_info_reg=getattr(kk_sm.regs, 'USCHED_INFO__WAIT{0}_END_GROUP__{0}'.format(min(15, wait_cycles-15))))
            self.add_pre_clock_sequels(nop.class_name, nop.enc_vals)
        if wait_cycles > 30:
            nop = sc.SASS_KK__NOP(kk_sm, usched_info_reg=getattr(kk_sm.regs, 'USCHED_INFO__WAIT{0}_END_GROUP__{0}'.format(min(15, wait_cycles-30))))
            self.add_pre_clock_sequels(nop.class_name, nop.enc_vals)
        if wait_cycles > 45:
            nop = sc.SASS_KK__NOP(kk_sm, usched_info_reg=getattr(kk_sm.regs, 'USCHED_INFO__WAIT{0}_END_GROUP__{0}'.format(min(15, wait_cycles-45))))
            self.add_pre_clock_sequels(nop.class_name, nop.enc_vals)
        if wait_cycles > 60:
            nop = sc.SASS_KK__NOP(kk_sm, usched_info_reg=getattr(kk_sm.regs, 'USCHED_INFO__WAIT{0}_END_GROUP__{0}'.format(min(15, wait_cycles-60))))
            self.add_pre_clock_sequels(nop.class_name, nop.enc_vals)

        # This one writes the value in R30 into f_output_base_ureg.
        # NOTE: f_output_base_ureg is incremented by 1 unit in every loop cycle
        # NOTE: MUST be done before the next clock measurement, otherwise, we add 15 cycles to the execution time of the NOP operations above.
        # That is bad because for this one, we care about the result being correct rather than the exact cycle measure. We can always subtract
        # 15 from the final result, but if we like to determine if an instruction concludes, moving the result to global memory exactly after
        # a given number of cycles, is not optional!!
        result = sc.SASS_KK__mov__RR(kk_sm,
                                     Pg_negate=False, Pg=PT,
                                     Rd=R38,
                                     Rb_reuse=False, Rb=R30,
                                     usched_info_reg=wait15)
        self.add_pre_clock_sequels(result.class_name, result.enc_vals)

        ################################################################################################
        # Subtract 30 cycles from the measurement:
        # props.cs2r_clk_reg_2 is the register that contains the last clock measurement.
        # We do that after the last clock measurement but before everything else. This removes
        # the clocks needed for the sc.SASS_KK__STG_RaRZ operation right above this one and 
        # the sc.SASS_KK__MOVImm operation at the beginning of the measurement needed for resetting
        # the register R34 before each conversion. Both need 15 fixed cycles with a sum total of 30.
        sub = sc.SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                       target_reg=props.cs2r_clk_reg_main_2,
                                       negate_Ra=False, Ra=props.cs2r_clk_reg_main_2,
                                       src_imm=-30, # subtract 30
                                       negate_Rc=False, Rc=RZ,
                                       usched_info_reg=wait15)
        self.add_post_clock_sequels(sub.class_name, sub.enc_vals)

        move = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.f_output_base_ureg, offset=0x0, 
                                   source_reg=R38, 
                                   usched_info_reg=wait15,
                                   rd=0x7,
                                   size=32)
        self.add_post_clock_sequels(move.class_name, move.enc_vals)

class BenchmarkFADD(BenchmarkBase):
    def __init__(self, sm_nr:int, experiment_nr:int=0):
        super().__init__(sm_nr, 
                         name='fadd',
                         purpose="\n".join([
                            "This benchmark tests FADD and measures how many cycles are required.",
                            "",
                            "It takes 5 cycles for each FADD"]),
                        implicit_replace=True)

        expected_result:float = float(10+15)
        template = '{0}/template_projects/template_1k_120/benchmark_binaries/template_1k_120_{1}.bin'.format(self.t_location, self.sm_nr)

        if experiment_nr in (0,1):
            # Experiment 1: find out how long FFMA takes exactly
            ####################################################
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            offset = 1
            bInstrList = [BInstr___fadd__RRR_RR___WAITX(self.kk_sm, props, w) for w in range(offset, 15)]
            # bInstrList = [BInstr___ffma__RRR_RRR___WAITX(self.kk_sm, props, 15)]
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'fadd')
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, bInstrList)
            print()
            # We run the generated binaries 20 times in sequence because the results can vary
            cycle_results = []
            for e in range(2):
                print(tc.colored("Test results with no barrier [{0}]".format(e), 'green'))
                for wt,gb in enumerate(generated_bins):
                    results = Helpers.run_single_kernel_bin(exe_name=gb.format(exe_name_stem), exe_arg=str(props.loop_count))
                    if all(r== expected_result for r in results[0][Helpers.CONST__AfterKernel][Helpers.CONST__FOutput]):
                        print(40*' ', '\r', tc.colored("Wait time: {0}".format(wt+offset), 'red'))    
                        Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__FOutput)
                        cycle_results.extend(results[0][Helpers.CONST__AfterKernel][Helpers.CONST__ClkOut1])
                        break
                    elif any(r== expected_result for r in results[0][Helpers.CONST__AfterKernel][Helpers.CONST__FOutput]):
                        print(40*' ', '\r', tc.colored("Wait time: {0} => some are ok".format(wt+offset), 'red'), end = '\r')
                    else:
                        print(40*' ', '\r', tc.colored("Wait time: {0}".format(wt+offset), 'red'), end = '\r')
            print(tc.colored("All test results with no barrier [{0}]".format(e), 'cyan'))
            print(cycle_results)
        else: 
            print("Pick an existing experiment")
            raise Exception(sp.CONST__ERROR_ILLEGAL)

if __name__ == '__main__':
    b = BenchmarkFADD(75, experiment_nr=0)
    print("Finished")
    pass
