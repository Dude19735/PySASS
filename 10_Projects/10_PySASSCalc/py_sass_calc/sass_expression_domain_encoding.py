import time
import sys
import os
import pickle
import zipfile
import datetime
import psutil
import itertools as itt
from py_sass import SASS_Expr
from py_sass import TT_Instruction
from py_sass import TT_Instruction, TT_Reg, TT_Func
from py_sass import TT_OpAtAbs, TT_OpAtInvert, TT_OpAtNegate, TT_OpAtNot, TT_OpAtSign
from py_sass import SM_SASS
from py_sass import SASS_Expr_Domain_Contract
from py_sass_ext import SASS_Range
from py_sass_ext import SASS_Bits
from py_sass_ext import SASS_Enc_Dom
import _config as sp
from _sass_expression_domain_calc import SASS_Expr_Domain_Calc
from _sass_expression_domain_limits import SASS_Expr_Domain_Limits

class SASS_Expr_Domain_Encoding:
    """
    This class contains a method to link the domains of the individual expressions of all CONDITIONS
    to the actual ENCODING stage for each instruction.

    Not all aliases are used in the CONDITIONS.
    """

    @staticmethod
    def check_tables(dom:dict, t_ind:dict, table:dict, t_all:list):
        t_ind_combs = list(itt.product(*[dom[k] for k in t_ind]))

        t_ind_inv = dict((v,k) for k,v in t_ind.items())
        t_args = []
        # get the indices of the original non-int args
        t_ind_inds = list(t_ind.values())
        for c_ind in range(0, len(t_ind_combs)):
            comb = t_ind_combs[c_ind]
            replace = [(i, int(comb[ci])) for ci,i in enumerate(t_ind_inds)]
            
            # first, make sure to copy...
            args = [x for x in t_all]
            # then replace the non-integer terms
            for rep in replace: args[rep[0]] = rep[1]
            t_args.append(args)

        # at this point all args are integererized
        # if not all(all(isinstance(i, int) for i in arg_line) for arg_line in t_args): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        # check which combinations have an entry in the table
        res = [sassb for sassb, arg in zip(t_ind_combs,t_args) if tuple(arg) in table]

        # add the alias name back using the inverted key map
        res_dicts = [dict((t_ind_inv[sbi], sb) for sbi,sb in zip(t_ind_inds, sassb)) for sassb in res]

        return res_dicts

    @staticmethod
    def collect_no_expr_domains(sass:SM_SASS, class_name:str, domains:list):
        print(" [{0}] Collect instruction class info...".format(class_name), end='')
        class_ = sass.sm.classes_dict[class_name]
        format_tt:TT_Instruction
        format_tt = class_.FORMAT

        # if we have alias duality, make sure that the variable sets are the same
        combs = list(itt.combinations(domains[0].keys(),2))
        pairs = [c for c in combs if format_tt.eval[c[0]] == format_tt.eval[c[1]]]
        for p in pairs:
            for d in domains:
                # intersect the domains for the vars that point to the same operand
                if not d[p[0]] == d[p[1]]: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        # Get all aliases that are actually used in the encoding step.
        # This step already filters out things like Op_Int and Op_Register. They already contain exact values and don't
        # require sampling of any kind.
        # If we have an 'X' inside the current class_.ENCODING, we don't use that one because it's technically a constant
        # encoding value that was replaced with a non-constant one for a cache bit.
        # For example: in SM86, the instruction 'bar__RED_II_optionalCount_II' doesn't have a WR cache bits entry. The ENCODING stage
        # contains 'BITS_3_112_110_dst_wr_sb=7;'. The parser 'finalize' step adds a '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$' in the FORMAT
        # and replaces 'BITS_3_112_110_dst_wr_sb=7;' with 'BITS_3_112_110_dst_wr_sb=VarLatOperandEnc(dst_wr_sb);'. This is to make all the
        # cache bits available and modifiable for all instructions. For the encodings calculations, we don't need this one though. We want to
        # only create the 'pure' instructions, without using modifications. This is because we don't want the instruction fuzzer to create instructions
        # that have modified encodings. Modified encodings should only be supported if done manually. But then, it should not add a giant mess to the code.
        enc_expr = [i['alias'] for i in class_.ENCODING if not 'X' in i]

        # All names of all ENCODINGs variables:
        # NOTE that get_alias_names() will return what is actually "written" in the file. At the end of the day
        # this is what we want.
        all_enc_vars = sorted(list(itt.chain.from_iterable([j for j in [e.get_alias_names() for e in enc_expr] if j])))
        all_enc_vars_s = set(all_enc_vars)
        dual_enc_vars = [(str(format_tt.eval[a].value), str(format_tt.eval[a].alias)) for a in all_enc_vars]

        enc_domains = [dict((r if r in all_enc_vars_s else a, d[r] if r in d else d[a] if a in d else dict()) for r,a in dual_enc_vars) for d in domains]
        enc_domains_vars = set(enc_domains[0].keys())

        # From all aliases in the ENCODINGS stage that still may need some filtering, 
        # get names and expressions that are included in an encoding expression using a table:
        t_names = []
        t_expr = []
        i:SASS_Expr
        for i in enc_expr:
            if i.startswith_table():
                t_names.append(i.get_table_args())
                t_expr.append(i)
        
        # get all other names
        # NOTE: due to a semi-oversight, x.alias is sometimes a string (for TT_Func) and sometimes a TT_Alias (for TT_Reg).
        # Thus, keep the str(..) operator. Changing x.alias to be a TT_Alias in TT_Func as well is not an easy task.
        # Also, it's not necessary, since alias is really only used to access the alias name from various locations and
        # needs to be in TT_Func, TT_Reg and all TT_AtOps since TT_Param is not the entry in the list anymore.
        # NOTE: It can be that t_names contains some name duality (particularly for extensions). Search
        # this file for CASInteger to find a documented example in some other comments.
        # If we get into this kind of trouble, we have to replace the name of this variable with the correct one. In
        # the example with CASInteger it is replacing 'size' with 'CASInteger'.
        # NOTE that digging the names out in this complicated way is necessary because table accesses in the ENCODINGS
        # stage can contain Op_Int and Op_Register too.
        t_names_str = [[n['s'] if n['s'] in enc_domains_vars else n['a'] for n in t['tt']] for t in t_names]
        # this one is a list of lists, where variables with a domain will be TT_Func and fixed values (like 0 or 1 or 50)
        # are their respective value.
        # Transform to alias string if not fixed value to prevent expensive copy operation for TT_TermXX
        t_names_all = [[str(p.alias) if not isinstance(p,int) else p for p in i['all']] for i in t_names]

        # It can be that t_names_str contains the wrong name for a variable (particularly for extensions). Search
        # this file for CASInteger to find a documented example in some other comments.
        # If we get into this kind of trouble, we have to replace the name of this variable with the correct one. In
        # the example with CASInteger it is replacing 'size' with 'CASInteger'.
        # NOTE that digging the names out in this complicated way is necessary because table accesses in the ENCODINGS
        # stage can contain Op_Int and Op_Register too.
        # t_names_str = [[n if n in all_enc_vars else str(format_tt.eval[n].value) for n in tns] for tns in t_names_str]

        # flattened names that are used in a table access somewhere
        t_test_names = list(itt.chain.from_iterable(t_names_str))

        # Get the names of the ENCODINGS stage that are not used in a table somewhere:
        e_names = [j for j in enc_domains_vars if not j in t_test_names]
        # Get names that have a domain:
        dom_names = [k for k,v in enc_domains[0].items() if v]
        # Get the names of the ENCODINGS stage that don't yet have a domain from the domain-reduce step
        # and are not just integers:
        enc_names = [k for k,v in enc_domains[0].items() if not v]
        
        print('ok')

        # We may have registers in here too... we reeeally have to limit their domains here too...
        # Imagine: 255*255 = 65025 but 32*32=1024 (which is already enough)
        to_limit = SASS_Expr_Domain_Limits.to_limit(sass.sm.details)
        # add domains for all variables that don't have them yet
        res_dom = []
        print(" [{0}] Get domains for all ENCODINGS variables that don't already have them from CONDITIONS...".format(class_name),end='')
        for dom in enc_domains:
            for k in enc_names:
                if not dom[k]:
                    v = format_tt.eval[k] 
                    if isinstance(v, TT_Reg):
                        r:TT_Reg = v
                        dom[k] = r.get_domain(to_limit)
                    elif isinstance(v, TT_OpAtAbs|TT_OpAtInvert|TT_OpAtNegate|TT_OpAtNot|TT_OpAtSign):
                        dom[k] = v.get_domain({})
                    elif isinstance(v, TT_Func):
                        dom[k] = v.get_domain({})
                    else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # NOTE: DON'T do this: enc_domains may contain the same aliases as domains but just translated to the register
        # name instead of the alias name...!! Mixing these two here can potentially break everything!!!
        # >> The original, incomplete domains are also here: the new stuff should be the same length as the old stuff
        # >> if not (len(enc_domains) == len(domains)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # >> for d,e in zip(domains, enc_domains): d |= e
        enc_domains = SASS_Expr_Domain_Limits.filter_domains(sass, class_name, enc_domains)

        # In the ENCODINGS stage, we may have table calls. Unfortunately for us
        # these are generally not covered in the CONDITIONS expressions XD
        # and we have to add one additional check for them here:

        # Check if we ever have a situation where an alias is used to access
        # a table twice. t_names_str looks for example like this:
        #   t_names_str = [['dst_wr_sb'], ['src_rel_sb']]
        # where each sublist contains the names of the arguments for one table access => product of all names constructs
        # all pairs. Then, there should be no pair where both entries are the same => no variable is used in two distinct table accesses.
        if any(len(i) != len(set(i)) for i in itt.product(*t_names_str)): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        print('ok')
        
        # Since for some of the variables, we may already have multiple domain candidates in the domains list
        # we have to iterate domains here too, even if we don't need it for all tables and we also have to
        # add the result to the correct domain at the end.
        res_dom = []
        msg = "[{0}] Translate and validate all CONDITIONS domains to ENCODING... {1}".format(class_name, len(enc_domains))
        print('|' + msg + (100-len(msg)-2)*' ' + '|')
        eq_mult = int(100 / 50)
        progr_v = (len(enc_domains) / 50)
        progr_n = 0
        # NOTE: enc_domains has a domain for every variable. We have to make sure though, that any table calls based
        # on it also exist
        
        # Some time measurement...
        t1=0
        t2=0
        t3=0
        s_overall = 5*[0]
        lt = time.time()
        for dom_ind, dom in enumerate(enc_domains):
            # preserve the indices of each arg that has a domain into the original list of table arguments
            # NOTE: use t_names_str here for the key because that is what is actually written in the ENCODINGS for the instruction class.
            # For example: [[{'dst_wr_sb': 0}], [{'src_rel_sb': 0}]] where 0 is the arg index for the table arguments.
            t10 = time.time()
            t_doms_ind = [dict((ns, n['i']) for n,ns in zip(t['tt'],ts)) for t,ts in zip(t_names,t_names_str)]
            
            new_table_doms = []
            for expr,tn,t_ind,t_all in zip(t_expr,t_names,t_doms_ind,t_names_all):
                t = [time.time()]
                # If we have a table with no vars to domain, for example like with "DestPred(`Predicate@PT)":
                # In those cases, all entries in t_all will be actual integers.
                if all(isinstance(tt, int) for tt in t_all): continue

                # there are no huge tables, thus we never need a SASS_Range for these variables
                if any(isinstance(dom[k], SASS_Range) for k in t_ind): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                # all combinations of the domains of t_ind in the same sequence as the keys show up in t_ind
                # t_dom =  [dom[k] for k in t_ind]
                table = expr.get_first_op().table
                t.append(time.time())
                # Turns out, this is much slower... 
                # res_dicts2 = CPP_Faster.check_tables(dom, t_ind, table, t_all)
                t.append(time.time())
                res_dicts = SASS_Expr_Domain_Encoding.check_tables(dom, t_ind, table, t_all)
                t.append(time.time())

                # Some test to test Python and cpp versions, not needed anymore, but keep for reference
                # if not all(i==j for i,j in zip(res_dicts, res_dicts2)): raise Exception("Unexpected")
                
                # group everything as in the domain calculation
                d_grouped = SASS_Expr_Domain_Contract.group(res_dicts)
                t.append(time.time())

                # update the new domains with all old domains
                # NOTE: there is no overlap
                new_t_doms = []
                nd:dict
                for nd in d_grouped:
                    od:dict
                    for od in new_table_doms:
                        # make sure that we reeeeally don't have any overlap between old domains keys and new domains keys
                        if any(ko in nd for ko in od): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                        nd.update(od)
                    new_t_doms.append(nd)
                # swap old domains with updated ones
                new_table_doms = new_t_doms
                t.append(time.time())

                s_overall = [si+(ff-ss) for si,ff,ss in zip(s_overall, t[1:], t[:-1])]
            t11 = time.time()
            t1 += t11-t10

            if t_expr:
                # If we have table accesses, make sure we don't get any empty stuff
                if not new_table_doms: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                # make sure that every new domain is non empty
                if not all(all(len(i)!=0 for i in ntd.values()) for ntd in new_table_doms): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                # Add all old domain values without the ones we just updated to the ones we just updated.
                # Cardinalities go like this: always 1 old domain but possible N new ones => iterate the new ones and update with the old one
                old_dom = dict((k,v) for k,v in dom.items() if not k in new_table_doms[0])
                ntd:dict
                for ntd in new_table_doms: ntd.update(old_dom)

                # some less stringent test
                if any(any(len(v)==0 for k,v in ad.items()) for ad in new_table_doms): raise Exception(sp.CONST__ERROR_UNEXPECTED)

                # Extend the updated domains with the new sets
                res_dom.extend(new_table_doms)
            else: 
                # otherwise we did nothing
                res_dom.append(dom)
            t12 = time.time()
            t2 += t12-t11
            # Make really sure that we don't have any empty domains
            # NOTE: this test takes a lot of time => use sparingly
            # if any(any(len(v)==0 for k,v in ad.items()) for ad in res_dom): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            t13 = time.time()
            t3 += t13-t12
            progr_n = SASS_Expr_Domain_Encoding.__pb(dom_ind, progr_v, progr_n, eq_mult)
        print('ok')
        print(round(time.time()-lt, 4), round(t1+t2+t3, 4), round(t1, 4), round(t2, 4), round(t3, 4), s_overall, sum(s_overall))

        print(" [{0}] Final checks...".format(class_name), end='')
        # Make sure we weed out doubles again.
        # There really should not be same domains here, though.
        res_dom = SASS_Expr_Domain_Calc.merge_same(res_dom, sass, class_name)

        # At this point, res_dom should contain all that is required for the ENCODINGS stage. If not, throw an exception.
        # Check this by first getting all variable names just from the ENCODINGS stage expressions and all variable names
        # from the actual table access part above, then sort them alphabetically, then compare each one individually:

        # All the ones we get from the table-access check:
        new_enc_vars = sorted(list(res_dom[0].keys()))
        # Very strict bar to pass...
        if new_enc_vars != all_enc_vars: 
            raise Exception(sp.CONST__ERROR_UNEXPECTED)

        print('ok')

        msg ="[{0}] Filter not fitting alias values...".format(class_name)
        # Now, for the single aliases (no table accesses and no functions), we may still get some values
        # that could be too large. One typical example is for the instruction class 'Const_DSET' on
        # SM 50 where we have one register 'Test' with alias 'fcomp' that is written into a 4 bit location
        # FComp. The register 'Test' has 31 values which needs 5 bits. But if we select only values smaller
        # than 16, we only need 4 bits.
        # Filter all of these and if necessary, adapt their domains. NOTE that we don't modify SASS_Range here
        # anymore.
        # Get all the encodings that contain only one single alias:
        a_enc = [(ind, str(i['alias'].get_first_op().value().alias), len(i['code_ind'][0])) for ind,i in enumerate(class_.ENCODING) if i['alias'].startswith_alias()]
        # Because of the names duality, if we don't find one alias in the domains we have so far (for example
        # if we have an Extension that is represented by its register name instead of its alias), we have
        # to check this and if necessary pick the relative other name.
        a_enc_doms = [(i[1] if i[1] in res_dom[0] else format_tt.eval[i[1]].value, i[2]) for i in a_enc]
        empty_encs = set()

        print('|' + msg + (100-len(msg)-2)*' ' + '|')
        eq_mult = int(100 / 25)
        progr_v = (len(a_enc_doms) / 25)
        progr_n = 0
        for d_ind, (a, ll) in enumerate(a_enc_doms):
            # in an earlier iteration for this domain possibility we emptied all of it => skip
            if d_ind in empty_encs: continue
            max_val = 2**ll-1
            doms:dict
            for doms in res_dom:
                dom = doms[a]
                # If we get a SASS_Range, skip it. If it doesn't fit
                # there may be a SCALE later on and we have things like the assembling strategy
                # that is supposed to deal with very large ranges.
                if isinstance(dom, SASS_Range): continue
                if not isinstance(dom, set): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                d:SASS_Bits
                # NOTE that we don't need to reduce the number of bits. In the encoding stage,
                # we explicitly allow that SASS_Bits may be larger than their encoding target location
                # provided that the overflow bits are all 0.
                if any(isinstance(d, tuple) for d in dom):
                    print(a, dom)
                    raise Exception(sp.CONST__ERROR_UNEXPECTED)
                new_dom = [d for d in dom if int(d) <= max_val]
                # if we have some values left, add the domain back, otherwise, add the index
                # to a list so that we may remove it later
                if new_dom: doms[a] = set(new_dom)
                else: empty_encs.add(d_ind)
            progr_n = SASS_Expr_Domain_Encoding.__pb(d_ind, progr_v, progr_n, eq_mult)
        print('==ok\n')
        
        # If we have empty domain possibilities, remove them from the list:
        if empty_encs:
            res_dom = [rd for ind,rd in enumerate(res_dom) if not ind in empty_encs]

        # If we have no possibilities, things suck...
        if not res_dom: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # If we pass, things are probably fiiiiine ^^
        return res_dom
    
    @staticmethod
    def __pb(ind:int, progr_v:int, progr_n:int, eq_mult:int):
        pn = ind // progr_v
        if pn > progr_n: 
            while progr_n < pn:
                print(eq_mult*'=',end='', flush=True)
                progr_n += 1
        return progr_n
    
    @staticmethod
    def consolidate(sm:list, load_enc:bool, enc_dom_test:bool, enc_dom_tester:str, single_class:bool, single_class_name:str):
        t_start = time.time()
        if not isinstance(sm, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(load_enc, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_dom_test, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(single_class, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if single_class and not (isinstance(single_class_name, str) and len(single_class_name) > 0): raise Exception(sp.CONST__ERROR_ILLEGAL)

        print("######################################################")
        print("consolidate domains for SM {0}".format(sm))
        print("######################################################")

        location = os.path.dirname(os.path.realpath(__file__)) + "/sm_expr_vals"
        # Check if we actually have a folder with the domain pickles
        print("[ALL] Check existence for all classes...", end='')
        if not os.path.exists(location): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        print("ok")

        max_mem = psutil.virtual_memory().used

        if sp.CONFIG__GEN_LARGE:
            gen_type = ""
        elif sp.CONFIG__GEN_SMALL:
            gen_type = ".small"
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)

        for s in sm:
            instr_p = location + "/sm_{0}.{1}.pickle"
            not_satisfiable_ok_path = location + "/sm_{0}.ok.non_sat.{1}.log"

            results_path = os.path.dirname(os.path.realpath(__file__)) + "/results"
            enc_dom_path = results_path + "/sm_{0}_domains{1}.lz4"

            # Check if we either have a pickle or a log that sais an instruction is not
            # satisfiable for every class in the system
            sass = SM_SASS(s)
            class_names = sass.sm.classes_dict.keys()
            msg = "SM_{0}: Check CONDITIONS domains availability for all classes...".format(s)
            print('|' + msg + (100-len(msg)-2)*' ' + '|')
            eq_mult = int(100 / 25)
            progr_v = (len(class_names) / 25)
            progr_n = 0
            
            archive_location = results_path
            archive = archive_location + "sm_{0}.all_expr_vals{1}.zip"
            for ind,c in enumerate(class_names):
                if single_class and not c == single_class_name: continue
                p1 = os.path.exists(instr_p.format(s, c))
                p2 = os.path.exists(not_satisfiable_ok_path.format(s,c))
                if not (p1 or p2):
                    # Check if we have a zip file. If not, we have to sample the CONDITIONS domains first
                    if not os.path.exists(archive.format(s, gen_type)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    # Otherwise, unzip it
                    with zipfile.ZipFile(archive.format(s, gen_type), 'r') as zz:
                        zz.extractall(archive_location)
                progr_n = SASS_Expr_Domain_Encoding.__pb(ind, progr_v, progr_n, eq_mult)
            print('==ok')

            n_max_mem = psutil.virtual_memory().used
            if max_mem < n_max_mem: max_mem = n_max_mem

            msg = "SM_{0}: Load all class CONDITIONS domains...".format(s)
            print('|' + msg + (100-len(msg)-2)*' ' + '|')
            eq_mult = int(100 / 25)
            progr_v = (len(class_names) / 25)
            progr_n = 0
            class_conditions_domains = dict()
            nok_classes = []
            for c in class_names:
                if single_class and not c == single_class_name: continue
                p1 = os.path.exists(instr_p.format(s, c))
                p2 = os.path.exists(not_satisfiable_ok_path.format(s,c))
                if p1:
                    with open(instr_p.format(s, c), 'rb') as f:
                        class_conditions_domains[c] =  pickle.load(f)
                elif p2:
                    nok_classes.append(c)
                else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                progr_n = SASS_Expr_Domain_Encoding.__pb(ind, progr_v, progr_n, eq_mult)
            print('==ok')
            
            n_max_mem = psutil.virtual_memory().used
            if max_mem < n_max_mem: max_mem = n_max_mem

            if sp.CONFIG__GEN_LARGE:
                gen_type = ""
            elif sp.CONFIG__GEN_SMALL:
                gen_type = ".small"
            else: raise Exception(sp.CONST__ERROR_ILLEGAL)

            if load_enc and os.path.exists(enc_dom_path.format(s, gen_type)):
                enc_dom = SASS_Enc_Dom(enc_dom_path.format(s, gen_type), show_progress=True)
            else:
                print("|SM_{0}: Translate and validate CONDITIONS domains to ENCODING domains...".format(s))

                enc_dom = SASS_Enc_Dom.create_new_empty()
                max_ind = str(len(class_conditions_domains.items())).rjust(4)
                for ind,(c,c_domains) in enumerate(class_conditions_domains.items()):
                    print("[{0}/{1}] Instruction class [{2}] with #(domains) = {3}:".format(str(ind+1).rjust(4), max_ind, c, len(c_domains)))
                    domains = SASS_Expr_Domain_Encoding.collect_no_expr_domains(sass, c, c_domains)

                    instr_class_ind:int = enc_dom.add_instr_class(c)
                    for dom in domains:
                        req_size = len(dom)
                        instr_class_enc_ind:int = enc_dom.add_instr_class_enc(instr_class_ind)
                        for enc_name, enc_values in dom.items():
                            if isinstance(enc_values, set):
                                cur_size = enc_dom.add_instr_class_enc_set(instr_class_ind, instr_class_enc_ind, enc_name, enc_values)
                            elif isinstance(enc_values, SASS_Range):
                                cur_size = enc_dom.add_instr_class_enc_range(instr_class_ind, instr_class_enc_ind, enc_name, enc_values)
                        if not enc_dom.check_instr_class_enc_len(instr_class_ind, instr_class_enc_ind, req_size): raise Exception(sp.CONST__ERROR_ILLEGAL)

                    n_max_mem = psutil.virtual_memory().used
                    if max_mem < n_max_mem: max_mem = n_max_mem

                    # check if list is non-empty
                    if not len(domains) > 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    # check if all dicts in the list are non-empty
                    if not all(len(d) > 0 for d in domains): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    # check if all aliases have non-empty sets
                    if not all(all(len(v) > 0 for k,v in d.items()) for d in domains): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    
                    # Maybe this does something?
                    del domains

                    # At this point we loaded and translated all domains from all CONDITIONS to domains for the
                    # ENCODING stage. NOTE that it is no longer always the case that all the aliases in the CONDITIONS
                    # domains are contained in the final domains too. For example in in SM 50 for the class "ALD",
                    # we have AIO and io that are the same and for some CONDITIONS AIO is used and io for others.
                    # In the ENCODING stage, only AIO is used, though. Thus, 'io' is no longer contained in the
                    # final domains (NOTE: ...so don't check for it)

                enc_dom.add_nok_instr_classes(nok_classes, clear_first=True)
                
                n_max_mem = psutil.virtual_memory().used
                if max_mem < n_max_mem: max_mem = n_max_mem

            if single_class and enc_dom_test and enc_dom_tester: print("|SM_{0}: ... single class => not testing enc_dom".format(s))
            elif enc_dom_test and enc_dom_tester:
                print("|SM_{0}: Test new enc_dom with {1}".format(s, enc_dom_tester))
                print("|SM_{0}: ... load {1}".format(s, enc_dom_tester))
                tester = SASS_Enc_Dom(enc_dom_tester, show_progress=True)
                print("|SM_{0}: ... compare to {1}".format(s, enc_dom_tester))
                res = enc_dom == tester
                if(not res): raise Exception("Unexpected")

            if not single_class:
                print("|SM_{0}: ... dump enc_dom to {1}".format(s, enc_dom_path.format(s, gen_type)))
                enc_dom.dump(enc_dom_path.format(s, gen_type))
            else: print("|SM_{0}: ... single class => not dumping enc_dom".format(s))
            print('ok')

            n_max_mem = psutil.virtual_memory().used
            if max_mem < n_max_mem: max_mem = n_max_mem

        sp.GLOBAL__USED_RAM_SAMPLES.append(max_mem)
        t_end = time.time()
        print("Consolidate finished at {0} after {1} seconds".format(datetime.datetime.now().strftime('%d.%m.%Y - %H:%M'), round(t_end - t_start, 2)))

# safeguard
if __name__ == '__main__':
    sp.GLOBAL__EXPRESSIONS_TESTED = set()
    if len(sys.argv) == 2:
        sm = int(sys.argv[1])
    else:
        sm = [90, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90]
    if not all(s in [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90] for s in sm): raise Exception(sp.CONST__ERROR_UNEXPECTED)

    SASS_Expr_Domain_Encoding.consolidate(sm)
