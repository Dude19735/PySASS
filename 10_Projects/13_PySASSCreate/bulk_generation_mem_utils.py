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
from py_sass import SASS_Class, SASS_Class_Props
sys.path.append("/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
from kk_sm import KK_SM
import _config as sp

class GenerationMemUtils:
    @staticmethod
    def gen_class_mem(kk_sm:KK_SM, class_nr:int, total_class_nr:int, class_name:str, limit:int) -> typing.Tuple[typing.Dict, typing.List[set], typing.List[dict], int]:
        print("[{0}/{1}] class [{2}]...".format(class_nr, total_class_nr, class_name), end='', flush=True)
        class_:SASS_Class = kk_sm.sass.sm.classes_dict[class_name]

        # if class_name == 'ipa_' or class_name == 'suatom_reg_':
        #     pass

        sm_regs = kk_sm.regs
        TRANS2 = sm_regs.USCHED_INFO__trans2__18
        TRANS1 = sm_regs.USCHED_INFO__trans1__17

        props:SASS_Class_Props = class_.props

        # Sample the instruction once
        # ===========================
        enc_vals = kk_sm.sass.encdom.pick(class_name)
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        # Create the barriers:
        # ===================
        barriers = dict()
        has_rd = False
        has_wr = False
        # Since we don't generally know which one to use (mostly it's the RD one, but who knows) and sometimes
        # only one of them seems to have the desired effect, we add both and then listen for all of them in the
        # benchmarking template
        if props.cash_has__rd:
            ss:SASS_Bits = enc_vals[props.cash_alias__rd]
            barriers[props.cash_alias__rd] = SASS_Bits.from_int(val = 0x0, bit_len=ss.bit_len, signed=ss.signed)
            has_rd = True
        if props.cash_has__wr and not (class_name=='setctaid_'):
            ss:SASS_Bits = enc_vals[props.cash_alias__wr]
            barriers[props.cash_alias__wr] = SASS_Bits.from_int(val = 0x1, bit_len=ss.bit_len, signed=ss.signed)
            has_wr = True

        # Get the registers and fix them
        # ==============================
        reg_alias = props.alias_regs
        regs = {r:{v} for r,v in enc_vals.items() if r in reg_alias}

        # Check if we have a const memory bank access
        # ===========================================
        const_bank_address = [(k,v) for k,v in props.const_bank_address.items()]
        if const_bank_address:
            # If we have const bank addresses, it's exactly one
            const_bank_address_ind = const_bank_address[0][0]
            # Get the sequenced aliases. The first one is alyways the bank, the second one is the address
            cb_aliases = class_.ENCODING[const_bank_address_ind]['alias'].get_sequenced_alias_names()
            cb_bank = cb_aliases[0]
            cb_addr = cb_aliases[1]

        # Check the functions
        # ===================
        tt_funcs = props.tt_funcs
        func_doms = dict()
        for f,tt in tt_funcs.items():
            if f in enc_vals:
                ss:SASS_Bits = enc_vals[f]
                # Memory banks have to respect conditions like the following ones:
                #   CONDITIONS
                #   INVALID_CONST_ADDR_SASS_ONLY_ERROR
                #     ((Sb_bank <= 17) || (Sb_bank >= 24 && Sb_bank <= 31)) :
                #     "Invalid constant bank error"
                #   MISALIGNED_ADDR_ERROR
                #     (Sb_addr & 0x7) == 0 :
                #     "Constant offsets must be aligned on a 8B boundary"
                #   INVALID_CONST_ADDR_ERROR
                #     (Sb_bank >= 24 && Sb_bank <= 31) -> (Sb_addr <= 255) :
                #     "RTV banks may not use an offset greater than 255"
                #   ILLEGAL_INSTR_ENCODING_SASS_ONLY_ERROR
                #     (%SHADER_TYPE == $ST_CS) -> !(Sb_bank >= 8 && Sb_bank <= 31) :
                #     "CS may not use RTV banks"
                if const_bank_address and f == cb_bank:
                    # We have: either
                    #  - Sb_bank >= 24 && Sb_bank <= 31
                    #  - Sb_bank <= 17
                    #  => this is a fairly small range. We can actually iterate that one
                    # Since we use a fixed iterator, if we put all possibilities for Sb_bank, we will
                    # always get a valid one for Sb_addr. If we hit one that doesn't have a possibility, we ignore it
                    banks = set()
                    # We could do this, but this will explode the number of variations and probably, most memory
                    # behaves the same
                    #  | for b in range(0, 32):
                    #  |    banks.add(SASS_Bits.from_int(val=b, bit_len=ss.bit_len, signed=ss.signed))
                    # Thus, we only add a few, but making sure, we cover all possibilities that may show up.
                    # NOTE: this requires knowledge of the device. but up to SM 120, all const memory bank limitations 
                    #       look exactly like this
                    banks.add(SASS_Bits.from_int(val=0, bit_len=ss.bit_len, signed=ss.signed))
                    banks.add(SASS_Bits.from_int(val=24, bit_len=ss.bit_len, signed=ss.signed))
                    
                    func_doms[f] = banks
                elif const_bank_address and f == cb_addr:
                    # Let this one free flow
                    pass
                elif tt.value in ('F16Imm', 'F32Imm', 'F64Imm', 'E6M9Imm', 'E8M7Imm', 'UImm', 'SImm'):
                    # These are generally floating point immediate values. They are already random, so maybe,
                    # don't touch it too much...

                    pass                    
                    # # If they are not, see if they are inside some list. If they are, they are likely an offset
                    # # to some memory offset.
                    # mem_imm = [(ind, ll['type']) for ind,ll in enumerate(props.list_rf_alias) if f in ll['a']]
                    # if mem_imm:
                    #     if len(mem_imm) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    #     attr_ind:int
                    #     attr_type:str
                    #     attr_ind, attr_type = mem_imm[0]
                    #     if attr_type.startswith('attr'):
                    #         pass
                    #     elif attr_type.startswith('list'):
                    #         pass
                    #     else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

                else:
                    raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        # Get all the operations
        # ======================
        # These are all either 0 or 1
        ops_alias = props.alias_ops
        ops_doms = dict()
        for oa in ops_alias:
            # NOTE: since we are using the small domains, Pg@not is always 0 and Pg always PT.
            if not oa in enc_vals: continue
            ss:SASS_Bits = enc_vals[oa]
            ops_doms[oa] = {SASS_Bits.from_int(val=0x0, bit_len=ss.bit_len, signed=ss.signed), SASS_Bits.from_int(val=0x1, bit_len=ss.bit_len, signed=ss.signed)}


        # Get all extensions full domains
        # ===============================
        # We want to iterate over every possible combination of the extensions that is legal.
        # For this we get the entire domains of all extensions. The fixed iterator will return an empty
        # set if a combination is not possible
        domains = {e:tt.value.get_domain({}) for e,tt in props.tt_exts.items()}

        # Merge the sets
        # NOTE: don't merge the barriers here because all domains were generated with them set to 0x7. Merging them here will result
        # in an empty set
        domains |= regs
        domains |= func_doms
        domains |= ops_doms

        fixed_keys = props.alias_exts.union(ops_doms.keys())
        # Add usched_info == WAIT1 or trans2 to the fixed values.
        # NOTE: we are not allowed to use trans1 to benchmark the instruction, but since
        # the encoding domain was generated with the tripple {DRAIN, WAIT1, TRANS1}, we have to pick
        # one of them here and change later => pick TRANS1
        # NOTE: the error if this is not respected is len(Params) == 0
        usched_info_ss:SASS_Bits = enc_vals[props.cash_alias__usched_info]
        domains[props.cash_alias__usched_info] = {SASS_Bits.from_int(TRANS1[-1], usched_info_ss.bit_len, usched_info_ss.signed)}

        ss = math.prod([len(d) for d in domains.values()])
        print("variants [{0}]...".format(ss), end='', flush=True)
        # if ss > limit:
        #     print("over the top => skip...", flush=True)
        #     return props.tt_regs, set(), [], ss

        # The fixed_iter will do this:
        #  - calculate the cross product: [x for x in itt.product(*domains.values())]
        #  - generate encoding values for every valid, fixed tuple
        #  - for example: for the cb_bank where we just picked the numbers 0 to 31, even though a segment of that range is not valid
        #    the fixed_iter will only include the ones that exist in a valid combination.
        # NOTE: all existing combinations are pre-calculated. The iterator is rather fast.
        
        # Create a fixed iterator with the values we have and iterate them
        # kk_sm.sass.encdom.fix(instr_class=class_name, ankers=domains, exceptions={})
        Params = []
        invalid_params_count = 0
        for ind,i in enumerate(kk_sm.sass.encdom.fixed_iter2(instr_class=class_name, ankers=domains)):
            encs:dict = i
            if not encs:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            if has_rd:
                encs[props.cash_alias__rd] = barriers[props.cash_alias__rd]
            if has_wr:
                encs[props.cash_alias__wr] = barriers[props.cash_alias__wr]
            # else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            encs[props.cash_alias__usched_info] = SASS_Bits.from_int(TRANS2[-1], usched_info_ss.bit_len, usched_info_ss.signed)
            # if Instr_CuBin.check_expr_conditions(class_, enc_vals, throw=False):
            Params.append(encs)
            # else: invalid_params_count += 1

        # Expected result
        # ===============
        # Assume the following encoding stage.
        #   BITS_3_14_12_Pg = Pg;
        #   BITS_1_15_15_Pg_not = Pg@not;
        #   BITS_13_91_91_11_0_opcode=Opcode;
        #   BITS_2_79_78_stride=rnd;
        #   BITS_8_23_16_Rd=Rd;
        #   BITS_8_31_24_Ra=Ra;
        #   BITS_1_73_73_sz=Ra@absolute;
        #   BITS_1_72_72_e=Ra@negate;
        #   BITS_5_58_54_Sc_bank,BITS_14_53_40_Sc_addr =  ConstBankAddress2(Sc_bank,Sc_addr);
        #   BITS_1_62_62_Sc_absolute=Sc@absolute;
        #   BITS_1_63_63_Sc_negate=Sc@negate;
        #   BITS_6_121_116_req_bit_set=req_bit_set;
        #   BITS_3_115_113_src_rel_sb=VarLatOperandEnc(src_rel_sb);
        #   BITS_3_112_110_dst_wr_sb=VarLatOperandEnc(dst_wr_sb);
        #   BITS_2_103_102_pm_pred=pm_pred;
        #   BITS_8_124_122_109_105_opex=TABLES_opex_2(batch_t,usched_info,reuse_src_a);
        #
        # The fixed_iter with the imposed limitations will yield something that has
        #  * len({int(p['Ra']) for p in Params}) == 1
        #       (NOTE: this one is fixed by the domain calculator. We always want to generate instructions that run by default)
        #  * len({int(p['Pg@not']) for p in Params}) == 1 
        #       (NOTE: this one is fixed by the domain calculator. We always want to generate instructions that run by default)
        #  * len({int(p['Ra@absolute']) for p in Params}) == 2
        #       (NOTE: the same for all other operators != Pg@not)
        #  * len({int(p['req_bit_set']) for p in Params}) == 1
        #  * len({int(p['reuse_src_a']) for p in Params}) == 2 
        #       (NOTE: this is one of the extensions we care about => all valid possibilities)
        #  * len({int(p['rnd']) for p in Params}) == 4 
        #       (NOTE: this is one of the extensions we care about => all valid possibilities)
        #  * len({int(p['Sc_bank']) for p in Params}) == 2 
        #      (NOTE: with the full range of possible memory banks, we would have 26 here...)
        #  * len({int(p['Sc_addr']) for p in Params}) == 99 <= len(Params)
        #      (NOTE: this one wasn't fixed, so we have at most len(Params) possible values here)
        #  * len(Params) <= product_of([len(d) for d in domains.values()])
        #      (NOTE: these are the fixed values, they produce possibilities, everything else is added at random)

        # Make sure we have results
        # NOTE: if this exception is thrown, it likely is because we fixed some enc_vals aliases
        # to values that don't exist in the domain picker. For example, use usched_info = TRANS2.
        if len(Params) == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        print("...ok", ("[invalid params count: {0}]".format(invalid_params_count) if invalid_params_count > 0 else ""), flush=True)

        # if len(Params) > limit:
        #     print("over the top => skip...", flush=True)
        #     return props.tt_regs, set(), [], len(Params)
        return props.tt_regs, fixed_keys, Params, ss
