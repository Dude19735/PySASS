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
    def resolve_operands(kk_sm:KK_SM, main_class_name:str, main_enc_vals:dict, props:KernelWLoopControlProps) -> typing.Tuple[typing.List[typing.Tuple[str, dict]], typing.Dict[str, SASS_Bits]]:
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

        # p_arg: 'p' for..., hmmmm, parametric?
        # i_arg: 'i' for 'instruction' as in 'decoded instruction' :-P
        for arg_ind, (p_arg, i_arg) in enumerate(zip(format_args, instr_args)):
            # The registers follow the following format:
            if isinstance(p_arg, TT_List):
                if not isinstance(i_arg, Instr_CuBin_Param_L): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                pr_instr, main_enc_vals = ResolveUtils.resolve_memory_operand_pure_list(kk_sm, main_enc_vals, instr.class_, arg_ind, p_arg, i_arg, props, alias_and_size)
                prequel_instructions.extend(pr_instr)

            elif isinstance(p_arg, TT_Param) and isinstance(p_arg.value, TT_Reg):
                # What kinds exactly?
                #  => in both instances RegisterFAU:Rd and C:srcConst are a [RegisterName]:[AliasName] pair
                # reg_vals[str(i.alias)] = set(int(x) for x in i.value.get_domain({}))
                if len(p_arg.attr) > 0:
                    if not isinstance(i_arg, Instr_CuBin_Param_Attr): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                    if len(p_arg.attr) == 1:
                        # single attribute operand
                        pr_instr, main_enc_vals = ResolveUtils.resolve_memory_operand_single_attrib(kk_sm, main_enc_vals, instr.class_, arg_ind, 
                                                                                                      p_arg.attr[0], i_arg.param1, 
                                                                                                      props, alias_and_size)
                        prequel_instructions.extend(pr_instr)
                    if len(p_arg.attr) == 2:
                        # double attribute operand
                        pr_instr, main_enc_vals = ResolveUtils.resolve_memory_operand_double_attrib(kk_sm, main_enc_vals, 
                                                                                                      instr.class_, arg_ind, 
                                                                                                      p_arg.attr[0], i_arg.param1,
                                                                                                      p_arg.attr[1], i_arg.param2,
                                                                                                      props, alias_and_size)
                        prequel_instructions.extend(pr_instr)
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

        return prequel_instructions, main_enc_vals
    
    @staticmethod
    def resolve_mem_access_pattern(kk_sm:KK_SM, main_enc_vals:dict, 
                                   class_:SASS_Class, arg_ind:int, 
                                   p_arg:TT_List, i_arg:typing.List[Instr_CuBin_Param_RF], 
                                   props:KernelWLoopControlProps, alias_and_size:dict) -> typing.List[typing.Tuple[str, dict]]:
        if not isinstance(p_arg, TT_List): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i_arg, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(pp, Instr_CuBin_Param_RF) for pp in i_arg): raise Exception(sp.CONST__ERROR_ILLEGAL)
        # Get the current access pattern...
        #   for example: {'NonZeroRegister', 'SImm', 'UniformRegister'}
        mem_access_pattern = set([i.value.value for i in p_arg.value])
        # ...and the entire access pattern for the current class
        #   for example: access_ops = [('list_1', <py_sass._tt_terms.TT_List object at 0x7351d32c0140>, ('NonZeroRegister', 'UniformRegister', 'SImm'))]
        #            access_pattern = [{'NonZeroRegister', 'SImm', 'UniformRegister'}]
        access_ops, access_pattern = kk_sm.sass.get_class_mem_access_patterns(class_)
        
        # Compare them and isolate the correct match. 
        # NOTE: we get arg_ind that corresponds to the overall-index of the current operand. 
        # NOTE: double attribute operands only count as one index.
        # NOTE: attribute operands contain stuff like attr_0.0, attr_0.1 => the first 0 has to be the same as the arg_ind, the second number
        #       is the index of the list in the attribute operand
        # NOTE: we match the pattern so that we know everything there is to know about the operand
        match = [ind for ind,p in enumerate(access_pattern) if mem_access_pattern == p and int(access_ops[ind][0].split('_')[-1].split('.')[0]) == arg_ind]
        if not match: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        index = match[0]

        is_first_attrib:bool = access_ops[index][0] == 'attr_{0}.0'.format(arg_ind)
        is_second_attrib:bool = access_ops[index][0] == 'attr_{0}.1'.format(arg_ind)
        is_list:bool = access_ops[index][0] == 'list_{0}'.format(arg_ind)

        if not (is_first_attrib or is_second_attrib or is_list): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # Check if we have some destination alias in here...
        # If we have memory access patterns, the alias are always source alias. For example
        # STG has Ra, URa, etc in their patterns, even if the memory access is techincally the destination
        list_tt_alias = [str(i.alias) for i in access_ops[index][1].value]
        if any(aa in class_.props.dst_names for aa in list_tt_alias): raise Exception(sp.CONST__ERROR_ILLEGAL)

        # Now we know everything. For example:
        #   mem_access_pattern = {'UImm', 'ZeroRegister'}
        #   str(access_ops[index][1])) = [ZeroRegister(RZ):Ra+UImm(32/0)*:Ra_offset]
        #    ...
        # Start figuring out the entires for all of them...
        # NOTE: really making sure we don't do ANYTHING we don't intent to is important!

        # Create a type map. For example
        #   type_map = {'ZeroRegister': 'Ra', 'UImm': 'Ra_offset'}
        # This helps with replacing stuff that is to come
        # NOTE: we know that this mapping can't fail, it's safe to access [0]
        type_map:dict = {aa:[str(i.value.alias) for i in access_ops[index][1].value if i.value.value == aa][0] for aa in access_ops[index][-1]}

        RZ = kk_sm.regs.Register__RZ__255
        PT = kk_sm.regs.Predicate__PT__7
        UPT = kk_sm.regs.UniformPredicate__UPT__7
        wait15 = kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15
        URZ = kk_sm.regs.UniformRegister__URZ__63
        R52 = kk_sm.regs.Register__R52__52
        R53 = kk_sm.regs.Register__R53__53
        UR52 = kk_sm.regs.UniformRegister__UR52__52
        UR53 = kk_sm.regs.UniformRegister__UR53__53

        prequel_instr = []
        if mem_access_pattern == {'NonZeroRegister', 'SImm'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                # Addresses are 64 bits: we really really need both of these. Otherwise we get a memory access error
                pc = sc.SASS_KK__MOVImm(kk_sm,exec_pred_inv=False, exec_pred=PT, target_reg=R52, imm_val=0x0, usched_info_reg=wait15, req=0x0)
                prequel_instr.append((pc.class_name, pc.enc_vals))
                pc = sc.SASS_KK__MOVImm(kk_sm,exec_pred_inv=False, exec_pred=PT, target_reg=R53, imm_val=0x0, usched_info_reg=wait15, req=0x0)
                prequel_instr.append((pc.class_name, pc.enc_vals))
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(R52, type_map['NonZeroRegister'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_offset, type_map['SImm'], main_enc_vals)
            elif is_list:
                pc = sc.SASS_KK__MOVImm(kk_sm,exec_pred_inv=False, exec_pred=PT, target_reg=R52, imm_val=0x0, usched_info_reg=wait15, req=0x0)
                prequel_instr.append((pc.class_name, pc.enc_vals))
                pc = sc.SASS_KK__MOVImm(kk_sm,exec_pred_inv=False, exec_pred=PT, target_reg=R53, imm_val=0x0, usched_info_reg=wait15, req=0x0)
                prequel_instr.append((pc.class_name, pc.enc_vals))
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(R52, type_map['NonZeroRegister'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_offset, type_map['SImm'], main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'NonZeroRegister', 'UniformRegister', 'SImm'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                pc = sc.SASS_KK__MOVImm(kk_sm,exec_pred_inv=False, exec_pred=PT, target_reg=R52, imm_val=0x0, usched_info_reg=wait15, req=0x0)
                prequel_instr.append((pc.class_name, pc.enc_vals))
                pc = sc.SASS_KK__MOVImm(kk_sm,exec_pred_inv=False, exec_pred=PT, target_reg=R53, imm_val=0x0, usched_info_reg=wait15, req=0x0)
                prequel_instr.append((pc.class_name, pc.enc_vals))
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(R52, type_map['NonZeroRegister'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_ureg, type_map['UniformRegister'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(0x0, type_map['SImm'], main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'NonZeroRegister', 'UniformRegister'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                pc = sc.SASS_KK__MOVImm(kk_sm,exec_pred_inv=False, exec_pred=PT, target_reg=R52, imm_val=0x0, usched_info_reg=wait15, req=0x0)
                prequel_instr.append((pc.class_name, pc.enc_vals))
                pc = sc.SASS_KK__MOVImm(kk_sm,exec_pred_inv=False, exec_pred=PT, target_reg=R53, imm_val=0x0, usched_info_reg=wait15, req=0x0)
                prequel_instr.append((pc.class_name, pc.enc_vals))
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(R52, type_map['NonZeroRegister'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_ureg, type_map['UniformRegister'], main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'NonZeroRegister'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'SImm', 'NonZeroUniformRegister'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'Register', 'SImm'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(RZ, type_map['Register'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_offset, type_map['SImm'], main_enc_vals)
            elif is_list:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(RZ, type_map['Register'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_offset, type_map['SImm'], main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'Register', 'UniformRegister', 'SImm'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(RZ, type_map['Register'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_ureg, type_map['UniformRegister'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(0x0, type_map['SImm'], main_enc_vals)
                
                # Some special things for this one
                if class_.class_name == 'ldgsts_memdesc_':
                    URXX = getattr(kk_sm.regs, 'UniformRegister__UR{0}__{0}'.format(props.ui_input_base_ureg[-1]+1))
                    main_enc_vals = SM_CuBin_Utils.overwrite_helper(URXX, 'Ra_URd', main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'ZeroRegister', 'SImm'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_offset, type_map['SImm'], main_enc_vals)
            elif is_list:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_offset, type_map['SImm'], main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'UImm'}:
            if is_first_attrib:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(0x0, type_map['UImm'], main_enc_vals)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'SImm'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'UniformRegister', 'SImm'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'UImm', 'UniformRegister'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'UniformRegister'}:
            if is_first_attrib:
                if class_.class_name == 'ldgsts_memdesc_':
                    # We cover this one on another place... leave it be, it is a weird one
                    pass
                else:
                    pc = sc.SASS_KK__umov__UR(kk_sm, negate_upred=False, upred=UPT, target_ureg=UR52, source_ureg=URZ, usched_info_reg=wait15)
                    prequel_instr.append((pc.class_name, pc.enc_vals))
                    pc = sc.SASS_KK__umov__UR(kk_sm, negate_upred=False, upred=UPT, target_ureg=UR53, source_ureg=URZ, usched_info_reg=wait15)
                    prequel_instr.append((pc.class_name, pc.enc_vals))
                    main_enc_vals = SM_CuBin_Utils.overwrite_helper(UR52, type_map['UniformRegister'], main_enc_vals)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'UImm', 'ZeroRegister'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_offset, type_map['UImm'], main_enc_vals)
            elif is_list:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_offset, type_map['UImm'], main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'ZeroRegister', 'UniformRegister', 'SImm'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_ureg, type_map['UniformRegister'], main_enc_vals)
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(0x0, type_map['SImm'], main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'ZeroRegister', 'UniformRegister'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                main_enc_vals = SM_CuBin_Utils.overwrite_helper(props.ui_input_base_ureg, type_map['UniformRegister'], main_enc_vals)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        elif mem_access_pattern == {'UImm', 'ZeroUniformRegister'}:
            if is_first_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_second_attrib:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            elif is_list:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            Instr_CuBin.check_expr_conditions(class_, main_enc_vals, throw=True)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return prequel_instr, main_enc_vals


    @staticmethod
    def resolve_memory_operand_pure_list(kk_sm:KK_SM, main_enc_vals:dict,
                                         class_:SASS_Class, arg_ind:int, 
                                         p_list:TT_List, i_list:Instr_CuBin_Param_L, 
                                         props:KernelWLoopControlProps, alias_and_size:dict) -> typing.List[typing.Tuple[str, dict]]:
        if not isinstance(p_list, TT_List): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i_list, Instr_CuBin_Param_L): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return ResolveUtils.resolve_mem_access_pattern(kk_sm, main_enc_vals, class_, arg_ind, p_list, i_list.param1, props, alias_and_size)
    
    @staticmethod
    def resolve_memory_operand_single_attrib(kk_sm:KK_SM, main_enc_vals:dict, 
                                             class_:SASS_Class, arg_ind:int, 
                                             p_param1:TT_List, i_param1:Instr_CuBin_Param_L, 
                                             props:KernelWLoopControlProps, alias_and_size:dict) -> typing.List[typing.Tuple[str, dict]]:
        if not isinstance(p_param1, TT_List): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i_param1, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(pp, Instr_CuBin_Param_RF) for pp in i_param1): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return ResolveUtils.resolve_mem_access_pattern(kk_sm, main_enc_vals, class_, arg_ind, p_param1, i_param1, props, alias_and_size)
    
    @staticmethod
    def resolve_memory_operand_double_attrib(kk_sm:KK_SM, main_enc_vals:dict, 
                                             class_:SASS_Class, arg_ind:int, 
                                             p_param1:TT_List, i_param1:Instr_CuBin_Param_L, 
                                             p_param2:TT_List, i_param2:Instr_CuBin_Param_L, 
                                             props:KernelWLoopControlProps, alias_and_size:dict) -> typing.List[typing.Tuple[str, dict]]:
        if not isinstance(p_param1, TT_List): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i_param1, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(pp, Instr_CuBin_Param_RF) for pp in i_param1): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(p_param2, TT_List): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i_param2, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(pp, Instr_CuBin_Param_RF) for pp in i_param2): raise Exception(sp.CONST__ERROR_ILLEGAL)
        bla1, main_enc_vals = ResolveUtils.resolve_mem_access_pattern(kk_sm, main_enc_vals, class_, arg_ind, p_param1, i_param1, props, alias_and_size)
        bla2, main_enc_vals = ResolveUtils.resolve_mem_access_pattern(kk_sm, main_enc_vals, class_, arg_ind, p_param2, i_param2, props, alias_and_size)
        return bla1 + bla2, main_enc_vals

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
