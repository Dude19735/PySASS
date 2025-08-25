import os
from py_cubin import SM_CuBin_File
from kk_sm import KK_SM
# import sass_create_86 as sc
import sass_create_75 as sc

class Kernel:
    def create_wipe(self, kk_sm:KK_SM, template:str) -> SM_CuBin_File:
        # wipe=True replaces all instructions with NOP implicitly
        target_cubin = SM_CuBin_File(kk_sm.sass, template, wipe=True)
        
        nrc = target_cubin.reg_count()
        nnrc = {n:k+10 for n,k in nrc.items()}
        target_cubin.overwrite_reg_count(nnrc)

        WAIT15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        i=0
        empty = sc.SASS_KK__Empty(kk_sm, WAIT15)
        # =====================================================
        # Add initial mov instruction
        target_cubin.create_instr(0, i, empty.class_name__mov, empty.enc_vals__mov)
        i+=1
        # =====================================================
        # Add final exit and bra instructions
        target_cubin.create_instr(0, i, empty.class_name__exit, empty.enc_vals__exit)
        i+=1
        target_cubin.create_instr(0, i, empty.class_name__bra, empty.enc_vals__bra)
        i+=1

        return target_cubin
    
    def create(self, kk_sm:KK_SM, template:str) -> SM_CuBin_File:
        target_cubin = SM_CuBin_File(kk_sm.sass, template)
        
        nrc = target_cubin.reg_count()
        nnrc = {n:k+10 for n,k in nrc.items()}
        target_cubin.overwrite_reg_count(nnrc)

        # Create one NOP instruction that can be multiplied to everywhere
        nop = sc.SASS_KK__NOP(kk_sm)
        for i in range(0, len(target_cubin[0])):
            target_cubin.create_instr(0, i, nop.class_name, nop.enc_vals)

        WAIT15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15

        i=0
        empty = sc.SASS_KK__Empty(kk_sm, WAIT15)
        # =====================================================
        # Add initial mov instruction
        target_cubin.create_instr(0, i, empty.class_name__mov, empty.enc_vals__mov)
        i+=1
        # =====================================================
        # Add final exit and bra instructions
        target_cubin.create_instr(0, i, empty.class_name__exit, empty.enc_vals__exit)
        i+=1
        target_cubin.create_instr(0, i, empty.class_name__bra, empty.enc_vals__bra)
        i+=1

        return target_cubin


    def __init__(self, sm_nr:int):
        kk_sm = KK_SM(sm_nr, ip='127.0.0.1', port=8180, webload=True)
        t_location = os.path.dirname(os.path.realpath(__file__))
        template = '{0}/template_projects/template_1k/benchmark_binaries/template_1k_{1}.bin'.format(t_location, sm_nr)
        modified_location = '{0}/tutorials_binaries'.format(t_location)
        exe_name = "{0}/tutorial_0_simple_kernel_{1}".format(modified_location, sm_nr)

        modified_file:SM_CuBin_File = self.create(kk_sm, template)
        modified_file.to_exec(exe_name)
        os.system('chmod +x {0}'.format(exe_name))


if __name__ == '__main__':
    b = Kernel(75)
    print("Finished")
    pass
