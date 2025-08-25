import typing
import datetime
import time
import psutil
import operator as op
from py_sass import SM_SASS
import _config as sp
from _sass_expression_domain_common import SASS_Expr_Domain_Common
from _sass_expression_domain_range import SASS_Expr_Domain_Range

"""
This script is used in sass_gen_all.py. It produces the expr_stats...txt files too.
"""

class SASS_Expression_Domain_Parse:
    HEAD = """
from . import _config as sp
from ._sass_expression_ops import *
from .sm_sass import SM_SASS

"""
    EXPR_TYPE = "__EXPR_TYPE_{nr}"
    EXPR_F = "__expr_type_{nr}"
    TEMPLATE = """    # {expr}
    # {class_ex} | {sm1} to {sm2}
    # old_pattern: {old_pattern}
    {expr_type} = {pattern}.__hash__()
    @staticmethod
    def {expr_f}(sass:SM_SASS, expr:list, alias_nt:list, domain_vals:dict):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

"""
    LAST = """    __EXPR_TYPES = [
        {content}
    ]

    @staticmethod
    def expr_types() -> dict: return SASS_Expr_Domain_Common.__EXPR_TYPES
"""

    TEST_SASS = "sass_{s_nr} = None"

    TEST_TEMPLATE = """# {expr}
if not sass_{s_nr}: sass_{s_nr}=SM_SASS({s_nr})
SASS_Expr_Domain_Calc.collect_domains_str({nr}, {total}, sass_{s_nr}, '{class_ex}', override=True, test=True)
"""
    @staticmethod
    def gen(ge, ge_old_new, file_name, offset=True):
        with open(file_name,'w') as f:
            gev = sp.GLOBAL__EXPRESSIONS_VAR_COUNT
            gee = sp.GLOBAL__EXPRESSIONS_EXAMPLE
            gfs = sp.GLOBAL__EXPRESSIONS_FIRST_SM
            gls = sp.GLOBAL__EXPRESSIONS_LAST_SM
            gfi = sp.GLOBAL__EXPRESSIONS_FIRST_INSTR
            res = sorted([(i[1], i[0], c) for i,c in zip(ge.items(), ge_old_new.values())], key=op.itemgetter(0), reverse=True)
            
            f.write("################################################################################################################\n")
            f.write("# This file has been auto-generated. Use _sass_expression_domain_parse.py to regenerate after adjustments\n")
            f.write("################################################################################################################\n")

            f.write(SASS_Expression_Domain_Parse.HEAD)
            f.write("class SASS_Expr_Domain_Common:\n")

            if offset: start_nr = len(SASS_Expr_Domain_Common.expr_types()) + 5
            else: start_nr = 1
            # found = set()
            # for ind,i in enumerate(res):
            #     if not i[1].__hash__() in found and i[1].__hash__() in SASS_Expr_Domain_Common.expr_types():
            #         start_nr += 1
            #         found.add(i[1].__hash__())

            final = []
            test_sass_load = []
            test_classes = []
            test_expr = []
            total = start_nr
            if offset:
                for ind,i in enumerate(res):
                    # if (((i[0] >= 100) or (gee[i[1]].find('TEXPARAMA') > 0 and gee[i[1]].find('->') > 0 and i[0] < 100)) and not i[1].__hash__() in SASS_Expr_Domain_Common.expr_types()) or (offset==False and i[1].__hash__() in SASS_Expr_Domain_Range.expr_types()):
                    if (((i[0] >= 100)) and (not i[1].__hash__() in SASS_Expr_Domain_Common.expr_types())) or (offset==False and (not i[1].__hash__() in SASS_Expr_Domain_Range.expr_types())):
                        total += 1
            
            counter = 0
            for ind,i in enumerate(res):
                # if (((i[0] >= 100) or (gee[i[1]].find('TEXPARAMA') > 0 and gee[i[1]].find('->') > 0 and i[0] < 100)) and not i[1].__hash__() in SASS_Expr_Domain_Common.expr_types()) or (offset==False and i[1].__hash__() in SASS_Expr_Domain_Range.expr_types()):
                if (((i[0] >= 100)) and (not i[1].__hash__() in SASS_Expr_Domain_Common.expr_types())) or (offset==False and (not i[1].__hash__() in SASS_Expr_Domain_Range.expr_types())):
                    nr = start_nr + counter
                    ii = i[1]
                    ii_old = i[2]
                    expr_type_s = SASS_Expression_Domain_Parse.EXPR_TYPE.format(nr=nr)
                    expr_f_s = SASS_Expression_Domain_Parse.EXPR_F.format(nr=nr)
                    s_nr=int(gfs[ii].split('_')[1])

                    final.append(expr_type_s + " : " + expr_f_s)
                    new_sass = SASS_Expression_Domain_Parse.TEST_SASS.format(s_nr=s_nr)
                    if not new_sass in test_sass_load: test_sass_load.append(new_sass)
                    test_classes.append(SASS_Expression_Domain_Parse.TEST_TEMPLATE.format(nr=(ind+1), total=total, s_nr=s_nr, expr=gee[ii], class_ex=gfi[ii]))
                    f.write(SASS_Expression_Domain_Parse.TEMPLATE.format(expr=gee[ii], class_ex=gfi[ii], sm1=gfs[ii], sm2=gls[ii], expr_type=expr_type_s, expr_f=expr_f_s, old_pattern=ii_old, pattern=ii))

                    counter += 1
            
            content = ",\n        ".join(final)
            f.write(SASS_Expression_Domain_Parse.LAST.format(content=content).replace('[','{').replace(']','}'))
            f.write("\n#######################################################\n")
            f.write("# test class calls for test script for each expression\n")
            f.write("#######################################################\n")
            f.write("\n# load all sasses\n")
            f.write("\n".join(test_sass_load))
            f.write("\n# run individual sass")
            f.write("\n".join(test_classes))
    @staticmethod
    def tab_str(item, tab_len = 8):
        return ' '*(tab_len - len(str(item)))
    @staticmethod
    def space_str(items, item, tab_len=8):
        res = ""
        for i in items: res += ' '*tab_len
        res += str(item)
        return res
    @staticmethod
    def line_str(item, tab_len=8):
        return "{0}{1}".format(item, SASS_Expression_Domain_Parse.tab_str(item, tab_len=tab_len))
    @staticmethod
    def stats(f:typing.TextIO, expr_dict:dict, expr_old_dict:dict):
        ge = expr_dict
        ge_old = expr_old_dict
        gev = sp.GLOBAL__EXPRESSIONS_VAR_COUNT
        gee = sp.GLOBAL__EXPRESSIONS_EXAMPLE
        gfs = sp.GLOBAL__EXPRESSIONS_FIRST_SM
        gls = sp.GLOBAL__EXPRESSIONS_LAST_SM
        gfi = sp.GLOBAL__EXPRESSIONS_FIRST_INSTR

        f.write("{0}{1}{2}{3}{4}\n".format(
            SASS_Expression_Domain_Parse.line_str('Num'),
            SASS_Expression_Domain_Parse.line_str('VarC'),
            SASS_Expression_Domain_Parse.line_str('f.Sm'),
            SASS_Expression_Domain_Parse.line_str('l.Sm'),
            'Pattern | Old Pattern | Example | First Class',
        ))

        res = sorted([(i[1], i[0], c) for i,c in zip(ge.items(),ge_old.values())], key=op.itemgetter(0), reverse=True)
        for i in res: f.write("{0}{1}{2}{3}{4}\n{5}\n{6}\n{7}\n".format(
            SASS_Expression_Domain_Parse.line_str(i[0]),
            SASS_Expression_Domain_Parse.line_str(gev[i[1]]),
            SASS_Expression_Domain_Parse.line_str(gfs[i[1]]),
            SASS_Expression_Domain_Parse.line_str(gls[i[1]]),
            i[1],
            '   ' + SASS_Expression_Domain_Parse.space_str([i[0], gev[i[1]], gfs[i[1]], gls[i[1]]], i[2]),
            '   ' + SASS_Expression_Domain_Parse.space_str([i[0], gev[i[1]], gfs[i[1]], gls[i[1]]], gee[i[1]]),
            '   ' + SASS_Expression_Domain_Parse.space_str([i[0], gev[i[1]], gfs[i[1]], gls[i[1]]], gfi[i[1]])
        ))
            
    @staticmethod
    def statistics(sms:list, reparse:bool, finalize:bool, opcode_gen:bool, lookup_gen:bool, web_crawl:bool):
        t_start = time.time()
        if not isinstance(sms, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(reparse, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(finalize, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(opcode_gen, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(lookup_gen, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(web_crawl, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)

        lf_expr = {}
        sp.GLOBAL__EXPRESSIONS = dict()
        sp.GLOBAL__EXPRESSIONS_OLD_NEW_COR = dict()
        sp.GLOBAL__LARGE_FUNC_EXPRESSIONS = dict()
        sp.GLOBAL__LARGE_FUNC_EXPRESSIONS_OLD_NEW_COR = dict()
        sp.GLOBAL__EXPRESSIONS_EXAMPLE = dict()
        sp.GLOBAL__EXPRESSIONS_VAR_COUNT = dict()
        sp.GLOBAL__EXPRESSIONS_FIRST_SM = dict()
        sp.GLOBAL__EXPRESSIONS_LAST_SM = dict()
        sp.GLOBAL__EXPRESSIONS_ALL_RANGE_INSTR = dict()
        
        # We just have to load every SM_SASS. The numbers for the statistics are defined
        # globaly and each loading will just add their stuff to them
        for sm in sms:
            sp.GLOBAL__CUR_SM = sm
            sass = SM_SASS(sm, reparse=reparse, finalize=finalize, opcode_gen=opcode_gen, lookup_gen=lookup_gen, web_crawl=web_crawl)
            sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)

        # Now we can just write the statistics to a file
        print("Write statistics to file...")
        with open('expr_stats.autogen.txt','w') as f: SASS_Expression_Domain_Parse.stats(f, sp.GLOBAL__EXPRESSIONS, sp.GLOBAL__EXPRESSIONS_OLD_NEW_COR)
        with open('expr_stats_lf.autogen.txt','w') as f: SASS_Expression_Domain_Parse.stats(f, sp.GLOBAL__LARGE_FUNC_EXPRESSIONS, sp.GLOBAL__LARGE_FUNC_EXPRESSIONS_OLD_NEW_COR)
        with open('expr_stats_lf_instr.autogen.txt','w') as f:
            for i in sp.GLOBAL__EXPRESSIONS_ALL_RANGE_INSTR.items():
                f.write(str(i[0]) + "\n   " + sp.GLOBAL__EXPRESSIONS_EXAMPLE[i[0]] + "\n   " + str(i[1]) + "\n")

        SASS_Expression_Domain_Parse.gen(sp.GLOBAL__EXPRESSIONS, sp.GLOBAL__EXPRESSIONS_OLD_NEW_COR, '__auto_generated_temp_f.py')
        SASS_Expression_Domain_Parse.gen(sp.GLOBAL__LARGE_FUNC_EXPRESSIONS, sp.GLOBAL__LARGE_FUNC_EXPRESSIONS_OLD_NEW_COR, '__auto_generated_temp_fl.py', offset=False)

        t_end = time.time()
        sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)
        print("Statistics finished at {0} after {1} seconds".format(datetime.datetime.now().strftime('%d.%m.%Y - %H:%M'), round(t_start - t_end, 2)))

if __name__ == '__main__':
    sms = [50, 52, 53, 60, 61, 62] #, 70, 72, 75, 80, 86, 90, 100, 120]
    reparse = False
    finalize = True
    opcode_gen = False
    lookup_gen = False
    web_crawl = False
    SASS_Expression_Domain_Parse.statistics(sms, reparse, finalize, opcode_gen, lookup_gen, web_crawl)