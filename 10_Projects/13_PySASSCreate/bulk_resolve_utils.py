import os
import sys
import re
import typing
import math
from py_sass import SM_SASS
from py_sass import SASS_Class
from py_sass import SASS_Class_Props
from py_sass_ext import SASS_Bits
from py_sass import TT_List, TT_Param, TT_Reg, TT_Instruction, TT_Func
from py_cubin import Instr_CuBin_Repr, Instr_CuBin_Param_RF, Instr_CuBin_Param_Attr, Instr_CuBin_Param_L
from py_cubin import Instr_CuBin
from py_sass import SM_Cu_Props
from py_sass import SM_Cu_Details
from py_cubin import SM_CuBin_Utils
from py_sass import SASS_Class, SASS_Class_Props
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
import _config as sp
import sass_create as sc
from kernel_w_loop_control_props import KernelWLoopControlProps

class ResolveUtils:
    @staticmethod
    def resolve_operands(kk_sm:KK_SM, main_class_name:str, main_enc_vals:dict, props:KernelWLoopControlProps) -> typing.Tuple[typing.List[typing.Tuple[str, dict]]]:
        instr:Instr_CuBin_Repr = Instr_CuBin_Repr.create_from_enc_vals(kk_sm.sass, 0, '0x0', '0x0', main_class_name, main_enc_vals)
        class_props:SASS_Class_Props = kk_sm.sass.sm.classes_dict[main_class_name].props

        if class_props.cash_has__rd and class_props.cash_has__wr: 
            b_type = 'rdwr'
        elif class_props.cash_has__rd: 
            b_type = 'rd'
        elif class_props.cash_has__wr: 
            b_type = 'wr'
        elif class_props.cash_has__wr_early: 
            # This is a subset of wr but may have to be reimplemented for Hopper and upwards
            pass
        
        if b_type not in ('rd', 'wr', 'rdwr', 'wr_early'): raise Exception(sp.CONST__ERROR_ILLEGAL)

        prequel_instructions = []
        format_tt:TT_Instruction = instr.class_.FORMAT
        
        # Some instructions don't have a destination operand. The ones that
        # do, will start with regs[1:], the others with regs[0:] => discard the destination operands.
        # They don't need to exist before the instruction
        p_arg:TT_Param|TT_List
        format_args = format_tt.regs
        instr_args = instr.universes[0]['regs']
        alias_and_size = class_props.alias_and_size

        alias_and_size = {a:(s if isinstance(s, int) else int(s(main_enc_vals))) for a,s in alias_and_size.items()}
        
        if not len(format_args) == len(instr_args):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

        for p_arg, i_arg in zip(format_args, instr_args):
            # The registers follow the following format:
            if isinstance(p_arg, TT_List):
                if not isinstance(i_arg, Instr_CuBin_Param_L): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                # For now, we assume that we don't have lists in the instructions we deal with here
                # === Memory access instruction ===
                # What kinds exactly?
                #  - all lists of stuff: [ZeroRegister(RZ):Ra + UImm(20/0)*:uImm]
                reg_first = False
                nz_reg_first = False
                for p_elem, i_elem in zip(p_arg.value, i_arg.param1):
                    # lists always contain TT_Param, ...Param_L always contain ...Param_RF
                    if not isinstance(p_elem, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    if not isinstance(i_elem, Instr_CuBin_Param_RF): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                    # TT_Param contain either TT_Reg or TT_Func
                    if isinstance(p_elem.value, TT_Reg):
                        reg_first = True
                        # If there is only a Zero(Uniform)Register preceding a potential immediate value in a list
                        # then the immediate value has to be a real offset, like 0x160, otherwise it can be 0x0
                        if p_elem.value.value not in ('ZeroRegister', 'ZeroUniformRegister'): 
                            nz_reg_first = True
                        else: nz_reg_first = False
                        prequel_instructions.extend(ResolveUtils.resolve_register_operand(kk_sm, p_elem, i_elem, True, props, alias_and_size))
                    elif isinstance(p_elem.value, TT_Func):
                        # This one is an address offset => necessary to set such that it's not an overflow
                        # but it won't generate prequel instructions
                        f_alias = p_elem.value.alias
                        # The alias has to be part of the enc_vals, otherwise it's an undefined situation
                        if not f_alias in main_enc_vals: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                        # Since this is an address inside of a list, we also have to have encountered a register first.
                        # It's always a base register + some offset... Thus, the offset can be 0x0
                        if not (reg_first or nz_reg_first): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                        # If the previous register was RZ or URZ, the offset has to be directly onto the address of the memory segment
                        if not nz_reg_first: val = props.control_base_offset
                        else: val = 0x0
                        main_enc_vals = SM_CuBin_Utils.overwrite_helper(val=val, val_str=f_alias, enc_vals=main_enc_vals)
                    else: 
                        raise Exception(sp.CONST__ERROR_UNEXPECTED)

            elif isinstance(p_arg, TT_Param) and isinstance(p_arg.value, TT_Reg):
                # What kinds exactly?
                #  => in both instances RegisterFAU:Rd and C:srcConst are a [RegisterName]:[AliasName] pair
                # reg_vals[str(i.alias)] = set(int(x) for x in i.value.get_domain({}))
                if len(p_arg.attr) > 0:
                    if not isinstance(i_arg, Instr_CuBin_Param_Attr): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    
                    for p_attr, i_attr in zip(p_arg.attr, [i_arg.param1, i_arg.param2]):
                        # === Memory access instruction ===
                        #  - registers with attributs: C:srcConst[UImm(5/0*):constBank]*[ZeroRegister(RZ):Ra+SImm(17)*:immConstOffset]
                        # Attributs are always lists of things and the lists always contain TT_Param
                        # We have to make sure that all entries in the attributes listings exist
                        if not isinstance(p_attr, TT_List): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    
                        reg_first = False
                        nz_reg_first = False
                        for attr_pos, (p_elem, i_elem) in enumerate(zip(p_attr.value, i_attr)):
                            if not isinstance(p_elem, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                            if not isinstance(i_elem, Instr_CuBin_Param_RF): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                            # TT_Param contain either TT_Reg or TT_Func
                            if isinstance(p_elem.value, TT_Reg):
                                reg_first = True
                                # If there is only a Zero(Uniform)Register preceding a potential immediate value in a list
                                # then the immediate value has to be a real offset, like 0x160, otherwise it can be 0x0
                                if p_elem.value.value not in ('ZeroRegister', 'ZeroUniformRegister'): 
                                    nz_reg_first = True
                                else: nz_reg_first = False
                                prequel_instructions.extend(ResolveUtils.resolve_register_operand(kk_sm, p_elem, i_elem, True, props, alias_and_size))
                            elif isinstance(p_elem.value, TT_Func):
                                # This one is an address offset => necessary to set such that it's not an overflow
                                # but it won't generate a prequel instruction. We can simply modify the enc_vals
                                f_alias = p_elem.value.alias
                                # The alias has to be part of the enc_vals, otherwise it's an undefined situation
                                if not f_alias in main_enc_vals: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                                
                                # Since this is an address inside of a list, we also have to have encountered a register first.
                                # It's always a base register + some offset... Thus, the offset can be 0x0
                                # NOTE: this turned out to be an incorrect assumption: there is a weird instruction class 'ttust_'
                                #    @PT [TTUST] ttuAddr[UImm(0x20aa)], R36, RZ
                                # >>> if not (reg_first or nz_reg_first): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                                # The memory banks are sufficiently taken care of
                                if f_alias in class_props.const_bank_address: pass

                                val = 0x0
                                main_enc_vals = SM_CuBin_Utils.overwrite_helper(val=val, val_str=f_alias, enc_vals=main_enc_vals)
                            else: 
                                raise Exception(sp.CONST__ERROR_UNEXPECTED)
                else:
                    # === Instruction needs values ===
                    # If we have attributes, this one will point to C:srcConst (or equivalent) and we don't need this part
                    # otherwise, we have a regular instruction operand of the kind
                    #  - regular registers: RegisterFAU:Ra

                    # BAR instructions with two registers:
                    #  - assume: Ra == barrier to wait for
                    #  - assume: Rb == number of threads to wait for
                    if not isinstance(i_arg, Instr_CuBin_Param_RF): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    prequel_instructions.extend(ResolveUtils.resolve_register_operand(kk_sm, p_arg, i_arg, False, props, alias_and_size))
            elif isinstance(p_arg, TT_Param) and isinstance(p_arg.value, TT_Func):
                # This one is just a random number => nothing to do, but case is covered
                pass
            else: 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return prequel_instructions

    @staticmethod
    def resolve_register_operand(kk_sm:KK_SM, p_arg:TT_Param, i_arg:Instr_CuBin_Param_RF, is_address:bool, props:KernelWLoopControlProps, alias_and_size:dict) -> typing.List[typing.Tuple[str, dict]]:
        if not isinstance(p_arg, TT_Param): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i_arg, Instr_CuBin_Param_RF): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(p_arg.value, TT_Reg|TT_Func): raise Exception(sp.CONST__ERROR_ILLEGAL)

        # Don't do anything for the destination
        if isinstance(p_arg.value, TT_Reg) and p_arg.alias and (str(p_arg.alias).endswith('d') or str(p_arg.alias).endswith('2')): return []

        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15
        PT = kk_sm.regs.Predicate__PT__7
        UPT = kk_sm.regs.UniformPredicate__UPT__7

        res = []
        if p_arg.value.value in ('Register', 'NonZeroRegister', 'ZeroRegister'):
            # We should not have RZ and a NonZeroRegister type
            if p_arg.value.value == 'NonZeroRegister' and i_arg.value.d == props.RZ_num: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if p_arg.value.value == 'ZeroRegister' and i_arg.value.d != props.RZ_num: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # Selector for the register value: if we have 255, it's register RZ and not R255!
            # Also, RZ is a constant, no need to generate data for that one
            if i_arg.value.d < props.RZ_num: 
                val_str:str = str(i_arg.value.d)
                target_reg:tuple = getattr(kk_sm.regs, 'Register__R{0}__{1}'.format(val_str, i_arg.value.d))

                if not is_address:
                    prequel = sc.SASS_KK__MOVImm(kk_sm, 
                                    exec_pred_inv=False, exec_pred=PT, 
                                    target_reg=target_reg, imm_val=12,
                                    usched_info_reg=wait15)

                    res.append((prequel.class_name, prequel.enc_vals))
                else:
                    prequel1 = sc.SASS_KK__MOVImm(kk_sm, 
                                    exec_pred_inv=False, exec_pred=PT, 
                                    target_reg=target_reg, imm_val=props.ui_input_base_offset,
                                    usched_info_reg=wait15)
                    
                    # This is a memory access based on a regular register. We have to load the subsequent odd register
                    # with the base_address + 0x4 as well because of 64 bit issues
                    val_str_odd:str = str(i_arg.value.d+1)
                    target_reg_odd:tuple = getattr(kk_sm.regs, 'Register__R{0}__{1}'.format(val_str_odd, i_arg.value.d+1))
                    prequel2 = sc.SASS_KK__MOVImm(kk_sm, 
                                    exec_pred_inv=False, exec_pred=PT, 
                                    target_reg=target_reg_odd, imm_val=props.ui_input_base_offset+0x4,
                                    usched_info_reg=wait15)

                    res.append((prequel1.class_name, prequel1.enc_vals))
                    res.append((prequel2.class_name, prequel2.enc_vals))

        elif p_arg.value.value == 'Predicate':
            # Selector for the register value: if we have 7, it's register PT and not P7!
            # Also, PT is a constant, no need to generate data for this one
            if i_arg.value.d < props.PT_num: 
                val_str:str = str(i_arg.value.d)
                # Set this one to True
                target_pred:tuple = getattr(kk_sm.regs, 'Predicate__P{0}__{1}'.format(val_str, i_arg.value.d))

                if not is_address:
                    src_reg = kk_sm.regs.Register__R20__20
                    prequel1 = sc.SASS_KK__MOVImm(kk_sm, 
                                    exec_pred_inv=False, exec_pred=PT, 
                                    target_reg=src_reg, imm_val=12,
                                    usched_info_reg=wait15)
                    prequel2 = sc.SASS_KK__ISETP_RsIR_RIR(kk_sm, target_pred=target_pred, 
                                                        aux_pred=PT, reg=src_reg, imm=10,
                                                        comp_op=kk_sm.regs.ICmpAll__GT__4, fmt=kk_sm.regs.FMT__S32__1,
                                                        bop_op=kk_sm.regs.Bop__AND__0, 
                                                        invert_Pp=False, Pp=PT,
                                                        usched_info_reg=wait15)
                    
                    res.append((prequel1.class_name, prequel1.enc_vals))
                    res.append((prequel2.class_name, prequel2.enc_vals))
                else:
                    raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        elif p_arg.value.value == 'UniformPredicate':
            # Selector for the register value: if we have 7, it's register PT and not P7!
            # Also, UPT is a constant, no need to generate data for this one
            if i_arg.value.d < props.UPT_num: 
                val_str:str = str(i_arg.value.d)
                # Set this one to True
                utarget_pred:tuple = getattr(kk_sm.regs, 'UniformPredicate__UP{0}__{1}'.format(val_str, i_arg.value.d))

                if not is_address:
                    src_ureg:tuple = kk_sm.regs.UniformRegister__UR20__20
                    prequel1 = sc.SASS_KK__UMOVImm(kk_sm, 
                                    negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7,
                                    target_ureg=src_ureg, imm_val=12,
                                    usched_info_reg=wait15)
                    prequel2 = sc.SASS_KK__uisetp__URsIUR_URIR(kk_sm, negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7,
                                                            target_UPu=utarget_pred, src_URa=src_ureg, 
                                                            icmp=kk_sm.regs.ICmpAll__GT__4, fmt=kk_sm.regs.FMT__S32__1,
                                                            src_imm_val=10, usched_info_reg=wait15)

                    res.append((prequel1.class_name, prequel1.enc_vals))
                    res.append((prequel2.class_name, prequel2.enc_vals))
                else:
                    raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        elif p_arg.value.value in ('UniformRegister', 'NonZeroUniformRegister',):
            # We should not have RZ and a NonZeroRegister type
            if p_arg.value.value == 'NonZeroUniformRegister' and i_arg.value.d == props.URZ_num: 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # Selector for the register value: if we have 255, it's register RZ and not R255!
            # Also URZ is a constant, no need to generate data for that one
            if i_arg.value.d < props.URZ_num: 
                val_str:str = str(i_arg.value.d)
                target_ureg:tuple = getattr(kk_sm.regs, 'UniformRegister__UR{0}__{1}'.format(val_str, i_arg.value.d))

                if not is_address:
                    prequel = sc.SASS_KK__UMOVImm(kk_sm, 
                                    negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7,
                                    target_ureg=target_ureg, imm_val=12,
                                    usched_info_reg=wait15)

                    res.append((prequel.class_name, prequel.enc_vals))
                else:
                    # This is an address, we require something valid, like uniform_input_base_reg
                    # Move the value of that one into the one we have
                    # This is the size of the current operand.
                    # NOTE: all registers involved in one operand should be based on the same size. At least this is what it looks like...
                    cur_size = alias_and_size[str(p_arg.alias)]
                    if cur_size not in (64, 32, 16, 8): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    
                    # point the UR(eg) onto the correct location with the required size
                    # Note, that we can't simply use the regular ULDC because that one also accesses some memory...
                    prequel = sc.SASS_KK__UMOVImm(
                        kk_sm, negate_upred=False, upred=UPT,
                        target_ureg=target_ureg, imm_val=0x0, usched_info_reg=wait15
                    )
                    # prequel = sc.SASS_KK__ULDC(kk_sm, 
                    #         uniform_reg=target_ureg, 
                    #         m_offset=props.ui_input_base_offset, 
                    #         size=cur_size,
                    #         usched_info_reg=wait15)

                    res.append((prequel.class_name, prequel.enc_vals))
        elif p_arg.value.value in ('PARAMA_2D_3D', 'COMP_STATUSONLY', 'TEXPARAMA', 
                                   'PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D', 'PARAMA_ARRAY_2D_ARRAY_1D_2D_1D_3D',
                                   'PARAMA_ARRAY_2D_ARRAY_1D_2D_1D', 'TXQQUERY'):
            # These are special, constant configuration registers. Cover them, but no need to do anything with it
            pass
        elif p_arg.value.value in ('SpecialRegister'):
            # These are special registers that should access some value. Cover them, but no need to do anything special with them.
            # The assumption is, that they already contain some value.
            pass
        else: 
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return res
