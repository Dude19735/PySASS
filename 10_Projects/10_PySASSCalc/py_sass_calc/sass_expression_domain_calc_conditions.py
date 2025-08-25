import time
import sys
import zipfile
import os
import datetime
import psutil
from py_sass import SM_SASS
import _config as sp
from _sass_expression_domain_calc import SASS_Expr_Domain_Calc

################################################################################################################
# This file can be used to generate the domains for one SM
# ========================================================
# Projected calculation times
# 50: 150s
# 52: 150s
# 53: 150s
# 60: 150s
# 61: 150s
# 62: 150s
# 70: 1400s
# 72: 1400s
# 75: 5500s
# 80: 5500s
# 86: 5500s
# 90: 5500s
################################################################################################################

class SASS_Expression_Domain_Calc_Conditions:
    @staticmethod
    def gen(sms:list, override:bool, test:bool, stop_on_exception:bool, skip_tested:bool, single_class:bool, single_class_name:str):
        t_start = time.time()
        if not isinstance(sms, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(override, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(test, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(stop_on_exception, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(skip_tested, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(single_class, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if single_class and not (isinstance(single_class_name, str) and len(single_class_name) > 0): raise Exception(sp.CONST__ERROR_ILLEGAL)

        print("######################################################")
        print("Generate domains for SM {0}".format(sms))
        print("######################################################")

        sp.GLOBAL__EXPRESSIONS_TESTED = set()

        if sp.CONFIG__GEN_LARGE:
            gen_type = ""
        elif sp.CONFIG__GEN_SMALL:
            gen_type = ".small"
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)

        for s in sms:
            t1 = time.time()
            sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)
            sass=SM_SASS(s)
            print("SASS {0} loaded".format(s))

            ind_count = len(sass.sm.all_class_names)
            for ind, class_name in enumerate(sass.sm.all_class_names):
                if single_class and not class_name == single_class_name: continue
                SASS_Expr_Domain_Calc.collect_domains_str(ind+1, ind_count, sass, class_name, override, test, stop_on_exception, skip_tested)

            # store all pickles inside a zip for safety
            if not single_class:
                print("Store SM {0} to zip...".format(s))
                pickle_location = os.path.dirname(os.path.realpath(__file__)) + "/sm_expr_vals/sm_{0}.{1}.pickle"
                ok_log_location = os.path.dirname(os.path.realpath(__file__)) + "/sm_expr_vals/sm_{0}.ok.non_sat.{1}.log"
                xx_log_location = os.path.dirname(os.path.realpath(__file__)) + "/sm_expr_vals/sm_{0}.xx.non_sat.{1}.log"
                archive_location = os.path.dirname(os.path.realpath(__file__)) + "/results/sm_{0}.all_expr_vals{1}.zip"
                xx_rename = os.path.dirname(os.path.realpath(__file__)) + "/sm_expr_vals/sm_{0}.xx.non_sat.rename"
                # if os.path.exists(xx_rename_location.format(s)):
                #     with open(xx_rename_location.format(s), 'r') as f:
                #         xx_rename = dict([i.strip().split('|') for i in f.readlines()[1:]])
                # else: xx_rename = dict()

                with zipfile.ZipFile(archive_location.format(s, gen_type), 'w') as zz:
                    for ind, class_name in enumerate(sass.sm.all_class_names):
                        # if os.path.exists(ok_log_location.format(s, class_name, gen_type)):
                        #     pp = ok_log_location.format(s, class_name, gen_type)
                        #     zz.write(pp, os.path.basename(pp))
                        if os.path.exists(xx_log_location.format(s, class_name)):
                            # NOTE: if this exception is thrown, there is something wrong!!
                            # Most likely some constraints are too tight, such that some CONDITIONS inside the instructions.txt
                            # fail, even though they shouldn't. 
                            # >>>>> DON'T IGNORE THIS EXCEPTION! <<<<<
                            if not class_name in sass.sm.skipped_classes: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                            pp = xx_log_location.format(s, class_name)
                            pp_head, pp_tail = os.path.split(pp)
                            # if not pp_tail in xx_rename:raise Exception(sp.CONST__ERROR_UNEXPECTED)
                            pp2 = os.path.join(pp_head, pp_tail.replace('xx', 'ok'))
                            os.rename(pp, pp2)
                            zz.write(pp2, os.path.basename(pp2))
                        else: 
                            if class_name in sass.sm.skipped_classes:
                                if not sass.sm.skipped_classes[class_name].deprecated_by_nvidia:
                                    raise Exception(sp.CONST__ERROR_UNEXPECTED)
                            else:
                                pp = pickle_location.format(s, class_name)
                                zz.write(pp, os.path.basename(pp))
            else:
                print("Store SM {0}? Single class => don't store to zip!".format(s))
            sp.GLOBAL__USED_RAM_SAMPLES.append(psutil.virtual_memory().used)
            print("SM {0} finished after {1}s".format(s, time.time() - t1))

        t_end = time.time()
        print("Domain calc gen finished at {0} after {1} seconds".format(datetime.datetime.now().strftime('%d.%m.%Y - %H:%M'), round(t_end - t_start, 2)))

# safeguard
if __name__ == '__main__':
    if len(sys.argv) == 2:
        sms = [int(sys.argv[1])]
    elif len(sys.argv) == 1:
        sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90]
    else:
        raise Exception(sp.CONST__ERROR_UNEXPECTED)
    if not all(s in [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90] for s in sms): raise Exception(sp.CONST__ERROR_UNEXPECTED)

    override=False
    test=True
    stop_on_exception=False
    skip_tested=True
    SASS_Expression_Domain_Calc_Conditions.gen(sms, override, test, stop_on_exception, skip_tested)

