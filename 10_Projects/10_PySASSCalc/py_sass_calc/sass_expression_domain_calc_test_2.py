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
sass_70 = None
sass_50 = None
sass_80 = None
sass_90 = None
sass_75 = None
# (ind, ind_count, sass, class_name, override=False, test=True, stop_on_exception=False, skip_tested=True)

# # (((Rd) == `Register@RZ) || ((Rd) <= (%MAX_REG_COUNT - 1)))
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(2, 86, sass_50, 'AL2P', True, True, True, True)

# # (Ra != `Register@RZ)
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(4, 86, sass_50, 'ALD_PHYS', True, True, True, True)

# # ((ParamA != `ParamA@ARRAY_3D))
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(7, 86, sass_50, 'TMML', True, True, True, True)

# # (size == `SQInteger@32) -> (((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 1))
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(21, 86, sass_50, 'ATOM', True, True, True, True)

# # (constBank <= %MAX_CONST_BANK)
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(22, 86, sass_50, 'BConst_IADD3', True, True, True, True)

# # (((size == `SQInteger@U32) || (size == `SQInteger@S32) || (size == `SQInteger@U64)))
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(29, 86, sass_50, 'ATOM_CAS', True, True, True, True)

# # (dst_wr_sb == 7)
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(30, 86, sass_50, 'AST', True, True, True, True)

# # IsEven(((Rd) + ((Rd) == `Register@RZ)))
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(31, 86, sass_50, 'Const1_DFMA', True, True, True, True)

# # (((Rd) + ((Rd) == `Register@RZ)) % ARegAlignment(AInteger)) == 0
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(35, 86, sass_50, 'ALD', True, True, True, True)

# # (%SHADER_TYPE == $ST_UNKNOWN) || (%SHADER_TYPE == $ST_CS)
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(36, 86, sass_50, 'ATOMS', True, True, True, True)

# # ((srcfmt == `Integer@U8) || (srcfmt == `Integer@S8)) -> (dstfmt != `Float@F64)
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(55, 86, sass_50, 'Const_I2F', True, True, True, True)

# # !IsOdd(sbfmt)
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(56, 86, sass_50, 'Imm_VSHL', True, True, True, True)

# # Test <= `Test@T
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(57, 86, sass_50, 'Const1_FCMP', True, True, True, True)

# # ((((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)) > 2) -> ((((Rd) + ((Rd) == 255)) & 0x3) == 0)
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(58, 86, sass_50, 'TEX', True, True, True, True)

# # # ((((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)) == 2) -> ((((Rd) + ((Rd) == 255)) & 0x1) == 0)
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(59, 86, sass_50, 'TEX', True, True, True, True)

# # # (((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - (((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0))))
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(60, 86, sass_50, 'TEX', True, True, True, True)

# # (cctltop == `CCTLTOp@IVTH)
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(62, 86, sass_50, 'CCTLT_IDX', True, True, True, True)

# # # ((atom == `AtomOp@INC) -> ((size == `SQInteger@U32)))
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(63, 86, sass_50, 'ATOM', True, True, True, True)

# # # E -> IsEven(((Ra) + ((Ra) == `Register@RZ)))
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(65, 86, sass_50, 'ATOM', True, True, True, True)

# # # E -> (((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(66, 86, sass_50, 'ATOM', True, True, True, True)

# # ((size == `CASInteger@64) -> ((Rb == `Register@RZ) || (Rb % 4 == 0)))
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(67, 86, sass_50, 'ATOMS_CAS', True, True, True, True)

# # # ((size == `CASInteger@32) -> ((Rb % 2 == 0) && (Rb != `Register@RZ) && ((Rc == Rb + 1) || (Rc == `Register@RZ))))
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(68, 86, sass_50, 'ATOMS_CAS', True, True, True, True)

# # ((ftz == `FTZ@FTZ) -> (fmts == 10))
# if not sass_50: sass_50=SM_SASS(50)
# SASS_Expr_Domain_Calc.collect_domains_str(69, 86, sass_50, 'Const_F2F_1', True, True, True, True)

# # # (p == `POnly@P) -> (Rb == `Register@RZ)
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(70, 86, sass_50, 'ALD', True, True, True, True)

# # # ((atom == `AtomOp@AND) -> ((size == `SQInteger@U32) || (size == `SQInteger@S32) || (size == `SQInteger@U64)))
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(73, 86, sass_50, 'ATOM', True, True, True, True)

# # # (%SHADER_TYPE == $ST_UNKNOWN) || (%SHADER_TYPE != $ST_CS)
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(80, 86, sass_50, 'AL2P', True, True, True, True)

# # # (DC == `DC@DC) -> (ParamA != `ParamA@_3D)
# # if not sass_50: sass_50=SM_SASS(50)
# # SASS_Expr_Domain_Calc.collect_domains_str(84, 86, sass_50, 'TEX', True, True, True, True)

# run individual sass# (((Rd) == `Register@RZ) || (((Rd) <= (%MAX_REG_COUNT - 1)) && ((Rd) != `Register@R254)))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(1, 86, sass_70, 'al2p__RaNonRZ', True, True, True, True)

# # DEFINED TABLES_opex_0(batch_t,usched_info)
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(3, 86, sass_70, 'al2p__RaNonRZ', True, True, True, True)

# (((Rb) + ((Rb) == `Register@RZ)) % 2) == 0
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(5, 86, sass_70, 'bmov_dst64__R', True, True, True, True)

# (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D))) -> ((((Ra) != `Register@RZ)) && (((Rb) != `Register@RZ)))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(6, 86, sass_70, 'tex_scr_', True, True, True, True)

# run individual sass# (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(117, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(118, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(163, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(164, 117, sass_70, 'tex_', True, True, True, True)

# # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@1D))) -> ((((Ra) != `Register@RZ)) && (((Rb) == `Register@RZ)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(183, 117, sass_70, 'tex_scr_', True, True, True, True)

# # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D))) -> ((((Ra) != `Register@RZ)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(244, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D))) -> ((((Ra) != `Register@RZ)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(258, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 3))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(259, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(260, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> ((((Ra) != `Register@RZ)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(261, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(331, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(332, 117, sass_70, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> ((((Ra) != `Register@RZ)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(333, 117, sass_70, 'tex_', True, True, True, True)

# (((sz == `AInteger@64))) -> (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 2))))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(8, 86, sass_70, 'ald__LOGICAL_RaRZ_default', True, True, True, True)

# # ((Ra) != `Register@RZ)
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(9, 86, sass_70, 'al2p__RaNonRZ', True, True, True, True)

# # (((sz == `AInteger@64))) -> (((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(10, 86, sass_70, 'ald__LOGICAL_RaRZ_default', True, True, True, True)

# ((cop != `COP@INVALID6) && (cop != `COP@INVALID7))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(11, 86, sass_70, 'atom__RaNonRZ', True, True, True, True)

# # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))) && ((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(12, 86, sass_70, 'tex_scr_', True, True, True, True)

# # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0) && ((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(13, 86, sass_70, 'tex_scr_', True, True, True, True)

# ((reuse_src_a == 1) || (reuse_src_b == 1)) -> ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(14, 86, sass_70, 'bmsk__RRR_RRR', True, True, True, True)

# (((dc == `DC@noDC)) && ((toff == `TOFF@PTP))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(15, 86, sass_70, 'tld4_', True, True, True, True)

# (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(16, 86, sass_70, 'atom_cas__RaNonRZ_CAS', True, True, True, True)

# # (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(17, 86, sass_70, 'atom_cas__RaNonRZ_CAS', True, True, True, True)

# ((reuse_src_a == 1)) -> ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(18, 86, sass_70, 'bmsk__RCR_RCR', True, True, True, True)

# ((Sb_bank <= 17) || (Sb_bank >= 24 && Sb_bank <= 31))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(19, 86, sass_70, 'bmov_dst64__C', True, True, True, True)

# (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64))) -> ((((Rb) != `Register@RZ)))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(20, 86, sass_70, 'atomg_cas__RaNonRZ', True, True, True, True)

# (%SHADER_TYPE == $ST_UNKNOWN) || ((%SHADER_TYPE == $ST_TRAP) || (%SHADER_TYPE == $ST_TI))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(24, 86, sass_70, 'ast__PATCH_RaNonRZOffset', True, True, True, True)

# # (((e == `E@E))) -> ((((Ra) != `Register@RZ)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(25, 86, sass_70, 'atom__RaNonRZ', True, True, True, True)

# (((dc == `DC@noDC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D))) -> ((((Ra) != `Register@RZ)) && (((Rb) != `Register@RZ)))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(32, 86, sass_70, 'tld4_scr_', True, True, True, True)

# ((Ra) == `Register@RZ)
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(33, 86, sass_70, 'al2p__RaRZ', True, True, True, True)

# (((pquad == `PQUAD@PQUAD))) -> (((cbu_state == `CBU_STATE_DIST@MACTIVE)))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(34, 86, sass_70, 'bmov_pquad__RCR', True, True, True, True)

# # (((dc == `DC@noDC)) && ((toff == `TOFF@AOFFI))) -> ((((Rb) != `Register@RZ)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(38, 86, sass_70, 'tld4_', True, True, True, True)

# # (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@S64) || (sz == `REDATOMSIZE@F64.RN))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(39, 86, sass_70, 'atom__RaNonRZ', True, True, True, True)

# # (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@S64) || (sz == `REDATOMSIZE@F64.RN))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(40, 86, sass_70, 'atom__RaNonRZ', True, True, True, True)

# ((reuse_src_a == 1) || (reuse_src_b == 1) || (reuse_src_c == 1)) -> ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(41, 86, sass_70, 'dfma__RRR_RRR', True, True, True, True)

# (((Ra@negate == 1))) -> (((Sb@negate == 0)))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(42, 86, sass_70, 'iadd3_noimm__RCR_RCR', True, True, True, True)

# # (((dc == `DC@noDC)) && ((toff == `TOFF@PTP))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(43, 86, sass_70, 'tld4_', True, True, True, True)

# # ((wmsk == 1) || (wmsk == 2) || (wmsk == 3) || (wmsk == 4) || (wmsk == 5) || (wmsk == 6) || (wmsk == 7) || (wmsk == 8) || (wmsk == 9) || (wmsk == 10) || (wmsk == 11) || (wmsk == 12) || (wmsk == 13) || (wmsk == 14) || (wmsk == 15))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(44, 86, sass_70, 'tex_', True, True, True, True)

# # (((dc == `DC@DC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))) && ((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(45, 86, sass_70, 'tld4_scr_', True, True, True, True)

# # (((dc == `DC@DC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0) && ((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(46, 86, sass_70, 'tld4_scr_', True, True, True, True)

# (((Ra@invert == 1))) -> (((Sb@invert == 0)))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(47, 86, sass_70, 'iadd3_x_noimm__RCR_RCR', True, True, True, True)

# # (((op == `AtomsOp@INC) || (op == `AtomsOp@DEC))) -> (((sz == `REDATOMSIZE@U32) || (sz == `REDATOMSIZE@32)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(48, 86, sass_70, 'atom__RaNonRZ', True, True, True, True)

# (((op == `ATOMGOP_DIST@SAFEADD))) -> (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64)))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(49, 86, sass_70, 'atomg__RaNonRZ', True, True, True, True)

# # (((f16rm == `F16RM@nof16rm)) && ((wmsk == 3) || (wmsk == 5) || (wmsk == 6) || (wmsk == 7) || (wmsk == 9) || (wmsk == 10) || (wmsk == 11) || (wmsk == 12) || (wmsk == 13) || (wmsk == 14) || (wmsk == 15))) -> (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 2))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(50, 86, sass_70, 'tex_', True, True, True, True)

# # (((f16rm == `F16RM@nof16rm)) && ((wmsk == 3) || (wmsk == 5) || (wmsk == 6) || (wmsk == 7) || (wmsk == 9) || (wmsk == 10) || (wmsk == 11) || (wmsk == 12) || (wmsk == 13) || (wmsk == 14) || (wmsk == 15))) -> (((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(51, 86, sass_70, 'tex_', True, True, True, True)

# # (((f16rm == `F16RM@nof16rm)) && ((wmsk == 15))) -> (((((Rd2) == `Register@RZ) || ((Rd2) <= %MAX_REG_COUNT - 2))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(52, 86, sass_70, 'tex_', True, True, True, True)

# # (((f16rm == `F16RM@nof16rm)) && ((wmsk == 15))) -> (((((Rd2) + ((Rd2) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(53, 86, sass_70, 'tex_', True, True, True, True)

# # ((op != `ATOMGOP_DIST@INVALID10) && (op != `ATOMGOP_DIST@INVALID11) && (op != `ATOMGOP_DIST@INVALID12) && (op != `ATOMGOP_DIST@INVALID13) && (op != `ATOMGOP_DIST@INVALID14) && (op != `ATOMGOP_DIST@INVALID15))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(54, 86, sass_70, 'atomg__RaNonRZ', True, True, True, True)

# # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@ARRAY_CUBE))) -> (((aoffi == `AOFFI@noaoffi)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(61, 86, sass_70, 'tex_', True, True, True, True)

# # (((op == `AtomsOp@ADD))) -> (((sz == `REDATOMSIZE@U32) || (sz == `REDATOMSIZE@32) || (sz == `REDATOMSIZE@S32) || (sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@F32.FTZ.RN) || (sz == `REDATOMSIZE@F16x2.RN) || (sz == `REDATOMSIZE@F64.RN)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(64, 86, sass_70, 'atom__RaNonRZ', True, True, True, True)

# # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC))) -> ((((Rb) != `Register@RZ)))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(71, 86, sass_70, 'tex_', True, True, True, True)

# ((sco != `MEMBAR_SCO@INVALID4) && (sco != `MEMBAR_SCO@INVALID6) && (sco != `MEMBAR_SCO@INVALID7))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(72, 86, sass_70, 'membar_', True, True, True, True)

# # (((aoffi == `AOFFI@AOFFI)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(74, 86, sass_70, 'tex_', True, True, True, True)

# # (((aoffi == `AOFFI@AOFFI)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(75, 86, sass_70, 'tex_', True, True, True, True)

# # ((paramA != `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@INVALID0) && (paramA != `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@INVALID2) && (paramA != `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@INVALID4) && (paramA != `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@INVALID6))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(76, 86, sass_70, 'tld4_', True, True, True, True)

# (((aoffi == `AOFFI@noaoffi)) && ((lc == `LC@nolc)) && ((paramA == `PARAMA_ARRAY_2D_ARRAY_1D_2D_1D@2D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(78, 86, sass_70, 'txd_', True, True, True, True)

# # (((aoffi == `AOFFI@noaoffi)) && ((lc == `LC@nolc)) && ((paramA == `PARAMA_ARRAY_2D_ARRAY_1D_2D_1D@2D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(79, 86, sass_70, 'txd_', True, True, True, True)

# (((sz == `ATOMCASSZ@32) || (sz == `ATOMCASSZ@U32) || (sz == `ATOMCASSZ@S32))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
if not sass_70: sass_70=SM_SASS(70)
SASS_Expr_Domain_Calc.collect_domains_str(81, 86, sass_70, 'suatom_cas_imm_', True, True, True, True)

# # (((sz == `ATOMCASSZ@32) || (sz == `ATOMCASSZ@U32) || (sz == `ATOMCASSZ@S32))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(82, 86, sass_70, 'suatom_cas_imm_', True, True, True, True)

# # ((op != `AtomsOp@INVALID9) && (op != `AtomsOp@INVALID10) && (op != `AtomsOp@INVALID11) && (op != `AtomsOp@INVALID12) && (op != `AtomsOp@INVALID13) && (op != `AtomsOp@INVALID14) && (op != `AtomsOp@INVALID15))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(83, 86, sass_70, 'atom__RaNonRZ', True, True, True, True)

# # (%SHADER_TYPE == $ST_UNKNOWN) || ((%SHADER_TYPE == $ST_TRAP) || (%SHADER_TYPE == $ST_VSA) || (%SHADER_TYPE == $ST_VSB) || (%SHADER_TYPE == $ST_GS) || (%SHADER_TYPE == $ST_TS) || (%SHADER_TYPE == $ST_TI))
# if not sass_70: sass_70=SM_SASS(70)
# SASS_Expr_Domain_Calc.collect_domains_str(85, 86, sass_70, 'al2p__RaNonRZ', True, True, True, True)

# (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@1D))) -> ((((Ra) != `Register@RZ)))
if not sass_75: sass_75=SM_SASS(75)
SASS_Expr_Domain_Calc.collect_domains_str(325, 117, sass_75, 'tex_', True, True, True, True)

# (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
if not sass_75: sass_75=SM_SASS(75)
SASS_Expr_Domain_Calc.collect_domains_str(380, 117, sass_75, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
# if not sass_75: sass_75=SM_SASS(75)
# SASS_Expr_Domain_Calc.collect_domains_str(381, 117, sass_75, 'tex_', True, True, True, True)

# # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> ((((Ra) != `Register@RZ)))
# if not sass_75: sass_75=SM_SASS(75)
# SASS_Expr_Domain_Calc.collect_domains_str(382, 117, sass_75, 'tex_', True, True, True, True)

# (((paramA == `TEXPARAMA@1D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> ((((Ra) != `Register@RZ)))
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(184, 117, sass_80, 'tex_', True, True, True, True)

# # (((paramA == `TEXPARAMA@2D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(247, 117, sass_80, 'tex_', True, True, True, True)

# # (((paramA == `TEXPARAMA@2D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(248, 117, sass_80, 'tex_', True, True, True, True)

# # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 3))))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(249, 117, sass_80, 'tex_', True, True, True, True)

# # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(250, 117, sass_80, 'tex_', True, True, True, True)

# # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> ((((Ra) != `Register@RZ)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(251, 117, sass_80, 'tex_', True, True, True, True)

# # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(252, 117, sass_80, 'tex_', True, True, True, True)

# # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(253, 117, sass_80, 'tex_', True, True, True, True)

# # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV))) -> ((((Ra) != `Register@RZ)))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(254, 117, sass_80, 'tex_', True, True, True, True)

# (%SHADER_TYPE == $ST_CS) ->  !(Sb_bank >= 8 && Sb_bank <= 31)
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(23, 86, sass_80, 'bmov_dst64__C', True, True, True, True)

# (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC@nolodlc))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(26, 86, sass_80, 'tex_scr_', True, True, True, True)

# # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC@nolodlc))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
# if not sass_80: sass_80=SM_SASS(80)
# SASS_Expr_Domain_Calc.collect_domains_str(27, 86, sass_80, 'tex_scr_', True, True, True, True)

# !DEFINED TABLES_mem_0_illegal_encodings(sem,sco,private)
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(37, 86, sass_80, 'atom__RaNonRZ', True, True, True, True)

# (((ofmt == `OFMT@F16_V2)))
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(77, 86, sass_80, 'hmul2__RC', True, True, True, True)

# (((srcfmt == `SRCFMT@E8M10) || (srcfmt == `SRCFMT@TF32)) && ((size == `SIZE_1688_16816_16832@16816))) -> (((id == 0) || (id == 1)))
if not sass_80: sass_80=SM_SASS(80)
SASS_Expr_Domain_Calc.collect_domains_str(86, 86, sass_80, 'hmma_sparse_', True, True, True, True)

# (((dstfmt == `FloatNo64@F32)) && ((size == `SIZE_64..2@64x8x16) || (size == `SIZE_64..2@64x8x8))) -> (((((Rc) == `Register@RZ) || ((Rc) <= %MAX_REG_COUNT - 4))))
if not sass_90: sass_90=SM_SASS(90)
SASS_Expr_Domain_Calc.collect_domains_str(28, 86, sass_90, 'hgmma_Ra_URb_Rc_', True, True, True, True)
