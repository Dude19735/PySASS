from py_sass._sass_expression_ops import *
import _config as sp

class SASS_Expr_Domain_Utils:
    @staticmethod
    def test_overlap(ls:dict, rs:dict):
        overlap = set(ls).intersection(set(rs))
        if overlap:
            for o in overlap:
                res = ls[o].intersection(rs[o])
                ls[o] = res
                rs[o] = res
        return ls, rs

    @staticmethod
    def implication(left_side_T:list, left_side_F:list, right_side_T:list, right_side_F:list):
        if not isinstance(left_side_F, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(left_side_T, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(right_side_F, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(right_side_T, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        # There are quite some implications A->B that require calculating the left side and the right side
        # separatedly and then stitch together the results according to the truth table
        # A | B |A->B
        # ------------
        # T | T | T 
        # T | F | F 
        # F | T | T 
        # F | F | T
        # ¬A v B

        pp = []
        if right_side_T:
            # case T | T: take true left-side and add true right-side
            for i in left_side_T: 
                if any(not j for j in i.values()): continue
                for z in right_side_T:
                    if any(not j for j in z.values()): continue
                    i,z = SASS_Expr_Domain_Utils.test_overlap(i,z)
                    pp.append(i | z)
            # case F | T: take false left-side and add true right-side
            for i in left_side_F:
                if any(not j for j in i.values()): continue
                for z in right_side_T:
                    if any(not j for j in z.values()): continue
                    i,z = SASS_Expr_Domain_Utils.test_overlap(i,z)
                    pp.append(i | z)
        if right_side_F:
            # case F | F: take false left-side and false right-side
            for i in left_side_F:
                if any(not j for j in i.values()): continue
                for nz in right_side_F:
                    if any(not j for j in nz.values()): continue
                    i,nz = SASS_Expr_Domain_Utils.test_overlap(i,nz)
                    pp.append(i | nz)
        return pp
