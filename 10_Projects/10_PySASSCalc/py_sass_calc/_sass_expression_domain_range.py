import typing
import itertools as itt
from py_sass import TT_Reg
from py_sass._sass_expression_ops import *
from py_sass import SM_SASS
from py_sass import SASS_Expr_Domain_Contract
from py_sass_ext import SASS_Range
from py_sass_ext import SASS_Bits
import _config as sp
from _sass_expression_domain_utils import SASS_Expr_Domain_Utils


class Mini_Alias:
    """Mini representation for an alias in the func world (Do Not Use outside of _sass_expression_domain_range.py)"""
    def __init__(self, n, tt, d):
        self.n = n
        self.tt = tt
        self.d = d
        self.is_func = True

        self.is_addr = None
        self.bit_len = None
        self.has_default = None
        self.sign = None
        self.default_val = None
        self.has_max_val = None
        self.max_val = None

class SASS_Expr_Domain_Range:
    @staticmethod
    def __get_alias_sequence(expr_alias_tt:list, alias_nt:list, to_limit) -> list[Mini_Alias]:
        rr = [[Mini_Alias(n=aa, tt=tt, d=tt.get_domain(to_limit)) for aa in alias_nt if (str(tt).startswith(aa) or str(tt.alias).startswith(aa))] for tt in expr_alias_tt]
        if not all(len(i)==1 for i in rr): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        rr2 = list(itt.chain.from_iterable(rr))
        
        r:Mini_Alias
        for r in rr2:
            if isinstance(r.tt, TT_Reg): 
                r.is_func = False
                continue
            r.is_addr = r.tt.is_address
            r.bit_len = r.tt.arg_default.bit_len
            r.has_default = r.tt.arg_default.has_default
            r.sign = int(r.tt.func.sign())
            if r.has_default: r.default_val = r.tt.arg_default.default_val
            r.has_max_val = r.tt.arg_default.has_max_val
            if r.has_max_val: r.tt.arg_default.max_val 

        return rr2

    @staticmethod
    def __attach_results(new_aliases:typing.List[dict]|dict, aliases:typing.List[dict]):
        # This one attaches new results (new_aliases) to a dictionary of already present aliases.
        # All CONDITIONS have an AND relationship. Consecutive CONDITIONS that use the same aliases
        # need to be merged with an AND as well. That is what this method does.
        if isinstance(new_aliases, list):
            # if we have nothing, just set
            if aliases == [{}]: aliases = new_aliases
            else:
                res_alias = []
                pp = list(itt.product(new_aliases, aliases))
                for nn,oo in pp:
                    new_r_dict = {}
                    nk = [k for k in nn if not k in oo] # only in new expression
                    ok = [k for k in nn if k in oo]     # in new and in old expression
                    ek = [k for k in oo if not k in nn] # only in old expression
                    for k in nk:
                        # If we only have new values, we can just add them
                        new_r_dict[k] = nn[k]
                    for k in ok:
                        # This is merging existing results with new ones using a set intersection
                        new_r_dict[k] = oo[k].intersection(nn[k])
                    for k in ek:
                        # If we only have old values, we just copy them into the new dictionary
                        new_r_dict[k] = oo[k]
                    if new_r_dict and all(i in new_r_dict.keys() and len(new_r_dict[i]) > 0 for i in nn.keys() | oo.keys()):
                        # Add the newly merged new_r_dict to the results. Make sure that any entry in new_r_dict (representing an alias)
                        # has values (len(new_r_dict[i]) > 0) and that every alias both in old and new results is contained inside the
                        # new_r_dict (i in new_r_dict.keys()). This is to make sure that "new_r_dict[k] = oo[k].intersection(nn[k])" didn't
                        # accidentally eliminate the values for an alias
                        res_alias.append(new_r_dict)
                
                # If we don't have any alias values here anymore, it's a bug
                # NOTE: do not ignore this exception => if it's raised, it's a bug and you need to investigate!
                if not res_alias: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                # only keep the results where all aliases have some values
                return res_alias
        elif isinstance(new_aliases, dict):
            raise Exception(sp.CONST__ERROR_ILLEGAL)
            # if we have nothing, just set and convert to list
            if aliases == [{}]: aliases = [new_aliases]
            else:
                for a in aliases:
                    for r in new_aliases:
                        if r in a:
                            raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
                        else:
                            a[r] = new_aliases[r]
        return aliases
    
    # (immConstOffset & 0x3) == 0
    # BConst_IADD3 | sm_50 to sm_90
    __OLD_EXPR_TYPE_1 = ('Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int').__hash__()
    __EXPR_TYPE_1 = ('Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int').__hash__()
    @staticmethod
    def __expr_type_1(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)
        if not int_tt[1] == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        a0 = a_seq[0]
        rr = a0.d.add_bit_mask(int_tt[0])
        res = [{a0.n : rr}]

        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (Sb_bank >= 24 && Sb_bank <= 31) -> (Sb_addr <= 255)
    # bmov_dst64__C | sm_75 to sm_90
    __OLD_EXPR_TYPE_2 = ('Op_LBrace', 'Op_Alias', 'Op_GreaterOrEqual', 'Op_Int', 'Op_And', 'Op_Alias', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace').__hash__()
    __EXPR_TYPE_2 = ('Op_LBrace', 'Op_Alias_0', 'Op_GreaterOrEqual', 'Op_Int', 'Op_And', 'Op_Alias_0', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias_1', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_2(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt = a_seq[0]
        # (Sb_bank >= 24 && Sb_bank <= 31)
        if tt.sign: tt_max = 2**(tt.bit_len-1)-1
        else: tt_max = 2**(tt.bit_len)-1
        left_T = [{tt.n: tt.d.intersection(SASS_Range(int_tt[0], int_tt[1], tt.bit_len, tt.sign, bit_mask=0))}]
        left_F = [{tt.n: tt.d.intersection(SASS_Range(0, int_tt[0]-1, tt.bit_len, tt.sign, bit_mask=0))},
                  {tt.n: tt.d.intersection(SASS_Range(int_tt[1]+1, tt_max, tt.bit_len, tt.sign, bit_mask=0))}]
        
        tt = a_seq[1]
        # (Sb_addr <= 255)
        if tt.sign: tt_max = 2**(tt.bit_len-1)-1
        else: tt_max = 2**(tt.bit_len)-1
        right_T = [{tt.n: tt.d.intersection(SASS_Range(0, int_tt[2], tt.bit_len, tt.sign, bit_mask=0))}]
        right_F = [{tt.n: tt.d.intersection(SASS_Range(int_tt[2]+1, tt_max, tt.bit_len, tt.sign, bit_mask=0))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0)))
    # scatter_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_3 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_3 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_3(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        tt3 = a_seq[3]
        # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d, tt3.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt4 = a_seq[4]
        if tt4.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 1) || (vecidx == 0)))
        vals = [i for i in tt4.d]
        right_T = [{tt4.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt4.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2)))
    # scatter_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_4 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_4 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_4(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        tt3 = a_seq[3]
        # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d, tt3.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt4 = a_seq[4]
        if tt4.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2)))
        vals = [i for i in tt4.d]
        right_T = [{tt4.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt4.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 0)))
    # scatter_ | sm_80 to sm_90
    # __EXPR_TYPE_5 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_5 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_5(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        tt3 = a_seq[3]
        # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d, tt3.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt4 = a_seq[4]
        if tt4.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 0)))
        vals = [i for i in tt4.d]
        right_T = [{tt4.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt4.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30)))
    # scatter_ | sm_80 to sm_90
    # __EXPR_TYPE_6 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_6 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_6(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        tt3 = a_seq[3]
        # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d, tt3.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt4 = a_seq[4]
        if tt4.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30)))
        vals = [i for i in tt4.d]
        right_T = [{tt4.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt4.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0)))
    # spmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_7 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_7 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_7(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        if tt3.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 1) || (vecidx == 0)))
        vals = [i for i in tt3.d]
        right_T = [{tt3.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt3.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 0)))
    # spmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_8 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_8 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_8(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U4_H0)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        if tt3.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 0)))
        vals = [i for i in tt3.d]
        right_T = [{tt3.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt3.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 56) || (vecidx == 54) || (vecidx == 42) || (vecidx == 48) || (vecidx == 43) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 49) || (vecidx == 52) || (vecidx == 53) || (vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 28) || (vecidx == 29) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 51) || (vecidx == 39) || (vecidx == 38) || (vecidx == 59) || (vecidx == 58) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 33) || (vecidx == 55) || (vecidx == 32) || (vecidx == 57) || (vecidx == 50)))
    # scatter_ | sm_80 to sm_90
    # __EXPR_TYPE_9 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_9 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_9(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        tt3 = a_seq[3]
        # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d, tt3.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt4 = a_seq[4]
        if tt4.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 56) || (vecidx == 54) || (vecidx == 42) || (vecidx == 48) || (vecidx == 43) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 49) || (vecidx == 52) || (vecidx == 53) || (vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 28) || (vecidx == 29) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 51) || (vecidx == 39) || (vecidx == 38) || (vecidx == 59) || (vecidx == 58) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 33) || (vecidx == 55) || (vecidx == 32) || (vecidx == 57) || (vecidx == 50)))
        vals = [i for i in tt4.d]
        right_T = [{tt4.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt4.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6)))
    # scatter_ | sm_80 to sm_90
    # __EXPR_TYPE_10 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_10 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_10(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        tt3 = a_seq[3]
        # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_H0)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d, tt3.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt4 = a_seq[4]
        if tt4.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6)))
        vals = [i for i in tt4.d]
        right_T = [{tt4.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt4.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8)))
    # scatter_ | sm_80 to sm_90
    # __EXPR_TYPE_11 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_11 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_11(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        tt3 = a_seq[3]
        # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d, tt3.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt4 = a_seq[4]
        if tt4.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8)))
        vals = [i for i in tt4.d]
        right_T = [{tt4.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt4.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30)))
    # spmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_12 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_12 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_12(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        if tt3.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30)))
        vals = [i for i in tt3.d]
        right_T = [{tt3.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt3.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_H0))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2)))
    # spmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_13 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_13 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_13(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_H0)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        if tt3.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2)))
        vals = [i for i in tt3.d]
        right_T = [{tt3.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt3.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8)))
    # spmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_14 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_14 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_14(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        if tt3.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8)))
        vals = [i for i in tt3.d]
        right_T = [{tt3.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt3.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # ((dep_scbd & (1 << sbidx)) == 0)
    # DEPBAR_LE | sm_50 to sm_90
    # __EXPR_TYPE_15 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_LBrace', 'Op_Int', 'Op_LShift', 'Op_Alias', 'Op_RBrace', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    __EXPR_TYPE_15 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_LBrace', 'Op_Int', 'Op_LShift', 'Op_Alias_1', 'Op_RBrace', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_15(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        a0 = a_seq[0]
        a1 = a_seq[1]
        if a0.bit_len > 6: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if int_tt[0] != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if int_tt[1] != 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        masks = [(i, SASS_Bits.from_int(int_tt[0], bit_len=a0.bit_len, signed=a0.sign) << int(i)) for i in a1.d]
        vals = list(itt.chain.from_iterable([[{a0.n: i, a1.n: m[0]} for m in masks if (i & m[1] == int_tt[1])] for i in a0.d]))
        res = SASS_Expr_Domain_Contract.group(vals)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (dst_wr_sb == 7)
    # AST | sm_50 to sm_90
    # __EXPR_TYPE_16 = ('Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    __EXPR_TYPE_16 = ('Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_16(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        # reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)
        a1 = a_seq[0]
        res = [{a1.n : {SASS_Bits.from_int(int_tt[0], bit_len=a1.bit_len, signed=a1.sign)}}]
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 0) || (vecidx == 4) || (vecidx == 8) || (vecidx == 119) || (vecidx == 120) || (vecidx == 121) || (vecidx == 122) || (vecidx == 123) || (vecidx == 124) || (vecidx == 125) || (vecidx == 126) || (vecidx == 127) || (vecidx == 118) || (vecidx == 59) || (vecidx == 58) || (vecidx == 55) || (vecidx == 54) || (vecidx == 57) || (vecidx == 56) || (vecidx == 51) || (vecidx == 50) || (vecidx == 53) || (vecidx == 52) || (vecidx == 115) || (vecidx == 114) || (vecidx == 88) || (vecidx == 89) || (vecidx == 111) || (vecidx == 110) || (vecidx == 113) || (vecidx == 112) || (vecidx == 82) || (vecidx == 83) || (vecidx == 80) || (vecidx == 81) || (vecidx == 86) || (vecidx == 87) || (vecidx == 84) || (vecidx == 85) || (vecidx == 3) || (vecidx == 7) || (vecidx == 108) || (vecidx == 109) || (vecidx == 102) || (vecidx == 103) || (vecidx == 100) || (vecidx == 101) || (vecidx == 106) || (vecidx == 107) || (vecidx == 104) || (vecidx == 105) || (vecidx == 39) || (vecidx == 38) || (vecidx == 33) || (vecidx == 32) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 64) || (vecidx == 65) || (vecidx == 66) || (vecidx == 67) || (vecidx == 68) || (vecidx == 69) || (vecidx == 2) || (vecidx == 6) || (vecidx == 99) || (vecidx == 98) || (vecidx == 91) || (vecidx == 90) || (vecidx == 93) || (vecidx == 92) || (vecidx == 95) || (vecidx == 94) || (vecidx == 97) || (vecidx == 96) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 117) || (vecidx == 116) || (vecidx == 48) || (vecidx == 49) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 42) || (vecidx == 43) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 5) || (vecidx == 9) || (vecidx == 77) || (vecidx == 76) || (vecidx == 75) || (vecidx == 74) || (vecidx == 73) || (vecidx == 72) || (vecidx == 71) || (vecidx == 70) || (vecidx == 79) || (vecidx == 78)))
    # scatter_ | sm_80 to sm_90
    # __EXPR_TYPE_17 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_17 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_17(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        tt3 = a_seq[3]
        # (((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d, tt3.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2, tt3.n:a3} for a0,a1,a2,a3 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt4 = a_seq[4]
        if tt4.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 0) || (vecidx == 4) || (vecidx == 8) || (vecidx == 119) || (vecidx == 120) || (vecidx == 121) || (vecidx == 122) || (vecidx == 123) || (vecidx == 124) || (vecidx == 125) || (vecidx == 126) || (vecidx == 127) || (vecidx == 118) || (vecidx == 59) || (vecidx == 58) || (vecidx == 55) || (vecidx == 54) || (vecidx == 57) || (vecidx == 56) || (vecidx == 51) || (vecidx == 50) || (vecidx == 53) || (vecidx == 52) || (vecidx == 115) || (vecidx == 114) || (vecidx == 88) || (vecidx == 89) || (vecidx == 111) || (vecidx == 110) || (vecidx == 113) || (vecidx == 112) || (vecidx == 82) || (vecidx == 83) || (vecidx == 80) || (vecidx == 81) || (vecidx == 86) || (vecidx == 87) || (vecidx == 84) || (vecidx == 85) || (vecidx == 3) || (vecidx == 7) || (vecidx == 108) || (vecidx == 109) || (vecidx == 102) || (vecidx == 103) || (vecidx == 100) || (vecidx == 101) || (vecidx == 106) || (vecidx == 107) || (vecidx == 104) || (vecidx == 105) || (vecidx == 39) || (vecidx == 38) || (vecidx == 33) || (vecidx == 32) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 64) || (vecidx == 65) || (vecidx == 66) || (vecidx == 67) || (vecidx == 68) || (vecidx == 69) || (vecidx == 2) || (vecidx == 6) || (vecidx == 99) || (vecidx == 98) || (vecidx == 91) || (vecidx == 90) || (vecidx == 93) || (vecidx == 92) || (vecidx == 95) || (vecidx == 94) || (vecidx == 97) || (vecidx == 96) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 117) || (vecidx == 116) || (vecidx == 48) || (vecidx == 49) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 42) || (vecidx == 43) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 5) || (vecidx == 9) || (vecidx == 77) || (vecidx == 76) || (vecidx == 75) || (vecidx == 74) || (vecidx == 73) || (vecidx == 72) || (vecidx == 71) || (vecidx == 70) || (vecidx == 79) || (vecidx == 78)))
        vals = [i for i in tt4.d]
        right_T = [{tt4.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt4.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 56) || (vecidx == 54) || (vecidx == 42) || (vecidx == 48) || (vecidx == 43) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 49) || (vecidx == 52) || (vecidx == 53) || (vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 28) || (vecidx == 29) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 51) || (vecidx == 39) || (vecidx == 38) || (vecidx == 59) || (vecidx == 58) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 33) || (vecidx == 55) || (vecidx == 32) || (vecidx == 57) || (vecidx == 50)))
    # spmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_18 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_18 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_18(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        if tt3.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 56) || (vecidx == 54) || (vecidx == 42) || (vecidx == 48) || (vecidx == 43) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 49) || (vecidx == 52) || (vecidx == 53) || (vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 28) || (vecidx == 29) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 51) || (vecidx == 39) || (vecidx == 38) || (vecidx == 59) || (vecidx == 58) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 33) || (vecidx == 55) || (vecidx == 32) || (vecidx == 57) || (vecidx == 50)))
        vals = [i for i in tt3.d]
        right_T = [{tt3.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt3.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6)))
    # spmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_19 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_19 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_19(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        if tt3.bit_len > 8: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6)))
        vals = [i for i in tt3.d]
        right_T = [{tt3.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt3.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # !(bpt == `BPTMode@TRAP && (sImm < 1 || sImm > 7))
    # BPT | sm_50 to sm_62
    # __EXPR_TYPE_20 = ('Op_Not', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_Smaller', 'Op_Int', 'Op_Or', 'Op_Alias', 'Op_Greater', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_20 = ('Op_Not', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_And', 'Op_LBrace', 'Op_Alias_1', 'Op_Smaller', 'Op_Int', 'Op_Or', 'Op_Alias_1', 'Op_Greater', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_20(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        a0 = a_seq[0]
        a1 = a_seq[1]
        # !(bpt == `BPTMode@TRAP && (sImm < 1 || sImm > 7))
        # === !(bpt == `BPTMode@TRAP) or !(sImm < 1 || sImm > 7)
        # === (bpt != `BPTMode@TRAP) or (sImm >= 1 && sImm <= 7)
        
        # (bpt != `BPTMode@TRAP) and sImm == SASS_Range
        or_1 = {a0.n: set([i for i in a0.d if i != reg_tt[0]]), a1.n: a1.d}
        # (bpt == `BPTMode@TRAP) and (sImm >= 1 && sImm <= 7)
        or_2 = {a0.n: set([i for i in a0.d if i == reg_tt[0]]), a1.n: set([SASS_Bits.from_int(i, bit_len=a1.bit_len, signed=a1.sign) for i in range(int_tt[0], int_tt[1]+1)])}

        res = [or_1, or_2]
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # ((sImm & 0x7) == 0)
    # PEXIT | sm_50 to sm_62
    # __EXPR_TYPE_21 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    __EXPR_TYPE_21 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_21(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        return SASS_Expr_Domain_Range.__expr_type_1(aliases, sass, expr[1:-1], alias_nt, to_limit)

    # ((Sb == 3088))
    # ide_ | sm_70 to sm_90
    # __EXPR_TYPE_22 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_22 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_22(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        return SASS_Expr_Domain_Range.__expr_type_16(aliases, sass, expr[1:-1], alias_nt, to_limit)

    # (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq))) -> (((mdidx == 11) || (mdidx == 10) || (mdidx == 13) || (mdidx == 12) || (mdidx == 14) || (mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 9) || (mdidx == 8)) && ((vecidx6 == 0)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_23 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_23 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_23(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 11) || (mdidx == 10) || (mdidx == 13) || (mdidx == 12) || (mdidx == 14) || (mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 9) || (mdidx == 8)) && ((vecidx6 == 0)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 in int_tt[:-1]) and (a4 == int_tt[-1]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 in int_tt[:-1]) and (a4 == int_tt[-1]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 6)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_24 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_24 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_24(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 6)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 in int_tt[:7]) and (a4 in int_tt[7:]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 in int_tt[:7]) and (a4 in int_tt[7:]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 2)) && ((vecidx6 == 56) || (vecidx6 == 54) || (vecidx6 == 42) || (vecidx6 == 48) || (vecidx6 == 43) || (vecidx6 == 60) || (vecidx6 == 61) || (vecidx6 == 62) || (vecidx6 == 63) || (vecidx6 == 49) || (vecidx6 == 52) || (vecidx6 == 53) || (vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 46) || (vecidx6 == 47) || (vecidx6 == 44) || (vecidx6 == 45) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 40) || (vecidx6 == 41) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 51) || (vecidx6 == 39) || (vecidx6 == 38) || (vecidx6 == 59) || (vecidx6 == 58) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30) || (vecidx6 == 37) || (vecidx6 == 36) || (vecidx6 == 35) || (vecidx6 == 34) || (vecidx6 == 33) || (vecidx6 == 55) || (vecidx6 == 32) || (vecidx6 == 57) || (vecidx6 == 50)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_25 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_25 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_25(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@noseq)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 1) || (mdidx == 0) || (mdidx == 2)) && ((vecidx6 == 56) || (vecidx6 == 54) || (vecidx6 == 42) || (vecidx6 == 48) || (vecidx6 == 43) || (vecidx6 == 60) || (vecidx6 == 61) || (vecidx6 == 62) || (vecidx6 == 63) || (vecidx6 == 49) || (vecidx6 == 52) || (vecidx6 == 53) || (vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 46) || (vecidx6 == 47) || (vecidx6 == 44) || (vecidx6 == 45) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 40) || (vecidx6 == 41) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 51) || (vecidx6 == 39) || (vecidx6 == 38) || (vecidx6 == 59) || (vecidx6 == 58) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30) || (vecidx6 == 37) || (vecidx6 == 36) || (vecidx6 == 35) || (vecidx6 == 34) || (vecidx6 == 33) || (vecidx6 == 55) || (vecidx6 == 32) || (vecidx6 == 57) || (vecidx6 == 50)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 in int_tt[:3]) and (a4 in int_tt[3:]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 in int_tt[:3]) and (a4 in int_tt[3:]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq))) -> (((mdidx == 11) || (mdidx == 10) || (mdidx == 12) || (mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 9) || (mdidx == 8)) && ((vecidx6 == 0)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_26 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_26 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_26(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 11) || (mdidx == 10) || (mdidx == 12) || (mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 9) || (mdidx == 8)) && ((vecidx6 == 0)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 in int_tt[:-1]) and (a4 == int_tt[-1]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 in int_tt[:-1]) and (a4 == int_tt[-1]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 8)) && ((vecidx6 == 0)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_27 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_27 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_27(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 8)) && ((vecidx6 == 0)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 in int_tt[:-1]) and (a4 == int_tt[-1]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 in int_tt[:-1]) and (a4 == int_tt[-1]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 4)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_28 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_28 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_28(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 4)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 in int_tt[:5]) and (a4 in int_tt[5:]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 in int_tt[:5]) and (a4 in int_tt[5:]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq))) -> (((mdidx == 0)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_29 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_29 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_29(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 0)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 == int_tt[0]) and (a4 in int_tt[1:]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 == int_tt[0]) and (a4 in int_tt[1:]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@noseq))) -> (((mdidx == 0)) && ((vecidx6 == 56) || (vecidx6 == 54) || (vecidx6 == 42) || (vecidx6 == 48) || (vecidx6 == 43) || (vecidx6 == 60) || (vecidx6 == 61) || (vecidx6 == 62) || (vecidx6 == 63) || (vecidx6 == 49) || (vecidx6 == 52) || (vecidx6 == 53) || (vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 46) || (vecidx6 == 47) || (vecidx6 == 44) || (vecidx6 == 45) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 40) || (vecidx6 == 41) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 51) || (vecidx6 == 39) || (vecidx6 == 38) || (vecidx6 == 59) || (vecidx6 == 58) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30) || (vecidx6 == 37) || (vecidx6 == 36) || (vecidx6 == 35) || (vecidx6 == 34) || (vecidx6 == 33) || (vecidx6 == 55) || (vecidx6 == 32) || (vecidx6 == 57) || (vecidx6 == 50)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_30 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_30 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    def __expr_type_30(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@noseq)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 0)) && ((vecidx6 == 56) || (vecidx6 == 54) || (vecidx6 == 42) || (vecidx6 == 48) || (vecidx6 == 43) || (vecidx6 == 60) || (vecidx6 == 61) || (vecidx6 == 62) || (vecidx6 == 63) || (vecidx6 == 49) || (vecidx6 == 52) || (vecidx6 == 53) || (vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 46) || (vecidx6 == 47) || (vecidx6 == 44) || (vecidx6 == 45) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 40) || (vecidx6 == 41) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 51) || (vecidx6 == 39) || (vecidx6 == 38) || (vecidx6 == 59) || (vecidx6 == 58) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30) || (vecidx6 == 37) || (vecidx6 == 36) || (vecidx6 == 35) || (vecidx6 == 34) || (vecidx6 == 33) || (vecidx6 == 55) || (vecidx6 == 32) || (vecidx6 == 57) || (vecidx6 == 50)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 == int_tt[0]) and (a4 in int_tt[1:]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 == int_tt[0]) and (a4 in int_tt[1:]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 4)) && ((vecidx6 == 1) || (vecidx6 == 0)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_31 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_31 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_31(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 4)) && ((vecidx6 == 1) || (vecidx6 == 0)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 in int_tt[:6]) and (a4 == int_tt[-1]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 in int_tt[:6]) and (a4 == int_tt[-1]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 0)) && ((vecidx6 == 0)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_32 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_32 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_32(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 0)) && ((vecidx6 == 0)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 == int_tt[0]) and (a4 == int_tt[1]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 == int_tt[0]) and (a4 == int_tt[1]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 0)) && ((vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30)))
    # genmetadata_ | sm_80 to sm_90
    # __EXPR_TYPE_33 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_33 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_33(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        tt2 = a_seq[2]
        # (((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@SEQ)))
        pp = list(itt.product(tt0.d, tt1.d, tt2.d))
        left_T = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1, tt2.n:a2} for a0,a1,a2 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt3 = a_seq[3]
        tt4 = a_seq[4]
        pp2 = list(itt.product(tt3.d, tt4.d))
        # (((mdidx == 0)) && ((vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30)))
        right_T = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if    ( (a3 == int_tt[0]) and (a4 in int_tt[1:]) )] 
        right_F = [{tt3.n:a3, tt4.n:a4} for a3,a4 in pp2 if not( (a3 == int_tt[0]) and (a4 in int_tt[1:]) )]
        if right_T: right_T = SASS_Expr_Domain_Contract.group(right_T)
        if right_F: right_F = SASS_Expr_Domain_Contract.group(right_F)

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((Sb == 0)))
    # hadd2_F32i_ | sm_86 to sm_90
    # __EXPR_TYPE_34 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_34 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_34(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        return SASS_Expr_Domain_Range.__expr_type_16(aliases, sass, expr[2:-2], alias_nt, to_limit)

    # (((idxsize == `IDXSIZE@U4_H0) || (idxsize == `IDXSIZE@U4_H1)) && ((mode == `MODE_scatter@THREAD))) -> (((vecidx == 0) || (vecidx == 1) || (vecidx == 2) || (vecidx == 3)))
    # scatter_ | sm_75 to sm_75
    # __EXPR_TYPE_35 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_35 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_35(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        # (((idxsize == `IDXSIZE@U4_H0) || (idxsize == `IDXSIZE@U4_H1)) && ((mode == `MODE_scatter@THREAD)))
        # idxsize and mode are registers
        pp = list(itt.product(tt0.d, tt1.d))
        left_T = [{tt0.n:a0, tt1.n:a1} for a0,a1 in pp if    ( (a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1} for a0,a1 in pp if not( (a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt2 = a_seq[2]
        if tt2.bit_len > 6: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 0) || (vecidx == 1) || (vecidx == 2) || (vecidx == 3)))
        vals = [i for i in tt2.d]
        right_T = [{tt2.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt2.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((idxsize == `IDXSIZE@U4_H0) || (idxsize == `IDXSIZE@U4_H1)) && ((mode == `MODE_scatter@QUAD))) -> (((vecidx == 0)))
    # scatter_ | sm_75 to sm_75
    # __EXPR_TYPE_36 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_36 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_36(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        # (((idxsize == `IDXSIZE@U4_H0) || (idxsize == `IDXSIZE@U4_H1)) && ((mode == `MODE_scatter@QUAD)))
        # idxsize and mode are registers
        pp = list(itt.product(tt0.d, tt1.d))
        left_T = [{tt0.n:a0, tt1.n:a1} for a0,a1 in pp if    ( (a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1} for a0,a1 in pp if not( (a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt2 = a_seq[2]
        if tt2.bit_len > 6: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 0)))
        vals = [i for i in tt2.d]
        right_T = [{tt2.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt2.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((idxsize == `IDXSIZE@U8)) && ((mode == `MODE_scatter@QUAD))) -> (((vecidx == 0) || (vecidx == 1) || (vecidx == 2) || (vecidx == 3) || (vecidx == 4) || (vecidx == 5) || (vecidx == 6) || (vecidx == 7) || (vecidx == 8) || (vecidx == 9) || (vecidx == 10) || (vecidx == 11) || (vecidx == 12) || (vecidx == 13) || (vecidx == 14) || (vecidx == 15)))
    # scatter_ | sm_75 to sm_75
    # __EXPR_TYPE_37 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_37 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_37(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        tt1 = a_seq[1]
        # (((idxsize == `IDXSIZE@U8)) && ((mode == `MODE_scatter@QUAD)))
        # idxsize and mode are registers
        pp = list(itt.product(tt0.d, tt1.d))
        left_T = [{tt0.n:a0, tt1.n:a1} for a0,a1 in pp if    ( (a0==reg_tt[0]) and (a1==reg_tt[1]) )] 
        left_F = [{tt0.n:a0, tt1.n:a1} for a0,a1 in pp if not( (a0==reg_tt[0]) and (a1==reg_tt[1]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt2 = a_seq[2]
        if tt2.bit_len > 6: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # (((vecidx == 0)))
        vals = [i for i in tt2.d]
        right_T = [{tt2.n: set(v for v in vals if    (v in int_tt))}]
        right_F = [{tt2.n: set(v for v in vals if not(v in int_tt))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((word_mask == 217) || (word_mask == 214) || (word_mask == 213) || (word_mask == 211) || (word_mask == 218) || (word_mask == 133) || (word_mask == 131) || (word_mask == 137) || (word_mask == 134) || (word_mask == 138) || (word_mask == 25) || (word_mask == 26) || (word_mask == 21) || (word_mask == 22) || (word_mask == 28) || (word_mask == 220) || (word_mask == 121) || (word_mask == 122) || (word_mask == 124) || (word_mask == 58) || (word_mask == 54) || (word_mask == 57) || (word_mask == 51) || (word_mask == 53) || (word_mask == 90) || (word_mask == 198) || (word_mask == 195) || (word_mask == 197) || (word_mask == 115) || (word_mask == 117) || (word_mask == 89) || (word_mask == 83) || (word_mask == 86) || (word_mask == 118) || (word_mask == 85) || (word_mask == 3) || (word_mask == 245) || (word_mask == 108) || (word_mask == 246) || (word_mask == 243) || (word_mask == 102) || (word_mask == 101) || (word_mask == 106) || (word_mask == 105) || (word_mask == 38) || (word_mask == 37) || (word_mask == 35) || (word_mask == 60) || (word_mask == 179) || (word_mask == 67) || (word_mask == 252) || (word_mask == 69) || (word_mask == 250) || (word_mask == 172) || (word_mask == 170) || (word_mask == 249) || (word_mask == 182) || (word_mask == 181) || (word_mask == 186) || (word_mask == 6) || (word_mask == 188) || (word_mask == 185) || (word_mask == 99) || (word_mask == 169) || (word_mask == 229) || (word_mask == 227) || (word_mask == 165) || (word_mask == 166) || (word_mask == 92) || (word_mask == 163) || (word_mask == 10) || (word_mask == 12) || (word_mask == 19) || (word_mask == 150) || (word_mask == 153) || (word_mask == 154) || (word_mask == 156) || (word_mask == 234) || (word_mask == 236) || (word_mask == 230) || (word_mask == 233) || (word_mask == 44) || (word_mask == 42) || (word_mask == 41) || (word_mask == 5) || (word_mask == 9) || (word_mask == 201) || (word_mask == 147) || (word_mask == 202) || (word_mask == 204) || (word_mask == 140) || (word_mask == 149) || (word_mask == 76) || (word_mask == 74) || (word_mask == 73) || (word_mask == 70))) -> (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 2))))
    # ldg_256_memdesc__Ra64 | sm_100 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_40 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_40(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        # (((word_mask == 217) || (word_mask == 214) || (word_mask == 213) || (word_mask == 211) || (word_mask == 218) || (word_mask == 133) || (word_mask == 131) || (word_mask == 137) || (word_mask == 134) || (word_mask == 138) || (word_mask == 25) || (word_mask == 26) || (word_mask == 21) || (word_mask == 22) || (word_mask == 28) || (word_mask == 220) || (word_mask == 121) || (word_mask == 122) || (word_mask == 124) || (word_mask == 58) || (word_mask == 54) || (word_mask == 57) || (word_mask == 51) || (word_mask == 53) || (word_mask == 90) || (word_mask == 198) || (word_mask == 195) || (word_mask == 197) || (word_mask == 115) || (word_mask == 117) || (word_mask == 89) || (word_mask == 83) || (word_mask == 86) || (word_mask == 118) || (word_mask == 85) || (word_mask == 3) || (word_mask == 245) || (word_mask == 108) || (word_mask == 246) || (word_mask == 243) || (word_mask == 102) || (word_mask == 101) || (word_mask == 106) || (word_mask == 105) || (word_mask == 38) || (word_mask == 37) || (word_mask == 35) || (word_mask == 60) || (word_mask == 179) || (word_mask == 67) || (word_mask == 252) || (word_mask == 69) || (word_mask == 250) || (word_mask == 172) || (word_mask == 170) || (word_mask == 249) || (word_mask == 182) || (word_mask == 181) || (word_mask == 186) || (word_mask == 6) || (word_mask == 188) || (word_mask == 185) || (word_mask == 99) || (word_mask == 169) || (word_mask == 229) || (word_mask == 227) || (word_mask == 165) || (word_mask == 166) || (word_mask == 92) || (word_mask == 163) || (word_mask == 10) || (word_mask == 12) || (word_mask == 19) || (word_mask == 150) || (word_mask == 153) || (word_mask == 154) || (word_mask == 156) || (word_mask == 234) || (word_mask == 236) || (word_mask == 230) || (word_mask == 233) || (word_mask == 44) || (word_mask == 42) || (word_mask == 41) || (word_mask == 5) || (word_mask == 9) || (word_mask == 201) || (word_mask == 147) || (word_mask == 202) || (word_mask == 204) || (word_mask == 140) || (word_mask == 149) || (word_mask == 76) || (word_mask == 74) || (word_mask == 73) || (word_mask == 70)))
        pp = tt0.d
        left_T = [{tt0.n:a0} for a0 in pp if    ( (a0 in int_tt[:-1]) )] 
        left_F = [{tt0.n:a0} for a0 in pp if not( (a0 in int_tt[:-1]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt1 = a_seq[1]
        # (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 2))))
        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        vals = [i for i in tt1.d]
        right_T = [{tt1.n: set(v for v in vals if    ( (int(v) == reg_tt[0]) or (int(v) <= (param_tt[0] - int_tt[-1])) ))}]
        right_F = [{tt1.n: set(v for v in vals if not( (int(v) == reg_tt[0]) or (int(v) <= (param_tt[0] - int_tt[-1])) ))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)

        return aliases

    # (((word_mask == 217) || (word_mask == 214) || (word_mask == 213) || (word_mask == 211) || (word_mask == 218) || (word_mask == 133) || (word_mask == 131) || (word_mask == 137) || (word_mask == 134) || (word_mask == 138) || (word_mask == 25) || (word_mask == 26) || (word_mask == 21) || (word_mask == 22) || (word_mask == 28) || (word_mask == 220) || (word_mask == 121) || (word_mask == 122) || (word_mask == 124) || (word_mask == 58) || (word_mask == 54) || (word_mask == 57) || (word_mask == 51) || (word_mask == 53) || (word_mask == 90) || (word_mask == 198) || (word_mask == 195) || (word_mask == 197) || (word_mask == 115) || (word_mask == 117) || (word_mask == 89) || (word_mask == 83) || (word_mask == 86) || (word_mask == 118) || (word_mask == 85) || (word_mask == 3) || (word_mask == 245) || (word_mask == 108) || (word_mask == 246) || (word_mask == 243) || (word_mask == 102) || (word_mask == 101) || (word_mask == 106) || (word_mask == 105) || (word_mask == 38) || (word_mask == 37) || (word_mask == 35) || (word_mask == 60) || (word_mask == 179) || (word_mask == 67) || (word_mask == 252) || (word_mask == 69) || (word_mask == 250) || (word_mask == 172) || (word_mask == 170) || (word_mask == 249) || (word_mask == 182) || (word_mask == 181) || (word_mask == 186) || (word_mask == 6) || (word_mask == 188) || (word_mask == 185) || (word_mask == 99) || (word_mask == 169) || (word_mask == 229) || (word_mask == 227) || (word_mask == 165) || (word_mask == 166) || (word_mask == 92) || (word_mask == 163) || (word_mask == 10) || (word_mask == 12) || (word_mask == 19) || (word_mask == 150) || (word_mask == 153) || (word_mask == 154) || (word_mask == 156) || (word_mask == 234) || (word_mask == 236) || (word_mask == 230) || (word_mask == 233) || (word_mask == 44) || (word_mask == 42) || (word_mask == 41) || (word_mask == 5) || (word_mask == 9) || (word_mask == 201) || (word_mask == 147) || (word_mask == 202) || (word_mask == 204) || (word_mask == 140) || (word_mask == 149) || (word_mask == 76) || (word_mask == 74) || (word_mask == 73) || (word_mask == 70))) -> (((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0))
    # ldg_256_memdesc__Ra64 | sm_100 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_41 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_41(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        # (((word_mask == 217) || (word_mask == 214) || (word_mask == 213) || (word_mask == 211) || (word_mask == 218) || (word_mask == 133) || (word_mask == 131) || (word_mask == 137) || (word_mask == 134) || (word_mask == 138) || (word_mask == 25) || (word_mask == 26) || (word_mask == 21) || (word_mask == 22) || (word_mask == 28) || (word_mask == 220) || (word_mask == 121) || (word_mask == 122) || (word_mask == 124) || (word_mask == 58) || (word_mask == 54) || (word_mask == 57) || (word_mask == 51) || (word_mask == 53) || (word_mask == 90) || (word_mask == 198) || (word_mask == 195) || (word_mask == 197) || (word_mask == 115) || (word_mask == 117) || (word_mask == 89) || (word_mask == 83) || (word_mask == 86) || (word_mask == 118) || (word_mask == 85) || (word_mask == 3) || (word_mask == 245) || (word_mask == 108) || (word_mask == 246) || (word_mask == 243) || (word_mask == 102) || (word_mask == 101) || (word_mask == 106) || (word_mask == 105) || (word_mask == 38) || (word_mask == 37) || (word_mask == 35) || (word_mask == 60) || (word_mask == 179) || (word_mask == 67) || (word_mask == 252) || (word_mask == 69) || (word_mask == 250) || (word_mask == 172) || (word_mask == 170) || (word_mask == 249) || (word_mask == 182) || (word_mask == 181) || (word_mask == 186) || (word_mask == 6) || (word_mask == 188) || (word_mask == 185) || (word_mask == 99) || (word_mask == 169) || (word_mask == 229) || (word_mask == 227) || (word_mask == 165) || (word_mask == 166) || (word_mask == 92) || (word_mask == 163) || (word_mask == 10) || (word_mask == 12) || (word_mask == 19) || (word_mask == 150) || (word_mask == 153) || (word_mask == 154) || (word_mask == 156) || (word_mask == 234) || (word_mask == 236) || (word_mask == 230) || (word_mask == 233) || (word_mask == 44) || (word_mask == 42) || (word_mask == 41) || (word_mask == 5) || (word_mask == 9) || (word_mask == 201) || (word_mask == 147) || (word_mask == 202) || (word_mask == 204) || (word_mask == 140) || (word_mask == 149) || (word_mask == 76) || (word_mask == 74) || (word_mask == 73) || (word_mask == 70)))
        pp = tt0.d
        left_T = [{tt0.n:a0} for a0 in pp if    ( (a0 in int_tt[:-2]) )] 
        left_F = [{tt0.n:a0} for a0 in pp if not( (a0 in int_tt[:-2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt1 = a_seq[1]
        # (((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0))
        vals = [i for i in tt1.d]
        right_T = [{tt1.n: set(v for v in vals if    ( (int(v) + (int(v) == (reg_tt[0] % int_tt[-2])) ) == int_tt[-1]) )}]
        right_F = [{tt1.n: set(v for v in vals if not( (int(v) + (int(v) == (reg_tt[0] % int_tt[-2])) ) == int_tt[-1]) )}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)

        return aliases

    # (((word_mask == 151) || (word_mask == 215) || (word_mask == 155) || (word_mask == 126) || (word_mask == 157) || (word_mask == 158) || (word_mask == 190) || (word_mask == 43) || (word_mask == 251) || (word_mask == 61) || (word_mask == 62) || (word_mask == 238) || (word_mask == 110) || (word_mask == 135) || (word_mask == 235) || (word_mask == 199) || (word_mask == 139) || (word_mask == 174) || (word_mask == 119) || (word_mask == 87) || (word_mask == 171) || (word_mask == 206) || (word_mask == 27) || (word_mask == 222) || (word_mask == 23) || (word_mask == 46) || (word_mask == 173) || (word_mask == 45) || (word_mask == 29) || (word_mask == 253) || (word_mask == 107) || (word_mask == 183) || (word_mask == 254) || (word_mask == 187) || (word_mask == 7) || (word_mask == 219) || (word_mask == 189) || (word_mask == 203) || (word_mask == 142) || (word_mask == 141) || (word_mask == 39) || (word_mask == 77) || (word_mask == 75) || (word_mask == 109) || (word_mask == 125) || (word_mask == 71) || (word_mask == 91) || (word_mask == 103) || (word_mask == 93) || (word_mask == 167) || (word_mask == 205) || (word_mask == 94) || (word_mask == 221) || (word_mask == 78) || (word_mask == 11) || (word_mask == 13) || (word_mask == 59) || (word_mask == 14) || (word_mask == 55) || (word_mask == 30) || (word_mask == 247) || (word_mask == 123) || (word_mask == 231) || (word_mask == 237))) -> (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 3))))
    # ldg_256_memdesc__Ra64 | sm_100 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_42 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_42(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)

        tt0 = a_seq[0]
        # (((word_mask == 151) || (word_mask == 215) || (word_mask == 155) || (word_mask == 126) || (word_mask == 157) || (word_mask == 158) || (word_mask == 190) || (word_mask == 43) || (word_mask == 251) || (word_mask == 61) || (word_mask == 62) || (word_mask == 238) || (word_mask == 110) || (word_mask == 135) || (word_mask == 235) || (word_mask == 199) || (word_mask == 139) || (word_mask == 174) || (word_mask == 119) || (word_mask == 87) || (word_mask == 171) || (word_mask == 206) || (word_mask == 27) || (word_mask == 222) || (word_mask == 23) || (word_mask == 46) || (word_mask == 173) || (word_mask == 45) || (word_mask == 29) || (word_mask == 253) || (word_mask == 107) || (word_mask == 183) || (word_mask == 254) || (word_mask == 187) || (word_mask == 7) || (word_mask == 219) || (word_mask == 189) || (word_mask == 203) || (word_mask == 142) || (word_mask == 141) || (word_mask == 39) || (word_mask == 77) || (word_mask == 75) || (word_mask == 109) || (word_mask == 125) || (word_mask == 71) || (word_mask == 91) || (word_mask == 103) || (word_mask == 93) || (word_mask == 167) || (word_mask == 205) || (word_mask == 94) || (word_mask == 221) || (word_mask == 78) || (word_mask == 11) || (word_mask == 13) || (word_mask == 59) || (word_mask == 14) || (word_mask == 55) || (word_mask == 30) || (word_mask == 247) || (word_mask == 123) || (word_mask == 231) || (word_mask == 237)))
        pp = tt0.d
        left_T = [{tt0.n:a0} for a0 in pp if    ( (a0 in int_tt[:-1]) )] 
        left_F = [{tt0.n:a0} for a0 in pp if not( (a0 in int_tt[:-1]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt1 = a_seq[1]
        # (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 3))))
        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        vals = [i for i in tt1.d]
        right_T = [{tt1.n: set(v for v in vals if    ( (int(v) == reg_tt[0]) or (int(v) <= (param_tt[0] - int_tt[-1])) ))}]
        right_F = [{tt1.n: set(v for v in vals if not( (int(v) == reg_tt[0]) or (int(v) <= (param_tt[0] - int_tt[-1])) ))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((word_mask == 151) || (word_mask == 215) || (word_mask == 155) || (word_mask == 126) || (word_mask == 157) || (word_mask == 158) || (word_mask == 190) || (word_mask == 43) || (word_mask == 251) || (word_mask == 61) || (word_mask == 62) || (word_mask == 238) || (word_mask == 110) || (word_mask == 135) || (word_mask == 235) || (word_mask == 199) || (word_mask == 139) || (word_mask == 174) || (word_mask == 119) || (word_mask == 87) || (word_mask == 171) || (word_mask == 206) || (word_mask == 27) || (word_mask == 222) || (word_mask == 23) || (word_mask == 46) || (word_mask == 173) || (word_mask == 45) || (word_mask == 29) || (word_mask == 253) || (word_mask == 107) || (word_mask == 183) || (word_mask == 254) || (word_mask == 187) || (word_mask == 7) || (word_mask == 219) || (word_mask == 189) || (word_mask == 203) || (word_mask == 142) || (word_mask == 141) || (word_mask == 39) || (word_mask == 77) || (word_mask == 75) || (word_mask == 109) || (word_mask == 125) || (word_mask == 71) || (word_mask == 91) || (word_mask == 103) || (word_mask == 93) || (word_mask == 167) || (word_mask == 205) || (word_mask == 94) || (word_mask == 221) || (word_mask == 78) || (word_mask == 11) || (word_mask == 13) || (word_mask == 59) || (word_mask == 14) || (word_mask == 55) || (word_mask == 30) || (word_mask == 247) || (word_mask == 123) || (word_mask == 231) || (word_mask == 237))) -> (((((Rd) + ((Rd) == `Register@RZ)) % 4) == 0))
    # ldg_256_memdesc__Ra64 | sm_100 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_43 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_43(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)
        
        tt0 = a_seq[0]
        # (((word_mask == 151) || (word_mask == 215) || (word_mask == 155) || (word_mask == 126) || (word_mask == 157) || (word_mask == 158) || (word_mask == 190) || (word_mask == 43) || (word_mask == 251) || (word_mask == 61) || (word_mask == 62) || (word_mask == 238) || (word_mask == 110) || (word_mask == 135) || (word_mask == 235) || (word_mask == 199) || (word_mask == 139) || (word_mask == 174) || (word_mask == 119) || (word_mask == 87) || (word_mask == 171) || (word_mask == 206) || (word_mask == 27) || (word_mask == 222) || (word_mask == 23) || (word_mask == 46) || (word_mask == 173) || (word_mask == 45) || (word_mask == 29) || (word_mask == 253) || (word_mask == 107) || (word_mask == 183) || (word_mask == 254) || (word_mask == 187) || (word_mask == 7) || (word_mask == 219) || (word_mask == 189) || (word_mask == 203) || (word_mask == 142) || (word_mask == 141) || (word_mask == 39) || (word_mask == 77) || (word_mask == 75) || (word_mask == 109) || (word_mask == 125) || (word_mask == 71) || (word_mask == 91) || (word_mask == 103) || (word_mask == 93) || (word_mask == 167) || (word_mask == 205) || (word_mask == 94) || (word_mask == 221) || (word_mask == 78) || (word_mask == 11) || (word_mask == 13) || (word_mask == 59) || (word_mask == 14) || (word_mask == 55) || (word_mask == 30) || (word_mask == 247) || (word_mask == 123) || (word_mask == 231) || (word_mask == 237)))
        pp = tt0.d
        left_T = [{tt0.n:a0} for a0 in pp if    ( (a0 in int_tt[:-2]) )] 
        left_F = [{tt0.n:a0} for a0 in pp if not( (a0 in int_tt[:-2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt1 = a_seq[1]
        # (((((Rd) + ((Rd) == `Register@RZ)) % 4) == 0))
        vals = [i for i in tt1.d]
        right_T = [{tt1.n: set(v for v in vals if    ( (int(v) + (int(v) == (reg_tt[0] % int_tt[-2])) ) == int_tt[-1]) )}]
        right_F = [{tt1.n: set(v for v in vals if not( (int(v) + (int(v) == (reg_tt[0] % int_tt[-2])) ) == int_tt[-1]) )}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)

        return aliases

    # (((word_mask == 15) || (word_mask == 143) || (word_mask == 207) || (word_mask == 159) || (word_mask == 47) || (word_mask == 31) || (word_mask == 191) || (word_mask == 223) || (word_mask == 63) || (word_mask == 111) || (word_mask == 239) || (word_mask == 127) || (word_mask == 175) || (word_mask == 95) || (word_mask == 79) || (word_mask == 255))) -> (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 4))))
    # ldg_256_memdesc__Ra64 | sm_100 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_44 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_44(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)
        
        tt0 = a_seq[0]
        # (((word_mask == 15) || (word_mask == 143) || (word_mask == 207) || (word_mask == 159) || (word_mask == 47) || (word_mask == 31) || (word_mask == 191) || (word_mask == 223) || (word_mask == 63) || (word_mask == 111) || (word_mask == 239) || (word_mask == 127) || (word_mask == 175) || (word_mask == 95) || (word_mask == 79) || (word_mask == 255)))
        pp = tt0.d
        left_T = [{tt0.n:a0} for a0 in pp if    ( (a0 in int_tt[:-1]) )] 
        left_F = [{tt0.n:a0} for a0 in pp if not( (a0 in int_tt[:-1]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt1 = a_seq[1]
        # (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 4))))
        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        vals = [i for i in tt1.d]
        right_T = [{tt1.n: set(v for v in vals if    ( (int(v) == reg_tt[0]) or (int(v) <= (param_tt[0] - int_tt[-1])) ))}]
        right_F = [{tt1.n: set(v for v in vals if not( (int(v) == reg_tt[0]) or (int(v) <= (param_tt[0] - int_tt[-1])) ))}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)
        return aliases

    # (((word_mask == 15) || (word_mask == 143) || (word_mask == 207) || (word_mask == 159) || (word_mask == 47) || (word_mask == 31) || (word_mask == 191) || (word_mask == 223) || (word_mask == 63) || (word_mask == 111) || (word_mask == 239) || (word_mask == 127) || (word_mask == 175) || (word_mask == 95) || (word_mask == 79) || (word_mask == 255))) -> (((((Rd) + ((Rd) == `Register@RZ)) % 4) == 0))
    # ldg_256_memdesc__Ra64 | sm_100 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_45 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_45(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)
        
        tt0 = a_seq[0]
        # (((word_mask == 15) || (word_mask == 143) || (word_mask == 207) || (word_mask == 159) || (word_mask == 47) || (word_mask == 31) || (word_mask == 191) || (word_mask == 223) || (word_mask == 63) || (word_mask == 111) || (word_mask == 239) || (word_mask == 127) || (word_mask == 175) || (word_mask == 95) || (word_mask == 79) || (word_mask == 255)))
        pp = tt0.d
        left_T = [{tt0.n:a0} for a0 in pp if    ( (a0 in int_tt[:-2]) )] 
        left_F = [{tt0.n:a0} for a0 in pp if not( (a0 in int_tt[:-2]) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt1 = a_seq[1]
        # (((((Rd) + ((Rd) == `Register@RZ)) % 4) == 0))
        vals = [i for i in tt1.d]
        right_T = [{tt1.n: set(v for v in vals if    ( (int(v) + (int(v) == (reg_tt[0] % int_tt[-2])) ) == int_tt[-1]) )}]
        right_F = [{tt1.n: set(v for v in vals if not( (int(v) + (int(v) == (reg_tt[0] % int_tt[-2])) ) == int_tt[-1]) )}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)

        return aliases

    # (((word_mask == 144) || (word_mask == 48) || (word_mask == 16) || (word_mask == 32) || (word_mask == 192) || (word_mask == 0) || (word_mask == 208) || (word_mask == 64) || (word_mask == 240) || (word_mask == 112) || (word_mask == 128) || (word_mask == 176) || (word_mask == 80) || (word_mask == 224) || (word_mask == 160) || (word_mask == 96))) -> ((((Rd) == `Register@RZ)))
    # ldg_256_memdesc__Ra64 | sm_100 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_46 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_46(aliases:typing.List[dict], sass:SM_SASS, expr:list, alias_nt:list, to_limit):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        a_seq = SASS_Expr_Domain_Range.__get_alias_sequence(alias_tt, alias_nt, to_limit)
        
        tt0 = a_seq[0]
        # (((word_mask == 144) || (word_mask == 48) || (word_mask == 16) || (word_mask == 32) || (word_mask == 192) || (word_mask == 0) || (word_mask == 208) || (word_mask == 64) || (word_mask == 240) || (word_mask == 112) || (word_mask == 128) || (word_mask == 176) || (word_mask == 80) || (word_mask == 224) || (word_mask == 160) || (word_mask == 96)))
        pp = tt0.d
        left_T = [{tt0.n:a0} for a0 in pp if    ( (a0 in int_tt) )] 
        left_F = [{tt0.n:a0} for a0 in pp if not( (a0 in int_tt) )] 
        if left_T: left_T = SASS_Expr_Domain_Contract.group(left_T)
        if left_F: left_F = SASS_Expr_Domain_Contract.group(left_F)

        tt1 = a_seq[1]
        # ((((Rd) == `Register@RZ)))
        vals = [i for i in tt1.d]
        right_T = [{tt1.n: set(v for v in vals if    (v == reg_tt[0]) )}]
        right_F = [{tt1.n: set(v for v in vals if not(v == reg_tt[0]) )}]

        res = SASS_Expr_Domain_Utils.implication(left_T, left_F, right_T, right_F)
        aliases = SASS_Expr_Domain_Range.__attach_results(res, aliases)

        return aliases

    __EXPR_TYPES = {
        __EXPR_TYPE_1 : __expr_type_1,
        __EXPR_TYPE_2 : __expr_type_2,
        __EXPR_TYPE_3 : __expr_type_3,
        __EXPR_TYPE_4 : __expr_type_4,
        __EXPR_TYPE_5 : __expr_type_5,
        __EXPR_TYPE_6 : __expr_type_6,
        __EXPR_TYPE_7 : __expr_type_7,
        __EXPR_TYPE_8 : __expr_type_8,
        __EXPR_TYPE_9 : __expr_type_9,
        __EXPR_TYPE_10 : __expr_type_10,
        __EXPR_TYPE_11 : __expr_type_11,
        __EXPR_TYPE_12 : __expr_type_12,
        __EXPR_TYPE_13 : __expr_type_13,
        __EXPR_TYPE_14 : __expr_type_14,
        __EXPR_TYPE_15 : __expr_type_15,
        __EXPR_TYPE_16 : __expr_type_16,
        __EXPR_TYPE_17 : __expr_type_17,
        __EXPR_TYPE_18 : __expr_type_18,
        __EXPR_TYPE_19 : __expr_type_19,
        __EXPR_TYPE_20 : __expr_type_20,
        __EXPR_TYPE_21 : __expr_type_21,
        __EXPR_TYPE_22 : __expr_type_22,
        __EXPR_TYPE_23 : __expr_type_23,
        __EXPR_TYPE_24 : __expr_type_24,
        __EXPR_TYPE_25 : __expr_type_25,
        __EXPR_TYPE_26 : __expr_type_26,
        __EXPR_TYPE_27 : __expr_type_27,
        __EXPR_TYPE_28 : __expr_type_28,
        __EXPR_TYPE_29 : __expr_type_29,
        __EXPR_TYPE_30 : __expr_type_30,
        __EXPR_TYPE_31 : __expr_type_31,
        __EXPR_TYPE_32 : __expr_type_32,
        __EXPR_TYPE_33 : __expr_type_33,
        __EXPR_TYPE_34 : __expr_type_34,
        __EXPR_TYPE_35 : __expr_type_35,
        __EXPR_TYPE_36 : __expr_type_36,
        __EXPR_TYPE_37 : __expr_type_37,
        __EXPR_TYPE_40 : __expr_type_40,
        __EXPR_TYPE_41 : __expr_type_41,
        __EXPR_TYPE_42 : __expr_type_42,
        __EXPR_TYPE_43 : __expr_type_43,
        __EXPR_TYPE_44 : __expr_type_44,
        __EXPR_TYPE_45 : __expr_type_45,
        __EXPR_TYPE_46 : __expr_type_46
    }

    @staticmethod
    def expr_types() -> dict: return SASS_Expr_Domain_Range.__EXPR_TYPES
