import os
from py_cubin import SM_CuBin_File
from kk_sm import KK_SM
# import sass_create_86 as sc
import sass_create_75 as sc

class Kernel:
    def add_clk_measure(self, kk_sm:KK_SM, 
                        i:int,                      # instruction index
                        target_cubin:SM_CuBin_File, # target binary
                        wait_reg:tuple,
                        set_req:bool,               # do we wait?
                        clk_output_ureg:tuple,      # output ureg for clk
                        ui_output_ureg:tuple,       # alternate ureg output
                        ui_input_ureg:tuple,        # alternate ureg output
                        stg_offset:int              # offset into output ureg
        ) -> int:
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15
        wait2 = kk_sm.regs.USCHED_INFO__WAIT2_END_GROUP__2
        RZ = kk_sm.regs.Register__RZ__255
        PT = kk_sm.regs.Predicate__PT__7

        clk_diff_R10 = kk_sm.regs.Register__R10__10
        clk_diffo_R11 = kk_sm.regs.Register__R11__11
        clk1_R6 = kk_sm.regs.Register__R6__6
        clk1o_R7 = kk_sm.regs.Register__R7__7
        clk2_R8 = kk_sm.regs.Register__R8__8
        clk2o_R9 = kk_sm.regs.Register__R9__9
        clk_diff_R10 = kk_sm.regs.Register__R10__10
        staging_R12 = kk_sm.regs.Register__R12__12

        # Make sure we build on zeros
        # Conditionally set a barrier wait requirement if a flag
        # is set.
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                            exec_pred_inv=False, exec_pred=PT, 
                            target_reg=clk1_R6, imm_val=0x0, 
                            usched_info_reg=wait15, 
                            req=0b000011 if set_req else 0x0)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                            exec_pred_inv=False, exec_pred=PT, 
                            target_reg=clk1o_R7, imm_val=0x0, 
                            usched_info_reg=wait15, 
                            req=0x0)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                            exec_pred_inv=False, exec_pred=PT, 
                            target_reg=clk2_R8, imm_val=0x0, 
                            usched_info_reg=wait15, 
                            req=0x0)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                            exec_pred_inv=False, exec_pred=PT, 
                            target_reg=clk2o_R9, imm_val=0x0, 
                            usched_info_reg=wait15, 
                            req=0x0)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                            exec_pred_inv=False, exec_pred=PT, 
                            target_reg=clk_diffo_R11, imm_val=0x0, 
                            usched_info_reg=wait15, 
                            req=0x0)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1

        # Measure the first clock
        ii = sc.SASS_KK__CS2R(kk_sm, 
                              target_reg=clk1_R6, 
                              usched_info_reg=wait_reg, 
                              req=0x0)
        # don't forget to add
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        # don't forget to increment
        i+=1
        # Move the clock value into another register: we want to 
        # know if the value is correct or not after waitX cycles
        ii = sc.SASS_KK__IADD3_NOIMM_RRR_RRR(kk_sm,
                                    target_reg=staging_R12,
                                    negate_Ra=False, src_Ra=clk1_R6,
                                    negate_Rb=False, src_Rb=RZ,
                                    negate_Rc=False, src_Rc=RZ,
                                    usched_info_reg=wait15)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        # Measure the second clock
        ii = sc.SASS_KK__CS2R(kk_sm, 
                              target_reg=clk2_R8, 
                              usched_info_reg=wait15, req=0x0)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        # Compute the difference of the two clocks.
        # Subtract 15 because we don't want the clocks of the MOV
        # instruction in the result
        ii = sc.SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                        target_reg=clk_diff_R10,
                                        negate_Ra=False, Ra=clk2_R8,
                                        src_imm=-15,
                                        negate_Rc=True, Rc=clk1_R6,
                                        usched_info_reg=wait15)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        # Store the clock diff in the clock output array.
        # Set a barrier that we can wait for the next time we call this
        # method.
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, uniform_reg=clk_output_ureg, 
                                   offset=stg_offset,
                                   source_reg=clk_diff_R10, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x0,
                                   size=32)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, uniform_reg=ui_output_ureg, 
                                   offset=stg_offset,
                                   source_reg=staging_R12, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x1,
                                   size=32)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, uniform_reg=ui_input_ureg, 
                                   offset=stg_offset,
                                   source_reg=clk1_R6, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x1,
                                   size=32)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        return i

    def create(self, kk_sm:KK_SM, template:str) -> SM_CuBin_File:
        target_cubin = SM_CuBin_File(kk_sm.sass, template, wipe=True)

        nrc = target_cubin.reg_count()
        nnrc = {n:100 for n,k in nrc.items()}
        target_cubin.overwrite_reg_count(nnrc)

        # Zero and True: we need them all the time
        RZ = kk_sm.regs.Register__RZ__255
        PT = kk_sm.regs.Predicate__PT__7
        # Some temp blabla
        staging_R2 = kk_sm.regs.Register__R2__2

        # =====================================================
        # It is a good idea to initialize registers in this
        # way to make things more readable. The kk_sm.regs
        # are tuples with 3 entries:
        # UniformRegister__UR2__2 = ('UniformRegister', 'UR2', 2)
        #  - register category
        #  - register name
        #  - register number (can be different than register name!)
        wait1 = kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1
        wait2 = kk_sm.regs.USCHED_INFO__WAIT2_END_GROUP__2
        wait3 = kk_sm.regs.USCHED_INFO__WAIT3_END_GROUP__3
        wait4 = kk_sm.regs.USCHED_INFO__WAIT4_END_GROUP__4
        wait5 = kk_sm.regs.USCHED_INFO__WAIT5_END_GROUP__5
        wait6 = kk_sm.regs.USCHED_INFO__WAIT6_END_GROUP__6
        wait7 = kk_sm.regs.USCHED_INFO__WAIT7_END_GROUP__7
        wait8 = kk_sm.regs.USCHED_INFO__WAIT8_END_GROUP__8
        wait9 = kk_sm.regs.USCHED_INFO__WAIT9_END_GROUP__9
        wait10 = kk_sm.regs.USCHED_INFO__WAIT10_END_GROUP__10
        wait11 = kk_sm.regs.USCHED_INFO__WAIT11_END_GROUP__11
        wait12 = kk_sm.regs.USCHED_INFO__WAIT12_END_GROUP__12
        wait13 = kk_sm.regs.USCHED_INFO__WAIT13_END_GROUP__13
        wait14 = kk_sm.regs.USCHED_INFO__WAIT14_END_GROUP__14
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15
        
        a_UR2 = kk_sm.regs.UniformRegister__UR2__2
        control_UR4 = kk_sm.regs.UniformRegister__UR4__4
        ui_output_UR6 = kk_sm.regs.UniformRegister__UR6__6
        d_output_UR8 = kk_sm.regs.UniformRegister__UR8__8
        ui_input_UR10 = kk_sm.regs.UniformRegister__UR10__10
        d_input_UR12 = kk_sm.regs.UniformRegister__UR12__12
        clk_UR14 = kk_sm.regs.UniformRegister__UR14__14
        f_output_UR16 = kk_sm.regs.UniformRegister__UR16__16

        # 1. load all ptr registers
        # 2. load first value
        # 3. deal with floats
        # => create a two int kernel thing...

        a_R4 = kk_sm.regs.Register__R4__4
        
        # ui0_R10_f32 = kk_sm.regs.Register__R10__10
        # ui0_R12_f64 = kk_sm.regs.Register__R12__12
        # ui0_rcp32_R16 = kk_sm.regs.Register__R16__16
        # ui0_rcp64_R18 = kk_sm.regs.Register__R18__18
        # a32_d_ui032_R20 = kk_sm.regs.Register__R20__20
        # a64_d_ui064_R22 = kk_sm.regs.Register__R22__22

        # Kernel index
        ki = 0
        i=0
        empty = sc.SASS_KK__Empty(kk_sm, wait15)
        # =====================================================
        # Add initial mov instruction
        target_cubin.create_instr(ki, i, 
                                  empty.class_name__mov, 
                                  empty.enc_vals__mov)
        i+=1

        # =====================================================
        # Load unsigned int once using ULDG and another time
        # using IMAD (equivalent)
        # With ULDC we can pass the size, which makes it
        # easier to deal with larger data types, it is more
        # cumbersome if we have value types. In this instance
        # the value of a is stored into U2, and there is a lack
        # of nice instructions to do things with it. Thus, IMAD
        # is the better choice.
        # Generally, the UniformRegister category is considered
        # a 'distinct data path' and is most often used to deal
        # with addresses.
        ii = sc.SASS_KK__ULDC(kk_sm, 
                              uniform_reg=a_UR2, 
                              m_offset=0x160, 
                              usched_info_reg=wait15, size=32)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__IMAD_RRC_RRC(kk_sm,
                                      Rd=a_R4, Ra=RZ, Rb=RZ, 
                                      m_bank=0x0, m_bank_offset=0x160, 
                                      usched_info_reg=wait15)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1

        # =====================================================
        # For pointer types, using ULDC is the best option. It
        # exists on all architectures starting with SM 75 and
        # creates an uniform register with the base address.
        # There are a lot of useful instructions to do things
        # with this construct.
        ii = sc.SASS_KK__ULDC(kk_sm, 
                              uniform_reg=control_UR4, 
                              m_offset=0x168, 
                              usched_info_reg=wait15, size=64)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__ULDC(kk_sm, 
                              uniform_reg=ui_output_UR6, 
                              m_offset=0x170, 
                              usched_info_reg=wait15, size=64)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__ULDC(kk_sm, 
                              uniform_reg=d_output_UR8, 
                              m_offset=0x178, 
                              usched_info_reg=wait15, size=64)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__ULDC(kk_sm, 
                              uniform_reg=ui_input_UR10, 
                              m_offset=0x180, 
                              usched_info_reg=wait15, size=64)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__ULDC(kk_sm, 
                              uniform_reg=d_input_UR12, 
                              m_offset=0x188, 
                              usched_info_reg=wait15, size=64)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__ULDC(kk_sm, 
                              uniform_reg=clk_UR14, 
                              m_offset=0x190, 
                              usched_info_reg=wait15, size=64)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__ULDC(kk_sm, uniform_reg=f_output_UR16, 
                              m_offset=0x198, 
                              usched_info_reg=wait15, size=64)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1

        # ==================================================================
        # ==================================================================
        # == Compute a couple of clock cycles ==============================
        # ==================================================================
        # ==================================================================
        # The process is: 
        #  - write clk1 using 15 cycles
        #  - write clk2 using 1 to 15 cycles
        #  - compute clk2 - clk1 using 15 cycles
        #  - subtract 15 from the difference
        #  - write the difference in the return array

        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait1, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=False,
                                 stg_offset=0x0)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait2, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x8)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait3, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x10)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait4, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x18)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait5, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x20)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait6, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x28)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait7, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x30)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait8, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x38)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait9, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x40)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait10, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x48)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait11, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x50)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait12, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x58)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait13, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x60)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait14, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x68)
        i = self.add_clk_measure(kk_sm, i=i, target_cubin=target_cubin, 
                                 wait_reg=wait15, 
                                 clk_output_ureg=clk_UR14, 
                                 ui_output_ureg=ui_output_UR6,
                                 ui_input_ureg=ui_input_UR10,
                                 set_req=True,
                                 stg_offset=0x70)

        # ==================================================================
        # Write 815 in control array location index 0.
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                                 exec_pred_inv=False, 
                                 exec_pred=PT, 
                                 target_reg=staging_R2, 
                                 imm_val=815,
                                 req=0x0, 
                                 usched_info_reg=wait15)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, uniform_reg=control_UR4, 
                                   offset=0x0,
                                   source_reg=staging_R2, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x7,
                                   size=32)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1

        # ==================================================================
        # Add final exit and bra instructions
        target_cubin.create_instr(ki, i, 
                                  empty.class_name__exit, 
                                  empty.enc_vals__exit)
        i+=1
        target_cubin.create_instr(ki, i, 
                                  empty.class_name__bra, 
                                  empty.enc_vals__bra)
        i+=1

        return target_cubin


    def __init__(self, sm_nr:int):
        kk_sm = KK_SM(sm_nr, ip='127.0.0.1', port=8180, webload=True)
        t_location = os.path.dirname(os.path.realpath(__file__))
        temp_loc = '{0}/template_projects/template_1k_no_loop_240' \
                        .format(t_location)
        template = '{0}/benchmark_binaries/template_1k_no_loop_240_{1}.bin' \
                        .format(temp_loc, sm_nr)
        mod_loc = '{0}/tutorials_binaries'.format(t_location)
        exe_name = "{0}/tutorial_3_clocks_{1}.bin".format(mod_loc, sm_nr)

        modified_file:SM_CuBin_File = self.create(kk_sm, template)
        modified_file.to_exec(exe_name)
        os.system('chmod +x {0}'.format(exe_name))


if __name__ == '__main__':
    b = Kernel(75)
    print("Finished")
    pass
