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

class BInstr_B(BInstrBase):
    """This one tests the STG instruction with barriers.

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
        # Preparations: move a fixed value into the register R30
        value = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R30, imm_val=59716, 
                                   usched_info_reg=wait15)
        self.add_pre_clock_prequels(value.class_name, value.enc_vals)

        ################################################################################################
        # This is the main clock measuring area

        # This one takes R30 and writes it into the ui_output array at the respective position of the
        # current iteration.
        # NOTE: props.ui_output_base_ureg increments by one position in each loop iteration
        # NOTE: set RD barrier 0x0 and size=32. The latter one is very important since R30 is a 32 bit
        #       value. If we don't put size=32 there, it will at some point write garbage into the upper 32 bits.
        main = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.ui_output_base_ureg, 
                                   offset=0x0, 
                                   source_reg=R30, 
                                   usched_info_reg=wait1,
                                   rd=0x0,
                                   size=32)
        self.add_main(main.class_name, main.enc_vals)

        ################################################################################################

class BInstr_NB(BInstrBase):
    """This one tests STG without the barriers to check how long it really takes.
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
        # Preparations: move a fixed value into the register R30
        value = sc.SASS_KK__MOVImm(kk_sm, 
                                   exec_pred_inv=False, exec_pred=PT, 
                                   target_reg=R30, imm_val=59716, 
                                   usched_info_reg=wait15)
        self.add_pre_clock_prequels(value.class_name, value.enc_vals)

        ################################################################################################
        # This is the main clock measuring area

        # This one takes R30 and writes it into the ui_output array at the respective position of the
        # current iteration.
        # NOTE: props.ui_output_base_ureg increments by one position in each loop iteration
        # NOTE: set RD barrier 0x0 and size=32. The latter one is very important since R30 is a 32 bit
        #       value. If we don't put size=32 there, it will at some point write garbage into the upper 32 bits.
        main = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.ui_output_base_ureg, 
                                   offset=0x0, 
                                   source_reg=R30, 
                                   usched_info_reg=wait1,
                                   rd=0x7,
                                   size=32)
        self.add_main(main.class_name, main.enc_vals)

        ################################################################################################

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

class BInstr_RT(BInstrBase):
    """This one tests the STG instruction with barriers and a roundtrip.
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
        # Preparations: no need

        ################################################################################################
        # This is the main clock measuring area

        # First read from global memory into a register, then write that one into an output
        main_prep_1 = sc.SASS_KK__ldg_uniform_RaRZ(kk_sm, 
                                           Rd=R30, 
                                           Ra=RZ,
                                           Ra_URb=props.ui_input_base_ureg,
                                           ra_offset = 0x0,
                                           RD=0x0,
                                           WR=0x1,
                                           REQ=0x0,
                                           size=32,
                                           USCHED_INFO=wait1)
        # wait for the operation to be complete
        main_prep_2 = sc.SASS_KK__CS2R(kk_sm, 
                                       target_reg=R34, 
                                       usched_info_reg=wait15, 
                                       req=0b000011)
        self.add_post_clock_prequels(main_prep_1.class_name, main_prep_1.enc_vals)
        self.add_post_clock_prequels(main_prep_2.class_name, main_prep_2.enc_vals)
        
        main = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=props.ui_output_base_ureg, 
                                   offset=0x0, 
                                   source_reg=R30, 
                                   usched_info_reg=wait1,
                                   rd=0x0,
                                   size=32)
        self.add_main(main.class_name, main.enc_vals)

        ################################################################################################
        # Subtract 15 cycles from the measurement for the cycle tester:
        # props.cs2r_clk_reg_2 is the register that contains the last clock measurement.
        sub = sc.SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                       target_reg=props.cs2r_clk_reg_main_2,
                                       negate_Ra=False, Ra=props.cs2r_clk_reg_main_2,
                                       src_imm=-15, # subtract 30
                                       negate_Rc=False, Rc=RZ,
                                       usched_info_reg=wait15)
        self.add_post_clock_sequels(sub.class_name, sub.enc_vals)

class Benchmark(BenchmarkBase):
    def __init__(self, sm_nr:int, experiment_nr:int=0):
        super().__init__(sm_nr, 
                         name='stg_ldg',
                         purpose="\n".join([
                            "These benchmarks test STG with and without barrier.",
                            "They also test the full round trip LDG-STG"]),
                        implicit_replace=True)

        if experiment_nr in (0,1):
            expected_result:int = int(59716)
            print(tc.colored("Experiment 1", 'green', attrs=['bold', 'underline']))
            # Experiment 1: use usched_info = wait
            ######################################
            
            template = '{0}/template_projects/template_1k/benchmark_binaries/template_1k_{1}.bin'.format(self.t_location, self.sm_nr)
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=20, template=template)

            bInstr = BInstr_B(self.kk_sm, props)
            exe_name_stem = '{0}/{1}'.format(self.modified_location, '{0}_B'.format(self.name))
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, [bInstr])
            results = Helpers.run_single_kernel_bin(exe_name=generated_bins[0], exe_arg=str(props.loop_count))
            print()
            print("Test results with barrier and wait")
            Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__UiOutput)

        if experiment_nr in (0,2):
            expected_result:int = int(59716)
            print(tc.colored("Experiment 2", 'green', attrs=['bold', 'underline']))
            # Experiment 2: use no barriers at all with a known result
            ##########################################################
            #  - if the benchmarked instruction doesn't get enough cycles, the result will be wrong (77 in this case)
            #  - after the benchmarked instruction concludes, the result will be correct (30 in this case)
            #  - by creating kernels that wait between 25 and 50 cycles after an instruction has been dispatched
            #    and checking the result after each kernel ran individually, we can check how long an instruction requires
            template = '{0}/template_projects/template_1k/benchmark_binaries/template_1k_{1}.bin'.format(self.t_location, self.sm_nr)
            props = KernelWLoop.get_kernel_control_props(self.kk_sm, empty_instr=False, loop_count=10, template=template)
            
            offset = 1
            bInstrList = [BInstr_NB(self.kk_sm, props, wait_cycles=w) for w in range(offset, 71)]
            exe_name_stem = '{0}/{1}'.format(self.modified_location, '{0}_NB'.format(self.name))
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 2, exe_name_stem, props, KernelWLoop, bInstrList)
            print()
            # We run the generated binaries 20 times in sequence because the results can vary
            cycle_results = []
            for e in range(1):
                print(tc.colored("Test results with no barrier [{0}]".format(e), 'green'))
                for wt,gb in enumerate(generated_bins):
                    results = Helpers.run_single_kernel_bin(exe_name=gb.format(exe_name_stem), exe_arg=str(props.loop_count))
                    if all(r== expected_result for r in results[0][Helpers.CONST__AfterKernel][Helpers.CONST__UiOutput]):
                        print(40*' ', '\r', tc.colored("Wait time: {0}".format(wt+offset), 'red'))    
                        Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__UiOutput, output_all_arrays=True)
                        cycle_results.extend(results[0][Helpers.CONST__AfterKernel][Helpers.CONST__ClkOut1])
                        break
                    elif any(r== expected_result for r in results[0][Helpers.CONST__AfterKernel][Helpers.CONST__UiOutput]):
                        print(40*' ', '\r', tc.colored("Wait time: {0} => some are ok".format(wt+offset), 'red'), end = '\r')
                    else:
                        print(40*' ', '\r', tc.colored("Wait time: {0}".format(wt+offset), 'red'), end = '\r')
            print(tc.colored("All test results with no barrier [{0}]".format(e), 'cyan'))
            print(cycle_results)

        if experiment_nr in (0,3):
            loop_count = 10
            expected_result:list = [int(i+10001) for i in range(loop_count)]
            print(tc.colored("Experiment 3", 'green', attrs=['bold', 'underline']))
            # Experiment 3: use usched_info = wait
            ######################################
            template = '{0}/template_projects/template_1k/benchmark_binaries/template_1k_{1}.bin'.format(self.t_location, self.sm_nr)
            props = KernelWLoop.get_kernel_control_props(
                self.kk_sm, 
                empty_instr=False, 
                loop_count=loop_count, 
                template=template,
                increment_input_as_well=True)
            
            bInstr = BInstr_RT(self.kk_sm, props)
            exe_name_stem = '{0}/{1}'.format(self.modified_location, '{0}_RT'.format(self.name))
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, [bInstr])
            results = Helpers.run_single_kernel_bin(exe_name=generated_bins[0], exe_arg=str(props.loop_count))
            print()
            print("Test results with barrier and wait")
            Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__UiOutput, output_all_arrays=True)

        if experiment_nr in (0,4):
            expected_result:int = int(59716)
            print(tc.colored("Experiment 4", 'green', attrs=['bold', 'underline']))
            # Experiment 4: use usched_info = wait
            ######################################
            # This one is the same as Experiment 1 with the difference that the input is not incremented in each loop.
            # It wants to test, if there are penalties for saving the same number in the same place multiple times in a loop
            
            template = '{0}/template_projects/template_1k/benchmark_binaries/template_1k_{1}.bin'.format(self.t_location, self.sm_nr)
            props = KernelWLoop.get_kernel_control_props(
                self.kk_sm, 
                empty_instr=False, 
                loop_count=10, 
                template=template, 
                increment_output=False, 
                increment_input_as_well=False)

            bInstr = BInstr_B(self.kk_sm, props)
            exe_name_stem = '{0}/{1}'.format(self.modified_location, '{0}_B'.format(self.name))
            generated_bins = BenchmarkBase.create_modified_binaries_per_instruction(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, [bInstr])
            results = Helpers.run_single_kernel_bin(exe_name=generated_bins[0], exe_arg=str(props.loop_count))
            print()
            print("Test results with barrier and wait")
            Helpers.output_print_single_kernel_w_loop_results(results, expected_result, props, output=Helpers.CONST__UiOutput)

        if experiment_nr in (0,5):
            expected_result:int = int(59716)
            print(tc.colored("Experiment 5", 'green', attrs=['bold', 'underline']))
            # Experiment 5: use usched_info = wait
            ######################################
            # This one is the same as Experiment 4 but with an external loop

            template = '{0}/template_projects/template_1k_loop/benchmark_binaries/template_1k_loop_{1}.bin'.format(self.t_location, self.sm_nr)
            props = KernelWLoop.get_kernel_control_props(
                self.kk_sm, 
                empty_instr=False, 
                loop_count=10, 
                template=template, 
                increment_output=False, 
                increment_input_as_well=False)

            bInstr = BInstr_B(self.kk_sm, props)
            all_enc_vals_str = [BenchmarkBase.normatized_class_and_enc_vals_to_str(0, bInstr.class_name, bInstr.enc_vals)]
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'bin_file')
            generated_bins = BenchmarkBase.create_modified_binaries_per_k_instructions(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, 0, [bInstr], all_enc_vals_str)
            
            results = Helpers.run_bin_loop(1, props.loop_count, generated_bins, True)
            Helpers.process_output_multi_kernel_w_loop_results(results, 5000)

        if experiment_nr in (0,6):
            loop_count = 10
            expected_result:list = [int(i+10001) for i in range(loop_count)]
            print(tc.colored("Experiment 6", 'green', attrs=['bold', 'underline']))
            # Experiment 6: use usched_info = wait
            ######################################
            # This one is the same as experiment 3 but with a loop kernel template
            
            template = '{0}/template_projects/template_1k_loop/benchmark_binaries/template_1k_loop_{1}.bin'.format(self.t_location, self.sm_nr)
            props = KernelWLoop.get_kernel_control_props(
                self.kk_sm, 
                empty_instr=False, 
                loop_count=loop_count, 
                template=template,
                increment_output=False,
                increment_input_as_well=False)

            bInstr = BInstr_RT(self.kk_sm, props)
            all_enc_vals_str = [BenchmarkBase.normatized_class_and_enc_vals_to_str(0, bInstr.class_name, bInstr.enc_vals)]
            exe_name_stem = '{0}/{1}'.format(self.modified_location, 'bin_file')
            generated_bins = BenchmarkBase.create_modified_binaries_per_k_instructions(self.kk_sm, 1, exe_name_stem, props, KernelWLoop, 0, [bInstr], all_enc_vals_str)
            
            results = Helpers.run_bin_loop(1, props.loop_count, generated_bins, True)
            Helpers.process_output_multi_kernel_w_loop_results(results, 5000)

if __name__ == '__main__':
    b = Benchmark(86, experiment_nr=0)
    print("Finished")
    pass
