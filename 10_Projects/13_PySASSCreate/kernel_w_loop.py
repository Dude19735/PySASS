import os
import sys
import typing
import _config as sp
from py_cubin import SM_CuBin_File
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
from binstr_base import BInstrBase
from kernel_base import KernelBase
from kernel_output import KernelOutput
from kernel_w_loop_control_props import KernelWLoopControlProps
import sass_create as sc

class KernelWLoop(KernelBase):
    @staticmethod
    def get_kernel_control_props(kk_sm:KK_SM, 
                                 empty_instr:bool, 
                                 loop_count:int,
                                 template:str,
                                 increment_output:bool=True,
                                 increment_input_as_well:bool=False,
                                 json_file:str|None = None) -> KernelWLoopControlProps:
        """This one returns an object with all the registers that should be usable by other parts of the code.

        **NOTE**: it is PRUDENT to put all registers used in the SASS template in this method or in the main class
        (in this case KernelWLoop) itself. The reason is that one can easily search one file for already used
        registers, while spreading them out over multiple files yields the danger that we inadvertently reuse
        a register twice and don't get the result we want.

        For example
        * ui_output_base_ureg == base register for the field 'ui_output' (=> check template kernel)
        * clk_out_1_base_ureg == base register for the field 'clk_out_1' (=> check template kernel)
        * cs2r_clk_reg_2 == register that contains the final clock measurement

        Important:
        clk_out_1_base_ureg and all output uregs increment by 1 position in each loop!!

        :param kk_sm: _description_
        :type kk_sm: KK_SM
        :param empty_instr: _description_
        :type empty_instr: bool
        :param loop_count: _description_
        :type loop_count: int
        :param json_file: _description_, defaults to None
        :type json_file: str | None, optional
        :return: _description_
        :rtype: KernelWLoopControlProps
        """
        return KernelWLoopControlProps(kk_sm,
                                  min_required_reg_count = 100,
                                  min_required_instr_count = 60,
                                  template=template,
                                  a_base_ureg = kk_sm.regs.UniformRegister__UR2__2,
                                  a_base_offset = 0x160,
                                  control_base_ureg = kk_sm.regs.UniformRegister__UR4__4,
                                  control_base_offset=0x168,
                                  ui_output_base_ureg = kk_sm.regs.UniformRegister__UR6__6,
                                  ui_output_base_offset = 0x170,
                                  d_output_base_ureg = kk_sm.regs.UniformRegister__UR8__8,
                                  d_output_base_offset = 0x178,
                                  ui_input_base_ureg = kk_sm.regs.UniformRegister__UR10__10,
                                  ui_input_base_offset = 0x180,
                                  d_input_base_ureg = kk_sm.regs.UniformRegister__UR12__12,
                                  d_input_base_offset = 0x188,
                                  clk_out_1_base_ureg = kk_sm.regs.UniformRegister__UR14__14,
                                  clk_out_1_base_offset = 0x190,
                                  f_output_base_ureg = kk_sm.regs.UniformRegister__UR16__16,
                                  f_output_base_offset = 0x198,
                                  f_output_odd_base_ureg = kk_sm.regs.UniformRegister__UR17__17,
                                  f_output_odd_base_offset = 0x19c,
                                  cs2r_clk_reg_start = kk_sm.regs.Register__R10__10,
                                  cs2r_clk_reg_init = kk_sm.regs.Register__R12__12,
                                  cs2r_clk_reg_prequels = kk_sm.regs.Register__R14__14,
                                  cs2r_clk_reg_main_1 = kk_sm.regs.Register__R16__16,
                                  cs2r_clk_reg_main_2 = kk_sm.regs.Register__R18__18,
                                  cs2r_clk_reg_sequels = kk_sm.regs.Register__R20__20,
                                  cs2r_clk_reg_end = kk_sm.regs.Register__R22__22,
                                  increment_output = increment_output,
                                  increment_input_as_well = increment_input_as_well,
                                  empty_instr = empty_instr,
                                  json_file = json_file,
                                  loop_count = loop_count)

    @staticmethod
    def __add_securities(kk_sm:KK_SM, target_cubin:SM_CuBin_File, kernel_index:int, i:int, uniform_base_reg:tuple, staging_reg:tuple, imm_val:int, offset_val:int=0x0):
        PT = kk_sm.regs.Predicate__PT__7
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15
        ii = sc.SASS_KK__MOVImm(kk_sm, exec_pred_inv=False, exec_pred=PT, target_reg=staging_reg, imm_val=imm_val, 
                                usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, 
                                  uniform_reg=uniform_base_reg, offset=offset_val, 
                                   source_reg=staging_reg, 
                                   usched_info_reg=wait15, req=0x0, rd=0x7, size=32)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        return i
    
    @staticmethod
    def __load_input_base_regs(kk_sm:KK_SM, target_cubin:SM_CuBin_File, i:int, props:KernelWLoopControlProps, kernel_index:int):
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15
        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.a_base_ureg, 
                               m_offset=props.a_base_offset, 
                               usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1
        
        ii = sc.SASS_KK__ULDC(kk_sm, 
                              uniform_reg=props.control_base_ureg, 
                              m_offset=props.control_base_offset, 
                              usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.ui_output_base_ureg, 
                               m_offset=props.ui_output_base_offset, 
                               usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.d_output_base_ureg, 
                               m_offset=props.d_output_base_offset, 
                               usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.ui_input_base_ureg, 
                               m_offset=props.ui_input_base_offset, 
                               usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.d_input_base_ureg, 
                               m_offset=props.d_input_base_offset, 
                               usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.d_input_base_ureg, 
                               m_offset=props.d_input_base_offset, 
                               usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.clk_out_1_base_ureg, 
                               m_offset=props.clk_out_1_base_offset, 
                               usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # NOTE: since this one is 32 bit, it requires the even and the following 
        # odd register to be loaded.
        # If you forget the odd part, only half the 64 bit address is loaded and there will
        # be a 'an illegal memory access was encountered' Cuda error
        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.f_output_base_ureg, 
                               m_offset=props.f_output_base_offset, 
                               usched_info_reg=wait15,
                               size=32) # 32 bits size instead of 64
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=props.f_output_odd_base_ureg, 
                               m_offset=props.f_output_odd_base_offset, 
                               usched_info_reg=wait15,
                               size=32) # 32 bits size instead of 64
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        return i
        
    @staticmethod
    def create(kk_sm:KK_SM, props:KernelWLoopControlProps, binstr:BInstrBase, kernel_index:int, target_cubin:SM_CuBin_File) -> KernelOutput:
        if not isinstance(kk_sm, KK_SM): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(props, KernelWLoopControlProps): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(binstr, BInstrBase): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(kernel_index, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(target_cubin, SM_CuBin_File): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if kernel_index >= len(target_cubin):
            raise Exception("Attempted to access kernel indexed [{0}] in a binary with only [{1}] kernel".format(kernel_index, len(target_cubin)))

        # Baseline usched_info value
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15
        RZ = kk_sm.regs.Register__RZ__255
        PT = kk_sm.regs.Predicate__PT__7
        STAGING_REG = kk_sm.regs.Register__R2__2
        SHADER_TYPE_REG = kk_sm.regs.SpecialRegister__SM_SHADER_TYPE__20

        cs2r_clk_reg_start:tuple = props.cs2r_clk_reg_start
        cs2r_clk_reg_init:tuple = props.cs2r_clk_reg_init
        cs2r_clk_reg_prequels:tuple = props.cs2r_clk_reg_prequels
        cs2r_clk_reg_main_1:tuple = props.cs2r_clk_reg_main_1
        cs2r_clk_reg_main_2:tuple = props.cs2r_clk_reg_main_2
        cs2r_clk_reg_sequels:tuple = props.cs2r_clk_reg_sequels
        cs2r_clk_reg_end:tuple = props.cs2r_clk_reg_end

        i=0
        # introductory mov instruction
        # This one uses register R1
        empty = sc.SASS_KK__Empty(kk_sm, wait15)
        target_cubin.create_instr(kernel_index, i, empty.class_name__mov, empty.enc_vals__mov)
        i+=1

        ii = sc.SASS_KK__CS2R(kk_sm, target_reg=cs2r_clk_reg_start, usched_info_reg=wait15, req=0x0)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # =========================================================================================
        # use ULDC to get a uniform register onto the base address for 'a'
        a_base_ureg = props.a_base_ureg
        a_offset = props.a_base_offset
        # use ULDC to get a uniform register onto the base address for "ui_output"
        CONTROL_UR = props.control_base_ureg
        control_offset = props.control_base_offset
        # use ULDC to get a uniform register onto the base address for "control"
        UI_OUTPUT_UR = props.ui_output_base_ureg
        ui_output_offset = props.ui_output_base_offset
        # use ULDC to get a uniform register onto the base address for "d_output"
        d_output_offset = props.d_output_base_offset
        D_OUTPUT_UR = props.d_output_base_ureg
        # use ULDC to get a uniform register onto the base address for "f_output"
        f_output_offset = props.f_output_base_offset
        F_OUTPUT_UR = props.f_output_base_ureg
        # use ULDC to get a uniform register onto the base address for "ui_input"
        ui_input_offset = props.ui_input_base_offset
        UI_INPUT_UR = props.ui_input_base_ureg
        # use ULDC to get a uniform register onto the base address for "d_input"
        d_input_offset = props.d_input_base_offset
        D_INPUT_UR = props.d_input_base_ureg
        # use ULDC to get a uniform register onto the base address for "clk_out_1"
        clk_out_1_offset = props.clk_out_1_base_offset
        CLK_OUT_1_UR = props.clk_out_1_base_ureg

        i = KernelWLoop.__load_input_base_regs(kk_sm, target_cubin, i, props, kernel_index)

        # =========================================================================================
        # Move an immediate 42 value into R2
        #  => if something crashes, the first output of ui_output is going to be 42 which indicates an error
        i = KernelWLoop.__add_securities(kk_sm, target_cubin, kernel_index, i, CONTROL_UR, STAGING_REG, 42)

        ii = sc.SASS_KK__MOVImm(kk_sm, 
                                 exec_pred_inv=False, 
                                 exec_pred=PT, 
                                 target_reg=STAGING_REG, 
                                 imm_val=3828,
                                 req=0x0, 
                                 usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Move some value that is not 0 into the control array at position 6 (index=5). We will load
        # the shader type number in here later and since that one is likely 0 (ST_UNKNOWN), we want
        # to see something change here.
        ii = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=CONTROL_UR, 
                                   offset=0x28,
                                   source_reg=STAGING_REG, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x0,
                                   size=32)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # =========================================================================================
        # Load the value inside of 'a' into register R4
        # NOTE: req=6 == wait for nothing, req=1 == wait for barrier '0x0'
        # Set barrier 2 for this one
        a_iter_max:tuple = kk_sm.regs.Register__R4__4
        ii = sc.SASS_KK__IMAD_RRC_RRC(kk_sm,
                                      Rd=a_iter_max,
                                      Ra=RZ, Rb=RZ, 
                                      m_bank=0x0, m_bank_offset=0x160, 
                                      usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Initiate the iteration variable to 0 inside of register R6!
        a_iter_var:tuple = kk_sm.regs.Register__R6__6
        ii = sc.SASS_KK__IADD3_NOIMM_RRR_RRR(kk_sm, 
                                            target_reg=a_iter_var, 
                                            negate_Ra=False, src_Ra=RZ,
                                            negate_Rb=False, src_Rb=RZ,
                                            negate_Rc=False, src_Rc=RZ,
                                            usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Check if the iteration maximum is 0. If so, exit early...
        branch_pred = kk_sm.regs.Predicate__P0__0
        ii = sc.SASS_KK__isetp__RRR_RRR_noEX(kk_sm, 
                                 pred_invert=False, pred=PT, 
                                 Pu=branch_pred, 
                                 Ra=a_iter_max,
                                 icmp=kk_sm.regs.ICmpAll__EQ__2,
                                 Rb=a_iter_var,
                                 fmt=kk_sm.regs.FMT__S32__1,
                                 usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # This one exits if the previous ISETP instruction yields branch_pred == PT
        ii = sc.SASS_KK__EXIT(kk_sm, pred_invert=False, pred=branch_pred, Pp_invert=False, Pp=PT, usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # =========================================================================================
        

        # Generally we use CS2R with the time to catch barriers. But until here, there is nothing
        # that requires catching.
        ii = sc.SASS_KK__CS2R(kk_sm, target_reg=cs2r_clk_reg_init, usched_info_reg=wait15, req=0x0)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # =========================================================================================
        # =========================================================================================
        # =========================================================================================
        # Begin of benchmarking slot

        # Add the prequel instructions here:
        # these will init the operands for the instruction to benchmark
        # =============================================================
        pre_clock_prequel_inds = []
        i = binstr.add_pre_clock_prequels_to_target(kernel_index, i, target_cubin, pre_clock_prequel_inds)

        # Last instruction before the loop is a clock that waits for all barriers
        # This one must listen to all barriers, because we potentially added instructions that may
        # initialize a barrier with 'binstr.add_pre_clock_prequels_to_target'
        ii = sc.SASS_KK__CS2R(kk_sm, target_reg=cs2r_clk_reg_prequels, usched_info_reg=wait15, req=0b111111)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        pre_clock_prequel_inds.append(i)
        i+=1

        # =========================================================================================
        # The loop will jump into this spot for the benchmarking
        # ======================================================
        # This one waits for nothing, it just marks the beginning.
        i_start = i # store the start index in i_start => calculate the difference later
        ii = sc.SASS_KK__CS2R(kk_sm, target_reg=cs2r_clk_reg_main_1, usched_info_reg=wait15, req=0x0)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        post_clock_prequel_inds = []
        i = binstr.add_post_clock_prequels_to_target(kernel_index, i, target_cubin, post_clock_prequel_inds)

        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        # This is where the tested instruction is supposed to go
        i, benchmark_index = binstr.add_instr_to_target(kernel_index, i, target_cubin)

        # Add the pre-clock sequel instructions here:
        # They can do things like write results of the benchmarked instruction to an output
        # =================================================================================
        pre_clock_sequel_inds = []
        i = binstr.add_pre_clock_sequels_to_target(kernel_index, i, target_cubin, pre_clock_sequel_inds)

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # Make sure we have a well defined behaviour for the first CS2R => use at least WAIT6
        # Wait for barrier 0x0
        ii = sc.SASS_KK__CS2R(kk_sm, target_reg=cs2r_clk_reg_main_2, usched_info_reg=wait15, req=0b111111)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Add the post-clock sequel instructions here:
        # these will do things like put the result in an output register
        # ==============================================================
        post_clock_sequel_inds = []
        i = binstr.add_post_clock_sequels_to_target(kernel_index, i, target_cubin, post_clock_sequel_inds)

        # Make sure we have a well defined behaviour for the first CS2R => use at least WAIT6
        # We may have added post_clock_sequels that set some barrier => Wait for all barriers
        # to be sure that everything works as intended
        ii = sc.SASS_KK__CS2R(kk_sm, target_reg=cs2r_clk_reg_sequels, usched_info_reg=wait15, req=0b111111)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # =========================================================================================
        # End of benchmarking slot
        # =========================================================================================
        # =========================================================================================
        # =========================================================================================

        # Calculate the difference between the two clock measurements (and add the iteration variable for testing)
        diff_reg = kk_sm.regs.Register__R24__24
        ii = sc.SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                       target_reg=diff_reg,
                                       negate_Ra=False, Ra=cs2r_clk_reg_main_2,
                                       src_imm=-15, # subtract 15 for the first CS2R duration
                                       negate_Rc=True, Rc=cs2r_clk_reg_main_1,
                                       usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Write return value to memory, set barrier 0x0
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, 
                                  uniform_reg=CLK_OUT_1_UR, offset=0x0, 
                                  source_reg=diff_reg, 
                                  usched_info_reg=wait15, 
                                  req=0x0, rd=0x7,
                                  size=32)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Add 0x8 to the base registers of all clock measurements and outputs
        #  - clk_out_1_base_ureg
        #  - ui_output_base_ureg
        #  - d_output_base_ureg
        #  - f_output_base_ureg (only add 0x4 here because it's a 4 byte thing)
        # Wait for barrier 0x0 to do it.
        ii = sc.SASS_KK__UIADD3_URsIUR_RIR(kk_sm, 
                                      target_ureg=CLK_OUT_1_UR, 
                                      src_ureg=CLK_OUT_1_UR, 
                                      src_ureg_neg=False, 
                                      src_imm=0x8, 
                                      usched_info_reg=wait15,
                                      req=0b000001)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        if props.increment_output:
            ii = sc.SASS_KK__UIADD3_URsIUR_RIR(kk_sm, 
                                        target_ureg=UI_OUTPUT_UR, 
                                        src_ureg=UI_OUTPUT_UR, 
                                        src_ureg_neg=False, 
                                        src_imm=0x8, 
                                        usched_info_reg=wait15,
                                        req=0b000001)
            target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
            i+=1
            ii = sc.SASS_KK__UIADD3_URsIUR_RIR(kk_sm, 
                                        target_ureg=D_OUTPUT_UR, 
                                        src_ureg=D_OUTPUT_UR, 
                                        src_ureg_neg=False, 
                                        src_imm=0x8, 
                                        usched_info_reg=wait15,
                                        req=0b000001)
            target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
            i+=1
            ii = sc.SASS_KK__UIADD3_URsIUR_RIR(kk_sm, 
                                        target_ureg=F_OUTPUT_UR, 
                                        src_ureg=F_OUTPUT_UR, 
                                        src_ureg_neg=False, 
                                        src_imm=0x4, 
                                        usched_info_reg=wait15,
                                        req=0b000001)
            target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
            i+=1

        # If we want to increment the input array register as well...
        if props.increment_input_as_well:
            ii = sc.SASS_KK__UIADD3_URsIUR_RIR(kk_sm, 
                                        target_ureg=UI_INPUT_UR, 
                                        src_ureg=UI_INPUT_UR, 
                                        src_ureg_neg=False, 
                                        src_imm=0x8, 
                                        usched_info_reg=wait15,
                                        req=0b000001)
            target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
            i+=1
            ii = sc.SASS_KK__UIADD3_URsIUR_RIR(kk_sm, 
                                        target_ureg=D_INPUT_UR, 
                                        src_ureg=D_INPUT_UR, 
                                        src_ureg_neg=False, 
                                        src_imm=0x8, 
                                        usched_info_reg=wait15,
                                        req=0b000001)
            target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
            i+=1

        # Add 1 to the loop iteration variable
        ii = sc.SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                            target_reg=a_iter_var, 
                                            negate_Ra=False, Ra=a_iter_var, 
                                            src_imm=1, 
                                            negate_Rc=False, Rc=RZ, 
                                            usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Check if the value is still greater than the target (that is zero)
        # While the iteration variable is less than the one passed in the input, branch to beginning
        branch_pred = kk_sm.regs.Predicate__P0__0
        ii = sc.SASS_KK__isetp__RRR_RRR_noEX(kk_sm, 
                                 pred_invert=False, pred=PT, 
                                 Pu=branch_pred, 
                                 Ra=a_iter_max,
                                 icmp=kk_sm.regs.ICmpAll__GT__4,
                                 Rb=a_iter_var,
                                 fmt=kk_sm.regs.FMT__S32__1,
                                 usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # branch instruction if we are still in the loop => jump back if branch_pred is 'true'
        i_end = i # store the end index in i_end => i_end-i_start is the number of instructions the branch has to jump back
        ii = sc.SASS_KK__BRA(kk_sm, 
                             pred_invert=False, pred=branch_pred, 
                             Pp_invert=False, 
                             Pp=PT, 
                             imm_val=int(-16*(i_end - i_start + 1)), 
                             usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1
        
        # =========================================================================================
        # Write modified values into the control output array:
        # NOTE: don't change these!!! There are still 10 spots left and if you need more, you can always make
        #       the control array larger_
        #        - goto kernel_w_loop_template_gen.py
        #        - change "int control_size = 15" to whatever you like.
        # NOTE: if you do change these, you also have to change all Python methods that check stuff!!!
        # ---------------------------------------------------
        # Write read input value to control output in second place (offset=0x8)
        ii = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=CONTROL_UR, 
                                   offset=0x8, 
                                   source_reg=a_iter_max, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x0,
                                   size=32)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Write iteration variable in control output in third place
        ii = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=CONTROL_UR, 
                                   offset=0x10, 
                                   source_reg=a_iter_var, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x0,
                                   size=32)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Write the last difference between the two benchmark clocks in control position 4
        ii = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=CONTROL_UR, 
                                   offset=0x18, 
                                   source_reg=diff_reg, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x0,
                                   size=32)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Write the current kernel sequence in the fifth position of the control sequence.
        # This is to check that we really have the correct kernel runing.
        # NOTE: Checking out this MOV instruction in the decoder will also reveal the real
        # kernel index as it was iterated by the generator.
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                                 exec_pred_inv=False, 
                                 exec_pred=PT, 
                                 target_reg=STAGING_REG, 
                                 imm_val=kernel_index,
                                 req=0x0, 
                                 usched_info_reg=wait15)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=CONTROL_UR, 
                                   offset=0x20,
                                   source_reg=STAGING_REG, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x0,
                                   size=32)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # Load shader type into the control position 6
        ii = sc.SASS_KK__CS2R(kk_sm, target_reg=STAGING_REG, usched_info_reg=wait15, req=0x0, clk=False, special_reg=SHADER_TYPE_REG)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=CONTROL_UR, 
                                   offset=0x28,
                                   source_reg=STAGING_REG, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x0,
                                   size=32)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        ii = sc.SASS_KK__CS2R(kk_sm, target_reg=cs2r_clk_reg_end, usched_info_reg=wait15, req=0b111111)
        target_cubin.create_instr(kernel_index, i, ii.class_name, ii.enc_vals)
        i+=1

        # =========================================================================================
        # add end securities
        #  => the first ui_output must be 815, otherwise something crashed
        i = KernelWLoop.__add_securities(kk_sm, target_cubin, kernel_index, i, CONTROL_UR, STAGING_REG, 815)

        # =========================================================================================
        # Add final exit and bra instructions
        #  => this is SASS boilerplate
        target_cubin.create_instr(kernel_index, i, empty.class_name__exit, empty.enc_vals__exit)
        i+=1
        target_cubin.create_instr(kernel_index, i, empty.class_name__bra, empty.enc_vals__bra)
        i+=1

        return KernelOutput(target_cubin, benchmark_index, pre_clock_prequel_inds, post_clock_sequel_inds)