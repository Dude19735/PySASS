import sys
import os
import typing
from py_cubin import SM_CuBin_File
from py_sass_ext import SASS_Bits
from py_sass import TT_List, TT_Param, TT_Reg, TT_Instruction, TT_Func
from py_cubin import Instr_CuBin_Repr, Instr_CuBin_Param_RF, Instr_CuBin_Param_Attr, Instr_CuBin_Param_L
from py_sass import SM_Cu_Props
from py_sass import SM_Cu_Details
from py_sass import SASS_Class, SASS_Class_Props
from py_cubin import SM_CuBin_Regs
from py_cubin import SM_CuBin_File

sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
from control_props import ControlProps
from helpers import Helpers
import sass_create as sc
import _config as sp

class BInstrBase:
    # use this one to call super().__init__ in derived classes without having to pass a finished class_name and enc_vals yet
    CONST__EARLY_BIRD = 'early_bird'

    def __init__(self, kk_sm:KK_SM, props:ControlProps, class_name:str, enc_vals:dict, resolve_operands:bool):
        if not isinstance(kk_sm, KK_SM): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(props, ControlProps): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not (props.empty_instr or (enc_vals and class_name) or (class_name==BInstrBase.CONST__EARLY_BIRD and not enc_vals)): raise Exception(sp.CONST__ERROR_ILLEGAL)

        self.__props = props
        self.__enc_vals = enc_vals
        self.__pre_clock_prequels = []
        self.__post_clock_prequels = []
        self.__pre_clock_sequels = []
        self.__post_clock_sequels = []
        if self.__props.empty_instr: 
            self.__class_name = 'empty_class_name'
            return

        self.__class_name = class_name

        if props.json_file is not None: 
            self.__restore_from_json(props.json_file)
            return
        if self.__enc_vals:
            self.__create_instruction(kk_sm, resolve_operands)

    @property
    def class_name(self): return self.__class_name
    @property
    def props(self): return self.__props
    @property
    def enc_vals(self): return self.__enc_vals
    @property
    def pre_clock_prequels(self): return self.__pre_clock_prequels
    @property
    def post_clock_prequels(self): return self.__post_clock_prequels
    @property
    def pre_clock_sequels(self): return self.__pre_clock_sequels
    @property
    def post_clock_sequels(self): return self.__post_clock_sequels

    def __restore_from_json(self, json_file):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        # with open(json_file, 'r') as f:
        #     json_str = f.read()
        #     instrs:dict = json.loads(json_str)
        
        # class_name:str = instrs['benchmarked_instr']['class_name']
        # self.class_name = class_name[class_name.find(' '):].strip()
        
        # enc_vals:dict = instrs['benchmarked_instr']['universes']['0']
        # self.__enc_vals = {k:SASS_Create_Utils.sass_bits_from_str(v) for k,v in enc_vals.items()}
        
        # prequels = [(i['instr']['class_name'], i['universes']['0']) for i in instrs['prequel']]
        # self.__prequels = [(i[0][i[0].find(' '):].strip(), {k:SASS_Create_Utils.sass_bits_from_str(v) for k,v in i[1].items()}) for i in prequels]

    def add_main(self, class_name:str, enc_vals:dict):
        """This one is to allow to call super().__init__ without having to pass a class already
        """
        self.__class_name = class_name
        self.__enc_vals = enc_vals

    def add_pre_clock_prequels(self, class_name:str, enc_vals:dict):
        self.__pre_clock_prequels.append((class_name, enc_vals))

    def add_pre_clock_prequels_to_target(self, kernel_index:int, i:int, target_cubin:SM_CuBin_File, prequel_inds:list) -> int:
        """Add the preparation for all operands of the instruction to benchmark
        """
        for pcn,pev in self.__pre_clock_prequels:
            target_cubin.create_instr(kernel_index, i, pcn, pev)    
            prequel_inds.append(i)
            i+=1
        return i
    
    def add_post_clock_prequels(self, class_name:str, enc_vals:dict):
        self.__post_clock_prequels.append((class_name, enc_vals))

    def add_post_clock_prequels_to_target(self, kernel_index, i:int, target_cubin:SM_CuBin_File, prequel_inds:list) -> int:
        """Add the preparation for all operands of the instruction to benchmark
        """
        for pcn,pev in self.__post_clock_prequels:
            target_cubin.create_instr(kernel_index, i, pcn, pev)    
            prequel_inds.append(i)
            i+=1
        return i

    def add_instr_to_target(self, kernel_index, i:int, target_cubin:SM_CuBin_File) -> typing.Tuple[int]:
        """Add the actual instruction to the benchmarking kernel
        """
        if self.__props.empty_instr: return i, -1

        target_cubin.create_instr(kernel_index, i, self.class_name, self.__enc_vals)
        i+=1
        return i, i
    
    def add_pre_clock_sequels(self, class_name:str, enc_vals:dict):
        self.__pre_clock_sequels.append((class_name, enc_vals))

    def add_pre_clock_sequels_to_target(self, kernel_index, i:int, target_cubin:SM_CuBin_File, pre_clock_sequel_inds:list) -> int:
        """Add the sequel operations for all operands of the instruction to benchmark
        """
        for pcn,pev in self.__pre_clock_sequels:
            target_cubin.create_instr(kernel_index, i, pcn, pev)    
            pre_clock_sequel_inds.append(i)
            i+=1
        return i

    def add_post_clock_sequels(self, class_name:str, enc_vals:dict):
        self.__post_clock_sequels.append((class_name, enc_vals))

    def add_post_clock_sequels_to_target(self, kernel_index, i:int, target_cubin:SM_CuBin_File, post_clock_sequel_inds:list) -> int:
        """Add the sequel operations for all operands of the instruction to benchmark
        """
        for pcn,pev in self.__post_clock_sequels:
            target_cubin.create_instr(kernel_index, i, pcn, pev)    
            post_clock_sequel_inds.append(i)
            i+=1
        return i

    ####################################################################################
    ####################################################################################
    ####################################################################################
    
    def __create_instruction(self, kk_sm:KK_SM, resolve_operands:bool):
        details:SM_Cu_Details = kk_sm.sass.sm.details
        regs:SM_CuBin_Regs = kk_sm.regs

        # Set the barrier to what we pass above.
        # First we have to find out the correct 'alias' for the barrier, since they can vary.
        # Luckily the SASS_Class_Props knows the correct one.
        class_:SASS_Class = kk_sm.sass.sm.classes_dict[self.__props.benchmark_class_name]
        class_props:SASS_Class_Props = class_.props
        if self.__props.benchmark_barrier_type == ControlProps.BARRIER__RD: 
            barrier_alias:str = class_props.cash_alias__rd
        elif self.__props.benchmark_barrier_type == ControlProps.BARRIER__WR: 
            barrier_alias:str = class_props.cash_alias__wr
        elif self.__props.benchmark_barrier_type == ControlProps.BARRIER__RDWR:
            # STG == store to global has an RD barrier 
            #   => write to memory (no dst operand) has a read-barrier
            #   => read from memory (has dst operand) has a write-barrier
            if class_props.has_dst: barrier_alias:str = class_props.cash_alias__wr
            else: barrier_alias:str = class_props.cash_alias__rd
        elif self.__props.benchmark_barrier_type == ControlProps.BARRIER__WR_EARLY:
            # This one is Hopper that we don't know anyways...
            raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        # Set the barrier that the benchmarked instruction will set
        enc_vals = Helpers.overwrite_helper(self.__props.benchmark_barrier_num_to_set, barrier_alias, enc_vals)

        # Also, really make sure that we don't wait for anything.
        # NOTE: there are some instructions that don't have the REQ thing, for example on
        # SM 86 the instruction class 'ttust_'.
        if class_props.cash_alias__req is not None:
            enc_vals = Helpers.overwrite_helper(0, class_props.cash_alias__req, enc_vals)

        # Also, make sure that the predicate is always PT and never negated
        if class_.FORMAT.pred is not None:
            enc_vals = Helpers.overwrite_helper(7, 'Pg', enc_vals)
            enc_vals = Helpers.overwrite_helper(0, 'Pg@not', enc_vals)

        # set to noreuse for now...
        if class_.props.has_reuse:
            for a,v in class_.enc_vals__reuse_regs.items(): 
                enc_vals[v['a']] = v['d']['reuse']

        # Set usched info to trans1.
        # We need this one because otherwise the whole barrier thing is a dud.
        # usched_info = regs.USCHED_INFO__WAIT1_END_GROUP__1[-1]
        enc_vals = Helpers.overwrite_helper(regs.USCHED_INFO__trans1__17, 'usched_info', enc_vals)

        if resolve_operands:
            u:Instr_CuBin_Repr = Instr_CuBin_Repr.create_from_enc_vals(kk_sm.sass, 0, '0x0', '0x0', self.class_name, enc_vals)
            self.__enc_vals, self.__pre_clock_prequels = BInstrBase.__resolve_operands(kk_sm, self.__props.benchmark_barrier_type, u, enc_vals, self.__props)

    ####################################################################################
    ####################################################################################
    ####################################################################################

    @staticmethod
    def __resolve_operands(kk_sm:KK_SM, b_type:str, instr:Instr_CuBin_Repr, enc_vals:dict, data:ControlProps) -> typing.Tuple[dict, typing.List[typing.Tuple[str, dict]]]:
        if b_type not in ('rd', 'wr', 'rdwr', 'wr_early'): raise Exception(sp.CONST__ERROR_ILLEGAL)

        prequel_instructions = []
        format_tt:TT_Instruction = instr.class_.FORMAT
        
        # Some instructions don't have a destination operand. The ones that
        # do, will start with regs[1:], the others with regs[0:] => discard the destination operands.
        # They don't need to exist before the instruction
        has_dst:bool = instr.class_.props.has_dst
        p_arg:TT_Param|TT_List
        start_from:int = (1 if has_dst else 0)
        format_args = format_tt.regs[start_from:]
        instr_args = instr.universes[0]['regs'][start_from:]

        if not (len(format_args) == len(instr_args)):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

        for p_arg, i_arg in zip(format_args, instr_args):
            # The registers follow the following format:
            if isinstance(p_arg, TT_List):
                if not isinstance(i_arg, Instr_CuBin_Param_L): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
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
                        prequel_instructions.extend(BInstrBase.resolve_register_operand(kk_sm, has_dst, p_elem, i_elem, True, data))
                    elif isinstance(p_elem.value, TT_Func):
                        # This one is an address offset => necessary to set such that it's not an overflow
                        # but it won't generate prequel instructions
                        f_alias = p_elem.value.alias
                        # The alias has to be part of the enc_vals, otherwise it's an undefined situation
                        if not f_alias in enc_vals: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                        # Since this is an address inside of a list, we also have to have encountered a register first.
                        # It's always a base register + some offset... Thus, the offset can be 0x0
                        if not (reg_first or nz_reg_first): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                        # If the previous register was RZ or URZ, the offset has to be directly onto the address of the memory segment
                        if not nz_reg_first: val = data.control_base_offset
                        else: val = 0x0
                        enc_vals = Helpers.overwrite_helper(val=val, val_str=f_alias, enc_vals=enc_vals)
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
                                prequel_instructions.extend(BInstrBase.resolve_register_operand(kk_sm, has_dst, p_elem, i_elem, True, data))
                            elif isinstance(p_elem.value, TT_Func):
                                # This one is an address offset => necessary to set such that it's not an overflow
                                # but it won't generate a prequel instruction. We can simply modify the enc_vals
                                f_alias = p_elem.value.alias
                                # The alias has to be part of the enc_vals, otherwise it's an undefined situation
                                if not f_alias in enc_vals: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                                
                                # Since this is an address inside of a list, we also have to have encountered a register first.
                                # It's always a base register + some offset... Thus, the offset can be 0x0
                                # NOTE: this turned out to be an incorrect assumption: there is a weird instruction class 'ttust_'
                                #    @PT [TTUST] ttuAddr[UImm(0x20aa)], R36, RZ
                                # >>> if not (reg_first or nz_reg_first): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                                # If the previous register was RZ or URZ, the offset has to be directly onto the address of the memory segment
                                if f_alias.endswith('bank'):
                                    # Can be Sb_bank, Sc_bank, ...
                                    val = 0x0 # Use this one as fixed value
                                else:
                                    if not nz_reg_first: val = data.control_base_offset
                                    elif not (nz_reg_first or reg_first): 
                                        # because of 'ttust_', we assume that this works?
                                        val = data.control_base_offset
                                    else: val = 0x0
                                enc_vals = Helpers.overwrite_helper(val=val, val_str=f_alias, enc_vals=enc_vals)
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
                    prequel_instructions.extend(BInstrBase.resolve_register_operand(kk_sm, has_dst, p_arg, i_arg, False, data))
            elif isinstance(p_arg, TT_Param) and isinstance(p_arg.value, TT_Func):
                # This one is just a random number => nothing to do, but case is covered
                pass
            else: 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return enc_vals, prequel_instructions

    @staticmethod
    def resolve_register_operand(kk_sm:KK_SM, has_dest:bool, p_arg:TT_Param, i_arg:Instr_CuBin_Param_RF, is_address:bool, data:ControlProps) -> typing.List[typing.Tuple[str, dict]]:
        if not isinstance(p_arg, TT_Param): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(i_arg, Instr_CuBin_Param_RF): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(p_arg.value, TT_Reg|TT_Func): raise Exception(sp.CONST__ERROR_ILLEGAL)

        res = []
        if p_arg.value.value in ('Register', 'NonZeroRegister', 'ZeroRegister'):
            # We should not have RZ and a NonZeroRegister type
            if p_arg.value.value == 'NonZeroRegister' and i_arg.value.d == data.RZ_num: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if p_arg.value.value == 'ZeroRegister' and i_arg.value.d != data.RZ_num: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # Selector for the register value: if we have 255, it's register RZ and not R255!
            # Also, RZ is a constant, no need to generate data for that one
            if i_arg.value.d < data.RZ_num: 
                val_str:str = str(i_arg.value.d)
                target_reg:tuple = getattr(kk_sm.regs, 'Register__R{0}__{1}'.format(val_str, i_arg.value.d))

                if not is_address:
                    prequel = sc.SASS_KK__MOVImm(kk_sm, 
                                    exec_pred_inv=False, exec_pred=kk_sm.regs.Predicate__PT__7, 
                                    target_reg=target_reg, imm_val=12,
                                    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)

                    res.append((prequel.class_name, prequel.enc_vals))
                else:
                    prequel1 = sc.SASS_KK__MOVImm(kk_sm, 
                                    exec_pred_inv=False, exec_pred=kk_sm.regs.Predicate__PT__7, 
                                    target_reg=target_reg, imm_val=data.control_base_offset,
                                    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)
                    
                    # This is a memory access based on a regular register. We have to load the subsequent odd register
                    # with the base_address + 0x4 as well because of 64 bit issues
                    val_str_odd:str = str(i_arg.value.d+1)
                    target_reg_odd:tuple = getattr(kk_sm.regs, 'Register__R{0}__{1}'.format(val_str_odd, i_arg.value.d+1))
                    prequel2 = sc.SASS_KK__MOVImm(kk_sm, 
                                    exec_pred_inv=False, exec_pred=kk_sm.regs.Predicate__PT__7, 
                                    target_reg=target_reg_odd, imm_val=data.control_base_offset+0x4,
                                    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)

                    res.append((prequel1.class_name, prequel1.enc_vals))
                    res.append((prequel2.class_name, prequel2.enc_vals))

        elif p_arg.value.value == 'Predicate':
            # Selector for the register value: if we have 7, it's register PT and not P7!
            # Also, PT is a constant, no need to generate data for this one
            if i_arg.value.d < data.PT_num: 
                val_str:str = str(i_arg.value.d)
                # Set this one to True
                target_pred:tuple = getattr(kk_sm.regs, 'Predicate__P{0}__{1}'.format(val_str, i_arg.value.d))

                if not is_address:
                    src_reg = kk_sm.regs.Register__R20__20
                    prequel1 = sc.SASS_KK__MOVImm(kk_sm, 
                                    exec_pred_inv=False, exec_pred=kk_sm.regs.Predicate__PT__7, 
                                    target_reg=src_reg, imm_val=12,
                                    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)
                    prequel2 = sc.SASS_KK__ISETP_RsIR_RIR(kk_sm, target_pred=target_pred, 
                                                        aux_pred=kk_sm.regs.Predicate__PT__7, reg=src_reg, imm=10,
                                                        comp_op=kk_sm.regs.ICmpAll__GT__4, fmt=kk_sm.regs.FMT__S32__1,
                                                        bop_op=kk_sm.regs.Bop__AND__0, 
                                                        invert_Pp=False, Pp=kk_sm.regs.Predicate__PT__7,
                                                        usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)
                    
                    res.append((prequel1.class_name, prequel1.enc_vals))
                    res.append((prequel2.class_name, prequel2.enc_vals))
                else:
                    raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        elif p_arg.value.value == 'UniformPredicate':
            # Selector for the register value: if we have 7, it's register PT and not P7!
            # Also, UPT is a constant, no need to generate data for this one
            if i_arg.value.d < data.UPT_num: 
                val_str:str = str(i_arg.value.d)
                # Set this one to True
                utarget_pred:tuple = getattr(kk_sm.regs, 'UniformPredicate__UP{0}__{1}'.format(val_str, i_arg.value.d))

                if not is_address:
                    src_ureg:tuple = kk_sm.regs.UniformRegister__UR20__20
                    prequel1 = sc.SASS_KK__UMOVImm(kk_sm, 
                                    negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7,
                                    target_ureg=src_ureg, imm_val=12,
                                    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)
                    prequel2 = sc.SASS_KK__uisetp__URsIUR_URIR(kk_sm, negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7,
                                                            target_UPu=utarget_pred, src_URa=src_ureg, 
                                                            icmp=kk_sm.regs.ICmpAll__GT__4, fmt=kk_sm.regs.FMT__S32__1,
                                                            src_imm_val=10, usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)

                    res.append((prequel1.class_name, prequel1.enc_vals))
                    res.append((prequel2.class_name, prequel2.enc_vals))
                else:
                    raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        elif p_arg.value.value in ('UniformRegister', 'NonZeroUniformRegister',):
            # We should not have RZ and a NonZeroRegister type
            if p_arg.value.value == 'NonZeroUniformRegister' and i_arg.value.d == data.URZ_num: 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # Selector for the register value: if we have 255, it's register RZ and not R255!
            # Also URZ is a constant, no need to generate data for that one
            if i_arg.value.d < data.URZ_num: 
                val_str:str = str(i_arg.value.d)
                target_ureg:tuple = getattr(kk_sm.regs, 'UniformRegister__UR{0}__{1}'.format(val_str, i_arg.value.d))

                if not is_address:
                    prequel = sc.SASS_KK__UMOVImm(kk_sm, 
                                    negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7,
                                    target_ureg=target_ureg, imm_val=12,
                                    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)

                    res.append((prequel.class_name, prequel.enc_vals))
                else:
                    # This is an address, we require something valid, like uniform_input_base_reg
                    # Move the value of that one into the one we have
                    prequel = sc.SASS_KK__umov__UR(kk_sm, 
                                    negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7,
                                    target_ureg=target_ureg, source_ureg=data.control_base_ureg,
                                    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT15_END_GROUP__15)

                    res.append((prequel.class_name, prequel.enc_vals))
        elif p_arg.value.value in ('PARAMA_2D_3D', 'COMP_STATUSONLY', 'TEXPARAMA', 
                                   'PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D', 'PARAMA_ARRAY_2D_ARRAY_1D_2D_1D_3D',
                                   'PARAMA_ARRAY_2D_ARRAY_1D_2D_1D', 'TXQQUERY'):
            # These are special, constant configuration registers. Cover them, but no need to do anything with it
            pass
        elif p_arg.value.value in ('SpecialRegister'):
            # These are special registers that should access some value. Cover them, but no need to do anything special with them
            pass
        else: 
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return res