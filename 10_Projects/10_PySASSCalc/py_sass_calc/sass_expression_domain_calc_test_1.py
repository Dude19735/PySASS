from py_sass import SM_SASS
from _sass_expression_domain_calc import SASS_Expr_Domain_Calc

##########################################
# this test passed
##########################################

"""
Tests initially used to develop the domain calculations. It is not relevant anymore but kept for reference.
"""

# safeguard
if not __name__ == '__main__':
    exit(0)

all_ranged_instr = \
    [
        'BConst_IADD3', 'BRA_c', 'CAL_c', 'Const1_BFI', 'Const1_DFMA', 'Const1_FCMP', 
        'Const1_FFMA', 'Const1_ICMP', 'Const1_ICMP_U', 'Const1_IMAD', 'Const1_IMADSP', 
        'Const1_PRMT', 'ConstB_XMAD', 'ConstC_XMAD', 'Const_BFE', 'Const_BFI', 'Const_DADD', 
        'Const_DFMA', 'Const_DMNMX', 'Const_DMUL', 'Const_DSET', 'Const_DSETP', 'Const_F2F_1', 
        'Const_F2F_1_16', 'Const_F2F_1_64', 'Const_F2F_2', 'Const_F2F_2_16', 'Const_F2F_2_64', 
        'Const_F2F_2_64_16', 'Const_F2F_2_64_32', 'Const_F2I', 'Const_F2I_16', 'Const_F2I_64', 
        'Const_F2I_I64', 'Const_FADD', 'Const_FCHK', 'Const_FCMP', 'Const_FFMA', 'Const_FLO', 
        'Const_FMNMX', 'Const_FMUL', 'Const_FSET', 'Const_FSETP', 'Const_I2F', 'Const_I2F16', 
        'Const_I2F64', 'Const_I2F_F64', 'Const_I2I', 'Const_I2I16', 'Const_IADD', 'Const_ICMP', 
        'Const_ICMP_U', 'Const_IMAD', 'Const_IMADSP', 'Const_IMNMX', 'Const_IMUL', 'Const_ISCADD',
        'Const_ISET', 'Const_ISETP', 'Const_ISETP_U', 'Const_ISET_U', 'Const_LOP', 
        'Const_MOV', 'Const_P2R', 'Const_POPC', 'Const_PRMT', 'Const_R2P', 'Const_RRO', 
        'Const_SEL', 'Const_SHL', 'Const_SHR', 'JCAL_c', 'JMP_c', 'LEA_HI_CONST', 'LEA_LO_CONST', 
        'LOP3_Bconst', 'LOP3_LUT_BConst', 'NoBop_Const_DSET', 'NoBop_Const_DSETP', 'NoBop_Const_FSET', 
        'NoBop_Const_FSETP', 'NoBop_Const_ISET', 'NoBop_Const_ISETP', 'NoBop_Const_ISETP_U', 'NoBop_Const_ISET_U', 
        'PBK_c', 'PCNT_c', 'PLONGJMP_c', 'PRET_c', 'SSY_c', 'BPT', 'DEPBAR_LE', 'IDE_DI', 'IDE_EN', 'PEXIT'
    ]

sass = SM_SASS(50)
all_other_instr = [x.class_name for x in sass.sm.classes_dict.values() if not x in all_ranged_instr]

tt_instr = all_ranged_instr
for ind,class_name in enumerate(tt_instr):
    SASS_Expr_Domain_Calc.collect_domains_str(ind+1, len(tt_instr), sass, class_name, override=True, test=True)
print("finished")
