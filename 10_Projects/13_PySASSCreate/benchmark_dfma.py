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
from kernel_w_loop_control_props import KernelWLoopControlProps
from binstr_base import BInstrBase
from kernel_w_loop import KernelWLoop
from benchmark_base import BenchmarkBase
import sass_create as sc

class BInstr_dfma_B(BInstrBase):
    """This one tests the DFMA instruction with barriers.

    The goal is to have a comparison for the version without barriers.

    This one uses usched_info == wait
    """
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        trans1 = kk_sm.regs.USCHED_INFO__trans1__17
        trans2 = kk_sm.regs.USCHED_INFO__trans2__18
        wait1 = kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1
        wait2 = kk_sm.regs.USCHED_INFO__WAIT2_END_GROUP__2
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        usched_info_wb = wait1

        PT = kk_sm.regs.Predicate__PT__7
        RZ = kk_sm.regs.Register__RZ__255
        R30 = kk_sm.regs.Register__R30__30
        R31 = kk_sm.regs.Register__R31__31
        R32 = kk_sm.regs.Register__R32__32
        R34 = kk_sm.regs.Register__R34__34
        R36 = kk_sm.regs.Register__R36__36
        R38 = kk_sm.regs.Register__R38__38

        ########################################################################################
        # Preparations: create some 32 bit floats in R32, 34, 36
        f64_32 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R32, Sb=10, usched_info_reg=wait1, wr=0x0, rd=0x7)
        f64_34 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R34, Sb=15, usched_info_reg=wait1, wr=0x0, rd=0x7)
        f64_36 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R36, Sb=20, usched_info_reg=wait1, wr=0x0, rd=0x7)
        
        # Read the values into the operand registers
        self.add_pre_clock_prequels(f64_32.class_name, f64_32.enc_vals)
        self.add_pre_clock_prequels(f64_34.class_name, f64_34.enc_vals)
        self.add_pre_clock_prequels(f64_36.class_name, f64_36.enc_vals)

        ################################################################################################
        # This is the main clock measuring area

        # Put a well defined number in the FFMA target register that is not 10*15+20
        move1 = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R30, imm_val=0, 
                                   usched_info_reg=wait15)
        self.add_post_clock_prequels(move1.class_name, move1.enc_vals)
        move2 = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R31, imm_val=0, 
                                   usched_info_reg=wait15)
        self.add_post_clock_prequels(move2.class_name, move2.enc_vals)

        # Convert R30 from float to integer (F64 to SU64) into R32
        # Main instruction goes between the two CS2R clock measurements
        main = sc.SASS_KK__dfma__RRR_RRR(kk_sm,
                                         Pg_negate=False, Pg=PT,
                                         Rd=R30,
                                         Ra_reuse=False, Ra_negate=False, Ra_absolute=False, Ra=R32,
                                         Rb_reuse=False, Rb_negate=False, Rb_absolute=False, Rb=R34,
                                         Rc_reuse=False, Rc_negate=False, Rc_absolute=False, Rc=R36,
                                         usched_info_reg=usched_info_wb, req=0, wr=0x0, rd=0x7
                                         )
        self.add_main(main.class_name, main.enc_vals)

        ################################################################################################
        # This one takes R30 and writes it into the ui_output array at the respective position of the
        # current iteration
        result = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.d_output_base_ureg, 
                                   offset=0x0, 
                                   source_reg=R30, 
                                   usched_info_reg=wait15,
                                   rd=0x7,
                                   size=64)
        self.add_post_clock_sequels(result.class_name, result.enc_vals)

        # Subtract 15 cycles from the measurement:
        # Inside the measured clock area, we move a default value to R30/R31 (64 bit value), which takes exactly 2*15 cycles. 
        # Subtract them from props.cs2r_clk_reg_2 because that is the second clock measuring register. With this, we effectively
        # ignore the two SASS_KK__MOVImm.
        sub = sc.SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                       target_reg=props.cs2r_clk_reg_main_2,
                                       negate_Ra=False, Ra=props.cs2r_clk_reg_main_2,
                                       src_imm=-30,
                                       negate_Rc=False, Rc=RZ,
                                       usched_info_reg=wait15)
        self.add_post_clock_sequels(sub.class_name, sub.enc_vals)

class BInstr_dfma_NB(BInstrBase):
    """This one tests DFMA without the barriers to check how long it really takes.
    """
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps, wait_cycles:int):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        wait1 = kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        usched_info_wb = wait1
        usched_info_15 = wait15
        PT = kk_sm.regs.Predicate__PT__7
        RZ = kk_sm.regs.Register__RZ__255
        R30 = kk_sm.regs.Register__R30__30
        R31 = kk_sm.regs.Register__R31__31
        R32 = kk_sm.regs.Register__R32__32
        R34 = kk_sm.regs.Register__R34__34
        R36 = kk_sm.regs.Register__R36__36
        R38 = kk_sm.regs.Register__R38__38
        R39 = kk_sm.regs.Register__R39__39

        ########################################################################################
        # Preparations: create some 32 bit floats in R32, 34, 36
        f64_32 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R32, Sb=10, usched_info_reg=wait1, wr=0x0, rd=0x7)
        f64_34 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R34, Sb=15, usched_info_reg=wait1, wr=0x0, rd=0x7)
        f64_36 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R36, Sb=20, usched_info_reg=wait1, wr=0x0, rd=0x7)
        
        # Read the values into the operand registers
        self.add_pre_clock_prequels(f64_32.class_name, f64_32.enc_vals)
        self.add_pre_clock_prequels(f64_34.class_name, f64_34.enc_vals)
        self.add_pre_clock_prequels(f64_36.class_name, f64_36.enc_vals)

        ################################################################################################
        # This is the main clock measuring area

        # Put a well defined number in the FFMA target register that is not 10*15+20
        # NOTE: these are 64 bit values, so they need both registers R30 and R31!!
        # NOTE: this works, because we set the value to 0. Otherwise the format would be wrong.
        move1 = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R30, imm_val=0, 
                                   usched_info_reg=wait15)
        self.add_post_clock_prequels(move1.class_name, move1.enc_vals)
        move2 = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R31, imm_val=0, 
                                   usched_info_reg=wait15)
        self.add_post_clock_prequels(move2.class_name, move2.enc_vals)

        # Convert R30 from float to integer (F64 to SU64) into R32
        # Main instruction goes between the two CS2R clock measurements
        main_usched_info = getattr(kk_sm.regs, 'USCHED_INFO__WAIT{0}_END_GROUP__{0}'.format(min(15, wait_cycles)))
        main = sc.SASS_KK__dfma__RRR_RRR(kk_sm,
                                         Pg_negate=False, Pg=PT,
                                         Rd=R30,
                                         Ra_reuse=False, Ra_negate=False, Ra_absolute=False, Ra=R32,
                                         Rb_reuse=False, Rb_negate=False, Rb_absolute=False, Rb=R34,
                                         Rc_reuse=False, Rc_negate=False, Rc_absolute=False, Rc=R36,
                                         usched_info_reg=main_usched_info, req=0, wr=0x7, rd=0x7
                                         )
        self.add_main(main.class_name, main.enc_vals)

        # Add NOP instructions that wait for a given number of cycles. NOTE that with WAIT1, the actual wait is 2 cycles.
        # This is consistent accross all Nvidia GPUs.
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

        # This one writes the value in R34 into the uint64_t output ui_output in the position of the current iteration.
        # NOTE: props.ui_output_base_ureg increments by 1 position in each loop iteration!
        # NOTE: MUST be done before the next clock measurement, otherwise, we add 15 cycles to the execution time of the NOP operations above.
        # That is bad because for this one, we care about the result being correct rather than the exact cycle measure. We can always subtract
        # 15 from the final result, but if we like to determine if an instruction concludes, moving the result to global memory exactly after
        # a given number of cycles, is not optional!!

        # We can use a regular STG here with rd=0x7:
        #  - the move will be initiated to the current d_output_base_ureg
        #  - then d_output_base_ureg will be incremented by 1 position
        #  - it doesn't matter if this move is not finished in time, we just wait 15 cycles and don't care for the rest
        result = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.d_output_base_ureg, 
                                   offset=0x0, 
                                   source_reg=R30, 
                                   usched_info_reg=wait15,
                                   rd=0x7,
                                   size=64)
        self.add_pre_clock_sequels(result.class_name, result.enc_vals)

        ################################################################################################
        # Subtract 30 cycles from the measurement:
        # props.cs2r_clk_reg_2 is the register that contains the last clock measurement.
        # We do that after the last clock measurement but before everything else. This removes
        # the clocks needed for the sc.SASS_KK__STG_RaRZ operation right above this one and 
        # the FOUR sc.SASS_KK__MOVImm operations at the beginning of the measurement needed for resetting
        # the register R30 before each conversion. All need 15 fixed cycles with a sum total of 60.
        sub = sc.SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                       target_reg=props.cs2r_clk_reg_main_2,
                                       negate_Ra=False, Ra=props.cs2r_clk_reg_main_2,
                                       src_imm=-45,
                                       negate_Rc=False, Rc=RZ,
                                       usched_info_reg=usched_info_15)
        self.add_post_clock_sequels(sub.class_name, sub.enc_vals)

class BInstr_dfma_Sc_B(BInstrBase):
    """This one tests the DFMA instruction with barriers.

    The goal is to have a comparison for the version without barriers.

    This one uses usched_info == wait
    """
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        trans1 = kk_sm.regs.USCHED_INFO__trans1__17
        trans2 = kk_sm.regs.USCHED_INFO__trans2__18
        wait1 = kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1
        wait2 = kk_sm.regs.USCHED_INFO__WAIT2_END_GROUP__2
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        usched_info_wb = wait1

        PT = kk_sm.regs.Predicate__PT__7
        RZ = kk_sm.regs.Register__RZ__255
        R30 = kk_sm.regs.Register__R30__30
        R31 = kk_sm.regs.Register__R31__31
        R32 = kk_sm.regs.Register__R32__32
        R34 = kk_sm.regs.Register__R34__34
        R36 = kk_sm.regs.Register__R36__36
        R38 = kk_sm.regs.Register__R38__38

        ########################################################################################
        # Preparations: create some 32 bit floats in R32, 34, 36
        f64_32 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R32, Sb=10, usched_info_reg=wait1, wr=0x0, rd=0x7)
        f64_34 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=PT, Rd=R34, Sb=15, usched_info_reg=wait1, wr=0x0, rd=0x7)
        
        # Read the values into the operand registers
        self.add_pre_clock_prequels(f64_32.class_name, f64_32.enc_vals)
        self.add_pre_clock_prequels(f64_34.class_name, f64_34.enc_vals)

        ################################################################################################
        # This is the main clock measuring area

        # Put a well defined number in the FFMA target register that is not 10*15+20
        move1 = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R30, imm_val=0, 
                                   usched_info_reg=wait15)
        self.add_post_clock_prequels(move1.class_name, move1.enc_vals)
        move2 = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R31, imm_val=0, 
                                   usched_info_reg=wait15)
        self.add_post_clock_prequels(move2.class_name, move2.enc_vals)

        # Convert R30 from float to integer (F64 to SU64) into R32
        # Main instruction goes between the two CS2R clock measurements
        main = sc.SASS_KK__dfma__RRC_RRC(kk_sm,
                                         Pg_negate=False, Pg=PT,
                                         Rd=R30,
                                         Ra_reuse=False, Ra_negate=False, Ra_absolute=False, Ra=R32,
                                         Rb_reuse=False, Rb_negate=False, Rb_absolute=False, Rb=R34,
                                         Sc_negate=False, Sc_absolute=False, Sc_bank=0, Sc_addr=0x160,
                                         usched_info_reg=usched_info_wb, req=0, wr=0x0, rd=0x7
                                         )
        self.add_main(main.class_name, main.enc_vals)

        ################################################################################################
        # This one takes R30 and writes it into the ui_output array at the respective position of the
        # current iteration
        result = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.d_output_base_ureg, 
                                   offset=0x0, 
                                   source_reg=R30, 
                                   usched_info_reg=wait15,
                                   rd=0x7,
                                   size=64)
        self.add_post_clock_sequels(result.class_name, result.enc_vals)

        # Subtract 15 cycles from the measurement:
        # Inside the measured clock area, we move a default value to R30/R31 (64 bit value), which takes exactly 2*15 cycles. 
        # Subtract them from props.cs2r_clk_reg_2 because that is the second clock measuring register. With this, we effectively
        # ignore the two SASS_KK__MOVImm.
        sub = sc.SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                       target_reg=props.cs2r_clk_reg_main_2,
                                       negate_Ra=False, Ra=props.cs2r_clk_reg_main_2,
                                       src_imm=-30,
                                       negate_Rc=False, Rc=RZ,
                                       usched_info_reg=wait15)
        self.add_post_clock_sequels(sub.class_name, sub.enc_vals)

class Benchmark_DFMA(BenchmarkBase):
    def __init__(self, sm_nr:int, experiment_nr:int=0):
        super().__init__(sm_nr, 
                         name='dfma',
                         purpose="\n".join([
                            "These benchmarks test DFMA with and without barrier.",
                            "* With barrier the whole thing takes 55 cycles",
                            "* Without barrier the instruction needs 48 cycles",
                            "",
                            "Compared to FFMA, this is almost excessive..."]),
                        implicit_replace=True)

        expected_result:float = float(10*15 + 20)
        template = '{0}/template_projects/template_1k_120/benchmark_binaries/template_1k_120_{1}.bin'.format(self.t_location, self.sm_nr)

        if experiment_nr in (0,1):
            print(tc.colored("Experiment 1", 'green', attrs=['bold', 'underline']))
            # Experiment 1: use usched_info = wait
            ######################################
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            bInstr = BInstr_dfma_B(self.kk_sm, props)
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'dfma__RRR_RRR_B')
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, [bInstr])
            results = Helpers.run_single_kernel_bin(exe_name=generated_bins[0], exe_arg=str(props.loop_count))
            print()
            print("Test results with barrier and wait")
            Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__DOutput)

        if experiment_nr in (0,2):
            print(tc.colored("Experiment 2", 'green', attrs=['bold', 'underline']))
            # Experiment 2: use no barriers at all with a known result
            ##########################################################
            #  - if the benchmarked instruction doesn't get enough cycles, the result will be wrong (77 in this case)
            #  - after the benchmarked instruction concludes, the result will be correct (30 in this case)
            #  - by creating kernels that wait between 25 and 50 cycles after an instruction has been dispatched
            #    and checking the result after each kernel ran individually, we can check how long an instruction requires
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            offset = 20
            bInstrList = [BInstr_dfma_NB(self.kk_sm, props, wait_cycles=w) for w in range(offset, 71)]
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'dfma__RRR_RRR_NB')
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 2, exe_name_stem, props, KernelWLoop, bInstrList)
            print()
            # We run the generated binaries 20 times in sequence because the results can vary
            cycle_results = []
            for e in range(1):
                print(tc.colored("Test results with no barrier [{0}]".format(e), 'green'))
                for wt,gb in enumerate(generated_bins):
                    results = Helpers.run_single_kernel_bin(exe_name=gb.format(exe_name_stem), exe_arg=str(props.loop_count))
                    if all(r== expected_result for r in results[0][Helpers.CONST__AfterKernel][Helpers.CONST__DOutput]):
                        print(40*' ', '\r', tc.colored("Wait time: {0}".format(wt+offset), 'red'))    
                        Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__DOutput)
                        cycle_results.extend(results[0][Helpers.CONST__AfterKernel][Helpers.CONST__ClkOut1])
                        break
                    elif any(r== expected_result for r in results[0][Helpers.CONST__AfterKernel][Helpers.CONST__DOutput]):
                        print(40*' ', '\r', tc.colored("Wait time: {0} => some are ok".format(wt+offset), 'red'), end = '\r')
                    else:
                        print(40*' ', '\r', tc.colored("Wait time: {0}".format(wt+offset), 'red'), end = '\r')
            print(tc.colored("All test results with no barrier [{0}]".format(e), 'cyan'))
            print(cycle_results)
        
        if experiment_nr in (0,3):
            print(tc.colored("Experiment 3", 'green', attrs=['bold', 'underline']))
            # Experiment 1: use usched_info = wait
            ######################################
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            bInstr = BInstr_dfma_Sc_B(self.kk_sm, props)
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'dfma')
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, [bInstr])
            results = Helpers.run_single_kernel_bin(exe_name=generated_bins[0], exe_arg=str(props.loop_count))
            print()
            print("Test results with barrier and wait")
            Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__DOutput)


if __name__ == '__main__':
    b = Benchmark_DFMA(75, experiment_nr=0)
    print("Finished")
    pass
