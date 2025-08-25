import datetime
import psutil
import typing
import time
import os
import pickle
import itertools as itt
import _config as sp
from py_sass import Op_Alias
from py_sass import SASS_Expr
from py_sass import TT_Instruction, TT_Reg, TT_Func
from py_sass import TT_OpAtAbs, TT_OpAtInvert, TT_OpAtNegate, TT_OpAtNot, TT_OpAtSign
from py_sass import SM_SASS
from py_sass import SASS_Class
from py_sass import SASS_Expr_Domain_Contract
from py_sass import SM_Cu_Details
from py_sass_ext import SASS_Range
from _sass_expression_domain_range import SASS_Expr_Domain_Range
from _sass_expression_domain_common import SASS_Expr_Domain_Common
from _sass_expression_domain_limits import SASS_Expr_Domain_Limits

class SASS_Expr_Domain_Calc:
    """
    This one calculates all possible values for all instruction operands based on evaluation of all
    CONDITIONS for each instruction class.

    Exhaustive statistics can be generated with the script
    _sass_expression_domain_parse.py

    Generally, the problem of solving a giant number of expressions for all possible inputs is not solvable
    in reasonable time. In this case, though, the expressions follow a pattern that allows this.
     - There are very few expressions (37 in total) that need the concept of a 'range' because their domains is too large to enumerate.
       This includes all CONDITIONS that cover things to do with addresses or immediate values
     - The largest non-range set of values to be covered is 255, which are 8-bit registers
     - Most expressions have 1 or 2 variables
     - A small number of expressions appears thousands of times and can be optimized with a specialized method
    """

    @staticmethod
    def create_non_sat_log(log_path:str, expr:SASS_Expr, sass:SM_SASS, class_name:str, domains:list, d:dict):
        with open(log_path,"w") as f:
            f.write("not res => => Exception('Unsatisfiable') [{0}]\n".format(str(datetime.datetime.now())))
            f.write(str(expr) + "\n")
            f.write(str(expr.pattern) + "\n\n")
            f.write(str(sass.sm.get_from_all_classes(class_name)) + "\n\n")
            f.write("All domains in set:\n")
            for ind,dom in enumerate(domains):
                f.write("d_ind={0}\n".format(ind))
                for i in dom.items():
                    f.write("{0}: {1}\n".format(i[0], [int(j) for j in i[1]]))
                f.write("\n")
            f.write("\nLast domain before failing:\n")
            for i in d.items():
                f.write("{0}: {1}\n".format(i[0], [int(j) for j in i[1]]))
            f.write("\n\n")

    @staticmethod
    def aliases_and_res(aliases:typing.List[dict], res:dict):
        for a in aliases:
            for k in res:
                if k in a: a[k] = a[k].intersection(res[k])
        return aliases

    @staticmethod
    def test_range_domains(n:int, count:int, index:int, tot_index:int, class_name:str, sass:SM_SASS, expr:SASS_Expr, domains:list, failed_path:str, stop_on_exception:bool=True, skip_tested:bool=True):
        sm_xx = sass.sm.details.SM_XX
        if skip_tested and expr.pattern in sp.GLOBAL__EXPRESSIONS_TESTED: return
        sp.GLOBAL__EXPRESSIONS_TESTED.add(expr.pattern)

        max_mem = psutil.virtual_memory().used

        dom_count = len(domains)
        print("[{0}.{1} - class {2}/{3}] test range expr {4}/{5}".format(sm_xx, class_name, n, count, index, tot_index))
        for d_ind,d in enumerate(domains):
            # if we have way to many values, reduce a bit...
            # try to keep the relevant parts which are the parts at the edges
            too_large = [i[0] for i in d.items() if len(i[1])>32]
            d_test_l = [i for i in d.items() if not i[0] in too_large]
            inter_set = [(i[0], sorted(i[1])) for i in d.items() if isinstance(i[1], set) and i[0] in too_large]
            d_test_l.extend([(i[0],i[1][:8]+i[1][-8:]) for i in inter_set])
            d_test_l += [(i[0], [s for s in i[1].sized_iter(32)]) for i in d.items() if isinstance(i[1], SASS_Range) and i[0] in too_large]
            d_test = dict(d_test_l)

            var_pick = [[(n,dd) for dd in d_test[n]] for n in expr.get_alias_names()]
            enc_vals = [dict(i) for i in itt.product(*var_pick)]
            dom_size = len(enc_vals)

            n_max_mem = psutil.virtual_memory().used
            if max_mem < n_max_mem: max_mem = n_max_mem

            for ev_ind,ev in enumerate(enc_vals):
                rr = expr(ev)
                if not rr == True:
                    print("[{0}.{1} - class {2}/{3}] failed ... domain {4}/{5}, test [{6}/{7}]".format(sm_xx, class_name, n, count, d_ind, dom_count, ev_ind, dom_size))
                    with open(failed_path,"w") as f:
                        f.write("Detected wrong value set [{0}]\n".format(str(datetime.datetime.now())))
                        f.write(str(expr) + "\n")
                        f.write(str([(i[0], int(i[1])) for i in ev.items()]) + "\n")
                        f.write(str(expr.pattern) + "\n\n")
                        f.write(str(sass.sm.get_from_all_classes(class_name)) + "\n\n")
                if stop_on_exception and not rr == True:
                    assert(False)
        sp.GLOBAL__USED_RAM_SAMPLES.append(max_mem)

    @staticmethod
    def test_all_domains(n:int, count:int, failed_path:str, sass:SM_SASS, class_name:str, expr_ind:int, expr_count:int, expr:SASS_Expr, domains:list, stop_on_exception:bool=True, skip_tested:bool=True):
        sm_xx = sass.sm.details.SM_XX
        if skip_tested and expr.pattern in sp.GLOBAL__EXPRESSIONS_TESTED: return
        sp.GLOBAL__EXPRESSIONS_TESTED.add(expr.pattern)

        max_mem = psutil.virtual_memory().used

        dom_count = len(domains)
        print("[{0}.{1} - class {2}/{3}] test expr {4}/{5}".format(sm_xx, class_name, n, count, expr_ind, expr_count))
        for d_ind,d in enumerate(domains):
            # if we have way to many values, reduce a bit...
            # try to keep the relevant parts which are the parts at the edges
            too_large = [i[0] for i in d.items() if len(i[1])>32]
            d_test_l = [i for i in d.items() if not i[0] in too_large]
            inter = [(i[0], sorted(i[1])) for i in d.items() if i[0] in too_large]
            d_test_l.extend([(i[0],i[1][:8]+i[1][-8:]) for i in inter])
            d_test = dict(d_test_l)
            var_pick = [[(n,dd) for dd in d_test[n]] for n in expr.get_alias_names()]
            enc_vals = [dict(i) for i in itt.product(*var_pick)]
            dom_size = len(enc_vals)

            n_max_mem = psutil.virtual_memory().used
            if max_mem < n_max_mem: max_mem = n_max_mem

            for ev_ind,ev in enumerate(enc_vals):
                rr = expr(ev)
                if not rr == True:
                    print("[{0}.{1} - class {2}/{3}] failed ... domain {4}/{5}, test [{6}/{7}]".format(sm_xx, class_name, n, count, d_ind, dom_count, ev_ind, dom_size))                    
                    with open(failed_path,"w") as f:
                        f.write("Detected wrong value set [{0}]\n".format(str(datetime.datetime.now())))
                        f.write(str(expr) + "\n")
                        f.write(str([(i[0], int(i[1])) for i in ev.items()]) + "\n")
                        f.write(str(expr.pattern) + "\n\n")
                        f.write(str(sass.sm.get_from_all_classes(class_name)) + "\n\n")
                if stop_on_exception and not rr == True:
                    assert(False)
        sp.GLOBAL__USED_RAM_SAMPLES.append(max_mem)

    @staticmethod
    def merge_same(domains:list, sass:SM_SASS, class_name:str):
        class_:SASS_Class = sass.sm.get_from_all_classes(class_name)
        format_tt:TT_Instruction
        format_tt = class_.FORMAT

        # First, get all domain aliases and make sure that we don't have any doubles:
        # for example, in SM 50 for the class "ALD", we have AIO and io that are the same
        # and for some CONDITIONS AIO is used and io for others.
        # In this step, make sure that both have the same values in their domains.
        combs = list(itt.combinations(domains[0].keys(),2))
        pairs = [c for c in combs if format_tt.eval[c[0]] == format_tt.eval[c[1]]]
        for p in pairs:
            for d in domains:
                # intersect the domains for the vars that point to the same operand
                resd = d[p[0]].intersection(d[p[1]])
                # if we dare to have an empty set here, we will go nuts
                if len(resd) == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                d[p[0]] = resd
                d[p[1]] = resd

        return domains

    @staticmethod
    def get_alias_domains(n:int, count:int, class_name:str, sass:SM_SASS, expressions:typing.List[SASS_Expr], log_path:str, failed_path:str, stop_on_exception=True, skip_tested=False):
        """
        If we have a large function in the expression, we can get the alias domains using
        the calculation accelerators.

        Otherwise, we have to get them individually for every operand.

        """
        to_limit = SASS_Expr_Domain_Limits.to_limit(sass.sm.details)
        max_mem = psutil.virtual_memory().used

        aliases = [dict()]
        rtt = SASS_Expr_Domain_Range.expr_types()
        expr:SASS_Expr
        for ind,expr in enumerate(expressions):
            alias_nt = expr.get_alias()
            if alias_nt:
                if expr.has_large_func:
                    # this one needs to get the correct domains right away (do intersection and stuff)
                    if not expr.__hash__() in rtt: raise Exception(sp.CONST__ERROR_UNEXPECTED)

                    an = expr.get_alias_names()
                    # the large function calculation methods take a to_limit becaues they use the
                    # domain limitations at this stage already, if they are present
                    aliases = SASS_Expr_Domain_Range.expr_types()[expr.__hash__()](aliases, sass, expr.expr, an, to_limit)
                    if not aliases:
                        # we may have some non-satisfiable things in here => don't kill the program
                        SASS_Expr_Domain_Calc.create_non_sat_log(log_path, expr, sass, class_name, [], {})
                        return []

                    SASS_Expr_Domain_Calc.test_range_domains(n, count, ind, len(expressions), class_name, sass, expr, aliases, failed_path, stop_on_exception=stop_on_exception, skip_tested=skip_tested)
                    n_max_mem = psutil.virtual_memory().used
                    if max_mem < n_max_mem: max_mem = n_max_mem
                    # we need to make sure all aliases are consistent
                    #  => and-relationship between expressions and domains
                else:
                    # This one just assignes the domains. If they need reduction, do that in the get_domain method
                    v:Op_Alias
                    for k,v in alias_nt.items():
                        a:dict
                        if isinstance(v.value(), TT_Reg):
                            r:TT_Reg = v.value()
                            res = r.get_domain(to_limit)
                        elif isinstance(v.value(), TT_OpAtAbs|TT_OpAtInvert|TT_OpAtNegate|TT_OpAtNot|TT_OpAtSign):
                            res = v.value().get_domain({})
                        elif isinstance(v.value(), TT_Func):
                            res = v.value().get_domain({})
                        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                        if aliases and not (k in aliases[0]):
                            for a in aliases:
                                a[k] = res
                    n_max_mem = psutil.virtual_memory().used
                    if max_mem < n_max_mem: max_mem = n_max_mem
                # check if we have alias duality and if so, intersect the dual sets
                aliases = SASS_Expr_Domain_Calc.merge_same(aliases, sass, class_name)
                n_max_mem = psutil.virtual_memory().used
                if max_mem < n_max_mem: max_mem = n_max_mem
        sp.GLOBAL__USED_RAM_SAMPLES.append(max_mem)
        return aliases

    @staticmethod
    def reduce_common_domain_task(ind:int, d:dict, sass:SM_SASS, expr:SASS_Expr, an:list, ctt:dict, orig_dom_keys:list, log_path:str, class_name:str):
        # We get back a dictionary or a list.
        nd = ctt[expr.__hash__()](sass, expr.expr, an, d)

        # Remove domain versions that are empty
        nd = SASS_Expr_Domain_Common.remove_empty_variants(nd)

        # Check if we have anything left in the new domain(s). If not, the domain is not valid and we don't add it.
        if not SASS_Expr_Domain_Common.final_domain_check(nd): return []

        # Because the original domain 'd' was the input, the new domain 'nd' is at most equal to the old one.
        # This is an implied 'and' relationship between the expressions
        # NOTE: we DON'T need an itt.product here. We take one particular domain 'd' and either only reduce the sets for a few aliases
        # in there or we get multiple new (even if smaller) sets for a subset of the aliases out of it.
        # Since we use specialized functions for very common expressions, those specialized functions are responsible for either
        # returning one dictionary or a list of dictionaries.
        # We still only have to either replace or extend the input domain 'd'. Not add the results to all present 'domains'
        if isinstance(nd, dict):
            if not nd.keys() == orig_dom_keys:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # just replace the old domain with the new one
            # [Used to be res.append(nd)]
            # we will do res.extend in any case... => return encapsulated result to get an 'append'
            return [nd]
        elif isinstance(nd, list):
            new_d:dict
            if not all(new_d.keys() == orig_dom_keys for new_d in nd):
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # we get multiple possible domains back => need to extend the domains
            # [Used to be res.extend(nd)]
            # we will do res.extend in any case... => return pure result to get an 'extend'
            return nd
    
        return []
    
    @staticmethod
    def reduce_fallback_domain_task(d:dict, expr:SASS_Expr, sass:SM_SASS, orig_dom_keys:list, log_path:str, class_name:str):
        var_pick = [[(n,dd) for dd in d[n]] for n in expr.get_alias_names()]
        enc_vals = [dict(i) for i in itt.product(*var_pick)]
        okok = []
        # Test all the combinations out of itt.product. Each one is a dict with one value per alias.
        for ev in enc_vals:
            if expr(ev): okok.append(ev)

        # Only a subset of the possibilities will pass. To keep the domain number from exploding, we have to concatenate
        # the remaining possibilities in to as few subsets as possible. We do this by sorting the resulting list of dictionaries by
        # size of each alias in ascending order and then apply a groupby.
        if okok:
            # now, okok is a potentially long list with dictionaries, each containing one combination of the alias valies generated by
            # itt.product, that survived the expr(ev) test. Now we have to group them back into as few sets as possible.
            # We do this by applying a groupby where the keys are sorted in ascending order by the size of their result set. For example: if
            # the alias 'ipaop' has 4 values and the alias 'Rb' has 256, we do groupby('ipaop'). At the end we get 4 sets, one for each 'ipaop' value.
            # If we have 3 alias 'a', 'b' and 'c', where len('a') < len('b') < len('c'), we do groupby('a','b') and get len('a')*len('b') resulting sets.
            res = SASS_Expr_Domain_Contract.group(okok)

            # First, check if the new domain(s) have values for all variables. If not, the domain is not valid and we don't add it.
            if not SASS_Expr_Domain_Common.final_domain_check(res): return []

            # res can have multiple possible sets but as few sets as possible.
            # Extend each of the sets in res with all the remaining variables in the domain
            # We only used the aliases relevant for the expression. That is likely fewer aliases than we have in the entire domain.
            # Since len(res) >= 1, iterate all results in res and add the rest of the domain back to it
            for c in res: c.update([(i,d[i]) for i in d if not i in c])

            # each fully updated domain must contain all variables
            if not all(i.keys() == orig_dom_keys for i in res): 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # Now the tricky part: if we have N sets in 'domains', we apply the new expression 'expr' to each of those sets.
            # The results are only valid for the current domain 'd', not all of the domains. Thus, we only have to replace the current
            # 'd' in domains with the new result 'res'.
            # This is NOT another itt.product (which is nice)
            # [Used to be: new_sets.extend(res)]
            # return pure result to get an 'extend'
            return res
            
        return []

    @staticmethod
    def reduce(class_name:str, sass:SM_SASS, expressions:typing.List[SASS_Expr], domains:list, log_path:str):
        ctt = SASS_Expr_Domain_Common.expr_types()
        orig_dom_keys = domains[0].keys()

        max_mem = psutil.virtual_memory().used

        for expr in expressions:
            if not domains:
                # There may be instructions where the conditions are really not satisfiable. One example would be:
                # ATOMS_CAST_RZ_and_Rc in SM50: it has Rb = ZeroRegister and then later checks for
                # (Rb != `Register@RZ) which results in the empty set...
                # It's difficult to overstate how annoying these things are...
                return []
            an = expr.get_alias_names()
            ll = len(an)
            if ll == 0:
                # nothing to do because we have no variables (explicitly exclude this case here)
                pass
            elif expr.has_large_func:
                # already have them:
                # Expressions that require SASS_Range are fery few and are exhaustively covered in get_alias_domain. There are
                # no overlaps left.
                pass
            elif expr.__hash__() in ctt:
                # This 'elif' is an optimization. Since a small number of expressions appear thousands of times each, we can just
                # create a bunch of specialized methods for them. The principle is the same as SASS_Expr_Domain_Range. One example
                # is (((Ra)==`Register@RZ)||((Ra)<=(%MAX_REG_COUNT-1)))
                d:dict
                print("...run {0} domains tasks".format(len(domains)))
                res = []
                for ind,d in enumerate(domains):
                    res.extend(SASS_Expr_Domain_Calc.reduce_common_domain_task(ind, d, sass, expr, an, ctt, orig_dom_keys, log_path, class_name))
                    
                # If we don't have at least one valid domain (where each variable has at leas one value), we want to @#?#@%!?
                # => Ok, so, we may have instructions that really are in fact impossible. Need to log them somewhere...
                if not res:
                    SASS_Expr_Domain_Calc.create_non_sat_log(log_path, expr, sass, class_name, domains, d)
                    return []
                # check if we have alias duality and if so, intersect the dual sets
                res = SASS_Expr_Domain_Calc.merge_same(res, sass, class_name)
                n_max_mem = psutil.virtual_memory().used
                if max_mem < n_max_mem: max_mem = n_max_mem
                # Reassign..
                domains = res
            elif ll == 1:
                print("1 var...", flush=True)
                # This 'elif' is an optimization since the vast majority of all expressions only have 1 variable.
                # The only thing necessary, is to concatenate all results to a set and replace the original set for the alias.
                # We can't even get multiple resulting domain possibilities out of this.
                # This can never be an extension of the existing domain possibilities. It is not even a reassignment which makes our
                # inner self happy
                for d in domains:
                    alias = an[0]
                    vals = d[alias]
                    rr = set()
                    for v in vals:
                        r = expr({alias:v})
                        if r: rr.add(v)
                    if not rr:
                        SASS_Expr_Domain_Calc.create_non_sat_log(log_path, expr, sass, class_name, domains, d)
                        return []
                    d[alias] = rr

                # check if we have alias duality and if so, intersect the dual sets
                domains = SASS_Expr_Domain_Calc.merge_same(domains, sass, class_name)
                n_max_mem = psutil.virtual_memory().used
                if max_mem < n_max_mem: max_mem = n_max_mem
            else:
                print("Fallback...", flush=True)
                print(expr.pattern)
                # This is the generalized fallback for all remaining expressions. We have to get each domain 'd' in 'domains' and
                # construct all possible inputs to the current expression using itt.product. Luckily, we likely don't need all aliases
                # in the expression, which makes the testing space usually smaller than 1024.

                # fallback for all other stuff
                new_sets = []
                print("...run {0} domains tasks".format(len(domains)))
                for ind,d in enumerate(domains):
                    new_sets.extend(SASS_Expr_Domain_Calc.reduce_fallback_domain_task(d, expr, sass, orig_dom_keys, log_path, class_name))
                sp.GLOBAL__USED_RAM_SAMPLES.append(max_mem)
                
                # We don't expect that there will be zero ways to fit the instruction class.
                if not new_sets:
                    SASS_Expr_Domain_Calc.create_non_sat_log(log_path, expr, sass, class_name, domains, d)
                    return []
                # each fully updated domain must contain all variables
                if new_sets and not all(i.keys() == orig_dom_keys for i in new_sets):
                    raise Exception(sp.CONST__ERROR_UNEXPECTED)

                # check if we have alias duality and if so, intersect the dual sets
                new_sets = SASS_Expr_Domain_Calc.merge_same(new_sets, sass, class_name)
                # each domain has been updated. Reassign.
                domains = new_sets
        return domains

    @staticmethod
    def collect_domains_f(args):
        n, count, sass, class_name, override, test, stop_on_exception, skip_tested = args
        SASS_Expr_Domain_Calc.collect_domains_str(n, count, sass, class_name, override, test, stop_on_exception, skip_tested)

    @staticmethod
    def collect_domains_str(n:int, count:int, sass:SM_SASS, class_name:str, override:bool, test:bool, stop_on_exception:bool, skip_tested:bool):
        location = os.path.dirname(os.path.realpath(__file__)) + "/sm_expr_vals"
        instr_p = location + "/" + sass.sm.details.SM_XX + "." + class_name + ".pickle"
        failed_path = location + "/" + sass.sm.details.SM_XX + ".xx.failed." + class_name + ".log"
        not_satisfiable_path = location + "/" + sass.sm.details.SM_XX + ".xx.non_sat." + class_name + ".log"
        not_satisfiable_ok_path = location + "/" + sass.sm.details.SM_XX + ".ok.non_sat." + class_name + ".log"

        if not override:
            if os.path.exists(location) and os.path.exists(instr_p):
                print("{0}/{1} | Load instr {2} from {3}".format(str(n).rjust(len(str(count))), count, class_name, instr_p), flush=True)
                with open(instr_p, 'rb') as f:
                    domains = pickle.load(f)
                return domains
        
        # if os.path.exists(not_satisfiable_ok_path):
        #     print("{0}/{1} | Not satisfiable: instr {2} from {3}".format(str(n).rjust(len(str(count))), count, class_name, instr_p), flush=True)
        #     return []

        print("{0}/{1} | Collect instr {2}...".format(str(n).rjust(len(str(count))), count, class_name).ljust(40), flush=True)

        class_:SASS_Class = sass.sm.get_from_all_classes(class_name)
        tt_format:TT_Instruction = class_.FORMAT
        expressions = [i['expr'] for i in class_.CONDITIONS]
        expr:SASS_Expr
        for expr in expressions: expr.finalize(tt_format.eval)

        # Two types of expressions go last:
        #  DEFINED(...) and !DEFINED(...)
        better_sorting = [
            (len(i[1].get_alias_names()), i[1]) for i in
            sorted([(
                100 if i.startswith_defined() else 50 if i.startswith_not_defined() else len(i.get_alias_names()),
                i) for i in expressions],
                key=lambda x: x[0]
            )]

        s0 = time.time()
        # the large function expressions get their finished set already at this stage
        domains = SASS_Expr_Domain_Calc.get_alias_domains(n, count, class_name, sass, [i[1] for i in better_sorting], not_satisfiable_path, failed_path, stop_on_exception=stop_on_exception, skip_tested=skip_tested)
        # this is a new thing: if we generate the small domains, we have to filter out some values...
        domains = SASS_Expr_Domain_Limits.filter_domains(sass, class_name, domains)
        sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)
        if not domains:
            return []

        one_vars = [i[1] for i in better_sorting if i[0] == 1]
        remaining = [i[1] for i in better_sorting if i[0] > 1]
        # first reduce using all the one var expressions
        s1 = time.time()
        # The large function expressions do nothing anymore (the if has a 'pass' in it) while
        # the other expressions 
        domains = SASS_Expr_Domain_Calc.reduce(class_name, sass, one_vars, domains, not_satisfiable_path)
        # this is a new thing: if we generate the small domains, we have to filter out some values...
        domains = SASS_Expr_Domain_Limits.filter_domains(sass, class_name, domains)
        sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)
        if not domains:
            return []

        if test:
            expr_count = len(one_vars)
            for expr_ind, expr in enumerate(one_vars):
                SASS_Expr_Domain_Calc.test_all_domains(n, count, failed_path, sass, class_name, expr_ind, expr_count, expr, domains, stop_on_exception=stop_on_exception, skip_tested=skip_tested)
        s2 = time.time()
        sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)
        # reduce as much as possible

        # do the remaining ones using the hopefully reduceed domains from the one variable expressions
        # without overlapping the domains
        # res_dom = []
        expr_count = len(remaining)
        for expr_ind, expr in enumerate(remaining):
            print("[{0}.{1}: reduce expr {2}/{3}]".format(sass.sm.details.SM_XX, class_name, expr_ind, expr_count), flush=True)
            domains = SASS_Expr_Domain_Calc.reduce(class_name, sass, [expr], domains, not_satisfiable_path)
            # this is a new thing: if we generate the small domains, we have to filter out some values...
            domains = SASS_Expr_Domain_Limits.filter_domains(sass, class_name, domains)
            if not domains:
                return []

            if test:
                SASS_Expr_Domain_Calc.test_all_domains(n, count, failed_path, sass, class_name, expr_ind, expr_count, expr, domains, stop_on_exception=stop_on_exception, skip_tested=skip_tested)
        s3 = time.time()
        sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)

        rr = 1000000000
        v0 = "T(Domain)={0}".format(int((s1-s0)*rr)/rr).ljust(24)
        v1 = "T(Collect(1))={0}".format(int((s2-s1)*rr)/rr).ljust(25)
        v2 = "T(Collect(N))={0}".format(int((s3-s2)*rr)/rr).ljust(25)
        print(v0, v1, v2, flush=True)

        if override or not os.path.exists(instr_p):
            if not os.path.exists(location):
                os.mkdir(location)

            with open(instr_p, 'wb') as f: pickle.dump(domains, f, pickle.HIGHEST_PROTOCOL)

        return domains

