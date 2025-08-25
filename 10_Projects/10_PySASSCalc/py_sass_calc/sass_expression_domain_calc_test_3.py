import time
from py_sass import SM_SASS
import _config as sp
from _sass_expression_domain_calc import SASS_Expr_Domain_Calc

################################################################################################################
# The contents of this file have been partially auto-generated. 
# Use _sass_expression_domain_parse.py to regenerate after adjustments the contents after adjustment.
# Not doing so may result in more work later as adjustments have to be propagated trough the rest of the code!
################################################################################################################

# safeguard
if not __name__ == '__main__':
    exit(0)

sp.GLOBAL__EXPRESSIONS_TESTED = set()

# load all sasses
sass_50 = None
sass_75 = None
sass_80 = None
sass_70 = None
sass_86 = None
t1 = time.time()
# (ind, ind_count, sass, class_name, override=False, test=True, stop_on_exception=False, skip_tested=True)
# run individual sass# (immConstOffset & 0x3) == 0
if not sass_50: sass_50=SM_SASS(50)
SASS_Expr_Domain_Calc.collect_domains_str(1, 1, sass_50, 'BConst_IADD3', True, True, True, True)

# (Sb_bank >= 24 && Sb_bank <= 31) -> (Sb_addr <= 255)
if not sass_75: sass_75=SM_SASS(75)
SASS_Expr_Domain_Calc.collect_domains_str(2, 1, sass_75, 'bmov_dst64__C', True, True, True, True)

# ((dep_scbd & (1 << sbidx)) == 0)
if not sass_50: sass_50=SM_SASS(50)
SASS_Expr_Domain_Calc.collect_domains_str(15, 1, sass_50, 'DEPBAR_LE', True, True, True, True)

# (dst_wr_sb == 7)
if not sass_50: sass_50=SM_SASS(50)
SASS_Expr_Domain_Calc.collect_domains_str(16, 1, sass_50, 'AST', True, True, True, True)

# !(bpt == `BPTMode@TRAP && (sImm < 1 || sImm > 7))
if not sass_50: sass_50=SM_SASS(50)
SASS_Expr_Domain_Calc.collect_domains_str(20, 1, sass_50, 'BPT', True, True, True, True)

# ((sImm & 0x7) == 0)
if not sass_50: sass_50=SM_SASS(50)
SASS_Expr_Domain_Calc.collect_domains_str(21, 1, sass_50, 'PEXIT', True, True, True, True)

# ((Sb == 3088))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(22, 1, sass_70, 'ide_', True, True, True, True)

# (((idxsize == `IDXSIZE@U4_H0) || (idxsize == `IDXSIZE@U4_H1)) && ((mode == `MODE_scatter@THREAD))) -> (((vecidx == 0) || (vecidx == 1) || (vecidx == 2) || (vecidx == 3)))
if not sass_75: sass_75=SM_SASS(75)
SASS_Expr_Domain_Calc.collect_domains_str(35, 1, sass_75, 'scatter_', True, True, True, True)

# # (((idxsize == `IDXSIZE@U4_H0) || (idxsize == `IDXSIZE@U4_H1)) && ((mode == `MODE_scatter@QUAD))) -> (((vecidx == 0)))
# if not sass_75: sass_75=SM_SASS(75)
# SASS_Expr_Domain_Calc.collect_domains_str(36, 1, sass_75, 'scatter_', True, True, True, True)

# # (((idxsize == `IDXSIZE@U8)) && ((mode == `MODE_scatter@QUAD))) -> (((vecidx == 0) || (vecidx == 1) || (vecidx == 2) || (vecidx == 3) || (vecidx == 4) || (vecidx == 5) || (vecidx == 6) || (vecidx == 7) || (vecidx == 8) || (vecidx == 9) || (vecidx == 10) || (vecidx == 11) || (vecidx == 12) || (vecidx == 13) || (vecidx == 14) || (vecidx == 15)))
# if not sass_75: sass_75=SM_SASS(75)
# SASS_Expr_Domain_Calc.collect_domains_str(37, 1, sass_75, 'scatter_', True, True, True, True)

# (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0)))
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(3, 1, sass_80, 'scatter_', True, True, True, True)

# # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(4, 1, sass_80, 'scatter_', True, True, True, True)

# # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 0)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(5, 1, sass_80, 'scatter_', True, True, True, True)

# # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(6, 1, sass_80, 'scatter_', True, True, True, True)

# (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0)))
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(7, 1, sass_80, 'spmetadata_', True, True, True, True)

# # (((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 0)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(8, 1, sass_80, 'spmetadata_', True, True, True, True)

# # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 56) || (vecidx == 54) || (vecidx == 42) || (vecidx == 48) || (vecidx == 43) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 49) || (vecidx == 52) || (vecidx == 53) || (vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 28) || (vecidx == 29) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 51) || (vecidx == 39) || (vecidx == 38) || (vecidx == 59) || (vecidx == 58) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 33) || (vecidx == 55) || (vecidx == 32) || (vecidx == 57) || (vecidx == 50)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(9, 1, sass_80, 'scatter_', True, True, True, True)

# # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(10, 1, sass_80, 'scatter_', True, True, True, True)

# # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(11, 1, sass_80, 'scatter_', True, True, True, True)

# # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(12, 1, sass_80, 'spmetadata_', True, True, True, True)

# # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(13, 1, sass_80, 'spmetadata_', True, True, True, True)

# # (((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(14, 1, sass_80, 'spmetadata_', True, True, True, True)

# # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 0) || (vecidx == 4) || (vecidx == 8) || (vecidx == 119) || (vecidx == 120) || (vecidx == 121) || (vecidx == 122) || (vecidx == 123) || (vecidx == 124) || (vecidx == 125) || (vecidx == 126) || (vecidx == 127) || (vecidx == 118) || (vecidx == 59) || (vecidx == 58) || (vecidx == 55) || (vecidx == 54) || (vecidx == 57) || (vecidx == 56) || (vecidx == 51) || (vecidx == 50) || (vecidx == 53) || (vecidx == 52) || (vecidx == 115) || (vecidx == 114) || (vecidx == 88) || (vecidx == 89) || (vecidx == 111) || (vecidx == 110) || (vecidx == 113) || (vecidx == 112) || (vecidx == 82) || (vecidx == 83) || (vecidx == 80) || (vecidx == 81) || (vecidx == 86) || (vecidx == 87) || (vecidx == 84) || (vecidx == 85) || (vecidx == 3) || (vecidx == 7) || (vecidx == 108) || (vecidx == 109) || (vecidx == 102) || (vecidx == 103) || (vecidx == 100) || (vecidx == 101) || (vecidx == 106) || (vecidx == 107) || (vecidx == 104) || (vecidx == 105) || (vecidx == 39) || (vecidx == 38) || (vecidx == 33) || (vecidx == 32) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 64) || (vecidx == 65) || (vecidx == 66) || (vecidx == 67) || (vecidx == 68) || (vecidx == 69) || (vecidx == 2) || (vecidx == 6) || (vecidx == 99) || (vecidx == 98) || (vecidx == 91) || (vecidx == 90) || (vecidx == 93) || (vecidx == 92) || (vecidx == 95) || (vecidx == 94) || (vecidx == 97) || (vecidx == 96) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 117) || (vecidx == 116) || (vecidx == 48) || (vecidx == 49) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 42) || (vecidx == 43) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 5) || (vecidx == 9) || (vecidx == 77) || (vecidx == 76) || (vecidx == 75) || (vecidx == 74) || (vecidx == 73) || (vecidx == 72) || (vecidx == 71) || (vecidx == 70) || (vecidx == 79) || (vecidx == 78)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(17, 1, sass_80, 'scatter_', True, True, True, True)

# # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 56) || (vecidx == 54) || (vecidx == 42) || (vecidx == 48) || (vecidx == 43) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 49) || (vecidx == 52) || (vecidx == 53) || (vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 28) || (vecidx == 29) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 51) || (vecidx == 39) || (vecidx == 38) || (vecidx == 59) || (vecidx == 58) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 33) || (vecidx == 55) || (vecidx == 32) || (vecidx == 57) || (vecidx == 50)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(18, 1, sass_80, 'spmetadata_', True, True, True, True)

# # (((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(19, 1, sass_80, 'spmetadata_', True, True, True, True)

# (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq))) -> (((mdidx == 11) || (mdidx == 10) || (mdidx == 13) || (mdidx == 12) || (mdidx == 14) || (mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 9) || (mdidx == 8)) && ((vecidx6 == 0)))
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(23, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 6)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(24, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 2)) && ((vecidx6 == 56) || (vecidx6 == 54) || (vecidx6 == 42) || (vecidx6 == 48) || (vecidx6 == 43) || (vecidx6 == 60) || (vecidx6 == 61) || (vecidx6 == 62) || (vecidx6 == 63) || (vecidx6 == 49) || (vecidx6 == 52) || (vecidx6 == 53) || (vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 46) || (vecidx6 == 47) || (vecidx6 == 44) || (vecidx6 == 45) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 40) || (vecidx6 == 41) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 51) || (vecidx6 == 39) || (vecidx6 == 38) || (vecidx6 == 59) || (vecidx6 == 58) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30) || (vecidx6 == 37) || (vecidx6 == 36) || (vecidx6 == 35) || (vecidx6 == 34) || (vecidx6 == 33) || (vecidx6 == 55) || (vecidx6 == 32) || (vecidx6 == 57) || (vecidx6 == 50)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(25, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq))) -> (((mdidx == 11) || (mdidx == 10) || (mdidx == 12) || (mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 9) || (mdidx == 8)) && ((vecidx6 == 0)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(26, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 8)) && ((vecidx6 == 0)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(27, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 4)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(28, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq))) -> (((mdidx == 0)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(29, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@noseq))) -> (((mdidx == 0)) && ((vecidx6 == 56) || (vecidx6 == 54) || (vecidx6 == 42) || (vecidx6 == 48) || (vecidx6 == 43) || (vecidx6 == 60) || (vecidx6 == 61) || (vecidx6 == 62) || (vecidx6 == 63) || (vecidx6 == 49) || (vecidx6 == 52) || (vecidx6 == 53) || (vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 46) || (vecidx6 == 47) || (vecidx6 == 44) || (vecidx6 == 45) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 40) || (vecidx6 == 41) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 51) || (vecidx6 == 39) || (vecidx6 == 38) || (vecidx6 == 59) || (vecidx6 == 58) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30) || (vecidx6 == 37) || (vecidx6 == 36) || (vecidx6 == 35) || (vecidx6 == 34) || (vecidx6 == 33) || (vecidx6 == 55) || (vecidx6 == 32) || (vecidx6 == 57) || (vecidx6 == 50)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(30, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 4)) && ((vecidx6 == 1) || (vecidx6 == 0)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(31, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 0)) && ((vecidx6 == 0)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(32, 1, sass_80, 'genmetadata_', True, True, True, True)

# # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 0)) && ((vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(33, 1, sass_80, 'genmetadata_', True, True, True, True)

# (((Sb == 0)))
if not sass_86: sass_86=SM_SASS(86)
SASS_Expr_Domain_Calc.collect_domains_str(34, 1, sass_86, 'hadd2_F32i_', True, True, True, True)

print("Finished after {0}s".format(time.time() - t1))
