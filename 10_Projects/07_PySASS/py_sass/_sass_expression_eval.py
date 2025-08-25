"""
All evaluation things
"""

import typing
from . import _sass_expression_ops as oo
from . import _config as sp

class SASS_Expr_Eval:
    @staticmethod
    def SYAlgo(expr_opr:list):
        out_queue = []
        out_queue_str = []
        opr_stack = []
        for op in reversed(expr_opr):
            if any(isinstance(op, i) for i in oo.OP_OPERAND):
                out_queue.append(op)
                out_queue_str.append(str(op).strip())
            elif any(isinstance(op, i) for i in oo.OP_FUNCTION):
                opr_stack.append(op)
            elif any(isinstance(op, i) for i in oo.OP_OPERATOR):
                if opr_stack:
                    tt = opr_stack[-1]
                    while (not (isinstance(tt, oo.Op_RBrace) or isinstance(tt, oo.Op_If))) and (tt.P < op.P or tt.P==op.P and op.A=='R'): # type: ignore
                        out_queue.append(opr_stack.pop())
                        out_queue_str.append(str(out_queue[-1]).strip())
                        if not opr_stack: break
                        tt = opr_stack[-1]
                opr_stack.append(op)
            elif isinstance(op, list):
                sub_res, sub_str = SASS_Expr_Eval.SYAlgo(op)
                out_queue.append(sub_res)
                out_queue_str.extend([']', sub_str.strip(), '['])
            elif isinstance(op, oo.Op_Set):
                out_queue.append(op)
                out_queue_str.append(str(op))
            elif isinstance(op, oo.Op_RBrace):
                opr_stack.append(op)
            elif isinstance(op, oo.Op_LBrace):
                if not opr_stack: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                while opr_stack and not isinstance(opr_stack[-1], oo.Op_RBrace):
                    out_queue.append(opr_stack.pop())
                    out_queue_str.append(str(out_queue[-1]).strip())
                opr_stack.pop()
                if not opr_stack or not isinstance(opr_stack[-1], oo.Op_Function): continue
                out_queue.append(opr_stack.pop())
                out_queue_str.append(str(out_queue[-1]).strip())
            elif isinstance(op, oo.Op_Comma):
                if not opr_stack: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                if not out_queue: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                while opr_stack and not isinstance(opr_stack[-1], oo.Op_RBrace):
                    out_queue.append(opr_stack.pop())
                    out_queue_str.append(str(out_queue[-1]).strip())
                    if not opr_stack: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            elif isinstance(op, oo.Op_If):
                while opr_stack and not isinstance(opr_stack[-1], oo.Op_IfElse):
                    out_queue.append(opr_stack.pop())
                    out_queue_str.append(str(out_queue[-1]).strip())
                    if not opr_stack: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                if not opr_stack: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                opr_stack.pop()
                out_queue.append(op)
                out_queue_str.append(str(out_queue[-1]).strip())
            elif isinstance(op, oo.Op_IfElse):
                if not out_queue: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                while opr_stack and not isinstance(opr_stack[-1], oo.Op_RBrace):
                    out_queue.append(opr_stack.pop())
                    out_queue_str.append(str(out_queue[-1]).strip())
                out_queue.append(op)
                out_queue_str.append(str(out_queue[-1]).strip())
                opr_stack.append(op)
            else:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
        while opr_stack:
            tt = opr_stack.pop()
            if tt == oo.Op_LBrace or tt == oo.Op_RBrace: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            out_queue.append(tt)
            out_queue_str.append(str(tt).strip())

        res = list(reversed(out_queue))
        res_str = " ".join(reversed(out_queue_str))
        return res, res_str
    
    @staticmethod
    def isolate_ff_rec(ii:typing.Iterator, tt:oo.Op_Function):
        args = []
        arg = []
        op = next(ii, False)
        if not isinstance(op, oo.Op_LBrace): raise Exception(sp.CONST__ERROR_ILLEGAL)
        cc = 1
        while True:
            op = next(ii, False)
            if not op: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if isinstance(op, oo.Op_Function):
                arg.append(op)
                arg.extend(SASS_Expr_Eval.isolate_ff_rec(ii, op))
            elif isinstance(op, oo.Op_LBrace):
                cc += 1
                arg.append(op)
            elif isinstance(op, oo.Op_RBrace):
                cc -= 1
                if cc != 0:
                    arg.append(op)
                    continue
                elif arg:
                    args.append(arg)
                    if isinstance(tt, oo.Op_Reduce):
                        tt.set_reduce_op(args[0][0])
                        args = args[1:]
                    tt.set_arg_num(len(args))
                    break
                else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            elif isinstance(op, oo.Op_Comma):
                if not arg: raise Exception(sp.CONST__ERROR_ILLEGAL)
                args.append(arg)
                arg = []
            else: arg.append(op)
        if not isinstance(op, oo.Op_RBrace): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return args
    
    @staticmethod
    def isolate_set(ii:typing.Iterator):
        res = set()
        while True:
            op = next(ii, False)
            if not op: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if isinstance(op, oo.Op_RCBrace):
                return oo.Op_Set(res)
            elif isinstance(op, oo.Op_LCBrace): 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            elif not isinstance(op, oo.Op_Comma):
                res.add(op)

    @staticmethod
    def embedded_list_to_str_rec(ii:typing.Iterator):
        res = []
        while True:
            tt = next(ii, False)
            if not tt: break
            if isinstance(tt, list):
                res.append(' (')
                res.append(SASS_Expr_Eval.embedded_list_to_str_rec(iter(tt)))
                res.append(') ')
            else:
                res.append(tt)
        return "".join([str(i) for i in res])

    @staticmethod
    def embedded_list_to_str(emd_list:list):
        res = SASS_Expr_Eval.embedded_list_to_str_rec(iter(emd_list))
        return res

    @staticmethod
    def to_embedded_list_rec(ii:typing.Iterator):
        res = []
        while True:
            tt = next(ii, False)
            if not tt: break
            if isinstance(tt, oo.Op_LBrace):
                res.append(SASS_Expr_Eval.to_embedded_list_rec(ii))
            elif isinstance(tt, oo.Op_RBrace):
                return res
            elif isinstance(tt, oo.Op_Function):
                res.append(tt)
                res.extend(SASS_Expr_Eval.isolate_ff_rec(ii, tt))
            else:
                res.append(tt)
        return res

    @staticmethod
    def to_embedded_list(expr_opr:list):
        ii = iter(expr_opr)
        res = SASS_Expr_Eval.to_embedded_list_rec(ii)
        return res

    @staticmethod
    def preorder_rec2(expr_preorder:list, enc_vals:dict, res:list):
        e = expr_preorder.pop()
        # expr_preorder = expr_preorder[1:]
        if type(e) in oo.OP_OPERAND:
            res.append(e.op(enc_vals)) # type: ignore
        elif type(e) in oo.OP_OPERATOR:
            if isinstance(e, oo.Op_DualOperator):
                if not len(res) >= 2: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                arg1 = res.pop()
                arg2 = res.pop()
                res.append(e.op(arg1, arg2))
            else:
                if not len(res) >= 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                arg1 = res.pop()
                res.append(e.op(arg1)) # type: ignore
        elif isinstance(e, list):
            while e: 
                SASS_Expr_Eval.preorder_rec2(e, enc_vals, res)
        elif type(e) in oo.OP_FUNCTION:
            e:oo.Op_Function
            argn = e.get_arg_num()
            if not len(res) >= argn: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            args = [res.pop() for i in range(argn)]
            res.append(e.op(args, enc_vals))
        elif isinstance(e, oo.Op_If):
            if not len(res) >= 2: raise Exception(sp.CONST__ERROR_ILLEGAL)
            while expr_preorder: SASS_Expr_Eval.preorder_rec2(expr_preorder, enc_vals, res)
            if not len(res) >= 3: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            cond = res.pop()
            if_t = res.pop()
            else_t = res.pop()
            if cond: res.append(if_t)
            else: res.append(else_t) 
        elif isinstance(e, oo.Op_IfElse):
            if not len(res) >= 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else:
            raise Exception(sp.CONST__ERROR_ILLEGAL)
        pass

    @staticmethod
    def cp_rec(expr_preorder_in:list):
        out = []
        for i in expr_preorder_in:
            if isinstance(i, list):
                out.append(SASS_Expr_Eval.cp_rec(i))
            else: out.append(i)
        return out

    @staticmethod
    def preorder_eval(expr_preorder_in:list, enc_vals:dict):
        expr_preorder = SASS_Expr_Eval.cp_rec(expr_preorder_in)
        if not expr_preorder: raise Exception(sp.CONST__ERROR_ILLEGAL)
        res = []
        while expr_preorder:
            SASS_Expr_Eval.preorder_rec2(expr_preorder, enc_vals, res)
        assert(len(expr_preorder) == 0)
        if len(res) == 1: return res.pop()
        elif len(res) == 2: return res # this is for constBankAddress things
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)
