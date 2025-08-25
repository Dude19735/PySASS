import typing
import _config as sp
from py_sass import SM_SASS
from py_sass._sass_expression_ops import *
from py_sass import SASS_Expr_Domain_Contract
from py_sass_ext import SASS_Bits
from _sass_expression_domain_utils import SASS_Expr_Domain_Utils

##########################################################################################3
# NOTE: the further up a solve method, the more common.
##########################################################################################3

class SASS_Expr_Domain_Common:
    @staticmethod
    def __reduce_reg_dom(reg_dom:list):
        # NOTE: limiting register domains is dome in TT_Reg.get_domain()
        if not isinstance(reg_dom, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return reg_dom # [i for i in reg_dom if (i<5) or (100<i and i<105) or (i>245)]
    
    @staticmethod
    def __group_implication(left_side_T_ll:list, left_side_F_ll:list, right_side_T_ll:list, right_side_F_ll:list):
        if not isinstance(left_side_F_ll, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(left_side_T_ll, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(right_side_F_ll, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(right_side_T_ll, list): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if left_side_F_ll: left_side_F = SASS_Expr_Domain_Contract.group(left_side_F_ll)
        else: left_side_F = []
        if left_side_T_ll: left_side_T = SASS_Expr_Domain_Contract.group(left_side_T_ll)
        else: left_side_T = []
        if right_side_F_ll: right_side_F = SASS_Expr_Domain_Contract.group(right_side_F_ll)
        else: right_side_F = []
        if right_side_T_ll: right_side_T = SASS_Expr_Domain_Contract.group(right_side_T_ll)
        else: right_side_T = []

        return {'lt':left_side_T, 'lf':left_side_F, 'rt':right_side_T, 'rf':right_side_F}

    @staticmethod
    def __attach_results(new_d_vals:list|dict, old_d:dict):
        if isinstance(new_d_vals, list):
            if not new_d_vals: return []
            old_stuff = [i for i in old_d.items() if not i[0] in new_d_vals[0].keys()]
            for ndv in new_d_vals:
                ndv.update(old_stuff)
            return new_d_vals
        elif isinstance(new_d_vals, dict):
            if not new_d_vals: return {}
            old_stuff = [i for i in old_d.items() if not i[0] in new_d_vals.keys()]
            new_d_vals.update(old_stuff)
            return new_d_vals
        else:
            raise Exception(sp.CONST__ERROR_ILLEGAL)
        
    @staticmethod
    def remove_empty_variants(nd:typing.List[dict]|dict) -> typing.List[dict]|dict:
        if isinstance(nd, dict):
            if any([len(v)==0 for v in nd.values()]):
                return dict()
            else: return nd
        elif isinstance(nd, list):
            n = [r for r in nd if not any([len(v)==0 for v in r.values()])]
        else:
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return n

    @staticmethod
    def final_domain_check(res:typing.List[dict]|dict):
        if isinstance(res, dict):
            if res == dict(): return False
            if any([len(v)==0 for v in res.values()]): return False
        elif isinstance(res, list):
            if res == []: return False
            if any([any([len(v)==0 for v in r.values()]) for r in res]): return False
        else:
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return True

    @staticmethod
    def __get_alias_nt_domains(expr_alias_tt:list, alias_nt:list, domain_vals:dict, keep_sass_bits=False) -> list:
        """
        Get the domains of all aliases inside of expr_alias by matching the names inside of alias_nt to the names of all expr_alias
        @Input:
         - expr_alias_tt: list of TT_Term as generally stored in Op_Alias.value()
         - alias_nt: list of strings with the names of the aliases as they apear in the expression
         - domain_vals: dict of the domains for each entry in alias_nt using strings in alias_nt as keys

        NOTE: there are a few caveats:
         - if an expr_alias is a register, it's representative in alias_nt may be
            1. the name of the alias
            2. the name of the register
            3. the name of the register followed by "(default_val)", like AInteger(32) if the name in alias_nt is AInteger
               (this is related to that the instr class defs for registers sometimes use an alias, like 'size' inside of AInteger(32):size
               or 'AInteger' in the definitions of the CONDITIONS or generally for expressions or ENCODINGS => need to check both to make sure
               we find a match)
         - we have to return the matches in the same sequence as in expr_alias to make it usable 

         @Return a list of pairs [..(alias_nt[i], domain_vals[alias_nt[i]])..] matching the sequence of expr_alias
        """
        if not (len(expr_alias_tt)==len(alias_nt)): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        res = []
        # make sure we really only have one of match
        for tt in expr_alias_tt:
            sub_r = []
            for aa in alias_nt:
                # if we have a total match, we use that one
                if str(tt.alias) == aa:
                    sub_r.append((aa, list(domain_vals[aa])))
                    break
            if not sub_r:
                # if we have a match on the entire register, take that one
                for aa in alias_nt:
                    if str(tt).startswith(aa):
                        sub_r.append((aa, list(domain_vals[aa])))
                        break
            if not sub_r:
                # otherwise, we may at least have a match one the start of the alias...
                for aa in alias_nt:
                    if str(tt.alias).startswith(aa):
                        sub_r.append((aa, list(domain_vals[aa])))
                        break
            res.append(sub_r)

        # if not keep_sass_bits:
        #     res = [[(aa, list(domain_vals[aa])) for aa in alias_nt if (str(tt).startswith(aa) or str(tt.alias).startswith(aa))] for tt in expr_alias_tt]
        # else:
        #     res = [[(aa, [int(i) for i in domain_vals[aa]]) for aa in alias_nt if (str(tt).startswith(aa) or str(tt.alias).startswith(aa))] for tt in expr_alias_tt]
        
        # raise an exception if we find more than one match for one of them
        if not all([len(a)==1 for a in res]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # raise an exception if we didn't find a match for all of the expr_alias and alias_nt
        rr = [i[0] for i in res]
        if not keep_sass_bits:
            rr = [(a[0], [int(i) for i in a[1]]) for a in rr]

        xx = dict(rr)
        if not all(a in xx for a in alias_nt): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return rr

    # (Ra != `Register@RZ)
    # ALD_PHYS | sm_50 to sm_62
    __OLD_EXPR_TYPE_1  = ('Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace').__hash__()
    __EXPR_TYPE_1 = ('Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_1(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        vals = domain_vals[alias]
        non_val = expr[-2].value()
        if non_val in vals: 
            vals.remove(non_val)
            domain_vals[alias] = vals
        
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # (((Ra)==`Register@RZ)||((Ra)<=(%MAX_REG_COUNT-1)))
    # AL2P | sm_50 to sm_90
    __OLD_EXPR_TYPE_2  = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_LBrace', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_2 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_LBrace', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_2(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        vals = domain_vals[alias]
        sub_val = expr[-4].value()
        eq_val = expr[6].value()

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        leq_val = param_tt[0] - sub_val

        domain_vals[alias] = set(v for v in vals if (v == eq_val or v <= leq_val))
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals
    
    # (Ra == `Register@RZ)
    __OLD_EXPR_TYPE_3  = ('Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace').__hash__()
    __EXPR_TYPE_3 = ('Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_3(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        vals = domain_vals[alias]
        only_val = expr[-2].value()
        domain_vals[alias] = set(i for i in vals if i == only_val)
        
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals
    
    # (((Rd) == `Register@RZ) || (((Rd) <= (%MAX_REG_COUNT - 1)) && ((Rd) != `Register@R254)))
    # al2p__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_4 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_LBrace', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_4 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_LBrace', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_4(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        vals = domain_vals[alias]
        reg_val_1 = expr[6].value()
        sub_val = expr[18].value()
        reg_val_2 = expr[-4].value()
        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        leq_val = param_tt[0] - sub_val
        old = domain_vals[alias]
        domain_vals[alias] = set(v for v in vals if (v == reg_val_1 or (v <= leq_val and v != reg_val_2)))

        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # DEFINED TABLES_opex_0(batch_t,usched_info)
    # al2p__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_6 = ('Op_Defined',).__hash__()
    __EXPR_TYPE_6 = ('Op_Defined',).__hash__()
    @staticmethod
    def __expr_type_6(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        table = getattr(sass.sm.details.TABLES, str(expr[1]))

        args_all = [i.value() for i in expr[3:-1] if not isinstance(i, Op_Comma)]
        args_tt = [i for i in args_all if not isinstance(i, int)]
        tt_ind = [args_all.index(i) for i in args_tt]
        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(args_tt, alias_nt, domain_vals, keep_sass_bits=True)
        args = [i for i in args_all]
        for i,v in zip(tt_ind, expr_vals): args[i] = (v[0], v[1])
        for ind,i in enumerate(args):
            if not isinstance(i, tuple): args[ind] = ('_', [i])
        kk = [i[0] for i in args]
        pp = [dict([j for j in zip(kk,i) if j[0] != '_']) for i in itt.product(*[i[1] for i in args]) if i in table.keys()]
        res = SASS_Expr_Domain_Contract.group(pp)

        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # (((Rb) + ((Rb) == `Register@RZ)) % 2) == 0
    # bmov_dst64__R | sm_70 to sm_90
    __OLD_EXPR_TYPE_8 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int').__hash__()
    __EXPR_TYPE_8 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int').__hash__()
    @staticmethod
    def __expr_type_8(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        vals = domain_vals[alias]
        reg_val_1 = expr[11].value()
        mod_val = expr[15].value()

        old = domain_vals[alias]
        domain_vals[alias] = set(v for v in vals if ((v + int(v == reg_val_1)) % mod_val) == 0)
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D))) -> ((((Ra) != `Register@RZ)) && (((Rb) != `Register@RZ)))
    # tex_scr_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_9 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_9 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_9(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)) && (((Rb) != `Register@RZ)))
        pp2 = list(itt.product(
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[4]['v']),
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[5]['v'])
        ))
        right_T_ll = [{nn[4]['n']:a4, nn[5]['n']:a5} for a4,a5 in pp2 if    ((a4 != reg_tt[4]) and (a5 != reg_tt[5]))]
        right_F_ll = [{nn[4]['n']:a4, nn[5]['n']:a5} for a4,a5 in pp2 if not((a4 != reg_tt[4]) and (a5 != reg_tt[5]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((ParamA != `ParamA@ARRAY_3D))
    # TMML | sm_50 to sm_90
    __OLD_EXPR_TYPE_10 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_10 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_10(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        n_expr = expr[1:-1]
        assert(tuple(type(i).__name__ for i in n_expr).__hash__() == SASS_Expr_Domain_Common.__OLD_EXPR_TYPE_1)
        return SASS_Expr_Domain_Common.__expr_type_1(sass, n_expr, alias_nt, domain_vals)

    # (((sz == `AInteger@64))) -> (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 2))))
    # ald__LOGICAL_RaRZ_default | sm_70 to sm_90
    __OLD_EXPR_TYPE_11 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_11 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_11(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `AInteger@64)))
        left_T_ll = [{nn[0]['n']:a0} for a0 in nn[0]['v'] if (a0==reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in nn[0]['v'] if not(a0==reg_tt[0])]

        # (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 2))))
        right_T_ll = [{nn[1]['n']:a1} for a1 in nn[1]['v'] if (a1 == reg_tt[1] or a1 <= param_tt[0] - int_tt[0])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in nn[1]['v'] if not(a1 == reg_tt[1] or a1 <= param_tt[0] - int_tt[0])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((Ra) != `Register@RZ)
    # al2p__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_12 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace').__hash__()
    __EXPR_TYPE_12 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_12(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        n_expr = [expr[0], expr[2]] + expr[4:]
        assert(tuple(type(i).__name__ for i in n_expr).__hash__() == SASS_Expr_Domain_Common.__OLD_EXPR_TYPE_1)
        return SASS_Expr_Domain_Common.__expr_type_1(sass, n_expr, alias_nt, domain_vals)

    # (((sz == `AInteger@64))) -> (((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0))
    # ald__LOGICAL_RaRZ_default | sm_70 to sm_90
    __OLD_EXPR_TYPE_13 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_13 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_13(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `AInteger@64)))
        left_T_ll = [{nn[0]['n']:a0} for a0 in nn[0]['v'] if (a0==reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in nn[0]['v'] if not(a0==reg_tt[0])]

        # (((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0))
        right_T_ll = [{nn[1]['n']:a1} for a1 in nn[1]['v'] if (((int(a1) + (int(a1) == reg_tt[1])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in nn[1]['v'] if not(((int(a1) + (int(a1) == reg_tt[1])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((cop != `COP@INVALID6) && (cop != `COP@INVALID7))
    # atom__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_14 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_14 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_14(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        alias_vals = domain_vals[alias]
        reg_val_1 = expr[4].value()
        reg_val_2 = expr[-3].value()

        old = domain_vals[alias]
        domain_vals[alias] = set(v for v in alias_vals if (v != reg_val_1 and v != reg_val_2))
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))) && ((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
    # tex_scr_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_15 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_15 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_15(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))) && ((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
        pp2 = list(itt.product(
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[4]['v']),
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[5]['v'])
        ))
        right_T_ll = [{nn[4]['n']:a4, nn[5]['n']:a5} for a4,a5 in pp2 if    (((a4 == reg_tt[4]) or (a4 <= param_tt[0] - int_tt[0])) and ((a5 == reg_tt[5]) or (a5 <= param_tt[0] - int_tt[1])))]
        right_F_ll = [{nn[4]['n']:a4, nn[5]['n']:a5} for a4,a5 in pp2 if not(((a4 == reg_tt[4]) or (a4 <= param_tt[0] - int_tt[0])) and ((a5 == reg_tt[5]) or (a5 <= param_tt[0] - int_tt[1])))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0) && ((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
    # tex_scr_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_16 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_16 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_16(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@ARRAY_2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0) && ((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
        pp2 = list(itt.product(
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[4]['v']),
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[5]['v'])
        ))
        right_T_ll = [{nn[4]['n']:a4, nn[5]['n']:a5} for a4,a5 in pp2 if    ( (((int(a4) + int(a4 == reg_tt[4])) % int_tt[0]) == int_tt[1]) and (((int(a5) + int(a5 == reg_tt[5])) % int_tt[2]) == int_tt[3]) )]
        right_F_ll = [{nn[4]['n']:a4, nn[5]['n']:a5} for a4,a5 in pp2 if not( (((int(a4) + int(a4 == reg_tt[4])) % int_tt[0]) == int_tt[1]) and (((int(a5) + int(a5 == reg_tt[5])) % int_tt[2]) == int_tt[3]) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((reuse_src_a == 1) || (reuse_src_b == 1)) -> ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
    # bmsk__RRR_RRR | sm_70 to sm_90
    __OLD_EXPR_TYPE_17 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_17 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_17(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((reuse_src_a == 1) || (reuse_src_b == 1))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==int_tt[0]) or (a1==int_tt[1]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==int_tt[0]) or (a1==int_tt[1]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ( a2 in int_tt[2:] )]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not( a2 in int_tt[2:] )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((dc == `DC@noDC)) && ((toff == `TOFF@PTP))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
    # tld4_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_18 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_18 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_18(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((dc == `DC@noDC)) && ((toff == `TOFF@PTP)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2 == reg_tt[2]) or (a2 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2 == reg_tt[2]) or (a2 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
    # atom_cas__RaNonRZ_CAS | sm_70 to sm_90
    __OLD_EXPR_TYPE_19 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_19 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_19(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    ((a0==reg_tt[0]) or (a0==reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not((a0==reg_tt[0]) or (a0==reg_tt[1]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    ((a1 == reg_tt[2]) or (a1 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not((a1 == reg_tt[2]) or (a1 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
    # atom_cas__RaNonRZ_CAS | sm_70 to sm_90
    __OLD_EXPR_TYPE_20 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_20 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_20(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    ((a0==reg_tt[0]) or (a0==reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not((a0==reg_tt[0]) or (a0==reg_tt[1]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (((int(a1) + int(a1 == reg_tt[2])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(((int(a1) + int(a1 == reg_tt[2])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((reuse_src_a == 1)) -> ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
    # bmsk__RCR_RCR | sm_70 to sm_90
    __OLD_EXPR_TYPE_21 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_21 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_21(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((reuse_src_a == 1))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0==int_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0==int_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in int_tt[1:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in int_tt[1:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((Sb_bank <= 17) || (Sb_bank >= 24 && Sb_bank <= 31))
    # bmov_dst64__C | sm_70 to sm_90
    __OLD_EXPR_TYPE_22 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_GreaterOrEqual', 'Op_Int', 'Op_And', 'Op_Alias', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_22 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_GreaterOrEqual', 'Op_Int', 'Op_And', 'Op_Alias_0', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_22(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((Sb_bank <= 17) || (Sb_bank >= 24 && Sb_bank <= 31))
        pp = nn[0]['v']
        vals = set([a0 for a0 in pp if ((a0 <= int_tt[0]) or (a0 >= int_tt[1] and a0 <= int_tt[2]))])
        vals_dict = {nn[0]['n']:vals}
        xx = SASS_Expr_Domain_Common.__attach_results(vals_dict, domain_vals)
        return xx

    # (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64))) -> ((((Rb) != `Register@RZ)))
    # atomg_cas__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_23 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_23 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_23(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `ATOMCASSZ@U64) || (sz == `ATOMCASSZ@64)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    ((a0==reg_tt[0]) or (a0==reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not((a0==reg_tt[0]) or (a0==reg_tt[1]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rb) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 != reg_tt[2])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 != reg_tt[2])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (size == `SQInteger@32) -> (((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 1))
    # ATOM | sm_50 to sm_62
    __OLD_EXPR_TYPE_24 = ('Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_24 = ('Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_24(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (size == `SQInteger@32)
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0==reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0==reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 1))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    ((a1 == reg_tt[1]) or (a1 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not((a1 == reg_tt[1]) or (a1 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (constBank <= %MAX_CONST_BANK)
    # BConst_IADD3 | sm_50 to sm_62
    __OLD_EXPR_TYPE_25 = ('Op_LBrace', 'Op_Alias', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_RBrace').__hash__()
    __EXPR_TYPE_25 = ('Op_LBrace', 'Op_Alias_0', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_25(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        max_const_bank = sass.sm.details.PARAMETERS.MAX_CONST_BANK
        const_bank = alias_nt[0]
        vals = domain_vals[const_bank]

        domain_vals[const_bank] = set(v for v in vals if (v <= max_const_bank))
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # (%SHADER_TYPE == $ST_CS) ->  !(Sb_bank >= 8 && Sb_bank <= 31)
    # bmov_dst64__C | sm_80 to sm_90
    __OLD_EXPR_TYPE_26 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Implication', 'Op_Not', 'Op_LBrace', 'Op_Alias', 'Op_GreaterOrEqual', 'Op_Int', 'Op_And', 'Op_Alias', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace').__hash__()
    __EXPR_TYPE_26 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Implication', 'Op_Not', 'Op_LBrace', 'Op_Alias_0', 'Op_GreaterOrEqual', 'Op_Int', 'Op_And', 'Op_Alias_0', 'Op_SmallerOrEqual', 'Op_Int', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_26(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (%SHADER_TYPE == $ST_CS)
        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        const_tt = [i.value() for i in expr if isinstance(i, Op_Constant)]
        shader_type = param_tt[0]
        st_cs = const_tt[0]
        left = (shader_type == st_cs)

        # !(Sb_bank >= 8 && Sb_bank <= 31)
        pp = nn[0]['v']
        impl = [{nn[0]['n']: set(i for i in pp if (not left or (not (i >= int_tt[0] and i <= int_tt[1])) ) )}]
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (%SHADER_TYPE == $ST_UNKNOWN) || ((%SHADER_TYPE == $ST_TRAP) || (%SHADER_TYPE == $ST_TI))
    # ast__PATCH_RaNonRZOffset | sm_70 to sm_90
    __OLD_EXPR_TYPE_27 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_27 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_27(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        # Nothing to do cause no params ^^
        return domain_vals

    # (((e == `E@E))) -> ((((Ra) != `Register@RZ)))
    # atom__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_28 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_28 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_28(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((e == `E@E)))
        left_T_ll = [{nn[0]['n']:a0} for a0 in nn[0]['v'] if (a0==reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in nn[0]['v'] if not(a0==reg_tt[0])]

        # ((((Ra) != `Register@RZ)))
        right_T_ll = [{nn[1]['n']:a1} for a1 in nn[1]['v'] if (a1 != reg_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in nn[1]['v'] if not(a1 != reg_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC@nolodlc))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
    # tex_scr_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_29 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_29 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_29(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC@nolodlc)))
        pp = list(itt.product(nn[0]['v'], nn[1]['v'], nn[2]['v'], nn[3]['v']))
        left_T_ll = [{nn[0]['n']:a0,nn[1]['n']:a1,nn[2]['n']:a2,nn[3]['n']:a3} for a0,a1,a2,a3 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0,nn[1]['n']:a1,nn[2]['n']:a2,nn[3]['n']:a3} for a0,a1,a2,a3 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
        pp2 = nn[4]['v']
        right_T_ll = [{nn[4]['n']:a4} for a4 in pp2 if    ((a4==reg_tt[4]) or (a4 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[4]['n']:a4} for a4 in pp2 if not((a4==reg_tt[4]) or (a4 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC@nolodlc))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
    # tex_scr_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_30 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_30 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_30(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC@nolodlc)))
        pp = list(itt.product(nn[0]['v'], nn[1]['v'], nn[2]['v'], nn[3]['v']))
        left_T_ll = [{nn[0]['n']:a0,nn[1]['n']:a1,nn[2]['n']:a2,nn[3]['n']:a3} for a0,a1,a2,a3 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0,nn[1]['n']:a1,nn[2]['n']:a2,nn[3]['n']:a3} for a0,a1,a2,a3 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]) and (a3==reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
        pp2 = nn[4]['v']
        right_T_ll = [{nn[4]['n']:a4} for a4 in pp2 if    (((int(a4) + int(a4 == reg_tt[4])) % int_tt[0] ) == int_tt[1])]
        right_F_ll = [{nn[4]['n']:a4} for a4 in pp2 if not(((int(a4) + int(a4 == reg_tt[4])) % int_tt[0] ) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((dstfmt == `FloatNo64@F32)) && ((size == `SIZE_64..2@64x8x16) || (size == `SIZE_64..2@64x8x8))) -> (((((Rc) == `Register@RZ) || ((Rc) <= %MAX_REG_COUNT - 4))))
    # hgmma_Ra_URb_Rc_ | sm_90 to sm_90
    __OLD_EXPR_TYPE_31 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_31 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_31(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((dstfmt == `FloatNo64@F32)) && ((size == `SIZE_64..2@64x8x16) || (size == `SIZE_64..2@64x8x8)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0]) and ((a1==reg_tt[1]) or (a1==reg_tt[2])))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0]) and ((a1==reg_tt[1]) or (a1==reg_tt[2])))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rc) == `Register@RZ) || ((Rc) <= %MAX_REG_COUNT - 4))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2==reg_tt[3]) or (a2 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2==reg_tt[3]) or (a2 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((size == `SQInteger@U32) || (size == `SQInteger@S32) || (size == `SQInteger@U64)))
    # ATOM_CAS | sm_50 to sm_90
    __OLD_EXPR_TYPE_32 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_32 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_32(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        vals = domain_vals[alias]
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]

        domain_vals[alias] = set(v for v in vals if ((v==reg_tt[0]) or (v==reg_tt[1]) or (v==reg_tt[2])))
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # (dst_wr_sb == 7)
    # AST | sm_50 to sm_90
    __OLD_EXPR_TYPE_33 = ('Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    __EXPR_TYPE_33 = ('Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_33(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        int_tt = expr[3].value()

        domain_vals[alias] = set(i for i in domain_vals[alias] if i == int_tt)
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # IsEven(((Rd) + ((Rd) == `Register@RZ)))
    # Const1_DFMA | sm_50 to sm_62
    __OLD_EXPR_TYPE_34 = ('Op_IsEven', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_34 = ('Op_IsEven', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_34(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        pp2 = nn[0]['v']
        res = [{ nn[0]['n']: set(a0 for a0 in pp2 if (((int(a0) + int(a0 == reg_tt[0])) % 2) == 0)) }]
        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # (((dc == `DC@noDC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D))) -> ((((Ra) != `Register@RZ)) && (((Rb) != `Register@RZ)))
    # tld4_scr_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_35 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_35 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_35(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((dc == `DC@noDC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)) && (((Rb) != `Register@RZ)))
        pp2 = list(itt.product(
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v']),
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[4]['v'])
        ))
        right_T_ll = [{nn[3]['n']:a3,nn[4]['n']:a4} for a3,a4 in pp2 if    (a3 != reg_tt[3] and a4 != reg_tt[4])]
        right_F_ll = [{nn[3]['n']:a3,nn[4]['n']:a4} for a3,a4 in pp2 if not(a3 != reg_tt[3] and a4 != reg_tt[4])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((Ra) == `Register@RZ)
    # al2p__RaRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_36 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace').__hash__()
    __EXPR_TYPE_36 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_36(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        reg_tt = expr[5].value()

        domain_vals[alias] = set(i for i in domain_vals[alias] if i==reg_tt)
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # (((pquad == `PQUAD@PQUAD))) -> (((cbu_state == `CBU_STATE_DIST@MACTIVE)))
    # bmov_pquad__RCR | sm_70 to sm_90
    __OLD_EXPR_TYPE_37 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_37 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_37(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        pquad_tt = expr[3].value()
        cbu_state_tt = expr[-6].value()
        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains([pquad_tt, cbu_state_tt], alias_nt, domain_vals)

        pquad_name = expr_vals[0][0]
        pquad_val = expr_vals[0][1]
        cbu_state_name = expr_vals[1][0]
        cbu_state_val_val = expr_vals[1][1]
        
        reg1_val = expr[5].value()
        reg2_val = expr[-4].value()

        pquad_bitlen = pquad_tt.min_bit_len()
        cbu_state_bitlen = cbu_state_tt.min_bit_len()
        pp = [{
            pquad_name:SASS_Bits.from_int(a, bit_len=pquad_bitlen, signed=0), 
            cbu_state_name:SASS_Bits.from_int(b, bit_len=cbu_state_bitlen, signed=0)
            } for a,b in itt.product(pquad_val, cbu_state_val_val) if (not(a==reg1_val) or b==reg2_val)
        ]
        res = SASS_Expr_Domain_Contract.group(pp)

        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # (((Rd) + ((Rd) == `Register@RZ)) % ARegAlignment(AInteger)) == 0
    # ALD | sm_50 to sm_62
    __OLD_EXPR_TYPE_38 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_RBrace', 'Op_Equal', 'Op_Int').__hash__()
    __EXPR_TYPE_38 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_RBrace', 'Op_Equal', 'Op_Int').__hash__()
    @staticmethod
    def __expr_type_38(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        Rd_tt = expr[3].value()
        AInteger_tt = expr[-5].value()
        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains([Rd_tt, AInteger_tt], alias_nt, domain_vals)
        Rd_name = expr_vals[0][0]
        Rd_val = expr_vals[0][1]
        AInteger_name = expr_vals[1][0]
        AInteger_val = expr_vals[1][1]

        reg1_val = expr[11].value()
        table = getattr(sass.sm.details.TABLES, str(expr[-7]))

        res = []
        AInteger_bitlen = len(bin(max(max([i for i in k]) for k in table.keys()))[2:])
        Rd_bitlen = Rd_tt.min_bit_len()
        for AInteger in AInteger_val:
            for rd in Rd_val:
                if ((AInteger,) in table) and ((rd + (rd == reg1_val)) % table[(AInteger,)]) == 0:
                    res.append({
                        Rd_name: SASS_Bits.from_int(rd, bit_len=Rd_bitlen, signed=0), 
                        AInteger_name: SASS_Bits.from_int(AInteger, bit_len=AInteger_bitlen, signed=0)
                    })

        new_domain_vals = SASS_Expr_Domain_Contract.group(res)
        xx = SASS_Expr_Domain_Common.__attach_results(new_domain_vals, domain_vals)

        # SASS_Expr_Domain_Common.final_domain_check(new_domain_vals)
        return xx

    # (%SHADER_TYPE == $ST_UNKNOWN) || (%SHADER_TYPE == $ST_CS)
    # ATOMS | sm_50 to sm_62
    __OLD_EXPR_TYPE_39 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace').__hash__()
    __EXPR_TYPE_39 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_39(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        # ^^
        return domain_vals

    # !DEFINED TABLES_mem_0_illegal_encodings(sem,sco,private)
    # atom__RaNonRZ | sm_80 to sm_90
    __OLD_EXPR_TYPE_40 = ('Op_Not', 'Op_Defined').__hash__()
    __EXPR_TYPE_40 = ('Op_Not', 'Op_Defined').__hash__()
    @staticmethod
    def __expr_type_40(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        table = getattr(sass.sm.details.TABLES, str(expr[2]))

        args_all = [i.value() for i in expr[4:-1] if not isinstance(i, Op_Comma)]
        args_tt = [i for i in args_all if not isinstance(i, int)]
        tt_ind = [args_all.index(i) for i in args_tt]
        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(args_tt, alias_nt, domain_vals, keep_sass_bits=True)
        args = [i for i in args_all]
        for i,v in zip(tt_ind, expr_vals): args[i] = (v[0], v[1])
        for ind,i in enumerate(args):
            if not isinstance(i, tuple): args[ind] = ('_', [i])
        kk = [i[0] for i in args]
        pp = [dict([j for j in zip(kk,i) if j[0] != '_']) for i in itt.product(*[i[1] for i in args]) if not(i in table.keys())]

        res = SASS_Expr_Domain_Contract.group(pp)

        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # (((dc == `DC@noDC)) && ((toff == `TOFF@AOFFI))) -> ((((Rb) != `Register@RZ)))
    # tld4_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_41 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_41 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_41(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((dc == `DC@noDC)) && ((toff == `TOFF@AOFFI)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rb) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[2])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[2])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@S64) || (sz == `REDATOMSIZE@F64.RN))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
    # atom__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_42 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_42 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_42(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@S64) || (sz == `REDATOMSIZE@F64.RN)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 in reg_tt[:4])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 in reg_tt[:4])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    ((a1 == reg_tt[4]) or (a1 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not((a1 == reg_tt[4]) or (a1 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@S64) || (sz == `REDATOMSIZE@F64.RN))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
    # atom__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_43 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_43 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_43(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@S64) || (sz == `REDATOMSIZE@F64.RN)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 in reg_tt[:4])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 in reg_tt[:4])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (((int(a1) + int(a1 == reg_tt[4])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(((int(a1) + int(a1 == reg_tt[4])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((reuse_src_a == 1) || (reuse_src_b == 1) || (reuse_src_c == 1)) -> ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
    # dfma__RRR_RRR | sm_70 to sm_90
    __OLD_EXPR_TYPE_44 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_44 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_44(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((reuse_src_a == 1) || (reuse_src_b == 1) || (reuse_src_c == 1))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==int_tt[0]) or (a1==int_tt[1]) or (a2==int_tt[2]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==int_tt[0]) or (a1==int_tt[1]) or (a2==int_tt[2]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((usched_info == 17) || (usched_info == 18) || (usched_info == 19) || (usched_info == 20) || (usched_info == 21) || (usched_info == 22) || (usched_info == 23) || (usched_info == 24) || (usched_info == 25) || (usched_info == 26) || (usched_info == 27))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (a3 in int_tt[3:])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(a3 in int_tt[3:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((Ra@negate == 1))) -> (((Sb@negate == 0)))
    # iadd3_noimm__RCR_RCR | sm_70 to sm_90
    __OLD_EXPR_TYPE_45 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_AtNegate', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_AtNegate', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_45 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_AtNegate', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_AtNegate', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_45(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_AtNegate) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((Ra@negate == 1)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == int_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == int_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((Sb@negate == 0)))
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 == int_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((dc == `DC@noDC)) && ((toff == `TOFF@PTP))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
    # tld4_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_46 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_46 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_46(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((dc == `DC@noDC)) && ((toff == `TOFF@PTP)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2==reg_tt[2])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2==reg_tt[2])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((wmsk == 1) || (wmsk == 2) || (wmsk == 3) || (wmsk == 4) || (wmsk == 5) || (wmsk == 6) || (wmsk == 7) || (wmsk == 8) || (wmsk == 9) || (wmsk == 10) || (wmsk == 11) || (wmsk == 12) || (wmsk == 13) || (wmsk == 14) || (wmsk == 15))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_47 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_47 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_47(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        alias_vals = domain_vals[alias]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]
        
        domain_vals[alias] = set(v for v in alias_vals if v in int_tt)
        # SASS_Expr_Domain_Common.final_domain_check(domain_vals)
        return domain_vals

    # (((dc == `DC@DC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))) && ((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
    # tld4_scr_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_48 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_48 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_48(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((dc == `DC@DC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))) && ((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
        pp2 = list(itt.product(nn[3]['v'],nn[4]['v']))
        right_T_ll = [{nn[3]['n']:a3, nn[4]['n']:a4} for a3,a4 in pp2 if    ( ((int(a3) == reg_tt[3]) or (int(a3) <= param_tt[0] - int_tt[0])) and ((int(a4) == reg_tt[4]) or (int(a4) <= param_tt[1] - int_tt[1])) )]
        right_F_ll = [{nn[3]['n']:a3, nn[4]['n']:a4} for a3,a4 in pp2 if not( ((int(a3) == reg_tt[3]) or (int(a3) <= param_tt[0] - int_tt[0])) and ((int(a4) == reg_tt[4]) or (int(a4) <= param_tt[1] - int_tt[1])) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((dc == `DC@DC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0) && ((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
    # tld4_scr_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_49 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_49 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_49(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((dc == `DC@DC)) && ((toff == `TOFF@notoff)) && ((paramA == `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@ARRAY_2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0) && ((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
        pp2 = list(itt.product(nn[3]['v'],nn[4]['v']))
        right_T_ll = [{nn[3]['n']:a3, nn[4]['n']:a4} for a3,a4 in pp2 if    ( (((int(a3) + int(a3 == reg_tt[3])) % int_tt[0]) == int_tt[1]) and (((int(a4) + int(a4 == reg_tt[4])) % int_tt[2]) == int_tt[3]) )]
        right_F_ll = [{nn[3]['n']:a3, nn[4]['n']:a4} for a3,a4 in pp2 if not( (((int(a3) + int(a3 == reg_tt[3])) % int_tt[0]) == int_tt[1]) and (((int(a4) + int(a4 == reg_tt[4])) % int_tt[2]) == int_tt[3]) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx


    # (((Ra@invert == 1))) -> (((Sb@invert == 0)))
    # iadd3_x_noimm__RCR_RCR | sm_70 to sm_90
    __OLD_EXPR_TYPE_50 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_AtInvert', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_AtInvert', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_50 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_AtInvert', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_AtInvert', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_50(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_AtInvert) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((Ra@invert == 1)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == int_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == int_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((Sb@invert == 0)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 == int_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((op == `AtomsOp@INC) || (op == `AtomsOp@DEC))) -> (((sz == `REDATOMSIZE@U32) || (sz == `REDATOMSIZE@32)))
    # atom__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_51 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_51 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_51(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((op == `AtomsOp@INC) || (op == `AtomsOp@DEC)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    ((a0 == reg_tt[0]) or (a0 == reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not((a0 == reg_tt[0]) or (a0 == reg_tt[1]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((sz == `REDATOMSIZE@U32) || (sz == `REDATOMSIZE@32)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in reg_tt[2:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in reg_tt[2:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((op == `ATOMGOP_DIST@SAFEADD))) -> (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64)))
    # atomg__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_52 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_52 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_52(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((op == `ATOMGOP_DIST@SAFEADD)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    ((a0 == reg_tt[0]))]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not((a0 == reg_tt[0]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in reg_tt[1:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in reg_tt[1:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((f16rm == `F16RM@nof16rm)) && ((wmsk == 3) || (wmsk == 5) || (wmsk == 6) || (wmsk == 7) || (wmsk == 9) || (wmsk == 10) || (wmsk == 11) || (wmsk == 12) || (wmsk == 13) || (wmsk == 14) || (wmsk == 15))) -> (((((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - 2))))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_53 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_53 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_53(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        par_f16rm_tt = expr[3].value()
        reg_nof16rm_val = expr[5].value()
        par_wmsk_tt = expr[11].value()
        eq_int_x = set([i.value() for i in expr[13:-27][0::6]])

        par_Rd_tt = expr[-10].value()
        reg_RZ_val = expr[-15].value()
        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        sub_int = expr[-5].value()

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains([par_f16rm_tt, par_wmsk_tt, par_Rd_tt], alias_nt, domain_vals, keep_sass_bits=True)
        (par_f16rm_name,par_f16rm_val),(par_wmsk_name,par_wmsk_val),(par_Rd_name,par_Rd_val) = expr_vals

        rd_t_set = set(rd for rd in par_Rd_val if ((rd == reg_RZ_val or rd <= param_tt[0]-sub_int)))
        rd_t_vals = {par_Rd_name: rd_t_set}
        rd_f_set = set(rd for rd in par_Rd_val if not((rd == reg_RZ_val or rd <= param_tt[0]-sub_int)))
        rd_f_vals = {par_Rd_name: rd_f_set}

        ll_pos = list(itt.product(par_f16rm_val, par_wmsk_val))
        ll_t_vals_ll = [{par_f16rm_name:p, par_wmsk_name:w} for p,w in ll_pos if (p==reg_nof16rm_val and w in eq_int_x)]
        if ll_t_vals_ll: ll_t_vals = SASS_Expr_Domain_Contract.group(ll_t_vals_ll)
        else: ll_t_vals = []
        ll_f_vals_ll = [{par_f16rm_name:p, par_wmsk_name:w} for p,w in ll_pos if not(p==reg_nof16rm_val and w in eq_int_x)]
        if ll_f_vals_ll: ll_f_vals = SASS_Expr_Domain_Contract.group(ll_f_vals_ll)
        else: ll_f_vals = []

        impl = SASS_Expr_Domain_Utils.implication(ll_t_vals, ll_f_vals, [rd_t_vals], [rd_f_vals])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((f16rm == `F16RM@nof16rm)) && ((wmsk == 3) || (wmsk == 5) || (wmsk == 6) || (wmsk == 7) || (wmsk == 9) || (wmsk == 10) || (wmsk == 11) || (wmsk == 12) || (wmsk == 13) || (wmsk == 14) || (wmsk == 15))) -> (((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_54 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_54 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_54(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        par_f16rm_tt = expr[3].value()
        reg_nof16rm_val = expr[5].value()
        par_wmsk_tt = expr[11].value()
        eq_int_x = set([i.value() for i in expr[13:-27][0::6]])

        par_Rd_tt = expr[-13].value()
        reg_RZ_val = expr[-10].value()
        eq_int = expr[-3].value()
        mod_int = expr[-6].value()

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains([par_f16rm_tt, par_wmsk_tt, par_Rd_tt], alias_nt, domain_vals, keep_sass_bits=True)
        (par_f16rm_name,par_f16rm_val),(par_wmsk_name,par_wmsk_val),(par_Rd_name,par_Rd_val) = expr_vals

        # ((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0)
        rd_t_set = set(rd for rd in par_Rd_val if (((int(rd) + int(rd == reg_RZ_val)) % mod_int) == eq_int))
        rd_t_vals = {par_Rd_name: rd_t_set}
        rd_f_set = set(rd for rd in par_Rd_val if not(((int(rd) + int(rd == reg_RZ_val)) % mod_int) == eq_int))
        rd_f_vals = {par_Rd_name: rd_f_set}

        ll_pos = list(itt.product(par_f16rm_val, par_wmsk_val))
        ll_t_vals_ll = [{par_f16rm_name:p, par_wmsk_name:w} for p,w in ll_pos if (p==reg_nof16rm_val and w in eq_int_x)]
        if ll_t_vals_ll: ll_t_vals = SASS_Expr_Domain_Contract.group(ll_t_vals_ll)
        else: ll_t_vals = []
        ll_f_vals_ll = [{par_f16rm_name:p, par_wmsk_name:w} for p,w in ll_pos if not(p==reg_nof16rm_val and w in eq_int_x)]
        if ll_f_vals_ll: ll_f_vals = SASS_Expr_Domain_Contract.group(ll_f_vals_ll)
        else: ll_f_vals = []

        impl = SASS_Expr_Domain_Utils.implication(ll_t_vals, ll_f_vals, [rd_t_vals], [rd_f_vals])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((f16rm == `F16RM@nof16rm)) && ((wmsk == 15))) -> (((((Rd2) == `Register@RZ) || ((Rd2) <= %MAX_REG_COUNT - 2))))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_55 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_55 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_55(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        par_f16rm_tt = expr[3].value()
        reg_nof16rm_val = expr[5].value()
        par_wmsk_tt = expr[11].value()
        eq_int_x = [expr[13].value()]

        par_Rd_tt = expr[-10].value()
        reg_RZ_val = expr[-15].value()
        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        sub_int = expr[-5].value()

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains([par_f16rm_tt, par_wmsk_tt, par_Rd_tt], alias_nt, domain_vals, keep_sass_bits=True)
        (par_f16rm_name,par_f16rm_val),(par_wmsk_name,par_wmsk_val),(par_Rd_name,par_Rd_val) = expr_vals

        rd_t_set = set(rd for rd in par_Rd_val if ((rd == reg_RZ_val or rd <= param_tt[0]-sub_int)))
        rd_t_vals = {par_Rd_name: rd_t_set}
        rd_f_set = set(rd for rd in par_Rd_val if not((rd == reg_RZ_val or rd <= param_tt[0]-sub_int)))
        rd_f_vals = {par_Rd_name: rd_f_set}

        ll_pos = list(itt.product(par_f16rm_val, par_wmsk_val))
        ll_t_vals_ll = [{par_f16rm_name:p, par_wmsk_name:w} for p,w in ll_pos if (p==reg_nof16rm_val and w in eq_int_x)]
        if ll_t_vals_ll: ll_t_vals = SASS_Expr_Domain_Contract.group(ll_t_vals_ll)
        else: ll_t_vals = []
        ll_f_vals_ll = [{par_f16rm_name:p, par_wmsk_name:w} for p,w in ll_pos if not(p==reg_nof16rm_val and w in eq_int_x)]
        if ll_f_vals_ll: ll_f_vals = SASS_Expr_Domain_Contract.group(ll_f_vals_ll)
        else: ll_f_vals = []

        impl = SASS_Expr_Domain_Utils.implication(ll_t_vals, ll_f_vals, [rd_t_vals], [rd_f_vals])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((f16rm == `F16RM@nof16rm)) && ((wmsk == 15))) -> (((((Rd2) + ((Rd2) == `Register@RZ)) % 2) == 0))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_56 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_56 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_56(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        par_f16rm_tt = expr[3].value()
        reg_nof16rm_val = expr[5].value()
        par_wmsk_tt = expr[11].value()
        eq_int_x = [expr[13].value()]

        par_Rd_tt = expr[-13].value()
        reg_RZ_val = expr[-10].value()
        eq_int = expr[-3].value()
        mod_int = expr[-6].value()

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains([par_f16rm_tt, par_wmsk_tt, par_Rd_tt], alias_nt, domain_vals, keep_sass_bits=True)
        (par_f16rm_name,par_f16rm_val),(par_wmsk_name,par_wmsk_val),(par_Rd_name,par_Rd_val) = expr_vals

        # ((((Rd) + ((Rd) == `Register@RZ)) % 2) == 0)
        rd_t_set = set(rd for rd in par_Rd_val if (((int(rd) + int(rd == reg_RZ_val)) % mod_int) == eq_int))
        rd_t_vals = {par_Rd_name: rd_t_set}
        rd_f_set = set(rd for rd in par_Rd_val if not(((int(rd) + int(rd == reg_RZ_val)) % mod_int) == eq_int))
        rd_f_vals = {par_Rd_name: rd_f_set}

        ll_pos = list(itt.product(par_f16rm_val, par_wmsk_val))
        ll_t_vals_ll = [{par_f16rm_name:p, par_wmsk_name:w} for p,w in ll_pos if (p==reg_nof16rm_val and w in eq_int_x)]
        if ll_t_vals_ll: ll_t_vals = SASS_Expr_Domain_Contract.group(ll_t_vals_ll)
        else: ll_t_vals = []
        ll_f_vals_ll = [{par_f16rm_name:p, par_wmsk_name:w} for p,w in ll_pos if not(p==reg_nof16rm_val and w in eq_int_x)]
        if ll_f_vals_ll: ll_f_vals = SASS_Expr_Domain_Contract.group(ll_f_vals_ll)
        else: ll_f_vals = []

        impl = SASS_Expr_Domain_Utils.implication(ll_t_vals, ll_f_vals, [rd_t_vals], [rd_f_vals])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((op != `ATOMGOP_DIST@INVALID10) && (op != `ATOMGOP_DIST@INVALID11) && (op != `ATOMGOP_DIST@INVALID12) && (op != `ATOMGOP_DIST@INVALID13) && (op != `ATOMGOP_DIST@INVALID14) && (op != `ATOMGOP_DIST@INVALID15))
    # atomg__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_57 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_57 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_57(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((op != `ATOMGOP_DIST@INVALID10) && (op != `ATOMGOP_DIST@INVALID11) && (op != `ATOMGOP_DIST@INVALID12) && (op != `ATOMGOP_DIST@INVALID13) && (op != `ATOMGOP_DIST@INVALID14) && (op != `ATOMGOP_DIST@INVALID15))
        pp = nn[0]['v']
        res = [{nn[0]['n']: set(v for v in pp if v not in reg_tt)}]
        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # ((srcfmt == `Integer@U8) || (srcfmt == `Integer@S8)) -> (dstfmt != `Float@F64)
    # Const_I2F | sm_50 to sm_62
    __OLD_EXPR_TYPE_58 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace').__hash__()
    __EXPR_TYPE_58 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias_1', 'Op_NotEqual', 'Op_Register', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_58(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((srcfmt == `Integer@U8) || (srcfmt == `Integer@S8))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    ((a0 == reg_tt[0]) or (a0 == reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not((a0 == reg_tt[0]) or (a0 == reg_tt[1]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (dstfmt != `Float@F64)
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 != reg_tt[2])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 != reg_tt[2])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # !IsOdd(sbfmt)
    # Imm_VSHL | sm_50 to sm_62
    __OLD_EXPR_TYPE_59 = ('Op_Not', 'Op_IsOdd', 'Op_LBrace', 'Op_Alias', 'Op_RBrace').__hash__()
    __EXPR_TYPE_59 = ('Op_Not', 'Op_IsOdd', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_59(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        pp = nn[0]['v']
        res = [{nn[0]['n']: set(v for v in pp if not(v % 2 != 0))}]
        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # Test <= `Test@T
    # Const1_FCMP | sm_50 to sm_62
    __OLD_EXPR_TYPE_60 = ('Op_Alias', 'Op_SmallerOrEqual', 'Op_Register').__hash__()
    __EXPR_TYPE_60 = ('Op_Alias_0', 'Op_SmallerOrEqual', 'Op_Register').__hash__()
    @staticmethod
    def __expr_type_60(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        pp = nn[0]['v']
        res = [{nn[0]['n']: set(v for v in pp if (v <= reg_tt[0]))}]
        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # ((((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)) > 2) -> ((((Rd) + ((Rd) == 255)) & 0x3) == 0)
    # TEX | sm_50 to sm_62
    __OLD_EXPR_TYPE_61 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Greater', 'Op_Int', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    __EXPR_TYPE_61 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Greater', 'Op_Int', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_61(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)) > 2)
        pp = nn[0]['v']
        int_b0 = SASS_Bits.from_int(int_tt[0],bit_len=pp[0].bit_len,signed=0)
        int_b2 = SASS_Bits.from_int(int_tt[2],bit_len=pp[0].bit_len,signed=0)
        int_b4 = SASS_Bits.from_int(int_tt[4],bit_len=pp[0].bit_len,signed=0)
        int_b6 = SASS_Bits.from_int(int_tt[6],bit_len=pp[0].bit_len,signed=0)
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    ( ( int((a0 & int_b0) != int_tt[1]) + int((a0 & int_b2) != int_tt[3]) + int((a0 & int_b4) != int_tt[5]) + int((a0 & int_b6) != int_tt[7]) ) > int_tt[8] )]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not( ( int((a0 & int_b0) != int_tt[1]) + int((a0 & int_b2) != int_tt[3]) + int((a0 & int_b4) != int_tt[5]) + int((a0 & int_b6) != int_tt[7]) ) > int_tt[8] )]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rd) + ((Rd) == 255)) & 0x3) == 0)
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (((int(a1) + int(a1==int_tt[9])) & int_tt[10]) == int_tt[11])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(((int(a1) + int(a1==int_tt[9])) & int_tt[10]) == int_tt[11])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)) == 2) -> ((((Rd) + ((Rd) == 255)) & 0x1) == 0)
    # TEX | sm_50 to sm_62
    __OLD_EXPR_TYPE_62 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    __EXPR_TYPE_62 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_62(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)) == 2)
        pp = nn[0]['v']
        int_b0 = SASS_Bits.from_int(int_tt[0],bit_len=pp[0].bit_len,signed=0)
        int_b2 = SASS_Bits.from_int(int_tt[2],bit_len=pp[0].bit_len,signed=0)
        int_b4 = SASS_Bits.from_int(int_tt[4],bit_len=pp[0].bit_len,signed=0)
        int_b6 = SASS_Bits.from_int(int_tt[6],bit_len=pp[0].bit_len,signed=0)
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    ( ( int((a0 & int_b0) != int_tt[1]) + int((a0 & int_b2) != int_tt[3]) + int((a0 & int_b4) != int_tt[5]) + int((a0 & int_b6) != int_tt[7]) ) == int_tt[8] )]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not( ( int((a0 & int_b0) != int_tt[1]) + int((a0 & int_b2) != int_tt[3]) + int((a0 & int_b4) != int_tt[5]) + int((a0 & int_b6) != int_tt[7]) ) == int_tt[8] )]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rd) + ((Rd) == 255)) & 0x1) == 0)
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (((int(a1) + int(a1==int_tt[9])) & int_tt[10]) == int_tt[11])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(((int(a1) + int(a1==int_tt[9])) & int_tt[10]) == int_tt[11])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - (((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0))))
    # TEX | sm_50 to sm_62
    __OLD_EXPR_TYPE_63 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_63 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_BAnd', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_63(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((Rd) == `Register@RZ) || ((Rd) <= %MAX_REG_COUNT - (((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0))))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        bl = nn[0]['v'][0].bit_len
        int_b0 = SASS_Bits.from_int(int_tt[0],bit_len=bl,signed=0)
        int_b2 = SASS_Bits.from_int(int_tt[2],bit_len=bl,signed=0)
        int_b4 = SASS_Bits.from_int(int_tt[4],bit_len=bl,signed=0)
        int_b6 = SASS_Bits.from_int(int_tt[6],bit_len=bl,signed=0)
        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        res = [{nn[0]['n']:a0,nn[1]['n']:a1} for a0,a1 in pp 
               if ((a0==reg_tt[0]) or bool( int(a0 <= param_tt[0]) - int( ( int((a1 & int_b0) != int_tt[1]) + int((a1 & int_b2) != int_tt[3]) + int((a1 & int_b4) != int_tt[5]) + int(a1 & int_b6) ) != int_tt[7] ) ) )]

        res_g = SASS_Expr_Domain_Contract.group(res)
        xx = SASS_Expr_Domain_Common.__attach_results(res_g, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@ARRAY_CUBE))) -> (((aoffi == `AOFFI@noaoffi)))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_64 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_64 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_64(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        paramA = expr[3]
        paramA_tt = paramA.value()
        aoffi = expr[-6]
        aoffi_tt = aoffi.value()

        expr_val = SASS_Expr_Domain_Common.__get_alias_nt_domains([paramA_tt, aoffi_tt], alias_nt, domain_vals)
        paramA_name = expr_val[0][0]
        paramA_val = expr_val[0][1]
        aoffi_name = expr_val[1][0]
        aoffi_val = expr_val[1][1]

        reg1_val = expr[5].value()
        reg2_val = expr[11].value()
        reg3_val = expr[-4].value()
        # A -> B == ¬A v B

        paramA_bitlen = paramA_tt.min_bit_len()
        aoffi_bitlen = aoffi_tt.min_bit_len()
        pp = [{
            paramA_name:SASS_Bits.from_int(p, bit_len=paramA_bitlen, signed=0), 
            aoffi_name:SASS_Bits.from_int(a, bit_len=aoffi_bitlen, signed=0)
            } for p,a in itt.product(paramA_val, aoffi_val) if (not(p==reg1_val or p==reg2_val) or a==reg3_val)
        ]
        res = SASS_Expr_Domain_Contract.group(pp)

        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # # (cctltop == `CCTLTOp@IVTH)
    # # CCTLT_IDX | sm_50 to sm_62
    # __OLD_EXPR_TYPE_65 = ('Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace').__hash__()
    # __EXPR_TYPE_65 = ('Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace').__hash__()
    # @staticmethod
    # def __expr_type_65(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
    #     alias_tt = []
    #     for i in expr:
    #         if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
    #     reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
    #     int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

    #     expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
    #     nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

    #     pp = nn[0]['v']
    #     res = [{nn[0]['n']: set(v for v in pp if (v == reg_tt[0]))}]
    #     xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
    #     return xx

    # ((atom == `AtomOp@INC) -> ((size == `SQInteger@U32)))
    # ATOM | sm_50 to sm_62
    __OLD_EXPR_TYPE_66 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_66 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_66(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((atom == `AtomOp@INC)
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((size == `SQInteger@U32)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 == reg_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 == reg_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((op == `AtomsOp@ADD))) -> (((sz == `REDATOMSIZE@U32) || (sz == `REDATOMSIZE@32) || (sz == `REDATOMSIZE@S32) || (sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@F32.FTZ.RN) || (sz == `REDATOMSIZE@F16x2.RN) || (sz == `REDATOMSIZE@F64.RN)))
    # atom__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_67 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_67 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_67(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((op == `AtomsOp@ADD)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((sz == `REDATOMSIZE@U32) || (sz == `REDATOMSIZE@32) || (sz == `REDATOMSIZE@S32) || (sz == `REDATOMSIZE@U64) || (sz == `REDATOMSIZE@64) || (sz == `REDATOMSIZE@F32.FTZ.RN) || (sz == `REDATOMSIZE@F16x2.RN) || (sz == `REDATOMSIZE@F64.RN)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in reg_tt[1:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in reg_tt[1:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # E -> IsEven(((Ra) + ((Ra) == `Register@RZ)))
    # ATOM | sm_50 to sm_62
    __OLD_EXPR_TYPE_68 = ('Op_Alias', 'Op_Implication', 'Op_IsEven', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_68 = ('Op_Alias_0', 'Op_Implication', 'Op_IsEven', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_68(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # E
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp]
        left_F_ll = []

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # IsEven(((Ra) + ((Ra) == `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (((int(a1) + int(a1 == reg_tt[0])) % 2) == 0)]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(((int(a1) + int(a1 == reg_tt[0])) % 2) == 0)]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # E -> (((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))
    # ATOM | sm_50 to sm_62
    __OLD_EXPR_TYPE_69 = ('Op_Alias', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_69 = ('Op_Alias_0', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_69(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # E
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp]
        left_F_ll = []

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    ((a1 == reg_tt[0]) or (a1 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not((a1 == reg_tt[0]) or (a1 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((size == `CASInteger@64) -> ((Rb == `Register@RZ) || (Rb % 4 == 0)))
    # ATOMS_CAS | sm_50 to sm_62
    __OLD_EXPR_TYPE_70 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Mod', 'Op_Int', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_70 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Mod', 'Op_Int', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_70(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((size == `CASInteger@64)
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((Rb == `Register@RZ) || (Rb % 4 == 0)))
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    ( (int(a1) == reg_tt[1]) or ((int(a1) % int_tt[0]) == int_tt[1]) )]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not( (int(a1) == reg_tt[1]) or ((int(a1) % int_tt[0]) == int_tt[1]) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((size == `CASInteger@32) -> ((Rb % 2 == 0) && (Rb != `Register@RZ) && ((Rc == Rb + 1) || (Rc == `Register@RZ))))
    # ATOMS_CAS | sm_50 to sm_62
    __OLD_EXPR_TYPE_71 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Mod', 'Op_Int', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Alias', 'Op_Plus', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_71 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Mod', 'Op_Int', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_1', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Alias_1', 'Op_Plus', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_71(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((size == `CASInteger@32)
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((Rb % 2 == 0) && (Rb != `Register@RZ) && ((Rc == Rb + 1) || (Rc == `Register@RZ))))
        pp2 = list(itt.product(nn[1]['v'],nn[2]['v']))
        right_T_ll = [{nn[1]['n']:a1, nn[2]['n']:a2} for a1,a2 in pp2 if    ( ((int(a1) % int_tt[0]) == int_tt[1]) and (int(a1) != reg_tt[1]) and ((int(a2) == int(a1) + int_tt[2]) or (int(a2) == reg_tt[2])) )]
        right_F_ll = [{nn[1]['n']:a1, nn[2]['n']:a2} for a1,a2 in pp2 if not( ((int(a1) % int_tt[0]) == int_tt[1]) and (int(a1) != reg_tt[1]) and ((int(a2) == int(a1) + int_tt[2]) or (int(a2) == reg_tt[2])) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((ftz == `FTZ@FTZ) -> (fmts == 10))
    # Const_F2F_1 | sm_50 to sm_62
    __OLD_EXPR_TYPE_72 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_72 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_72(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((ftz == `FTZ@FTZ)
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (fmts == 10))
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 == int_tt[0])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 == int_tt[0])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (p == `POnly@P) -> (Rb == `Register@RZ)
    # ALD | sm_50 to sm_62
    __OLD_EXPR_TYPE_73 = ('Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace').__hash__()
    __EXPR_TYPE_73 = ('Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_73(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (p == `POnly@P)
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (Rb == `Register@RZ)
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 == reg_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 == reg_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC))) -> ((((Rb) != `Register@RZ)))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_74 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_74 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_74(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2] or a2==reg_tt[3] or a2==reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2] or a2==reg_tt[3] or a2==reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rb) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (a3 != reg_tt[5])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(a3 != reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((sco != `MEMBAR_SCO@INVALID4) && (sco != `MEMBAR_SCO@INVALID6) && (sco != `MEMBAR_SCO@INVALID7))
    # membar_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_75 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_75 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_75(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        pp = nn[0]['v']
        res = [{nn[0]['n']: set(v for v in pp if (v not in reg_tt))}]
        xx = SASS_Expr_Domain_Common.__attach_results(res, domain_vals)
        return xx

    # ((atom == `AtomOp@AND) -> ((size == `SQInteger@U32) || (size == `SQInteger@S32) || (size == `SQInteger@U64)))
    # ATOM | sm_50 to sm_62
    __OLD_EXPR_TYPE_76 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_76 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_76(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # ((atom == `AtomOp@INC)
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((size == `SQInteger@U32) || (size == `SQInteger@S32) || (size == `SQInteger@U64)))
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in reg_tt[1:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in reg_tt[1:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@AOFFI)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_77 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_77 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_77(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@AOFFI)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2] or a2==reg_tt[3] or a2==reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2] or a2==reg_tt[3] or a2==reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    ((a3 == reg_tt[5]) or (a3 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not((a3 == reg_tt[5]) or (a3 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@AOFFI)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_78 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_78 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_78(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@AOFFI)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2] or a2==reg_tt[3] or a2==reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and (a2==reg_tt[2] or a2==reg_tt[3] or a2==reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (((int(a3) + int(a3 == reg_tt[5])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(((int(a3) + int(a3 == reg_tt[5])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((paramA != `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@INVALID0) && (paramA != `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@INVALID2) && (paramA != `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@INVALID4) && (paramA != `PARAMA_ARRAY_2D_CUBE_ARRAY_CUBE_2D@INVALID6))
    # tld4_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_79 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_79 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_79(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        vals = domain_vals[alias]
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]

        domain_vals[alias] = set([v for v in vals if not v in reg_tt])
        return domain_vals

    # (((ofmt == `OFMT@F16_V2)))
    # hmul2__RC | sm_80 to sm_90
    __OLD_EXPR_TYPE_80 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_80 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_80(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        return SASS_Expr_Domain_Common.__expr_type_3(sass, expr[2:-2], alias_nt, domain_vals)

    # (((aoffi == `AOFFI@noaoffi)) && ((lc == `LC@nolc)) && ((paramA == `PARAMA_ARRAY_2D_ARRAY_1D_2D_1D@2D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
    # txd_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_81 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_81 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_81(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((lc == `LC@nolc)) && ((paramA == `PARAMA_ARRAY_2D_ARRAY_1D_2D_1D@2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and a2==reg_tt[2])] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and a2==reg_tt[2])] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
        pp2 = nn[3]['v']
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    ((a3==reg_tt[3]) or (a3 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not((a3==reg_tt[3]) or (a3 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((lc == `LC@nolc)) && ((paramA == `PARAMA_ARRAY_2D_ARRAY_1D_2D_1D@2D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
    # txd_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_82 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_82 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_82(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((lc == `LC@nolc)) && ((paramA == `PARAMA_ARRAY_2D_ARRAY_1D_2D_1D@2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1]) and a2==reg_tt[2])] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1]) and a2==reg_tt[2])] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
        pp2 = nn[3]['v']
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (((int(a3) + int(a3 == reg_tt[3])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(((int(a3) + int(a3 == reg_tt[3])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (%SHADER_TYPE == $ST_UNKNOWN) || (%SHADER_TYPE != $ST_CS)
    # AL2P | sm_50 to sm_62
    __OLD_EXPR_TYPE_83 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_NotEqual', 'Op_Constant', 'Op_RBrace').__hash__()
    __EXPR_TYPE_83 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_NotEqual', 'Op_Constant', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_83(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        # :-D
        return domain_vals

    # (((sz == `ATOMCASSZ@32) || (sz == `ATOMCASSZ@U32) || (sz == `ATOMCASSZ@S32))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
    # suatom_cas_imm_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_84 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_84 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_84(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `ATOMCASSZ@32) || (sz == `ATOMCASSZ@U32) || (sz == `ATOMCASSZ@S32)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 in reg_tt[:3])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 in reg_tt[:3])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 2))))
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    ( (int(a1) == reg_tt[3]) or (int(a1) <= param_tt[0] - int_tt[0]) )]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not( (int(a1) == reg_tt[3]) or (int(a1) <= param_tt[0] - int_tt[0]) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((sz == `ATOMCASSZ@32) || (sz == `ATOMCASSZ@U32) || (sz == `ATOMCASSZ@S32))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
    # suatom_cas_imm_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_85 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_85 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_85(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sz == `ATOMCASSZ@32) || (sz == `ATOMCASSZ@U32) || (sz == `ATOMCASSZ@S32)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 in reg_tt[:3])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 in reg_tt[:3])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) + ((Rb) == `Register@RZ)) % 2) == 0))
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    ( (((int(a1) + int(a1 == reg_tt[3])) % int_tt[0]) == int_tt[1]) )]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not( (((int(a1) + int(a1 == reg_tt[3])) % int_tt[0]) == int_tt[1]) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((op != `AtomsOp@INVALID9) && (op != `AtomsOp@INVALID10) && (op != `AtomsOp@INVALID11) && (op != `AtomsOp@INVALID12) && (op != `AtomsOp@INVALID13) && (op != `AtomsOp@INVALID14) && (op != `AtomsOp@INVALID15))
    # atom__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_86 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_86 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_86(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias = alias_nt[0]
        vals = domain_vals[alias]
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]

        domain_vals[alias] = set([v for v in vals if not v in reg_tt])

        return domain_vals

    # (DC == `DC@DC) -> (ParamA != `ParamA@_3D)
    # TEX | sm_50 to sm_62
    __OLD_EXPR_TYPE_87 = ('Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace').__hash__()
    __EXPR_TYPE_87 = ('Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_Alias_1', 'Op_NotEqual', 'Op_Register', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_87(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (DC == `DC@DC)
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (ParamA != `ParamA@_3D)
        pp2 = nn[1]['v']
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 != reg_tt[1])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 != reg_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (%SHADER_TYPE == $ST_UNKNOWN) || ((%SHADER_TYPE == $ST_TRAP) || (%SHADER_TYPE == $ST_VSA) || (%SHADER_TYPE == $ST_VSB) || (%SHADER_TYPE == $ST_GS) || (%SHADER_TYPE == $ST_TS) || (%SHADER_TYPE == $ST_TI))
    # al2p__RaNonRZ | sm_70 to sm_90
    __OLD_EXPR_TYPE_88 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_88 = ('Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Parameter', 'Op_Equal', 'Op_Constant', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_88(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        # Yessssss!! :-D
        return domain_vals

    # (((srcfmt == `SRCFMT@E8M10) || (srcfmt == `SRCFMT@TF32)) && ((size == `SIZE_1688_16816_16832@16816))) -> (((id == 0) || (id == 1)))
    # hmma_sparse_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_89 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_89 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_89(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((srcfmt == `SRCFMT@E8M10) || (srcfmt == `SRCFMT@TF32)) && ((size == `SIZE_1688_16816_16832@16816)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and a1==reg_tt[2])]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and a1==reg_tt[2])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((id == 0) || (id == 1)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2==int_tt[0]) or (a2==int_tt[1]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2==int_tt[0]) or (a2==int_tt[1]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx
    
    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_91 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_91 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_91(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and a1==reg_tt[2])]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and a1==reg_tt[2])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2 == reg_tt[3]) or (a2 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2 == reg_tt[3]) or (a2 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_92 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_92 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_92(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and a1==reg_tt[2])]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and a1==reg_tt[2])]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2 == reg_tt[3])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2 == reg_tt[3])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_93 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_93 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_93(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and a1==reg_tt[4])]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and a1==reg_tt[4])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2 == reg_tt[5]) or (a2 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2 == reg_tt[5]) or (a2 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
    # tex_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_94 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_94 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_94(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and a1==reg_tt[4])]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and a1==reg_tt[4])]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2 == reg_tt[5])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2 == reg_tt[5])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@1D))) -> ((((Ra) != `Register@RZ)) && (((Rb) == `Register@RZ)))
    # tex_scr_ | sm_70 to sm_90
    __OLD_EXPR_TYPE_95 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_95 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_95(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((lodlc == `LODLC@nolodlc)) && ((paramA == `TEXPARAMA@1D)))
        pp = list(itt.product(nn[0]['v'], nn[1]['v'], nn[2]['v'], nn[3]['v']))
        left_T_ll = [{nn[0]['n']:a0,nn[1]['n']:a1,nn[2]['n']:a2,nn[3]['n']:a3} for a0,a1,a2,a3 in pp if (a0==reg_tt[0] and a1==reg_tt[1] and a2==reg_tt[2] and a3==reg_tt[3])]
        left_F_ll = [{nn[0]['n']:a0,nn[1]['n']:a1,nn[2]['n']:a2,nn[3]['n']:a3} for a0,a1,a2,a3 in pp if not(a0==reg_tt[0] and a1==reg_tt[1] and a2==reg_tt[2] and a3==reg_tt[3])]

        # ((((Ra) != `Register@RZ)) && (((Rb) == `Register@RZ)))
        pp2 = list(itt.product(
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[4]['v']),
            SASS_Expr_Domain_Common.__reduce_reg_dom(nn[5]['v'])
        ))
        right_T_ll = [{nn[4]['n']:a4,nn[5]['n']:a5} for a4,a5 in pp2 if (a4 != reg_tt[4] and a5 == reg_tt[5])]
        right_F_ll = [{nn[4]['n']:a4,nn[5]['n']:a5} for a4,a5 in pp2 if not(a4 != reg_tt[4] and a5 == reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@1D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_96 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_96 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_96(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@1D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1] or a1==reg_tt[2] or a1==reg_tt[3] or a1 == reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1] or a1==reg_tt[2] or a1==reg_tt[3] or a1 == reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[5])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_70 to sm_72
    __OLD_EXPR_TYPE_97 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_97 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_97(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@1D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and a1==reg_tt[2])]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and a1==reg_tt[2])]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[3])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[3])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@2D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_98 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_98 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_98(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@2D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1] or a1==reg_tt[2] or a1==reg_tt[3] or a1 == reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1] or a1==reg_tt[2] or a1==reg_tt[3] or a1 == reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2 == reg_tt[5]) or (a2 == param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2 == reg_tt[5]) or (a2 == param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@2D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_99 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_99 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_99(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@2D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0]) and (a1==reg_tt[1] or a1==reg_tt[2] or a1==reg_tt[3] or a1 == reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0]) and (a1==reg_tt[1] or a1==reg_tt[2] or a1==reg_tt[3] or a1 == reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2 == reg_tt[5])) % int_tt[0]) == reg_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2 == reg_tt[5])) % int_tt[0]) == reg_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 3))))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_100 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_100 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_100(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4] or a1 == reg_tt[5]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4] or a1 == reg_tt[5]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 3))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2 == reg_tt[6]) or (a2 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2 == reg_tt[6]) or (a2 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_101 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_101 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_101(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4] or a1 == reg_tt[5]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4] or a1 == reg_tt[5]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2 == reg_tt[6])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2 == reg_tt[6])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_102 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_102 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_102(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4] or a1 == reg_tt[5]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4] or a1 == reg_tt[5]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[6])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[6])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_103 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_103 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_103(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2 == reg_tt[5]) or (a2 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2 == reg_tt[5]) or (a2 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_104 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_104 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_104(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2 == reg_tt[5])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2 == reg_tt[5])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_80 to sm_90
    __OLD_EXPR_TYPE_105 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_105 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_105(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)) && ((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4]))] 
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3] or a1==reg_tt[4]))] 

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[5])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_70 to sm_75
    __OLD_EXPR_TYPE_106 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_106 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_106(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and a1==reg_tt[4])]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and a1==reg_tt[4])]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[5])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 3))))
    # tex_ | sm_70 to sm_75
    __OLD_EXPR_TYPE_107 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_107 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_107(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and (a1==reg_tt[4] or a1==reg_tt[5]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and (a1==reg_tt[4] or a1==reg_tt[5]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 3))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((a2 == reg_tt[6]) or (a2 <= param_tt[0] - int_tt[0])))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((a2 == reg_tt[6]) or (a2 <= param_tt[0] - int_tt[0])))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
    # tex_ | sm_70 to sm_75
    __OLD_EXPR_TYPE_108 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_108 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_108(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and (a1==reg_tt[4] or a1==reg_tt[5]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and (a1==reg_tt[4] or a1==reg_tt[5]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2 == reg_tt[6])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2 == reg_tt[6])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_70 to sm_75
    __OLD_EXPR_TYPE_109 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_109 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_109(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LZ)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and (a1==reg_tt[4] or a1==reg_tt[5]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1] or a0==reg_tt[2] or a0==reg_tt[3]) and (a1==reg_tt[4] or a1==reg_tt[5]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[6])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[6])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@1D))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_75 to sm_75
    __OLD_EXPR_TYPE_110 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_110 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_110(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@1D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0 in reg_tt[:3]) and (a1 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0 in reg_tt[:3]) and (a1 == reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[4])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[4])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
    # tex_ | sm_70 to sm_72
    __OLD_EXPR_TYPE_111 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_111 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_111(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2 == reg_tt[4]) or (a2 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2 == reg_tt[4]) or (a2 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
    # tex_ | sm_70 to sm_72
    __OLD_EXPR_TYPE_112 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_112 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_112(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2 == reg_tt[4])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2 == reg_tt[4])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_70 to sm_72
    __OLD_EXPR_TYPE_113 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_113 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_113(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0==reg_tt[0] or a0==reg_tt[1]) and (a1==reg_tt[2] or a1==reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[4])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[4])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
    # tex_ | sm_75 to sm_75
    __OLD_EXPR_TYPE_114 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_114 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_114(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0 in reg_tt[:3]) and (a1 in reg_tt[3:5]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0 in reg_tt[:3]) and (a1 in reg_tt[3:5]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 4))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    ((a2==reg_tt[5]) or (a2 <= param_tt[0] - int_tt[0]))]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not((a2==reg_tt[5]) or (a2 <= param_tt[0] - int_tt[0]))]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
    # tex_ | sm_75 to sm_75
    __OLD_EXPR_TYPE_115 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_115 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_115(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0 in reg_tt[:3]) and (a1 in reg_tt[3:5]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0 in reg_tt[:3]) and (a1 in reg_tt[3:5]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 4) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (((int(a2) + int(a2 == reg_tt[5])) % int_tt[0]) == int_tt[1])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(((int(a2) + int(a2 == reg_tt[5])) % int_tt[0]) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D))) -> ((((Ra) != `Register@RZ)))
    # tex_ | sm_75 to sm_75
    __OLD_EXPR_TYPE_116 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    __EXPR_TYPE_116 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_116(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LC.FDV)) && ((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@3D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0 in reg_tt[:3]) and (a1 in reg_tt[3:5]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0 in reg_tt[:3]) and (a1 in reg_tt[3:5]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 != reg_tt[5])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 != reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx
    
    # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex))) -> (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
    # tex_scr_b_noConst_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_117 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_117(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v'],nn[4]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) == `Register@RZ) || ((Ra) <= %MAX_REG_COUNT - 2))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[5]['v'])
        right_T_ll = [{nn[5]['n']:a5} for a5 in pp2 if    ( ((int(a5) == reg_tt[5]) or (int(a5) <= (param_tt[0] - int_tt[0]) )) )]
        right_F_ll = [{nn[5]['n']:a5} for a5 in pp2 if not( ((int(a5) == reg_tt[5]) or (int(a5) <= (param_tt[0] - int_tt[0]) )) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex))) -> (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
    # tex_scr_b_noConst_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_118 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_118(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v'],nn[4]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Ra) + ((Ra) == `Register@RZ)) % 2) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[5]['v'])
        right_T_ll = [{nn[5]['n']:a5} for a5 in pp2 if    (((int(a5) + int(a5 == reg_tt[5])) % int_tt[0] ) == int_tt[1])]
        right_F_ll = [{nn[5]['n']:a5} for a5 in pp2 if not(((int(a5) + int(a5 == reg_tt[5])) % int_tt[0] ) == int_tt[1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex))) -> (((dc == `DC@noDC)))
    # tex_scr_b_noConst_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_119 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_119(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v'],nn[4]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((dc == `DC@noDC)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 == reg_tt[5])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 == reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex))) -> ((((Rb) != `Register@RZ)))
    # tex_scr_urc_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_120 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_120(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v'],nn[4]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rb) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[5]['v'])
        right_T_ll = [{nn[5]['n']:a5} for a5 in pp2 if    (a5 != reg_tt[5])]
        right_F_ll = [{nn[5]['n']:a5} for a5 in pp2 if not(a5 != reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex))) -> (((dc == `DC@noDC)))
    # tex_scr_b_noConst_ | sm_100 to sm_100
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_121 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_121(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((dc == `DC@noDC)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (a3 == reg_tt[3])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(a3 == reg_tt[3])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex))) -> ((((Ra) != `Register@RZ)))
    # tex_scr_b_noConst_ | sm_100 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_122 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_122(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_2D)) && ((lodlc == `LODLC_tex@nolodlc_tex)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[4]['v'])
        right_T_ll = [{nn[4]['n']:a4} for a4 in pp2 if    (a4 != reg_tt[4])]
        right_F_ll = [{nn[4]['n']:a4} for a4 in pp2 if not(a4 != reg_tt[4])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((ms == `MS@MS)) && ((paramA == `PARAMA_TLD@ARRAY_2D)) && ((lodlc == `LODLC_tld@LZ))) -> (((ms == `MS@noMS) || (ms == `MS@UMS)))
    # tld_scr_b_noConst_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_123 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_123(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((uai == `UAI@nouai)) && ((aoffi == `AOFFI@noaoffi)) && ((ms == `MS@MS)) && ((paramA == `PARAMA_TLD@ARRAY_2D)) && ((lodlc == `LODLC_tld@LZ)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v'],nn[4]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((ms == `MS@noMS) || (ms == `MS@UMS)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 in reg_tt[5:])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 in reg_tt[5:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((paramA == `TEXPARAMA@ARRAY_2D))) -> (((lodlc == `LODLC_tex@LZ) || (lodlc == `LODLC_tex@LB) || (lodlc == `LODLC_tex@LL) || (lodlc == `LODLC_tex@LC) || (lodlc == `LODLC_tex@LB.LC)))
    # tex_scr_b_noConst_ | sm_100 to sm_100
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_124 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_124(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((paramA == `TEXPARAMA@ARRAY_2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((lodlc == `LODLC_tex@LZ) || (lodlc == `LODLC_tex@LB) || (lodlc == `LODLC_tex@LL) || (lodlc == `LODLC_tex@LC) || (lodlc == `LODLC_tex@LB.LC)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (a3 in reg_tt[3:])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(a3 in reg_tt[3:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((lodlc == `LODLC_tex@nolodlc_tex))) -> (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@ARRAY_1D) || (paramA == `TEXPARAMA@ARRAY_CUBE) || (paramA == `TEXPARAMA@2D) || (paramA == `TEXPARAMA@1D) || (paramA == `TEXPARAMA@3D)))
    # tex_scr_b_noConst_ | sm_100 to sm_100
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_125 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_125(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@DC)) && ((lodlc == `LODLC_tex@nolodlc_tex)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((paramA == `TEXPARAMA@CUBE) || (paramA == `TEXPARAMA@ARRAY_1D) || (paramA == `TEXPARAMA@ARRAY_CUBE) || (paramA == `TEXPARAMA@2D) || (paramA == `TEXPARAMA@1D) || (paramA == `TEXPARAMA@3D)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (a3 in reg_tt[3:])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(a3 in reg_tt[3:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi)) && ((lc == `LC@nolc)) && ((paramA == `PARAMA_ARRAY_2D_ARRAY_1D_2D_1D@2D))) -> ((((Ra) != `Register@RZ)))
    # txd_ | sm_70 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_126 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_126(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((aoffi == `AOFFI@noaoffi)) && ((lc == `LC@nolc)) && ((paramA == `PARAMA_ARRAY_2D_ARRAY_1D_2D_1D@2D)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (a3 != reg_tt[3])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(a3 != reg_tt[3])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # ((sz != `ATOMCASSZ@INVALID3) && (sz != `ATOMCASSZ@INVALID4) && (sz != `ATOMCASSZ@INVALID5) && (sz != `ATOMCASSZ@INVALID6) && (sz != `ATOMCASSZ@INVALID7))
    # atom_cas__RaNonRZ_CAS | sm_70 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_127 = ('Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Alias_0', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_127(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # ((sz != `ATOMCASSZ@INVALID3) && (sz != `ATOMCASSZ@INVALID4) && (sz != `ATOMCASSZ@INVALID5) && (sz != `ATOMCASSZ@INVALID6) && (sz != `ATOMCASSZ@INVALID7))
        domain_vals[nn[0]['n']] = set(a0 for a0 in nn[0]['v'] if (a0 not in reg_tt))
        return domain_vals

    # (((elsize == `ELSIZE@U8))) -> (((idxsize == `IDXSIZE_scatter@U4_H0) || (idxsize == `IDXSIZE_scatter@U4_H1) || (idxsize == `IDXSIZE_scatter@U8)))
    # scatter_ | sm_80 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_128 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_128(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((elsize == `ELSIZE@U8)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 in reg_tt[:1])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 in reg_tt[:1])]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((idxsize == `IDXSIZE_scatter@U4_H0) || (idxsize == `IDXSIZE_scatter@U4_H1) || (idxsize == `IDXSIZE_scatter@U8)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in reg_tt[1:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in reg_tt[1:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((lodlc == `LODLC@LC.FDV)) && ((mode == `MODE_FOOTPRINT@TEX))) -> (((ndv == `NDV@nondv)))
    # footprint_ | sm_75 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_129 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_129(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((lodlc == `LODLC@LC.FDV)) && ((mode == `MODE_FOOTPRINT@TEX)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1} for a0,a1 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((ndv == `NDV@nondv)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 == reg_tt[2])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 == reg_tt[2])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((op == `AtomsOp@EXCH))) -> (((sz == `ATOMSSIZE@U32) || (sz == `ATOMSSIZE@32) || (sz == `ATOMSSIZE@S32) || (sz == `ATOMSSIZE@U64) || (sz == `ATOMSSIZE@64)))
    # atoms__RaNonRZ | sm_70 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_130 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_130(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((op == `AtomsOp@EXCH))) 
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 in reg_tt[:1])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 in reg_tt[:1])]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((sz == `ATOMSSIZE@U32) || (sz == `ATOMSSIZE@32) || (sz == `ATOMSSIZE@S32) || (sz == `ATOMSSIZE@U64) || (sz == `ATOMSSIZE@64)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in reg_tt[1:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in reg_tt[1:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((mode == `MODE_FOOTPRINT@TXD))) -> (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LC) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LZ)))
    # footprint_ | sm_75 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_131 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_131(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((mode == `MODE_FOOTPRINT@TXD)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 in reg_tt[:1])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 in reg_tt[:1])]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((lodlc == `LODLC@nolodlc) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LC) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LB.LC) || (lodlc == `LODLC@LZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in reg_tt[1:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in reg_tt[1:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((op == `ATOMICFPOPS@MIN) || (op == `ATOMICFPOPS@MAX))) -> (((sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@F16x2.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@F16x4.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@F16x8.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@BF16x2.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@BF16x4.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@BF16x8.RN)))
    # atom_fp__RaNonRZ | sm_90 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_132 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_132(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((op == `ATOMICFPOPS@MIN) || (op == `ATOMICFPOPS@MAX)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 in reg_tt[:2])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 in reg_tt[:2])]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@F16x2.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@F16x4.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@F16x8.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@BF16x2.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@BF16x4.RN) || (sz == `SZ_F16x2RN_F16x4RN_F16x8RN_BF16x2RN_BF16x4RN_BF16x8RN_F32FTZRN_F32x2FTZRN_F32x4FTZRN_F32RN_F32x2RN_F32x4RN_F64RN@BF16x8.RN)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 in reg_tt[2:])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 in reg_tt[2:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((iswzB == `ISWZB@H1_H1) || (iswzB == `ISWZB@H1_H0) || (iswzB == `ISWZB@H0_NH1) || (iswzB == `ISWZB@H0_H0)))
    # hfma2__RCR | sm_86 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_133 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_133(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((iswzB == `ISWZB@H1_H1) || (iswzB == `ISWZB@H1_H0) || (iswzB == `ISWZB@H0_NH1) || (iswzB == `ISWZB@H0_H0)))
        domain_vals[nn[0]['n']] = set(a0 for a0 in nn[0]['v'] if (a0 in reg_tt))
        return domain_vals

    # (((uai == `UAI@nouai)) && ((dc == `DC@DC)) && ((paramA == `PARAMA_TLD4@ARRAY_2D)) && ((toff == `TOFF@notoff))) -> (((dc == `DC@noDC)))
    # tld4_scr_b_noConst_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_134 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_134(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((uai == `UAI@nouai)) && ((dc == `DC@DC)) && ((paramA == `PARAMA_TLD4@ARRAY_2D)) && ((toff == `TOFF@notoff)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3} for a0,a1,a2,a3 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((dc == `DC@noDC)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[1]['v'])
        right_T_ll = [{nn[1]['n']:a1} for a1 in pp2 if    (a1 == reg_tt[4])]
        right_F_ll = [{nn[1]['n']:a1} for a1 in pp2 if not(a1 == reg_tt[4])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((op == `ATOMGOP@SAFEADD))) -> (((DEFINED TABLES_mem_0(sem,sco,private)) && ((TABLES_mem_0(sem,sco,private) != 10) && (TABLES_mem_0(sem,sco,private) != 12))))
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Defined', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    # atomg__RaNonRZ
    __EXPR_TYPE_135 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Defined', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_135(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]
        tables_tt = [i.table for i in expr if isinstance(i, Op_Table)]
        # make sure we use the same table in the entire expression
        if not len(set([str(i) for i in expr if isinstance(i, Op_Table)])) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((op == `ATOMGOP@SAFEADD)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        t_args = list([(int(x), int(y), int(z)) for x,y,z in itt.product(nn[1]['v'],nn[2]['v'],nn[3]['v'])])
        # (((DEFINED TABLES_mem_0(sem,sco,private)) && 
        defined_args = [arg for arg in t_args if       arg in tables_tt[0]]
        n_defined_args = [arg for arg in t_args if not(arg in tables_tt[0])]

        # ((TABLES_mem_0(sem,sco,private) != 10) && (TABLES_mem_0(sem,sco,private) != 12))))
        t_args2 = [arg for arg in defined_args if      (tables_tt[0][arg] not in int_tt)]
        n_t_args2 = [arg for arg in defined_args if not(tables_tt[0][arg] not in int_tt)] + n_defined_args

        n_sem = nn[1]['n']
        n_sco = nn[2]['n']
        n_private = nn[3]['n']

        b_sem = nn[1]['v'][0]
        b_sem_sign = 1 if b_sem.signed else 0
        b_sco = nn[2]['v'][0]
        b_sco_sign = 1 if b_sco.signed else 0
        b_private = nn[3]['v'][0]
        b_private_sign = 1 if b_private.signed else 0

        right_T_ll = [{
            n_sem:SASS_Bits.from_int(a1, bit_len=b_sem.bit_len, signed=b_sem_sign), 
            n_sco:SASS_Bits.from_int(a2, bit_len=b_sco.bit_len, signed=b_sco_sign), 
            n_private:SASS_Bits.from_int(a3, bit_len=b_private.bit_len, signed=b_private_sign)
        } for a1,a2,a3 in t_args2]

        right_F_ll = [{
            n_sem:SASS_Bits.from_int(a1, bit_len=b_sem.bit_len, signed=b_sem_sign), 
            n_sco:SASS_Bits.from_int(a2, bit_len=b_sco.bit_len, signed=b_sco_sign), 
            n_private:SASS_Bits.from_int(a3, bit_len=b_private.bit_len, signed=b_private_sign)
        } for a1,a2,a3 in n_t_args2]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx
    
    # (((sp2 == `SP2@LTC256B))) -> (((DEFINED TABLES_mem_1(sem,sco,private)) && ((TABLES_mem_1(sem,sco,private) != 10) && (TABLES_mem_1(sem,sco,private) != 4) && (TABLES_mem_1(sem,sco,private) != 5) && (TABLES_mem_1(sem,sco,private) != 6) && (TABLES_mem_1(sem,sco,private) != 7))))
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Defined', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    # ld__sImmOffset
    __EXPR_TYPE_136 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Defined', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_136(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]
        tables_tt = [i.table for i in expr if isinstance(i, Op_Table)]
        # make sure we use the same table in the entire expression
        if not len(set([str(i) for i in expr if isinstance(i, Op_Table)])) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]

        # (((sp2 == `SP2@LTC256B)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        t_args = list([(int(x), int(y), int(z)) for x,y,z in itt.product(nn[1]['v'],nn[2]['v'],nn[3]['v'])])
        # (((DEFINED TABLES_mem_1(sem,sco,private)) && 
        defined_args = [arg for arg in t_args if       arg in tables_tt[0]]
        n_defined_args = [arg for arg in t_args if not(arg in tables_tt[0])]

        # ((TABLES_mem_1(sem,sco,private) != 10) && (TABLES_mem_1(sem,sco,private) != 4) && (TABLES_mem_1(sem,sco,private) != 5) && (TABLES_mem_1(sem,sco,private) != 6) && (TABLES_mem_1(sem,sco,private) != 7))))
        t_args2 = [arg for arg in defined_args if      (tables_tt[0][arg] not in int_tt)]
        n_t_args2 = [arg for arg in defined_args if not(tables_tt[0][arg] not in int_tt)] + n_defined_args

        n_sem = nn[1]['n']
        n_sco = nn[2]['n']
        n_private = nn[3]['n']

        b_sem = nn[1]['v'][0]
        b_sem_sign = 1 if b_sem.signed else 0
        b_sco = nn[2]['v'][0]
        b_sco_sign = 1 if b_sco.signed else 0
        b_private = nn[3]['v'][0]
        b_private_sign = 1 if b_private.signed else 0

        right_T_ll = [{
            n_sem:SASS_Bits.from_int(a1, bit_len=b_sem.bit_len, signed=b_sem_sign), 
            n_sco:SASS_Bits.from_int(a2, bit_len=b_sco.bit_len, signed=b_sco_sign), 
            n_private:SASS_Bits.from_int(a3, bit_len=b_private.bit_len, signed=b_private_sign)
        } for a1,a2,a3 in t_args2]

        right_F_ll = [{
            n_sem:SASS_Bits.from_int(a1, bit_len=b_sem.bit_len, signed=b_sem_sign), 
            n_sco:SASS_Bits.from_int(a2, bit_len=b_sco.bit_len, signed=b_sco_sign), 
            n_private:SASS_Bits.from_int(a3, bit_len=b_private.bit_len, signed=b_private_sign)
        } for a1,a2,a3 in n_t_args2]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((seq == `SEQ_ublkcp@SEQUENCED))) -> (((DEFINED TABLES_mem_5(sem,sco,0)) && ((TABLES_mem_5(sem,sco,0) != 0))))
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Defined', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias', 'Op_Comma', 'Op_Alias', 'Op_Comma', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    # ublkcp_
    __EXPR_TYPE_137 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Defined', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Table', 'Op_LBrace', 'Op_Alias_1', 'Op_Comma', 'Op_Alias_2', 'Op_Comma', 'Op_Int', 'Op_RBrace', 'Op_NotEqual', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_137(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]
        tables_tt = [i.table for i in expr if isinstance(i, Op_Table)]
        # make sure we use the same table in the entire expression
        if not len(set([str(i) for i in expr if isinstance(i, Op_Table)])) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((seq == `SEQ_ublkcp@SEQUENCED)))
        pp = nn[0]['v']
        left_T_ll = [{nn[0]['n']:a0} for a0 in pp if    (a0 == reg_tt[0])]
        left_F_ll = [{nn[0]['n']:a0} for a0 in pp if not(a0 == reg_tt[0])]

        t_args = list([(int(x), int(y), int(z)) for x,y,z in itt.product(nn[1]['v'],nn[2]['v'], [0])])
        # (((DEFINED TABLES_mem_5(sem,sco,0)) &&
        defined_args = [arg for arg in t_args if       arg in tables_tt[0]]
        n_defined_args = [arg for arg in t_args if not(arg in tables_tt[0])]

        # ((TABLES_mem_5(sem,sco,0) != 0))))
        t_args2 = [arg for arg in defined_args if      (tables_tt[0][arg] not in int_tt)]
        n_t_args2 = [arg for arg in defined_args if not(tables_tt[0][arg] not in int_tt)] + n_defined_args

        n_sem = nn[1]['n']
        n_sco = nn[2]['n']

        b_sem = nn[1]['v'][0]
        b_sem_sign = 1 if b_sem.signed else 0
        b_sco = nn[2]['v'][0]
        b_sco_sign = 1 if b_sco.signed else 0

        right_T_ll = [{
            n_sem:SASS_Bits.from_int(a1, bit_len=b_sem.bit_len, signed=b_sem_sign), 
            n_sco:SASS_Bits.from_int(a2, bit_len=b_sco.bit_len, signed=b_sco_sign)
        } for a1,a2,_ in t_args2]

        right_F_ll = [{
            n_sem:SASS_Bits.from_int(a1, bit_len=b_sem.bit_len, signed=b_sem_sign), 
            n_sco:SASS_Bits.from_int(a2, bit_len=b_sco.bit_len, signed=b_sco_sign)
        } for a1,a2,_ in n_t_args2]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx
    
    # (((uai == `UAI@UAI)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_1D)) && ((lodlc == `LODLC_tex@nolodlc_tex))) -> ((((Rb) == `Register@RZ)))
    # tex_scr_urc_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_138 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_4', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_5', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_138(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((uai == `UAI@UAI)) && ((aoffi == `AOFFI@noaoffi)) && ((dc == `DC@noDC)) && ((paramA == `TEXPARAMA@ARRAY_1D)) && ((lodlc == `LODLC_tex@nolodlc_tex)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v'],nn[3]['v'],nn[4]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2, nn[3]['n']:a3, nn[4]['n']:a4} for a0,a1,a2,a3,a4 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]) and (a3 == reg_tt[3]) and (a4 == reg_tt[4]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rb) == `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[5]['v'])
        right_T_ll = [{nn[5]['n']:a5} for a5 in pp2 if    (a5 == reg_tt[5])]
        right_F_ll = [{nn[5]['n']:a5} for a5 in pp2 if not(a5 == reg_tt[5])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx
    
    # (((mode == `TEXONLY@TEX)) && ((paramA == `PARAMA_2D_3D@3D)) && ((lodlc == `LODLC@nolodlc))) -> (((lodlc == `LODLC@LZ) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)))
    # footprint_scr_b_noConst_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_139 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_139(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # # (((mode == `TEXONLY@TEX)) && ((paramA == `PARAMA_2D_3D@3D)) && ((lodlc == `LODLC@nolodlc)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 == reg_tt[2]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((lodlc == `LODLC@LZ) || (lodlc == `LODLC@LB) || (lodlc == `LODLC@LL) || (lodlc == `LODLC@LC) || (lodlc == `LODLC@LB.LC)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[2]['v'])
        right_T_ll = [{nn[2]['n']:a2} for a2 in pp2 if    (a2 in reg_tt[3:])]
        right_F_ll = [{nn[2]['n']:a2} for a2 in pp2 if not(a2 in reg_tt[3:])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((uai == `UAI@UAI)) && ((paramA == `TEXPARAMA@ARRAY_1D)) && ((lodlc == `LODLC_tex@nolodlc_tex) || (lodlc == `LODLC_tex@LZ) || (lodlc == `LODLC_tex@LB) || (lodlc == `LODLC_tex@LL) || (lodlc == `LODLC_tex@ULB) || (lodlc == `LODLC_tex@ULL) || (lodlc == `LODLC_tex@ULC) || (lodlc == `LODLC_tex@LB.ULC))) -> ((((Ra) != `Register@RZ)))    
    # tex_b_noConst_ | sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_140 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_140(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((uai == `UAI@UAI)) && ((paramA == `TEXPARAMA@ARRAY_1D)) && ((lodlc == `LODLC_tex@nolodlc_tex) || (lodlc == `LODLC_tex@LZ) || (lodlc == `LODLC_tex@LB) || (lodlc == `LODLC_tex@LL) || (lodlc == `LODLC_tex@ULB) || (lodlc == `LODLC_tex@ULL) || (lodlc == `LODLC_tex@ULC) || (lodlc == `LODLC_tex@LB.ULC)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 in reg_tt[2:-1]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 == reg_tt[1]) and (a2 in reg_tt[2:-1]))]

        # param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Ra) != `Register@RZ)))    
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    (a3 != reg_tt[-1])]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not(a3 != reg_tt[-1])]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@AOFFI)) && ((ms == `MS@noMS) || (ms == `MS@UMS)) && ((lodlc == `LODLC_tld@LL))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 3))))
    # tld_b_noConst_ |  sm_120 to sm_120
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_141 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_141(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@AOFFI)) && ((ms == `MS@noMS) || (ms == `MS@UMS)) && ((lodlc == `LODLC_tld@LL)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 in reg_tt[1:3]) and (a2 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 in reg_tt[1:3]) and (a2 == reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 3))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    ( (int(a3) == reg_tt[4]) or (int(a3) <= param_tt[0] - int_tt[0]) )]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not( (int(a3) == reg_tt[4]) or (int(a3) <= param_tt[0] - int_tt[0]) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx


    # (((aoffi == `AOFFI@AOFFI)) && ((ms == `MS@noMS) || (ms == `MS@UMS)) && ((lodlc == `LODLC_tld@LL))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 4) == 0))
    # tld_b_noConst_
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_142 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_142(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@AOFFI)) && ((ms == `MS@noMS) || (ms == `MS@UMS)) && ((lodlc == `LODLC_tld@LL)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 in reg_tt[1:3]) and (a2 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 in reg_tt[1:3]) and (a2 == reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ( ( ( ((Rb) + ((Rb) == `Register@RZ)) % 4) == 0) )
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    ( (( (int(a3) + (int(a3) == reg_tt[4])) ) % int_tt[0]) == int_tt[1] )]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not( (( (int(a3) + (int(a3) == reg_tt[4])) ) % int_tt[0]) == int_tt[1] )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx


    # (((aoffi == `AOFFI@AOFFI)) && ((ms == `MS@noMS) || (ms == `MS@UMS)) && ((lodlc == `LODLC_tld@LL))) -> ((((Rb) != `Register@RZ)))
    # tld_b_noConst
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_143 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_143(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@AOFFI)) && ((ms == `MS@noMS) || (ms == `MS@UMS)) && ((lodlc == `LODLC_tld@LL)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 == reg_tt[0]) and (a1 in reg_tt[1:3]) and (a2 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 == reg_tt[0]) and (a1 in reg_tt[1:3]) and (a2 == reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rb) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    ( a3 != reg_tt[4] )]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not( a3 != reg_tt[4] )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi) || (aoffi == `AOFFI@UAOFFI)) && ((ms == `MS@MS)) && ((lodlc == `LODLC_tld@LL))) -> (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 3))))
    # tld_b_noConst_
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_144 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_SmallerOrEqual', 'Op_Parameter', 'Op_Minus', 'Op_Int', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_144(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@noaoffi) || (aoffi == `AOFFI@UAOFFI)) && ((ms == `MS@MS)) && ((lodlc == `LODLC_tld@LL)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 in reg_tt[0:2]) and (a1 == reg_tt[2]) and (a2 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 in reg_tt[0:2]) and (a1 == reg_tt[2]) and (a2 == reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) == `Register@RZ) || ((Rb) <= %MAX_REG_COUNT - 3))))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    ( (int(a3) == reg_tt[4]) or (int(a3) <= (param_tt[0] - int_tt[0])) )]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not( (int(a3) == reg_tt[4]) or (int(a3) <= (param_tt[0] - int_tt[0])) )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi) || (aoffi == `AOFFI@UAOFFI)) && ((ms == `MS@MS)) && ((lodlc == `LODLC_tld@LL))) -> (((((Rb) + ((Rb) == `Register@RZ)) % 4) == 0))
    # tld_b_noConst_
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_145 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Plus', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_Mod', 'Op_Int', 'Op_RBrace', 'Op_Equal', 'Op_Int', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_145(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@noaoffi) || (aoffi == `AOFFI@UAOFFI)) && ((ms == `MS@MS)) && ((lodlc == `LODLC_tld@LL)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 in reg_tt[0:2]) and (a1 == reg_tt[2]) and (a2 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 in reg_tt[0:2]) and (a1 == reg_tt[2]) and (a2 == reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # (((((Rb) + ((Rb) == `Register@RZ)) % 4) == 0))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    ( ( (int(a3) + (int(a3) == reg_tt[4])) % int_tt[0]) == int_tt[1] )]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not( ( (int(a3) + (int(a3) == reg_tt[4])) % int_tt[0]) == int_tt[1] )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx

    # (((aoffi == `AOFFI@noaoffi) || (aoffi == `AOFFI@UAOFFI)) && ((ms == `MS@MS)) && ((lodlc == `LODLC_tld@LL))) -> ((((Rb) != `Register@RZ)))
    # tld_b_noConst_
    # old_pattern: ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace')
    __EXPR_TYPE_146 = ('Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_Or', 'Op_LBrace', 'Op_Alias_0', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_1', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_And', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_2', 'Op_Equal', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace', 'Op_Implication', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_LBrace', 'Op_Alias_3', 'Op_RBrace', 'Op_NotEqual', 'Op_Register', 'Op_RBrace', 'Op_RBrace', 'Op_RBrace').__hash__()
    @staticmethod
    def __expr_type_146(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        alias_tt = []
        for i in expr:
            if isinstance(i, Op_Alias) and not i.value() in alias_tt: alias_tt.append(i.value())
        reg_tt = [i.value() for i in expr if isinstance(i, Op_Register)]
        int_tt = [i.value() for i in expr if isinstance(i, Op_Int)]

        expr_vals = SASS_Expr_Domain_Common.__get_alias_nt_domains(alias_tt, alias_nt, domain_vals, keep_sass_bits=True)
        nn = [{'tt':tt, 'n':ee[0], 'v':ee[1]} for tt,ee in zip(alias_tt, expr_vals)]
        
        # (((aoffi == `AOFFI@noaoffi) || (aoffi == `AOFFI@UAOFFI)) && ((ms == `MS@MS)) && ((lodlc == `LODLC_tld@LL)))
        pp = list(itt.product(nn[0]['v'],nn[1]['v'],nn[2]['v']))
        left_T_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if    ((a0 in reg_tt[0:2]) and (a1 == reg_tt[2]) and (a2 == reg_tt[3]))]
        left_F_ll = [{nn[0]['n']:a0, nn[1]['n']:a1, nn[2]['n']:a2} for a0,a1,a2 in pp if not((a0 in reg_tt[0:2]) and (a1 == reg_tt[2]) and (a2 == reg_tt[3]))]

        param_tt = [i.value() for i in expr if isinstance(i, Op_Parameter)]
        # ((((Rb) != `Register@RZ)))
        pp2 = SASS_Expr_Domain_Common.__reduce_reg_dom(nn[3]['v'])
        right_T_ll = [{nn[3]['n']:a3} for a3 in pp2 if    ( a3 != reg_tt[4] )]
        right_F_ll = [{nn[3]['n']:a3} for a3 in pp2 if not( a3 != reg_tt[4] )]

        impl_p = SASS_Expr_Domain_Common.__group_implication(left_T_ll, left_F_ll, right_T_ll, right_F_ll)
        impl = SASS_Expr_Domain_Utils.implication(impl_p['lt'], impl_p['lf'], impl_p['rt'], impl_p['rf'])
        xx = SASS_Expr_Domain_Common.__attach_results(impl, domain_vals)
        return xx


    __EXPR_TYPES = {
        __EXPR_TYPE_1 : __expr_type_1,
        __EXPR_TYPE_2 : __expr_type_2,
        __EXPR_TYPE_3 : __expr_type_3,
        __EXPR_TYPE_4 : __expr_type_4,
        __EXPR_TYPE_6 : __expr_type_6,
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
        __EXPR_TYPE_38 : __expr_type_38,
        __EXPR_TYPE_39 : __expr_type_39,
        __EXPR_TYPE_40 : __expr_type_40,
        __EXPR_TYPE_41 : __expr_type_41,
        __EXPR_TYPE_42 : __expr_type_42,
        __EXPR_TYPE_43 : __expr_type_43,
        __EXPR_TYPE_44 : __expr_type_44,
        __EXPR_TYPE_45 : __expr_type_45,
        __EXPR_TYPE_46 : __expr_type_46,
        __EXPR_TYPE_47 : __expr_type_47,
        __EXPR_TYPE_48 : __expr_type_48,
        __EXPR_TYPE_49 : __expr_type_49,
        __EXPR_TYPE_50 : __expr_type_50,
        __EXPR_TYPE_51 : __expr_type_51,
        __EXPR_TYPE_52 : __expr_type_52,
        __EXPR_TYPE_53 : __expr_type_53,
        __EXPR_TYPE_54 : __expr_type_54,
        __EXPR_TYPE_55 : __expr_type_55,
        __EXPR_TYPE_56 : __expr_type_56,
        __EXPR_TYPE_57 : __expr_type_57,
        __EXPR_TYPE_58 : __expr_type_58,
        __EXPR_TYPE_59 : __expr_type_59,
        __EXPR_TYPE_60 : __expr_type_60,
        __EXPR_TYPE_61 : __expr_type_61,
        __EXPR_TYPE_62 : __expr_type_62,
        __EXPR_TYPE_63 : __expr_type_63,
        __EXPR_TYPE_64 : __expr_type_64,
        __EXPR_TYPE_66 : __expr_type_66,
        __EXPR_TYPE_67 : __expr_type_67,
        __EXPR_TYPE_68 : __expr_type_68,
        __EXPR_TYPE_69 : __expr_type_69,
        __EXPR_TYPE_70 : __expr_type_70,
        __EXPR_TYPE_71 : __expr_type_71,
        __EXPR_TYPE_72 : __expr_type_72,
        __EXPR_TYPE_73 : __expr_type_73,
        __EXPR_TYPE_74 : __expr_type_74,
        __EXPR_TYPE_75 : __expr_type_75,
        __EXPR_TYPE_76 : __expr_type_76,
        __EXPR_TYPE_77 : __expr_type_77,
        __EXPR_TYPE_78 : __expr_type_78,
        __EXPR_TYPE_79 : __expr_type_79,
        __EXPR_TYPE_80 : __expr_type_80,
        __EXPR_TYPE_81 : __expr_type_81,
        __EXPR_TYPE_82 : __expr_type_82,
        __EXPR_TYPE_83 : __expr_type_83,
        __EXPR_TYPE_84 : __expr_type_84,
        __EXPR_TYPE_85 : __expr_type_85,
        __EXPR_TYPE_86 : __expr_type_86,
        __EXPR_TYPE_87 : __expr_type_87,
        __EXPR_TYPE_88 : __expr_type_88,
        __EXPR_TYPE_89 : __expr_type_89,
        __EXPR_TYPE_91 : __expr_type_91,
        __EXPR_TYPE_92 : __expr_type_92,
        __EXPR_TYPE_93 : __expr_type_93,
        __EXPR_TYPE_94 : __expr_type_94,
        __EXPR_TYPE_95 : __expr_type_95,
        __EXPR_TYPE_96 : __expr_type_96,
        __EXPR_TYPE_97 : __expr_type_97,
        __EXPR_TYPE_98 : __expr_type_98,
        __EXPR_TYPE_99 : __expr_type_99,
        __EXPR_TYPE_100 : __expr_type_100,
        __EXPR_TYPE_101 : __expr_type_101,
        __EXPR_TYPE_102 : __expr_type_102,
        __EXPR_TYPE_103 : __expr_type_103,
        __EXPR_TYPE_104 : __expr_type_104,
        __EXPR_TYPE_105 : __expr_type_105,
        __EXPR_TYPE_106 : __expr_type_106,
        __EXPR_TYPE_107 : __expr_type_107,
        __EXPR_TYPE_108 : __expr_type_108,
        __EXPR_TYPE_109 : __expr_type_109,
        __EXPR_TYPE_110 : __expr_type_110,
        __EXPR_TYPE_111 : __expr_type_111,
        __EXPR_TYPE_112 : __expr_type_112,
        __EXPR_TYPE_113 : __expr_type_113,
        __EXPR_TYPE_114 : __expr_type_114,
        __EXPR_TYPE_115 : __expr_type_115,
        __EXPR_TYPE_116 : __expr_type_116,
        __EXPR_TYPE_117 : __expr_type_117,
        __EXPR_TYPE_118 : __expr_type_118,
        __EXPR_TYPE_119 : __expr_type_119,
        __EXPR_TYPE_120 : __expr_type_120,
        __EXPR_TYPE_121 : __expr_type_121,
        __EXPR_TYPE_122 : __expr_type_122,
        __EXPR_TYPE_123 : __expr_type_123,
        __EXPR_TYPE_124 : __expr_type_124,
        __EXPR_TYPE_125 : __expr_type_125,
        __EXPR_TYPE_126 : __expr_type_126,
        __EXPR_TYPE_127 : __expr_type_127,
        __EXPR_TYPE_128 : __expr_type_128,
        __EXPR_TYPE_129 : __expr_type_129,
        __EXPR_TYPE_130 : __expr_type_130,
        __EXPR_TYPE_131 : __expr_type_131,
        __EXPR_TYPE_132 : __expr_type_132,
        __EXPR_TYPE_133 : __expr_type_133,
        __EXPR_TYPE_134 : __expr_type_134,
        __EXPR_TYPE_135 : __expr_type_135,
        __EXPR_TYPE_136 : __expr_type_136,
        __EXPR_TYPE_137 : __expr_type_137,
        __EXPR_TYPE_138 : __expr_type_138,
        __EXPR_TYPE_139 : __expr_type_139,
        __EXPR_TYPE_140 : __expr_type_140,
        __EXPR_TYPE_141 : __expr_type_141,
        __EXPR_TYPE_142 : __expr_type_142,
        __EXPR_TYPE_143 : __expr_type_143,
        __EXPR_TYPE_144 : __expr_type_144,
        __EXPR_TYPE_145 : __expr_type_145,
        __EXPR_TYPE_146 : __expr_type_146

    }

    __OLD_EXPR_TYPES = {
        __OLD_EXPR_TYPE_1   : __EXPR_TYPE_1,
        __OLD_EXPR_TYPE_2   : __EXPR_TYPE_2,
        __OLD_EXPR_TYPE_3   : __EXPR_TYPE_3,
        __OLD_EXPR_TYPE_4   : __EXPR_TYPE_4,
        __OLD_EXPR_TYPE_6   : __EXPR_TYPE_6,
        __OLD_EXPR_TYPE_8   : __EXPR_TYPE_8,
        __OLD_EXPR_TYPE_9   : __EXPR_TYPE_9,
        __OLD_EXPR_TYPE_10  : __EXPR_TYPE_10, 
        __OLD_EXPR_TYPE_11  : __EXPR_TYPE_11, 
        __OLD_EXPR_TYPE_12  : __EXPR_TYPE_12, 
        __OLD_EXPR_TYPE_13  : __EXPR_TYPE_13, 
        __OLD_EXPR_TYPE_14  : __EXPR_TYPE_14, 
        __OLD_EXPR_TYPE_15  : __EXPR_TYPE_15, 
        __OLD_EXPR_TYPE_16  : __EXPR_TYPE_16, 
        __OLD_EXPR_TYPE_17  : __EXPR_TYPE_17, 
        __OLD_EXPR_TYPE_18  : __EXPR_TYPE_18, 
        __OLD_EXPR_TYPE_19  : __EXPR_TYPE_19, 
        __OLD_EXPR_TYPE_20  : __EXPR_TYPE_20, 
        __OLD_EXPR_TYPE_21  : __EXPR_TYPE_21, 
        __OLD_EXPR_TYPE_22  : __EXPR_TYPE_22, 
        __OLD_EXPR_TYPE_23  : __EXPR_TYPE_23, 
        __OLD_EXPR_TYPE_24  : __EXPR_TYPE_24, 
        __OLD_EXPR_TYPE_25  : __EXPR_TYPE_25, 
        __OLD_EXPR_TYPE_26  : __EXPR_TYPE_26, 
        __OLD_EXPR_TYPE_27  : __EXPR_TYPE_27, 
        __OLD_EXPR_TYPE_28  : __EXPR_TYPE_28, 
        __OLD_EXPR_TYPE_29  : __EXPR_TYPE_29, 
        __OLD_EXPR_TYPE_30  : __EXPR_TYPE_30, 
        __OLD_EXPR_TYPE_31  : __EXPR_TYPE_31, 
        __OLD_EXPR_TYPE_32  : __EXPR_TYPE_32, 
        __OLD_EXPR_TYPE_33  : __EXPR_TYPE_33, 
        __OLD_EXPR_TYPE_34  : __EXPR_TYPE_34, 
        __OLD_EXPR_TYPE_35  : __EXPR_TYPE_35, 
        __OLD_EXPR_TYPE_36  : __EXPR_TYPE_36, 
        __OLD_EXPR_TYPE_37  : __EXPR_TYPE_37, 
        __OLD_EXPR_TYPE_38  : __EXPR_TYPE_38, 
        __OLD_EXPR_TYPE_39  : __EXPR_TYPE_39, 
        __OLD_EXPR_TYPE_40  : __EXPR_TYPE_40, 
        __OLD_EXPR_TYPE_41  : __EXPR_TYPE_41, 
        __OLD_EXPR_TYPE_42  : __EXPR_TYPE_42, 
        __OLD_EXPR_TYPE_43  : __EXPR_TYPE_43, 
        __OLD_EXPR_TYPE_44  : __EXPR_TYPE_44, 
        __OLD_EXPR_TYPE_45  : __EXPR_TYPE_45, 
        __OLD_EXPR_TYPE_46  : __EXPR_TYPE_46, 
        __OLD_EXPR_TYPE_47  : __EXPR_TYPE_47, 
        __OLD_EXPR_TYPE_48  : __EXPR_TYPE_48, 
        __OLD_EXPR_TYPE_49  : __EXPR_TYPE_49, 
        __OLD_EXPR_TYPE_50  : __EXPR_TYPE_50, 
        __OLD_EXPR_TYPE_51  : __EXPR_TYPE_51, 
        __OLD_EXPR_TYPE_52  : __EXPR_TYPE_52, 
        __OLD_EXPR_TYPE_53  : __EXPR_TYPE_53, 
        __OLD_EXPR_TYPE_54  : __EXPR_TYPE_54, 
        __OLD_EXPR_TYPE_55  : __EXPR_TYPE_55, 
        __OLD_EXPR_TYPE_56  : __EXPR_TYPE_56, 
        __OLD_EXPR_TYPE_57  : __EXPR_TYPE_57, 
        __OLD_EXPR_TYPE_58  : __EXPR_TYPE_58, 
        __OLD_EXPR_TYPE_59  : __EXPR_TYPE_59, 
        __OLD_EXPR_TYPE_60  : __EXPR_TYPE_60, 
        __OLD_EXPR_TYPE_61  : __EXPR_TYPE_61, 
        __OLD_EXPR_TYPE_62  : __EXPR_TYPE_62, 
        __OLD_EXPR_TYPE_63  : __EXPR_TYPE_63, 
        __OLD_EXPR_TYPE_64  : __EXPR_TYPE_64, 
        __OLD_EXPR_TYPE_66  : __EXPR_TYPE_66, 
        __OLD_EXPR_TYPE_67  : __EXPR_TYPE_67, 
        __OLD_EXPR_TYPE_68  : __EXPR_TYPE_68, 
        __OLD_EXPR_TYPE_69  : __EXPR_TYPE_69, 
        __OLD_EXPR_TYPE_70  : __EXPR_TYPE_70, 
        __OLD_EXPR_TYPE_71  : __EXPR_TYPE_71, 
        __OLD_EXPR_TYPE_72  : __EXPR_TYPE_72, 
        __OLD_EXPR_TYPE_73  : __EXPR_TYPE_73, 
        __OLD_EXPR_TYPE_74  : __EXPR_TYPE_74, 
        __OLD_EXPR_TYPE_75  : __EXPR_TYPE_75, 
        __OLD_EXPR_TYPE_76  : __EXPR_TYPE_76, 
        __OLD_EXPR_TYPE_77  : __EXPR_TYPE_77, 
        __OLD_EXPR_TYPE_78  : __EXPR_TYPE_78, 
        __OLD_EXPR_TYPE_79  : __EXPR_TYPE_79, 
        __OLD_EXPR_TYPE_80  : __EXPR_TYPE_80, 
        __OLD_EXPR_TYPE_81  : __EXPR_TYPE_81, 
        __OLD_EXPR_TYPE_82  : __EXPR_TYPE_82, 
        __OLD_EXPR_TYPE_83  : __EXPR_TYPE_83, 
        __OLD_EXPR_TYPE_84  : __EXPR_TYPE_84, 
        __OLD_EXPR_TYPE_85  : __EXPR_TYPE_85, 
        __OLD_EXPR_TYPE_86  : __EXPR_TYPE_86, 
        __OLD_EXPR_TYPE_87  : __EXPR_TYPE_87, 
        __OLD_EXPR_TYPE_88  : __EXPR_TYPE_88, 
        __OLD_EXPR_TYPE_89  : __EXPR_TYPE_89, 
        __OLD_EXPR_TYPE_91  : __EXPR_TYPE_91, 
        __OLD_EXPR_TYPE_92  : __EXPR_TYPE_92, 
        __OLD_EXPR_TYPE_93  : __EXPR_TYPE_93, 
        __OLD_EXPR_TYPE_94  : __EXPR_TYPE_94, 
        __OLD_EXPR_TYPE_95  : __EXPR_TYPE_95, 
        __OLD_EXPR_TYPE_96  : __EXPR_TYPE_96, 
        __OLD_EXPR_TYPE_97  : __EXPR_TYPE_97, 
        __OLD_EXPR_TYPE_98  : __EXPR_TYPE_98, 
        __OLD_EXPR_TYPE_99  : __EXPR_TYPE_99, 
        __OLD_EXPR_TYPE_100 : __EXPR_TYPE_100,
        __OLD_EXPR_TYPE_101 : __EXPR_TYPE_101,
        __OLD_EXPR_TYPE_102 : __EXPR_TYPE_102,
        __OLD_EXPR_TYPE_103 : __EXPR_TYPE_103,
        __OLD_EXPR_TYPE_104 : __EXPR_TYPE_104,
        __OLD_EXPR_TYPE_105 : __EXPR_TYPE_105,
        __OLD_EXPR_TYPE_106 : __EXPR_TYPE_106,
        __OLD_EXPR_TYPE_107 : __EXPR_TYPE_107,
        __OLD_EXPR_TYPE_108 : __EXPR_TYPE_108,
        __OLD_EXPR_TYPE_109 : __EXPR_TYPE_109,
        __OLD_EXPR_TYPE_110 : __EXPR_TYPE_110,
        __OLD_EXPR_TYPE_111 : __EXPR_TYPE_111,
        __OLD_EXPR_TYPE_112 : __EXPR_TYPE_112,
        __OLD_EXPR_TYPE_113 : __EXPR_TYPE_113,
        __OLD_EXPR_TYPE_114 : __EXPR_TYPE_114,
        __OLD_EXPR_TYPE_115 : __EXPR_TYPE_115,
        __OLD_EXPR_TYPE_116 : __EXPR_TYPE_116
    }

    @staticmethod
    def expr_types() -> dict: return SASS_Expr_Domain_Common.__EXPR_TYPES
    @staticmethod
    def old_expr_types(): return SASS_Expr_Domain_Common.__OLD_EXPR_TYPES

if __name__ == '__main__':
    for o,n in SASS_Expr_Domain_Common.old_expr_types().items():
        if not all([nn.startswith(oo) for oo,nn in zip(o,n)]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
