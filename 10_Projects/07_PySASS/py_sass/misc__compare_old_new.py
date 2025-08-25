import os
import pickle
import typing
import itertools as itt
from . import _config as sp
from . import _sass_bits
import py_sass_ext
from .sm_sass import SM_SASS

"""
This script can be used to compare two SASS_Enc_Dom. It is not meant to just run or to be finished at some point.
"""

class TestOldNew:
    @staticmethod
    def load(classes_:dict, instr_p:str, not_satisfiable_ok_path:str, s:int):
        msg = "SM_{0}: Load all old class CONDITIONS domains...".format(s)
        print('|' + msg + (100-len(msg)-2)*' ' + '|')
        class_conditions_domains = dict()
        nok_classes = []
        for c in classes_.keys():
            p1 = os.path.exists(instr_p.format(s, c))
            p2 = os.path.exists(not_satisfiable_ok_path.format(s,c))
            if p1:
                with open(instr_p.format(s, c), 'rb') as f:
                    class_conditions_domains[c] =  pickle.load(f)
            elif p2:
                nok_classes.append(c)
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        print('ok')
        return class_conditions_domains
    
    @staticmethod
    def compare_instr_class(sass:SM_SASS, instr_class:typing.List[str], o_classes:dict, n_classes:dict):
        for ic in instr_class:
            oo = o_classes[ic]
            nn = n_classes[ic]
            
            if ic == 'Const1_IMAD':
                pass
            for ind,(o,n) in enumerate(zip(oo, nn)):
                for k in o.keys():
                    if isinstance(n[k], py_sass_ext.SASS_Range):
                        nlenl = [int(i) for i in str(n[k])[1:(str(n[k])[1:].find(']')+1)].split(',')]
                        nlen = nlenl[1] - nlenl[0]
                        if(nlen != len(o[k])):
                            raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    elif len(o[k]) != len(n[k]):
                        if k == 'constBank':
                            if len(o[k]) == 17 and len(n[k]) == 18:
                                pass
                            else:
                                raise Exception(sp.CONST__ERROR_UNEXPECTED)
                        else:
                            raise Exception(sp.CONST__ERROR_UNEXPECTED)
            
            # if len(oo) != len(nn):
            #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # pass

    @staticmethod
    def test():
        script_loc = "/".join(os.path.dirname(os.path.realpath(__file__)).split('/'))
        old_loc = script_loc + '/test/sm_50.all_expr_vals.old/'
        new_loc = script_loc + '/test/sm_50.all_expr_vals/'
        
        instr_p_old = old_loc + "sm_{0}.{1}.pickle"
        instr_p_new = new_loc + "sm_{0}.{1}.pickle"
        not_satisfiable_ok_path_old = old_loc + "sm_{0}.ok.non_sat.{1}.log"
        not_satisfiable_ok_path_new = new_loc + "sm_{0}.ok.non_sat.{1}.log"

        s = 50
        sass = SM_SASS(s)
        classes_ = sass.__sm.classes_dict

        ccdo = TestOldNew.load(classes_, instr_p_old, not_satisfiable_ok_path_old, s)
        ccdn = TestOldNew.load(classes_, instr_p_new, not_satisfiable_ok_path_new, s)

        o_classes = sorted(list(ccdo.keys()))
        n_classes = sorted(list(ccdn.keys()))
        if(o_classes != n_classes): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        TestOldNew.compare_instr_class(sass, n_classes, ccdo, ccdn)

if __name__ != '__main__':
    exit(0)

TestOldNew.test()