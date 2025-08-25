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

class BInstr_i2f_f2i_w(BInstrBase):
    """This one tests integer to float and back conversion using the respective instruction barriers.

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
        usched_info_15 = wait15
        PT = kk_sm.regs.Predicate__PT__7
        R30 = kk_sm.regs.Register__R30__30
        R32 = kk_sm.regs.Register__R32__32
        R34 = kk_sm.regs.Register__R34__34

        ################################################################################################
        # Put a well defined number in here...
        move1 = sc.SASS_KK__MOVImm(kk_sm,
                                   exec_pred_inv=False, exec_pred=PT, target_reg=R34, imm_val=77, usched_info_reg=usched_info_15)
        self.add_pre_clock_prequels(move1.class_name, move1.enc_vals)

        # Write and convert 10 to 10.0 from signed 32 bit integer to signed F64
        # Put it as prequel
        move_i2f30 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm,
                                                  Pg_negate=False, Pg=PT, Rd=R30,
                                                  Sb=10, 
                                                  usched_info_reg=usched_info_wb, req=0, wr=0x0, rd=0x7)
        self.add_pre_clock_prequels(move_i2f30.class_name, move_i2f30.enc_vals)

        # Do the same as before but with R32 and 20
        move_i2f32 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm,
                                                  Pg_negate=False, Pg=PT, Rd=R32,
                                                  Sb=20, 
                                                  usched_info_reg=usched_info_wb, req=0b000001, wr=0x0, rd=0x7)
        self.add_pre_clock_prequels(move_i2f32.class_name, move_i2f32.enc_vals)

        # Do the dad sum R30 = R30 + R32 with F64
        dadd = sc.SASS_KK__dadd__RRR_RR(kk_sm,
                                        Pg_negate=False, Pg=PT,
                                        Rd=R30,
                                        Ra_reuse=False, Ra_negate=False, Ra_absolute=False, Ra=R30,
                                        Rc_reuse=False, Rc_negate=False, Rc_absolute=False, Rc=R32,
                                        usched_info_reg=usched_info_wb, req=0b000001, wr=0x0, rd=0x7)
        self.add_pre_clock_prequels(dadd.class_name, dadd.enc_vals)

        ################################################################################################
        # Convert R30 from float to integer (F64 to SU64) into R32
        # Main instruction goes between the two CS2R clock measurements
        main = sc.SASS_KK__f2i_Rd64__Rb_64b(kk_sm,
                                            Pg_negate=False, Pg=PT,
                                            Rd=R34,
                                            Rb_absolute=False, Rb_negate=False, Rb=R30,
                                            signed=False, 
                                            usched_info_reg=usched_info_wb, req=0, wr=0x0, rd=0x7
                                            )
        self.add_main(main.class_name, main.enc_vals)

        ################################################################################################
        # This one takes R34 and writes it into the ui_output array at the respective position of the
        # current iteration
        result = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.ui_output_base_ureg, 
                                   offset=0x0, 
                                   source_reg=R34, 
                                   usched_info_reg=usched_info_15,
                                   rd=0x0)
        self.add_post_clock_sequels(result.class_name, result.enc_vals)

class BInstr_i2f_f2i_t(BInstrBase):
    """This one tests integer to float and back conversion using the respective instruction barriers.

    The goal is to have a comparison for the version without barriers.

    This one uses usched_info == trans.

    At least trans2 is necessary, otherwise it won't work.
    """
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        trans1 = kk_sm.regs.USCHED_INFO__trans1__17
        trans2 = kk_sm.regs.USCHED_INFO__trans2__18
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        usched_info_wb = trans2
        usched_info_15 = wait15
        PT = kk_sm.regs.Predicate__PT__7
        R30 = kk_sm.regs.Register__R30__30
        R32 = kk_sm.regs.Register__R32__32
        R34 = kk_sm.regs.Register__R34__34

        ################################################################################################
        # Put a well defined number in here...
        move1 = sc.SASS_KK__MOVImm(kk_sm,
                                   exec_pred_inv=False, exec_pred=PT, target_reg=R34, imm_val=77, usched_info_reg=usched_info_15)
        self.add_pre_clock_prequels(move1.class_name, move1.enc_vals)

        # Write and convert 10 to 10.0 from signed 32 bit integer to signed F64
        # Put it as prequel
        move_i2f30 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm,
                                                  Pg_negate=False, Pg=PT, Rd=R30,
                                                  Sb=10, 
                                                  usched_info_reg=usched_info_wb, req=0, wr=0x0, rd=0x7)
        self.add_pre_clock_prequels(move_i2f30.class_name, move_i2f30.enc_vals)

        # Do the same as before but with R32 and 20
        move_i2f32 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm,
                                                  Pg_negate=False, Pg=PT, Rd=R32,
                                                  Sb=20, 
                                                  usched_info_reg=usched_info_wb, req=0b000001, wr=0x0, rd=0x7)
        self.add_pre_clock_prequels(move_i2f32.class_name, move_i2f32.enc_vals)

        # Do the dad sum R30 = R30 + R32 with F64
        dadd = sc.SASS_KK__dadd__RRR_RR(kk_sm,
                                        Pg_negate=False, Pg=PT,
                                        Rd=R30,
                                        Ra_reuse=False, Ra_negate=False, Ra_absolute=False, Ra=R30,
                                        Rc_reuse=False, Rc_negate=False, Rc_absolute=False, Rc=R32,
                                        usched_info_reg=usched_info_wb, req=0b000001, wr=0x0, rd=0x7)
        self.add_pre_clock_prequels(dadd.class_name, dadd.enc_vals)

        ################################################################################################
        # Convert R30 from float to integer (F64 to SU64) into R32
        # Main instruction goes between the two CS2R clock measurements
        main = sc.SASS_KK__f2i_Rd64__Rb_64b(kk_sm,
                                            Pg_negate=False, Pg=PT,
                                            Rd=R34,
                                            Rb_absolute=False, Rb_negate=False, Rb=R30,
                                            signed=False, 
                                            usched_info_reg=usched_info_wb, req=0, wr=0x0, rd=0x7
                                            )
        self.add_main(main.class_name, main.enc_vals)

        ################################################################################################
        # This one takes R34 and writes it into the ui_output array at the respective position of the
        # current iteration
        result = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.ui_output_base_ureg, 
                                   offset=0x0, 
                                   source_reg=R34, 
                                   usched_info_reg=usched_info_15,
                                   rd=0x0)
        self.add_post_clock_sequels(result.class_name, result.enc_vals)

class BInstr_i2f_f2i_NB(BInstrBase):
    """This one tests integer to float and back conversion using no barriers.

    The goal is to have a comparison with the version with barriers and to verify that the instruction
    F2I indeed takes 45 cycles.
    """
    def __init__(self, kk_sm:KK_SM, props:KernelWLoopControlProps, wait_cycles:int):
        super().__init__(kk_sm, props, class_name=BInstrBase.CONST__EARLY_BIRD, enc_vals={}, resolve_operands=False)

        wait1 = kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        usched_info_wb = wait1
        usched_info_15 = wait15
        PT = kk_sm.regs.Predicate__PT__7
        R30 = kk_sm.regs.Register__R30__30
        R32 = kk_sm.regs.Register__R32__32
        R34 = kk_sm.regs.Register__R34__34
        RZ = kk_sm.regs.Register__RZ__255
        reset_R34_value:int = 77

        ################################################################################################
        # These run before any clock measurement. They are preparations for what is to come.
        
        # Write and convert 10 to 10.0 from signed 32 bit integer to signed F64
        # Put it as prequel
        move_i2f30 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm,
                                                  Pg_negate=False, Pg=PT, Rd=R30,
                                                  Sb=10, 
                                                  usched_info_reg=usched_info_wb, req=0b111111, wr=0x1, rd=0x0)
        self.add_pre_clock_prequels(move_i2f30.class_name, move_i2f30.enc_vals)

        # Do the same as before but with R32 and 20
        move_i2f32 = sc.SASS_KK__i2f_Rd64__IU_32b(kk_sm,
                                                  Pg_negate=False, Pg=PT, Rd=R32,
                                                  Sb=20, 
                                                  usched_info_reg=usched_info_wb, req=0b111111, wr=0x1, rd=0x0)
        self.add_pre_clock_prequels(move_i2f32.class_name, move_i2f32.enc_vals)

        # Do the dad sum R30 = R30 + R32 with F64
        dadd = sc.SASS_KK__dadd__RRR_RR(kk_sm,
                                        Pg_negate=False, Pg=PT,
                                        Rd=R30,
                                        Ra_reuse=False, Ra_negate=False, Ra_absolute=False, Ra=R30,
                                        Rc_reuse=False, Rc_negate=False, Rc_absolute=False, Rc=R32,
                                        usched_info_reg=usched_info_wb, req=0b111111, wr=0x1, rd=0x0)
        self.add_pre_clock_prequels(dadd.class_name, dadd.enc_vals)

        ################################################################################################
        # These run between the relevant clock measurements

        # Put a well defined number in here...
        move1 = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R34, imm_val=reset_R34_value, 
                                   usched_info_reg=usched_info_15)
        self.add_post_clock_prequels(move1.class_name, move1.enc_vals)

        # Convert R30 from float to integer (F64 to SU64) into R32
        # Main instruction goes between the two CS2R clock measurements
        main_usched_info = getattr(kk_sm.regs, 'USCHED_INFO__WAIT{0}_END_GROUP__{0}'.format(min(15, wait_cycles)))
        main = sc.SASS_KK__f2i_Rd64__Rb_64b(kk_sm,
                                            Pg_negate=False, Pg=PT,
                                            Rd=R34,
                                            Rb_absolute=False, Rb_negate=False, Rb=R30,
                                            signed=False, 
                                            usched_info_reg=main_usched_info, req=0b0, wr=0x7, rd=0x7
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
        # Use STG with rd=0x7 => d_output_base_ureg will be incremented before the next call => nothing bad happends
        result = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.ui_output_base_ureg, offset=0x0, 
                                   source_reg=R34, 
                                   usched_info_reg=usched_info_15,
                                   rd=0x7)
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
                                       usched_info_reg=usched_info_15)
        self.add_post_clock_sequels(sub.class_name, sub.enc_vals)
        

class Benchmark_I2F_F2I(BenchmarkBase):
    def __init__(self, sm_nr:int, experiment_nr:int=0):
        super().__init__(sm_nr, 
                         name='i2ff2i',
                         purpose="\n".join([
                            "These benchmarks test F2I and I2F and also check how many cycles it really takes to calculate F2I without using barriers.",
                            "",
                            "Notable: for the version with barriers, setting the WR barrier yields the correct result while setting the RD barrier doesn't",
                            "",
                            "Using barriers and the given value of 30.0, f2i_Rd64__Rb_64b consistently takes 45 cycles.",
                            "Using no barrier and the given value of 30.0, f2i_Rd64__Rb_64b consistently takes 37 cycles.",
                            "=> There seems to be a consistent overhead of 8 cylcles for the whole barrier mechanism.",
                            "",
                            "The expectation would have been that both take the same number of cycles."]),
                        implicit_replace=True)

        expected_result:int = 30
        template = '{0}/template_projects/template_1k/benchmark_binaries/template_1k_{1}.bin'.format(self.t_location, self.sm_nr)

        if experiment_nr in (0,1):
            print(tc.colored("Experiment 1", 'green', attrs=['bold', 'underline']))
            # Experiment 1: use usched_info = wait
            ######################################
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            bInstr = BInstr_i2f_f2i_w(self.kk_sm, props)
            exe_name_stem = '{0}/{1}'.format(self.modified_location, self.name)
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, [bInstr])
            results = Helpers.run_single_kernel_bin(exe_name="{0}.0.0.bin".format(exe_name_stem), exe_arg=str(props.loop_count))
            print()
            print("Test results with barrier and wait")
            Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__UiOutput)

        if experiment_nr in (0,2):
            print(tc.colored("Experiment 2", 'green', attrs=['bold', 'underline']))
            # Experiment 2: use usched_info = trans
            #######################################
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            bInstr = BInstr_i2f_f2i_t(self.kk_sm, props)
            exe_name_stem = '{0}/{1}'.format(self.modified_location, self.name)
            BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, [bInstr])
            results = Helpers.run_single_kernel_bin(exe_name="{0}.0.0.bin".format(exe_name_stem), exe_arg=str(props.loop_count))
            print()
            print("Test results with barrier and trans")
            Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__UiOutput)

        if experiment_nr in (0,3):
            print(tc.colored("Experiment 3", 'green', attrs=['bold', 'underline']))
            # Experiment 3: use no barriers at all with a known result
            ##########################################################
            #  - if the benchmarked instruction doesn't get enough cycles, the result will be wrong (77 in this case)
            #  - after the benchmarked instruction concludes, the result will be correct (30 in this case)
            #  - by creating kernels that wait between 25 and 50 cycles after an instruction has been dispatched
            #    and checking the result after each kernel ran individually, we can check how long an instruction requires
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            offset = 25
            bInstrList = [BInstr_i2f_f2i_NB(self.kk_sm, props, wait_cycles=w) for w in range(offset, 51)]
            exe_name_stem = '{0}/{1}'.format(self.modified_location, self.name)
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 2, exe_name_stem, props, KernelWLoop, bInstrList)
            print()
            # We run the generated binaries 20 times in sequence because the results can vary
            cycle_results = []
            for e in range(2):
                print(tc.colored("Test results with no barrier [{0}]".format(e), 'green'))
                for wt,gb in enumerate(generated_bins):
                    results = Helpers.run_single_kernel_bin(exe_name=gb.format(exe_name_stem), exe_arg=str(props.loop_count))
                    if all(r== expected_result for r in results[0][Helpers.CONST__AfterKernel][Helpers.CONST__UiOutput]):
                        print(40*' ', '\r', tc.colored("Wait time: {0}".format(wt+offset), 'red'))    
                        Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__UiOutput)
                        cycle_results.extend(results[0][Helpers.CONST__AfterKernel][Helpers.CONST__ClkOut1])
                        break
                    elif any(r== expected_result for r in results[0][Helpers.CONST__AfterKernel][Helpers.CONST__UiOutput]):
                        print(40*' ', '\r', tc.colored("Wait time: {0} => some are ok".format(wt+offset), 'red'), end = '\r')
                    else:
                        print(40*' ', '\r', tc.colored("Wait time: {0}".format(wt+offset), 'red'), end = '\r')
            print(tc.colored("All test results with no barrier [{0}]".format(e), 'cyan'))
            print(cycle_results)
        else:
            print("Choose existing experiment")
            raise Exception(sp.CONST__ERROR_ILLEGAL)

if __name__ == '__main__':
    b = Benchmark_I2F_F2I(86, experiment_nr=0)
    print("Finished")
    pass
