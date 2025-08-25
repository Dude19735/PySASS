import os
from py_cubin import SM_CuBin_File
from kk_sm import KK_SM
# import sass_create_86 as sc
import sass_create_75 as sc

class Kernel:
    def create(self, kk_sm:KK_SM, template:str) -> SM_CuBin_File:
        target_cubin = SM_CuBin_File(kk_sm.sass, template, wipe=True)

        nrc = target_cubin.reg_count()
        nnrc = {n:k+10 for n,k in nrc.items()}
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
        uii0_R6 = kk_sm.regs.Register__R6__6

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
        # Store the uint32 value a to the control register in second place
        # with offset 0x8.
        # NOTE that we initialize the control array with all 0, thus just
        # writing 32 bits into a 64 bit location is fine. If we didn't
        # initialize the control register, this could cause trouble and
        # produce garbage for the 32 LSB of the target location.
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, uniform_reg=control_UR4, 
                                   offset=0x8,
                                   source_reg=a_R4, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x7,
                                   size=32)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1

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
        # Use the size modifier size=32, since R2 is a 32 bit spot. Also
        # NOTE that we initialize the control array with all 0, thus just
        # writing 32 bits into a 64 bit location is fine. If we didn't
        # initialize the control register, this could cause trouble and
        # produce garbage for the 32 LSB of the target location.
        ii = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=control_UR4, 
                                   offset=0x0,
                                   source_reg=staging_R2, 
                                   usched_info_reg=wait15,
                                   req=0x0, rd=0x0,
                                   size=32)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1

        # ==================================================================
        # Use the base uniform register for uint64* ui_input to load the
        # first value into R6 using LDG and transfer it to the ui_output 
        # array using STG. NOTE the barrier WR in LDG and req in STG!
        ii = sc.SASS_KK__ldg_uniform_RaRZ(kk_sm, 
                                     Rd=uii0_R6, Ra=RZ, 
                                     Ra_URb=ui_input_UR10, ra_offset=0x0, 
                                     RD=0x7, WR=0x0, REQ=0x0, 
                                     USCHED_INFO=wait15, size=64)
        target_cubin.create_instr(ki, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm,
                                   uniform_reg=ui_output_UR6, 
                                   offset=0x0,
                                   source_reg=uii0_R6, 
                                   usched_info_reg=wait15,
                                   req=0b000001, rd=0x7,
                                   size=64)
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
        temp_loc = '{0}/template_projects/template_1k'.format(t_location)
        template = '{0}/benchmark_binaries/template_1k_{1}.bin'.format(temp_loc, sm_nr)
        mod_loc = '{0}/tutorials_binaries'.format(t_location)
        exe_name = "{0}/tutorial_1_load_kernel_args_{1}.bin".format(mod_loc, sm_nr)

        modified_file:SM_CuBin_File = self.create(kk_sm, template)
        modified_file.to_exec(exe_name)
        os.system('chmod +x {0}'.format(exe_name))


if __name__ == '__main__':
    b = Kernel(75)
    print("Finished")
    pass
