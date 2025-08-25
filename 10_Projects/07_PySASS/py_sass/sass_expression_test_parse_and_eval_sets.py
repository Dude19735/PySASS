from . import _sass_expression_ops as oo
from . import _config as sp
from ._sass_expression import SASS_Expr
from ._tt_instruction import TT_Instruction
from py_sass_ext import SASS_Bits
from .sass_parser_iter import SASS_Parser_Iter
from .sm_cu_details import SM_Cu_Details
from .sm_latency import OPERATION_SETS

"""
This is a testing part of the parser for the latencies.txt files.

It's not really working anymore with the current structure. Just the test cases are valid (so-to-speak)
"""

if not __name__ == '__main__':
    exit(0)

test_sets = """
    fxu_pipe = {ICMPfxu_pipe,ICMP,ISCADDfxu_pipe,ISCADD,ISCADD32Ifxu_pipe,ISCADD32I,IMNMXfxu_pipe,IMNMX,BFEfxu_pipe,BFE,BFIfxu_pipe,BFI,SHRfxu_pipe,SHR,SHLfxu_pipe,SHL,ISETfxu_pipe,ISET,ISETPfxu_pipe,ISETP,SHFfxu_pipe,SHF,IADD3fxu_pipe,IADDfxu_pipe,IADD32Ifxu_pipe,LOPfxu_pipe,LOP32Ifxu_pipe,LOP3fxu_pipe,XMADfxu_pipe,ISADfxu_pipe,ISAD,FFMAfxu_pipe,FFMA32Ifxu_pipe,FADDfxu_pipe,FADD32Ifxu_pipe,FMULfxu_pipe,FMUL32Ifxu_pipe,FCMPfxu_pipe,FCMP,FMNMXfxu_pipe,FMNMX,FSWZADDfxu_pipe,FSWZADD,FSETfxu_pipe,FSET,FSETPfxu_pipe,FSETP,FCHKfxu_pipe,FCHK,FSWZfxu_pipe,FSWZ,RROfxu_pipe,RRO,FCCOfxu_pipe,FCCO,MOVfxu_pipe,MOV32Ifxu_pipe,SELfxu_pipe,SEL,P2Rfxu_pipe,P2R,R2Pfxu_pipe,R2P,CSETfxu_pipe,CSET,CSETPfxu_pipe,CSETP,PSETfxu_pipe,PSET,PSETPfxu_pipe,PSETP,LEPCfxu_pipe,LEPC,VOTEfxu_pipe,VOTE,LEAfxu_pipe,LEA,SUCLAMPfxu_pipe,SUCLAMP,SUBFMfxu_pipe,SUBFM,SUEAUfxu_pipe,SUEAU,TEXDEPBARfxu_pipe,TEXDEPBAR,SHINTfxu_pipe,SHINT,VMAD8fxu_pipe,VMAD8,VADDfxu_pipe,VADD,VABSDIFFfxu_pipe,VABSDIFF,VMNMXfxu_pipe,VMNMX,VSETfxu_pipe,VSET,VSHLfxu_pipe,VSHL,VSHRfxu_pipe,VSHR,VSETPfxu_pipe,VSETP,VMAD16fxu_pipe,VADD2fxu_pipe,VADD2,VABSDIFF2fxu_pipe,VABSDIFF2,VMNMX2fxu_pipe,VMNMX2,VSET2fxu_pipe,VSET2,VSEL2fxu_pipe,VSEL2,VABSDIFF4fxu_pipe,VADD4fxu_pipe,VADD4,VMNMX4fxu_pipe,VMNMX4,VSET4fxu_pipe,VSET4,VSEL4fxu_pipe,VSEL4,CS2Rfxu_pipe,CS2R,IDEfxu_pipe,IDE,CCTLSfxu_pipe,CCTLS,SULDGAfxu_pipe,SULDGA,SUSTGAfxu_pipe,SUSTGA,LDUfxu_pipe,LDU,LDLKfxu_pipe,LDLK,STULfxu_pipe,STUL,STCULfxu_pipe,STCUL,STGAfxu_pipe,STGA,MOVIfxu_pipe,MOVI,SUQfxu_pipe,SUQ,DCHKfxu_pipe,DCHK, };
    fmai_pipe = {IADD3fmai_pipe,IADD3,IADDfmai_pipe,IADD,IADD32Ifmai_pipe,IADD32I,LOPfmai_pipe,LOP,LOP32Ifmai_pipe,LOP32I,LOP3fmai_pipe,LOP3,XMADfmai_pipe,XMAD,FFMAfmai_pipe,FFMA,FFMA32Ifmai_pipe,FFMA32I,FADDfmai_pipe,FADD,FADD32Ifmai_pipe,FADD32I,FMULfmai_pipe,FMUL,FMUL32Ifmai_pipe,FMUL32I,MOVfmai_pipe,MOV,MOV32Ifmai_pipe,MOV32I,PRMTfmai_pipe,PRMT,VMAD16fmai_pipe,VMAD16,VABSDIFF4fmai_pipe,VABSDIFF4, };
    mio_pipe = {IMADmio_pipe,IMAD,IMAD32Imio_pipe,IMAD32I,IMULmio_pipe,IMUL,IMUL32Imio_pipe,IMUL32I,IMADSPmio_pipe,IMADSP,POPCmio_pipe,POPC,FLOmio_pipe,FLO,DMNMXmio_pipe,DMNMX,DSETmio_pipe,DSET,DSETPmio_pipe,DSETP,MUFUmio_pipe,MUFU,IPAmio_pipe,IPA,IPAWmio_pipe,IPAW,IPAUmio_pipe,IPAU,IPASCmio_pipe,IPASC,F2Fmio_pipe,F2F,F2Imio_pipe,F2I,I2Fmio_pipe,I2F,I2Imio_pipe,I2I,I2I_RESTRICTEDmio_pipe,I2I_RESTRICTED,F2F64mio_pipe,F2F64,I2F64mio_pipe,I2F64,F2I64mio_pipe,F2I64,AL2Pmio_pipe,AL2P,STPmio_pipe,STP,SETCRSPTRmio_pipe,SETCRSPTR,GETCRSPTRmio_pipe,GETCRSPTR,SETLMEMBASEmio_pipe,SETLMEMBASE,GETLMEMBASEmio_pipe,GETLMEMBASE,S2Rmio_pipe,S2R,B2Rmio_pipe,B2R,R2Bmio_pipe,R2B,BARmio_pipe,BAR,VMADmio_pipe,VMAD,TEXmio_pipe,TEX,TEXSmio_pipe,TEXS,TLDmio_pipe,TLD,TLDSmio_pipe,TLDS,TLD4mio_pipe,TLD4,TLD4Smio_pipe,TLD4S,TMMLmio_pipe,TMML,TXAmio_pipe,TXA,TXDmio_pipe,TXD,TXQmio_pipe,TXQ,PIXLDmio_pipe,PIXLD,CCTLmio_pipe,CCTL,LDCmio_pipe,LDC,VILDmio_pipe,VILD,ALDmio_pipe,ALD,LDSmio_pipe,LDS,SHFLmio_pipe,SHFL,ISBERDmio_pipe,ISBERD,ATOMSmio_pipe,ATOMS,ASTmio_pipe,AST,STSmio_pipe,STS,OUTmio_pipe,OUT,MEMBARmio_pipe,MEMBAR,MEMBAR.CTAmio_pipe,MEMBAR.CTA,STGmio_pipe,STG,STLmio_pipe,STL,STmio_pipe,ST,REDmio_pipe,RED,SUSTmio_pipe,SUST,SUREDmio_pipe,SURED,LDGmio_pipe,LDG,LDLmio_pipe,LDL,LDmio_pipe,LD,ATOMmio_pipe,ATOM,CCTLLmio_pipe,CCTLL,SULDmio_pipe,SULD,SUATOMmio_pipe,SUATOM,SUCCTLmio_pipe,SUCCTL,CCTLTmio_pipe,CCTLT, };
    fma64lite_pipe = {DFMAfma64lite_pipe,DFMA,DADDfma64lite_pipe,DADD,DMULfma64lite_pipe,DMUL, };
    fe_pipe = {DEPBARfe_pipe,DEPBAR, };
    coupled_fe_pipe = {PMTRIGcoupled_fe_pipe,PMTRIG,VOTE.VTGcoupled_fe_pipe,VOTE.VTG,NOPcoupled_fe_pipe,NOP, };
    bru_pipe = {BRXbru_pipe,BRX,JMXbru_pipe,JMX,BRAbru_pipe,BRA,JMPbru_pipe,JMP,CALbru_pipe,CAL,JCALbru_pipe,JCAL,PRETbru_pipe,PRET,RETbru_pipe,RET,SSYbru_pipe,SSY,PBKbru_pipe,PBK,BRKbru_pipe,BRK,PCNTbru_pipe,PCNT,CONTbru_pipe,CONT,BPTbru_pipe,BPT,BPT.TRAPbru_pipe,BPT.TRAP,KILbru_pipe,KIL,EXITbru_pipe,EXIT,LONGJMPbru_pipe,LONGJMP,PLONGJMPbru_pipe,PLONGJMP,PEXITbru_pipe,PEXIT,SAMbru_pipe,SAM,RAMbru_pipe,RAM,RTTbru_pipe,RTT,RTT.FALLTHROUGHbru_pipe,RTT.FALLTHROUGH,SYNCbru_pipe,SYNC,WARPSYNCbru_pipe,WARPSYNC, };
    mixed_pipe = { VMAD, VMADmio_pipe };
    FXU_OPS = fxu_pipe + mixed_pipe + fe_pipe + coupled_fe_pipe;
    FMAI_OPS = fmai_pipe;
    FMALITE_OPS = fma64lite_pipe;
    BRU_OPS = bru_pipe + {BRX, BRXmio_pipe, JMX, JMXmio_pipe};
    MATH_OPS = FXU_OPS + FMAI_OPS + FMALITE_OPS;
    MIO_OPS = mio_pipe + bru_pipe - mixed_pipe;
    TEX_XU_OPS = {TEXmio_pipe,TEX,TEXSmio_pipe,TEXS,TLDmio_pipe,TLD,TLDSmio_pipe,
                    TLDS,TLD4mio_pipe,TLD4,TLD4Smio_pipe,TLD4S,TMMLmio_pipe,TMML,
                    TXAmio_pipe,TXA,TXDmio_pipe,TXD,TXQmio_pipe,TXQ,
                    POPCmio_pipe,POPC,FLOmio_pipe,FLO,MUFUmio_pipe,MUFU};
    MIO_FAST_OPS = MIO_OPS - TEX_XU_OPS;
    ALL_OPS = FXU_OPS + FMAI_OPS + FMALITE_OPS + MIO_OPS;
"""

expected_res = dict()
expected_res['fxu_pipe']= {'ICMPfxu_pipe','ICMP','ISCADDfxu_pipe','ISCADD','ISCADD32Ifxu_pipe','ISCADD32I','IMNMXfxu_pipe','IMNMX','BFEfxu_pipe','BFE','BFIfxu_pipe','BFI','SHRfxu_pipe','SHR','SHLfxu_pipe','SHL','ISETfxu_pipe','ISET','ISETPfxu_pipe','ISETP','SHFfxu_pipe','SHF','IADD3fxu_pipe','IADDfxu_pipe','IADD32Ifxu_pipe','LOPfxu_pipe','LOP32Ifxu_pipe','LOP3fxu_pipe','XMADfxu_pipe','ISADfxu_pipe','ISAD','FFMAfxu_pipe','FFMA32Ifxu_pipe','FADDfxu_pipe','FADD32Ifxu_pipe','FMULfxu_pipe','FMUL32Ifxu_pipe','FCMPfxu_pipe','FCMP','FMNMXfxu_pipe','FMNMX','FSWZADDfxu_pipe','FSWZADD','FSETfxu_pipe','FSET','FSETPfxu_pipe','FSETP','FCHKfxu_pipe','FCHK','FSWZfxu_pipe','FSWZ','RROfxu_pipe','RRO','FCCOfxu_pipe','FCCO','MOVfxu_pipe','MOV32Ifxu_pipe','SELfxu_pipe','SEL','P2Rfxu_pipe','P2R','R2Pfxu_pipe','R2P','CSETfxu_pipe','CSET','CSETPfxu_pipe','CSETP','PSETfxu_pipe','PSET','PSETPfxu_pipe','PSETP','LEPCfxu_pipe','LEPC','VOTEfxu_pipe','VOTE','LEAfxu_pipe','LEA','SUCLAMPfxu_pipe','SUCLAMP','SUBFMfxu_pipe','SUBFM','SUEAUfxu_pipe','SUEAU','TEXDEPBARfxu_pipe','TEXDEPBAR','SHINTfxu_pipe','SHINT','VMAD8fxu_pipe','VMAD8','VADDfxu_pipe','VADD','VABSDIFFfxu_pipe','VABSDIFF','VMNMXfxu_pipe','VMNMX','VSETfxu_pipe','VSET','VSHLfxu_pipe','VSHL','VSHRfxu_pipe','VSHR','VSETPfxu_pipe','VSETP','VMAD16fxu_pipe','VADD2fxu_pipe','VADD2','VABSDIFF2fxu_pipe','VABSDIFF2','VMNMX2fxu_pipe','VMNMX2','VSET2fxu_pipe','VSET2','VSEL2fxu_pipe','VSEL2','VABSDIFF4fxu_pipe','VADD4fxu_pipe','VADD4','VMNMX4fxu_pipe','VMNMX4','VSET4fxu_pipe','VSET4','VSEL4fxu_pipe','VSEL4','CS2Rfxu_pipe','CS2R','IDEfxu_pipe','IDE','CCTLSfxu_pipe','CCTLS','SULDGAfxu_pipe','SULDGA','SUSTGAfxu_pipe','SUSTGA','LDUfxu_pipe','LDU','LDLKfxu_pipe','LDLK','STULfxu_pipe','STUL','STCULfxu_pipe','STCUL','STGAfxu_pipe','STGA','MOVIfxu_pipe','MOVI','SUQfxu_pipe','SUQ','DCHKfxu_pipe','DCHK'}
expected_res['fmai_pipe'] = {'IADD3fmai_pipe','IADD3','IADDfmai_pipe','IADD','IADD32Ifmai_pipe','IADD32I','LOPfmai_pipe','LOP','LOP32Ifmai_pipe','LOP32I','LOP3fmai_pipe','LOP3','XMADfmai_pipe','XMAD','FFMAfmai_pipe','FFMA','FFMA32Ifmai_pipe','FFMA32I','FADDfmai_pipe','FADD','FADD32Ifmai_pipe','FADD32I','FMULfmai_pipe','FMUL','FMUL32Ifmai_pipe','FMUL32I','MOVfmai_pipe','MOV','MOV32Ifmai_pipe','MOV32I','PRMTfmai_pipe','PRMT','VMAD16fmai_pipe','VMAD16','VABSDIFF4fmai_pipe','VABSDIFF4'}
expected_res['mio_pipe'] = {'IMADmio_pipe','IMAD','IMAD32Imio_pipe','IMAD32I','IMULmio_pipe','IMUL','IMUL32Imio_pipe','IMUL32I','IMADSPmio_pipe','IMADSP','POPCmio_pipe','POPC','FLOmio_pipe','FLO','DMNMXmio_pipe','DMNMX','DSETmio_pipe','DSET','DSETPmio_pipe','DSETP','MUFUmio_pipe','MUFU','IPAmio_pipe','IPA','IPAWmio_pipe','IPAW','IPAUmio_pipe','IPAU','IPASCmio_pipe','IPASC','F2Fmio_pipe','F2F','F2Imio_pipe','F2I','I2Fmio_pipe','I2F','I2Imio_pipe','I2I','I2I_RESTRICTEDmio_pipe','I2I_RESTRICTED','F2F64mio_pipe','F2F64','I2F64mio_pipe','I2F64','F2I64mio_pipe','F2I64','AL2Pmio_pipe','AL2P','STPmio_pipe','STP','SETCRSPTRmio_pipe','SETCRSPTR','GETCRSPTRmio_pipe','GETCRSPTR','SETLMEMBASEmio_pipe','SETLMEMBASE','GETLMEMBASEmio_pipe','GETLMEMBASE','S2Rmio_pipe','S2R','B2Rmio_pipe','B2R','R2Bmio_pipe','R2B','BARmio_pipe','BAR','VMADmio_pipe','VMAD','TEXmio_pipe','TEX','TEXSmio_pipe','TEXS','TLDmio_pipe','TLD','TLDSmio_pipe','TLDS','TLD4mio_pipe','TLD4','TLD4Smio_pipe','TLD4S','TMMLmio_pipe','TMML','TXAmio_pipe','TXA','TXDmio_pipe','TXD','TXQmio_pipe','TXQ','PIXLDmio_pipe','PIXLD','CCTLmio_pipe','CCTL','LDCmio_pipe','LDC','VILDmio_pipe','VILD','ALDmio_pipe','ALD','LDSmio_pipe','LDS','SHFLmio_pipe','SHFL','ISBERDmio_pipe','ISBERD','ATOMSmio_pipe','ATOMS','ASTmio_pipe','AST','STSmio_pipe','STS','OUTmio_pipe','OUT','MEMBARmio_pipe','MEMBAR','MEMBAR.CTAmio_pipe','MEMBAR.CTA','STGmio_pipe','STG','STLmio_pipe','STL','STmio_pipe','ST','REDmio_pipe','RED','SUSTmio_pipe','SUST','SUREDmio_pipe','SURED','LDGmio_pipe','LDG','LDLmio_pipe','LDL','LDmio_pipe','LD','ATOMmio_pipe','ATOM','CCTLLmio_pipe','CCTLL','SULDmio_pipe','SULD','SUATOMmio_pipe','SUATOM','SUCCTLmio_pipe','SUCCTL','CCTLTmio_pipe','CCTLT'}
expected_res['fma64lite_pipe'] = {'DFMAfma64lite_pipe','DFMA','DADDfma64lite_pipe','DADD','DMULfma64lite_pipe','DMUL'}
expected_res['fe_pipe'] = {'DEPBARfe_pipe','DEPBAR'}
expected_res['coupled_fe_pipe'] = {'PMTRIGcoupled_fe_pipe','PMTRIG','VOTE.VTGcoupled_fe_pipe','VOTE.VTG','NOPcoupled_fe_pipe','NOP'}
expected_res['bru_pipe'] = {'BRXbru_pipe','BRX','JMXbru_pipe','JMX','BRAbru_pipe','BRA','JMPbru_pipe','JMP','CALbru_pipe','CAL','JCALbru_pipe','JCAL','PRETbru_pipe','PRET','RETbru_pipe','RET','SSYbru_pipe','SSY','PBKbru_pipe','PBK','BRKbru_pipe','BRK','PCNTbru_pipe','PCNT','CONTbru_pipe','CONT','BPTbru_pipe','BPT','BPT.TRAPbru_pipe','BPT.TRAP','KILbru_pipe','KIL','EXITbru_pipe','EXIT','LONGJMPbru_pipe','LONGJMP','PLONGJMPbru_pipe','PLONGJMP','PEXITbru_pipe','PEXIT','SAMbru_pipe','SAM','RAMbru_pipe','RAM','RTTbru_pipe','RTT','RTT.FALLTHROUGHbru_pipe','RTT.FALLTHROUGH','SYNCbru_pipe','SYNC','WARPSYNCbru_pipe','WARPSYNC'}
expected_res['mixed_pipe'] = {'VMAD','VMADmio_pipe'}
expected_res['FXU_OPS'] = expected_res['fxu_pipe'].union(expected_res['mixed_pipe']).union(expected_res['fe_pipe']).union(expected_res['coupled_fe_pipe'])
expected_res['FMAI_OPS'] = expected_res['fmai_pipe']
expected_res['FMALITE_OPS'] = expected_res['fma64lite_pipe']
expected_res['BRU_OPS'] = expected_res['bru_pipe'].union({'BRX','BRXmio_pipe','JMX','JMXmio_pipe'})
expected_res['MATH_OPS'] = expected_res['FXU_OPS'].union(expected_res['FMAI_OPS']).union(expected_res['FMALITE_OPS'])
expected_res['MIO_OPS'] = (expected_res['mio_pipe'].union(expected_res['bru_pipe'])).difference(expected_res['mixed_pipe'])
expected_res['TEX_XU_OPS'] = {'TEXmio_pipe','TEX','TEXSmio_pipe','TEXS','TLDmio_pipe','TLD','TLDSmio_pipe','TLDS','TLD4mio_pipe','TLD4','TLD4Smio_pipe','TLD4S','TMMLmio_pipe','TMML','TXAmio_pipe','TXA','TXDmio_pipe','TXD','TXQmio_pipe','TXQ','POPCmio_pipe','POPC','FLOmio_pipe','FLO','MUFUmio_pipe','MUFU'}
expected_res['MIO_FAST_OPS'] = expected_res['MIO_OPS'].difference(expected_res['TEX_XU_OPS'])
expected_res['ALL_OPS'] = expected_res['FXU_OPS'].union(expected_res['FMAI_OPS']).union(expected_res['FMALITE_OPS']).union(expected_res['MIO_OPS'])

# t_sets = OPERATION_SETS.set_parser(test_sets, {})

# eval_sets = dict()
# for i in range(0, len(t_sets), 2):
#     expr = SASS_Expr(t_sets[i+1], {},{},{},{},{})
#     expr.finalize({}, eval_sets)
#     eval_sets[t_sets[i+0]] = expr

# ex_sets = dict()
# for n,e in eval_sets.items():
#     ex_sets[n] = e({})

# for i in ex_sets:
#     assert(ex_sets[i] == expected_res[i])

pass
