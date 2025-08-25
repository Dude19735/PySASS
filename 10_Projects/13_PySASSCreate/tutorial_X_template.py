import sys
import os
import inspect
from py_cubin import SM_CuBin_File
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
import sass_create_86 as sc
# import sass_create_75 as sc

class Kernel:
    def create(self, kk_sm:KK_SM, template:str) -> SM_CuBin_File:
        target_cubin = SM_CuBin_File(kk_sm.sass, template)
        nrc = target_cubin.reg_count()
        nnrc = {n:k+10 for n,k in nrc.items()}
        target_cubin.overwrite_reg_count(nnrc)

        nop = sc.SASS_KK__NOP(kk_sm)
        for i in range(0, len(target_cubin[0])):
            target_cubin.create_instr(0, i, nop.class_name, nop.enc_vals)

        usched_info_reg = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        i=0
        # introductory mov instruction
        # This one uses register R1
        empty = sc.SASS_KK__Empty(kk_sm, usched_info_reg)
        target_cubin.create_instr(0, i, empty.class_name__mov, empty.enc_vals__mov)
        i+=1
        # ==================================================================
        # use ULDC to get a uniform register onto the base address for ui_output
        ui_output_ureg = kk_sm.regs.UniformRegister__UR2__2
        ui_output_offset = 0x168
        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=ui_output_ureg, 
                               m_offset=ui_output_offset, 
                               usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1

        # use ULDC to get a uniform register onto the base address for d_output
        d_output_offset = 0x170
        d_output_ureg = kk_sm.regs.UniformRegister__UR4__4
        ii = sc.SASS_KK__ULDC(kk_sm, 
                               uniform_reg=d_output_ureg, 
                               m_offset=d_output_offset, 
                               usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        # ==================================================================
        # move an immediate value into R2
        imm_reg = kk_sm.regs.Register__R38__38
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                                 exec_pred_inv=False, 
                                 exec_pred=kk_sm.regs.Predicate__PT__7, 
                                 target_reg=imm_reg, 
                                 imm_val=42, 
                                 usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, 
                                   uniform_reg=ui_output_ureg, 
                                   offset=0x0, 
                                   source_reg=imm_reg, 
                                   usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15,
                                   rd=0x0)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        # ==================================================================
        # use LDG to load the respective first values of ui_output and d_output into registers
        ui_rd:tuple = kk_sm.regs.Register__R2__2
        ii = sc.SASS_KK__ldg_uniform_RaRZ(kk_sm, 
                                           Rd=ui_rd, 
                                           Ra=kk_sm.regs.Register__RZ__255,
                                           Ra_URb=ui_output_ureg,
                                           ra_offset = 0x8,
                                           RD=0x7,
                                           WR=0x0,
                                           REQ=0b000001,
                                           USCHED_INFO=usched_info_reg)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1

        d_rd:tuple = kk_sm.regs.Register__R4__4
        ii = sc.SASS_KK__ldg_uniform_RaRZ(kk_sm, 
                                           Rd=d_rd, 
                                           Ra=kk_sm.regs.Register__RZ__255,
                                           Ra_URb=d_output_ureg,
                                           ra_offset = 0x8,
                                           RD=0x7,
                                           WR=0x1,
                                           REQ=0,
                                           USCHED_INFO=usched_info_reg)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        # ==================================================================
        # Test the EXIT instruction
        # pred_invert | Pp_invert ||
        #  True       |  True     || 815
        #  True       |  False    || 815
        #  False      |  True     || 815
        #  False      |  False    || 42
        # Both must be true for the EXIT instruction to run
        ii = sc.SASS_KK__EXIT(kk_sm, 
                              pred_invert=False, 
                              pred=kk_sm.regs.Predicate__PT__7, 
                              Pp_invert=False, 
                              Pp=kk_sm.regs.Predicate__PT__7,
                              usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1

        # Make sure we catch both WR barriers with this one
        ii = sc.SASS_KK__CS2R(kk_sm, 
                               target_reg=kk_sm.regs.Register__R6__6, 
                               usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT6_END_GROUP__6,
                               req=0b000011)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1

        # Make sure we have a well defined behaviour for the first CS2R => use WAIT6
        ii = sc.SASS_KK__CS2R(kk_sm, 
                               target_reg=kk_sm.regs.Register__R8__8, 
                               usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT6_END_GROUP__6)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1

        # ==================================================================
        # write back some values moved one slot to the right
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, 
                                   uniform_reg=ui_output_ureg, 
                                   offset=0x10, 
                                   source_reg=ui_rd, 
                                   usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        target_cubin.set_REQ(0, i, 0, req=0)
        i+=1

        ii = sc.SASS_KK__STG_RaRZ(kk_sm, 
                                   uniform_reg=d_output_ureg, 
                                   offset=0x10, 
                                   source_reg=d_rd, 
                                   usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        target_cubin.set_REQ(0, i, 0, req=1)
        i+=1
        # ==================================================================
        # add end securities
        imm_reg = kk_sm.regs.Register__R2__2
        ii = sc.SASS_KK__MOVImm(kk_sm, 
                                 exec_pred_inv=False, 
                                 exec_pred=kk_sm.regs.Predicate__PT__7, 
                                 target_reg=imm_reg, imm_val=815, 
                                 usched_info_reg=usched_info_reg)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        ii = sc.SASS_KK__STG_RaRZ(kk_sm, 
                                   uniform_reg=ui_output_ureg, 
                                   offset=0x0, 
                                   source_reg=imm_reg, 
                                   usched_info_reg=usched_info_reg)
        target_cubin.create_instr(0, i, ii.class_name, ii.enc_vals)
        i+=1
        # ==================================================================
        # Add final exit and bra instructions
        target_cubin.create_instr(0, i, empty.class_name__exit, empty.enc_vals__exit)
        i+=1
        target_cubin.create_instr(0, i, empty.class_name__bra, empty.enc_vals__bra)
        i+=1

        return target_cubin


    def __init__(self, sm_nr:int):
        kk_sm = KK_SM(sm_nr, ip='127.0.0.1', port=8180, webload=True)
        t_location = os.path.dirname(os.path.realpath(__file__))
        temp_loc = '{0}/template_projects/template_1k'.format(t_location)
        template = '{0}/benchmark_binaries/template_1k_{1}.bin'.format(temp_loc, sm_nr)
        mod_loc = '{0}/tutorials_binaries'.format(t_location)
        exe_name = "{0}/tutorial_0_simple_kernel_{1}.bin".format(mod_loc, sm_nr)

        modified_file:SM_CuBin_File = self.create(kk_sm, template)
        modified_file.to_exec(exe_name)
        os.system('chmod +x {0}'.format(exe_name))


if __name__ == '__main__':
    # x = ControlInstructions(86)
    b = Kernel(86)
    print("Finished")
    pass
