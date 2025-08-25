import sys
import os
import copy
import termcolor as tc
from py_cubin import SM_CuBin_File
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
import _config as sp
import sass_create as sc

class ControlProps:
    BARRIER__RD = 'RD'
    BARRIER__WR = 'WR'
    BARRIER__RDWR = 'RDWR'
    BARRIER__WR_EARLY = 'WR_EARLY'

    def __init__(self, kk_sm:KK_SM,
                 min_required_instr_count:int, min_required_reg_count:int, template:str,
                 empty_instr:bool, json_file:str|None):
        if not isinstance(kk_sm, KK_SM): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(empty_instr, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(min_required_instr_count, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(min_required_reg_count, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        # Just leave this one out for now...
        if json_file is not None: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        URZ_num = max([getattr(kk_sm.regs,x)[-1] for x in dir(kk_sm.regs) if x.startswith('UniformRegister')])
        RZ_num = max([getattr(kk_sm.regs,x)[-1] for x in dir(kk_sm.regs) if x.startswith('Register')])
        PT_num = max([getattr(kk_sm.regs,x)[-1] for x in dir(kk_sm.regs) if x.startswith('Predicate')])
        UPT_num = max([getattr(kk_sm.regs,x)[-1] for x in dir(kk_sm.regs) if x.startswith('UniformPredicate')])

        self.sm_nr = kk_sm.sass.sm_nr
        t_location = os.path.dirname(os.path.realpath(__file__))

        if not os.path.exists(template):
            print(tc.colored("KernelControlProps must be located in a folder with a subfolder '/binaries' containing the template file [{0}]".format(template), 'red'))
            raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        # Wipe the file with NOPs from the beginning
        target_cubin = SM_CuBin_File(kk_sm.sass, template, wipe=True)
        if len(target_cubin[0]) < min_required_instr_count:
            print(tc.colored("Template file instruction count [{0}] < [{1}] minimal required instruction count.".format(template, min_required_instr_count), 'red'))

        nrc = target_cubin.reg_count()
        nnrc = {n:min_required_reg_count for n,k in nrc.items()}
        target_cubin.overwrite_reg_count(nnrc)

        # nop = sc.SASS_KK__NOP(kk_sm)
        # for i in range(0, len(target_cubin[0])):
        #     target_cubin.create_instr(0, i, nop.class_name, nop.enc_vals)

        self.__target_cubin:SM_CuBin_File = target_cubin
        self.__json_file:str|None = json_file
        self.__empty_instr:bool = empty_instr
        self.__URZ_num:int = URZ_num
        self.__RZ_num:int = RZ_num
        self.__PT_num:int = PT_num
        self.__UPT_num:int = UPT_num
    
    def target_cubin(self) -> SM_CuBin_File:
        return copy.copy(self.__target_cubin)
    @property
    def nr_kernels(self) -> int: return len(self.__target_cubin)
    @property
    def json_file(self) -> str: return self.__json_file
    @property
    def empty_instr(self) -> bool: return self.__empty_instr
    @property
    def URZ_num(self) -> int: return self.__URZ_num
    @property
    def RZ_num(self) -> int: return self.__RZ_num
    @property
    def PT_num(self) -> int: return self.__PT_num
    @property
    def UPT_num(self) -> int: return self.__UPT_num