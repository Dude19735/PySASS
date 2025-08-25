from . import _sass_expression_ops as oo
from . import _config as sp
from ._sass_expression import SASS_Expr
from ._tt_instruction import TT_Instruction
from py_sass_ext import SASS_Bits
from .sass_parser_iter import SASS_Parser_Iter
from .sm_cu_details import SM_Cu_Details

"""
This script was used to test and implement the Shunting yard algo and more broadly the expression evaluation.
It still works.
"""

class Isolator:
    @staticmethod
    def parse_sm(sm:int):
        path = 'DocumentSASS/sm_'
        name = '_instructions.txt.in'
        instructions_txt = path + str(sm) + name
        result = SASS_Parser_Iter.parse(sm, instructions_txt)

        details = SM_Cu_Details(result, 'sm_{0}'.format(sm))
        all_format = {}
        all_enc_inds = {}
        for i in result['CLASS'].items():
            form:TT_Instruction = i[1]['FORMAT']
            form.finalize(details)
            bin_ind_l = [enc for enc in i[1][sp.CONST_NAME__ENCODING] if str(enc['alias']) == 'Opcode']
            if len(bin_ind_l) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            form.add_opcode_bin(i[1]['OPCODES'], bin_ind_l[0]['code_ind'])
            all_format[form.class_name] = form
            
            c_enc_ind = {}
            if form.class_name == 'ATOM_CAS':
                pass
            for enc in i[1]['ENCODING']:
                expr:SASS_Expr = enc['alias']
                evaled = expr.finalize(form.eval)
                aa = expr.get_alias_names()
                if not aa == []:
                    if len(aa) != len(enc['code']):
                        for ind,code in enumerate(aa):
                            c_enc_ind[code] = tuple(64*[0])
                    else:
                        for ind,code in enumerate(aa):
                            c_enc_ind[code] = enc['code_ind'][ind]
            all_enc_inds[form.class_name] = c_enc_ind

        return result, all_enc_inds, all_format, (result['TABLES'], result['CONSTANTS'], result['REGISTERS'], result['PARAMETERS'], result['TABLES_INV'])

    def unpack_args(args:dict):
        res = dict()
        for k,v in args.items():
            if isinstance(v,set):
                if len(v) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                res[k] = next(iter(v))
            else: res[k] = v
        return res

if __name__ == '__main__':
    result, all_enc_inds, all_format, args = Isolator.parse_sm(50)

    e_str = '(2 == 1 + 1 && 2 == 6 % 4)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_And, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Mod, oo.Op_Int, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ && == 2 + 1 1 == 2 % 6 4 ]')

    e_str = '(!(3 + 1) && 0)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Not, oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace, oo.Op_And, oo.Op_Int, oo.Op_RBrace)
    assert(res ==False)
    assert(expr.preorder_str == '[ && ! [ + 3 1 ] 0 ]')

    e_str = 'Reduce(+, 1, 2, 3, 4, 5)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Reduce, oo.Op_LBrace, oo.Op_Plus, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_RBrace)
    assert(res ==15)
    assert(expr.preorder_str == 'Reduce( + ) [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]')

    e_str = 'Reduce(+, 1, 2, (3+7+(5-3)), 4, Reduce(-, 10, 2, 3, 4), 5)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Reduce, oo.Op_LBrace, oo.Op_Plus, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_RBrace)
    assert(res ==25)
    assert(expr.preorder_str == 'Reduce( + ) [ 1 ] [ 2 ] [ + + 3 7 - 5 3 ] [ 4 ] [ Reduce( - ) [ 10 ] [ 2 ] [ 3 ] [ 4 ] ] [ 5 ]')

    e_str = 'Reduce(+, 1, 1) ? 2 + 4 : 3 - 5'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 6)
    assert(expr.preorder_str == 'Reduce( + ) [ 1 ] [ 1 ] ? + 2 4 : - 3 5')

    for p0, p1, r in zip([0,0,1,1],[0,1,0,1],[48,40,80,72]):
        e_str = '({p0} ? 64 : 32) + ({p1} ? 8 : 16)'.format(p0=p0,p1=p1)
        expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
        expr, evaled = expr.finalize({})
        res = expr({})
        # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace, oo.Op_Plus, oo.Op_LBrace, oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '+ [ {p0} ? 64 : 32 ] [ {p1} ? 8 : 16 ]'.format(p0=p0,p1=p1))

    for p0, r in zip([0,1],[16,32]):
        e_str = '(({p0} ? 0 : 8) ? 16 : 32)'.format(p0=p0)
        expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
        expr, evaled = expr.finalize({})
        res = expr({})
        # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '[ [ {p0} ? 0 : 8 ] ? 16 : 32 ]'.format(p0=p0))

    e_str = '((0 ? 4 : 0) ? 16 : 32)'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace)
    assert(res == 32)
    assert(expr.preorder_str == '[ [ 0 ? 4 : 0 ] ? 16 : 32 ]')

    for p0,p1,p2, r in zip([0,0,0,0,1,1,1,1],[0,0,1,1,0,0,1,1],[0,1,0,1,0,1,0,1],[9,3,9,3,1,1,2,2]):
        e_str = '{p0} ? ({p1} ? 2 : 1) : ({p2} ? 3 : 9)'.format(p0=p0,p1=p1,p2=p2)
        expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
        expr, evaled = expr.finalize({})
        res = expr({})
        # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '{p0} ? [ {p1} ? 2 : 1 ] : [ {p2} ? 3 : 9 ]'.format(p0=p0,p1=p1,p2=p2))

    e_str = 'tid MULTIPLY 4 SCALE 4'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['TEX'].eval)
    res = expr( Isolator.unpack_args( {'tid': SASS_Bits.from_int(1,bit_len=12, signed=0)}))
    # f = (oo.Op_Alias,)
    assert(res ==1 and res.bit_len == 12)
    assert(expr.preorder_str == 'SCALE MULTIPLY tid 4 4')

    e_str = 'tid MULTIPLY 4 SCALE 4'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['TEX'].eval)
    res = expr( Isolator.unpack_args( {'tid': SASS_Bits.from_int(int('0b101',2),bit_len=3, signed=0)}))
    # f = (oo.Op_Alias,)
    assert(res ==1 and res.bit_len == 3)
    assert(expr.preorder_str == 'SCALE MULTIPLY tid 4 4')

    e_str = 'tid MULTIPLY 4'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['TEX'].eval)
    res = expr( Isolator.unpack_args( {'tid': SASS_Bits.from_int(int('0b101',2),bit_len=12, signed=0)}))
    # f = (oo.Op_Alias,)
    assert(res ==int('0b10100',2) and res.bit_len == 12)
    assert(expr.preorder_str == 'MULTIPLY tid 4')

    e_str = 'tid MULTIPLY 4 SCALE 4'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['TEX'].eval)
    res = expr( Isolator.unpack_args( {'tid': SASS_Bits.from_int(int('0b101',2),bit_len=12, signed=0)}))
    # f = (oo.Op_Alias,)
    assert(res ==int('0b101',2) and res.bit_len == 12)
    assert(expr.preorder_str == 'SCALE MULTIPLY tid 4 4')

    e_str = 'tid SCALE 4'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['TEX'].eval)
    res = expr( Isolator.unpack_args( {'tid': SASS_Bits.from_int(int('0b101',2),bit_len=12, signed=0)}))
    # f = (oo.Op_Alias,)
    assert(res ==int('0b1',2) and res.bit_len == 12)
    assert(expr.preorder_str == 'SCALE tid 4')

    e_str = '!0'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Not, oo.Op_Int)
    assert(res == True)
    assert(expr.preorder_str == '! 0')

    e_str = '(!0 && 1)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Not, oo.Op_Int, oo.Op_And, oo.Op_Int, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ && ! 0 1 ]')

    e_str = '(!IsOdd(2))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Not, oo.Op_IsOdd, oo.Op_LBrace, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ ! IsOdd [ 2 ] ]')

    e_str = '(!(2 + 1 - 3) && 1)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Not, oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_Minus, oo.Op_Int, oo.Op_RBrace, oo.Op_And, oo.Op_Int, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ && ! [ - + 2 1 3 ] 1 ]')

    e_str = '(2 == 1 + 1 && 2 == IsEven((6 % 4)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_And, oo.Op_Int, oo.Op_Equal, oo.Op_IsEven, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_Mod, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == False)
    assert(expr.preorder_str == '[ && == 2 + 1 1 == 2 IsEven [ % 6 4 ] ]')

    e_str = 'IsOdd(IsEven(6))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_And, oo.Op_Int, oo.Op_Equal, oo.Op_IsOdd, oo.Op_LBrace, oo.Op_IsEven, oo.Op_LBrace, oo.Op_Int, oo.Op_Mod, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == 'IsOdd [ IsEven [ 6 ] ]')

    e_str = 'IsOdd(IsOdd(IsEven(6)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_And, oo.Op_Int, oo.Op_Equal, oo.Op_IsOdd, oo.Op_LBrace, oo.Op_IsEven, oo.Op_LBrace, oo.Op_Int, oo.Op_Mod, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == 'IsOdd [ IsOdd [ IsEven [ 6 ] ] ]')

    e_str = '(2 == 1 + 1 && 2 == IsOdd(IsEven(6 % 4)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_And, oo.Op_Int, oo.Op_Equal, oo.Op_IsOdd, oo.Op_LBrace, oo.Op_IsEven, oo.Op_LBrace, oo.Op_Int, oo.Op_Mod, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == False)
    assert(expr.preorder_str == '[ && == 2 + 1 1 == 2 IsOdd [ IsEven [ % 6 4 ] ] ]')

    e_str = '(2 == 1 + 1 && 1 == IsOdd(IsEven(6 % 4)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_And, oo.Op_Int, oo.Op_Equal, oo.Op_IsOdd, oo.Op_LBrace, oo.Op_IsEven, oo.Op_LBrace, oo.Op_Int, oo.Op_Mod, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ && == 2 + 1 1 == 1 IsOdd [ IsEven [ % 6 4 ] ] ]')

    e_str = '1 + 2 * 3'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_Mult, oo.Op_Int)
    assert(res == 7)
    assert(expr.preorder_str == '+ 1 * 2 3')

    e_str = '(1 + 2) * 3'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace, oo.Op_Mult, oo.Op_Int)
    assert(res == 9)
    assert(expr.preorder_str == '* [ + 1 2 ] 3')

    e_str = '(1 + 2) * (3 + 5)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace, oo.Op_Mult, oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace)
    assert(res == 24)
    assert(expr.preorder_str == '* [ + 1 2 ] [ + 3 5 ]')

    e_str = '1 * 2 * 3'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_Mult, oo.Op_Int, oo.Op_Mult, oo.Op_Int)
    assert(res == 6)
    assert(expr.preorder_str == '* * 1 2 3')

    e_str = '1 * 2 * 3 * 4 * 5'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_Mult, oo.Op_Int, oo.Op_Mult, oo.Op_Int, oo.Op_Mult, oo.Op_Int, oo.Op_Mult, oo.Op_Int)
    assert(res == 120)
    assert(expr.preorder_str == '* * * * 1 2 3 4 5')

    e_str = '(1 * 2 + 3)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Mult, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace)
    assert(res == 5)
    assert(expr.preorder_str == '[ + * 1 2 3 ]')

    e_str = '5 * (2 + 3)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_Mult, oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace)
    assert(res == 25)
    assert(expr.preorder_str == '* 5 [ + 2 3 ]')

    e_str = '1+1'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_Plus, oo.Op_Int)
    assert(res == 2)
    assert(expr.preorder_str == '+ 1 1')

    e_str = '(1+1)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace)
    assert(res == 2)
    assert(expr.preorder_str == '[ + 1 1 ]')

    e_str = 'PSign(0, 1, 1)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Table, oo.Op_LBrace, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_Comma, oo.Op_Int, oo.Op_RBrace)
    assert(res == 0)
    assert(expr.preorder_str == 'PSign [ 0 ] [ 1 ] [ 1 ]')

    e_str = 'DEFINED PSignFFMA(0,0)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Defined,)
    assert(res == True)
    assert(expr.preorder_str == 'DEFINED PSignFFMA [ 0 ] [ 0 ]')

    e_str = 'DEFINED PSignFFMA(2,0)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Defined,)
    assert(res == False)
    assert(expr.preorder_str == 'DEFINED PSignFFMA [ 2 ] [ 0 ]')

    e_str = '(%SHADER_TYPE == $ST_UNKNOWN) || ((%SHADER_TYPE == $ST_VSA || %SHADER_TYPE == $ST_VSB) -> (2 == `Register@RZ))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Parameter, oo.Op_Equal, oo.Op_Constant, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Parameter, oo.Op_Equal, oo.Op_Constant, oo.Op_Or, oo.Op_Parameter, oo.Op_Equal, oo.Op_Constant, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '|| [ == %SHADER_TYPE $ST_UNKNOWN ] [ -> [ || == %SHADER_TYPE $ST_VSA == %SHADER_TYPE $ST_VSB ] [ == 2 `Register@RZ ] ]')

    vv=[2, 255, 256]
    res = [True, True, False]
    for v,r in zip(vv,res):
        e_str = '((({v})==`Register@RZ)||(({v})<=(%MAX_REG_COUNT-1)))'.format(v=v)
        expr:SASS_Expr = SASS_Expr(e_str, *args)
        expr, evaled = expr.finalize({})
        res = expr({})
        # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_RBrace, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_RBrace, oo.Op_SmallerOrEqual, oo.Op_LBrace, oo.Op_Parameter, oo.Op_Minus, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '[ || [ == [ {v} ] `Register@RZ ] [ <= [ {v} ] [ - %MAX_REG_COUNT 1 ] ] ]'.format(v=v))

    for Ra, Rb, r in zip([0,0, 1,1, 2,2],[2,255, 2,255, 2,255],[False,True, True,True, False,True]):
        e_str = '(({Ra} == `IPAOp@PASS) || ({Ra} == `IPAOp@CONSTANT)) -> ({Rb} == `Register@RZ)'.format(Ra=Ra, Rb=Rb)
        expr:SASS_Expr = SASS_Expr(e_str, *args)
        expr, evaled = expr.finalize({})
        res = expr({})
        # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '-> [ || [ == {Ra} `IPAOp@PASS ] [ == {Ra} `IPAOp@CONSTANT ] ] [ == {Rb} `Register@RZ ]'.format(Ra=Ra, Rb=Rb))

    e_str = 'Pg@not'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['VSHL'].eval)
    res = expr( Isolator.unpack_args( {'Pg@not': SASS_Bits.from_int(1)}))
    # f = (oo.Op_AtNot,)
    assert(res == 1)
    assert(expr.preorder_str == 'Pg@not')

    e_str = 'PSignFFMA(Ra@negate,Rb@negate)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['FFMA'].eval)
    res = expr( Isolator.unpack_args( {'Ra@negate': SASS_Bits.from_int(1), 'Rb@negate': SASS_Bits.from_int(1)}))
    # f = (oo.Op_Table, oo.Op_LBrace, oo.Op_AtNegate, oo.Op_Comma, oo.Op_AtNegate, oo.Op_RBrace)
    assert(res == 0)
    assert(expr.preorder_str == 'PSignFFMA [ Ra@negate ] [ Rb@negate ]')

    for Sb, mufuop, r, bl in zip([5,6,7],[0,1,2],[0,1,2],[64,16,32]):
        e_str = '{Sb} convertFloatType({mufuop} == 0, F64Imm, {mufuop} == 1, F16Imm, F32Imm)'.format(Sb=Sb, mufuop=mufuop)
        expr:SASS_Expr = SASS_Expr(e_str, *args)
        expr, evaled = expr.finalize({})
        res = expr({})
        # f = (oo.Op_convertFloatType, oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Comma, oo.Op_TypeCast, oo.Op_LBrace, oo.Op_Int, oo.Op_RBrace, oo.Op_Comma, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_Comma, oo.Op_TypeCast, oo.Op_LBrace, oo.Op_Int, oo.Op_RBrace, oo.Op_Comma, oo.Op_TypeCast, oo.Op_LBrace, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace)
        assert(res == Sb and bl == bl)
        assert(expr.preorder_str == 'convertFloatType [ == {mufuop} 0 ] [ F64Imm [ {Sb} ] ] [ == {mufuop} 1 ] [ F16Imm [ {Sb} ] ] [ F32Imm [ {Sb} ] ]'.format(Sb=Sb, mufuop=mufuop))

    e_str = '3 + 5 + ((1 - 3) ? 2 + 4 : 3 - 5)'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 14)
    assert(expr.preorder_str == '+ + 3 5 [ [ - 1 3 ] ? + 2 4 : - 3 5 ]')

    e_str = '1 ? 2 + 4 : 3 - 5'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 6)
    assert(expr.preorder_str == '1 ? + 2 4 : - 3 5')

    e_str = 'Reduce(-, 1, 1) ? 2 + 4 : 3 - 5'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == -2)
    assert(expr.preorder_str == 'Reduce( - ) [ 1 ] [ 1 ] ? + 2 4 : - 3 5')

    e_str = '1 ? 64 : 32'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 64)
    assert(expr.preorder_str == '1 ? 64 : 32')

    e_str = '(1 ? 2 + 4 : 3 - 5)'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 6)
    assert(expr.preorder_str == '[ 1 ? + 2 4 : - 3 5 ]')

    e_str = '(1) ? (2 + 4) : (3 - 5)'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 6)
    assert(expr.preorder_str == '[ 1 ] ? [ + 2 4 ] : [ - 3 5 ]')

    for p,r in zip([0,1],[9,6]):
        e_str = '{p} ? 2 + 4 : 3 * (5 - 2)'.format(p=p)
        expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
        expr, evaled = expr.finalize({})
        res = expr({})
        # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
        assert(res == r)
        assert(expr.preorder_str == '{p} ? + 2 4 : * 3 [ - 5 2 ]'.format(p=p))

    e_str = '1 ? 2 * (4 - 6) : 3 - 5'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == -4)
    assert(expr.preorder_str == '1 ? * 2 [ - 4 6 ] : - 3 5')

    e_str = '(1 ? 2 + 4 : 3 - 5) + 7'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 13)
    assert(expr.preorder_str == '+ [ 1 ? + 2 4 : - 3 5 ] 7')

    e_str = '1 ? 2 + 4 : 3 - 5 + 7'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 6)
    assert(expr.preorder_str == '1 ? + 2 4 : + - 3 5 7')

    e_str = '0 ? 64 : 32'
    expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_Int, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int)
    assert(res == 32)
    assert(expr.preorder_str == '0 ? 64 : 32')

    for p1,p2,r in zip([1,5,5],[1,1,5],[32,128,64]):
        e_str = '(( {p1} <= 4 ) ? 1 : ( ( {p2} == 5 ) ? 2 : 4 ))*32'.format(p1=p1,p2=p2)
        expr:SASS_Expr = SASS_Expr(e_str, {}, {}, {}, {}, {})
        expr, evaled = expr.finalize({})
        res = expr({})
        f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_SmallerOrEqual, oo.Op_Int, oo.Op_RBrace, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Int, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_If, oo.Op_Int, oo.Op_IfElse, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Mult, oo.Op_Int)
        assert(res == r)
        assert(expr.preorder_str == '* [ [ <= {p1} 4 ] ? 1 : [ [ == {p2} 5 ] ? 2 : 4 ] ] 32'.format(p1=p1,p2=p2))

    e_str = '(1+2) - (2+3) - (3+4)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize({})
    res = expr({})
    # f = (oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace, oo.Op_Minus, oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace, oo.Op_Minus, oo.Op_LBrace, oo.Op_Int, oo.Op_Plus, oo.Op_Int, oo.Op_RBrace)
    assert(res == -9)
    assert(expr.preorder_str == '- - [ + 1 2 ] [ + 2 3 ] [ + 3 4 ]')

    e_str = '(PO -> ( !Ra@negate &&  !Rb@negate))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['IMAD'].eval)
    res = expr( Isolator.unpack_args( {'PO': SASS_Bits.from_int(0), 'Ra@negate': SASS_Bits.from_int(1), 'Rb@negate': SASS_Bits.from_int(1)}))
    # f = (oo.Op_LBrace, oo.Op_Alias, oo.Op_Implication, oo.Op_LBrace, oo.Op_Not, oo.Op_AtNegate, oo.Op_And, oo.Op_Not, oo.Op_AtNegate, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ -> PO [ && ! Ra@negate ! Rb@negate ] ]')

    for bpt,sImm,r in zip([3,3,0,0],[2,0,2,0],[1,0,1,1]):
        e_str = '!({bpt} == `BPTMode@TRAP && ({sImm} < 1 || {sImm} > 7))'.format(bpt=bpt,sImm=sImm)
        expr:SASS_Expr = SASS_Expr(e_str, *args)
        expr, evaled = expr.finalize(all_format['BPT'].eval)
        res = expr({})
        # f = (oo.Op_Not, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_And, oo.Op_LBrace, oo.Op_Alias, oo.Op_Smaller, oo.Op_Int, oo.Op_Or, oo.Op_Alias, oo.Op_Greater, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '! [ && == {bpt} `BPTMode@TRAP [ || < {sImm} 1 > {sImm} 7 ] ]'.format(bpt=bpt,sImm=sImm))

    e_str = '(uImm == 0xC10)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['IDE_EN'].eval)
    res = expr( Isolator.unpack_args( {'uImm': SASS_Bits.from_int(int('0xc10',16))}))
    # f = (oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ == uImm 0xC10 ]')

    for sImm,r in zip([8,9],[1,0]):
        e_str = '(({sImm} & 0x7) == 0)'.format(sImm=sImm)
        expr:SASS_Expr = SASS_Expr(e_str, *args)
        expr, evaled = expr.finalize(all_format['PEXIT'].eval)
        res = expr({})
        # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_BAnd, oo.Op_Int, oo.Op_RBrace, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '[ == [ & {sImm} 0x7 ] 0 ]'.format(sImm=sImm))

    result, all_enc_inds, all_format, args = Isolator.parse_sm(75)

    # idxsize = {'U4_H0': 0, 'U4_H1': 1, 'U8': 2, 'INVALID3': 3}
    idxsize_r = [0, 1, 2, 3]
    # mode = {'THREAD': 0, 'QUAD': 1}
    mode_r = [0,1,0,1]
    vecidx_r = [0,1,2,4]
    for idxsize,mode,vecidx,r in zip(idxsize_r, mode_r, vecidx_r, [True,True,True,True]):
        e_str = '((({idxsize} == `IDXSIZE@U4_H0) || ({idxsize} == `IDXSIZE@U4_H1)) && (({mode} == `MODE_scatter@THREAD))) -> ((({vecidx} == 0) || ({vecidx} == 1) || ({vecidx} == 2) || ({vecidx} == 3)))'.format(idxsize=idxsize,mode=mode,vecidx=vecidx)
        expr:SASS_Expr = SASS_Expr(e_str, *args)
        expr, evaled = expr.finalize(all_format['scatter_'].eval)
        res = expr({})
        # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '-> [ && [ || [ == {idxsize} `IDXSIZE@U4_H0 ] [ == {idxsize} `IDXSIZE@U4_H1 ] ] [ [ == {mode} `MODE_scatter@THREAD ] ] ] [ [ || || || [ == {vecidx} 0 ] [ == {vecidx} 1 ] [ == {vecidx} 2 ] [ == {vecidx} 3 ] ] ]'.format(idxsize=idxsize,mode=mode,vecidx=vecidx))

    e_str = '(((idxsize == `IDXSIZE@U4_H0) || (idxsize == `IDXSIZE@U4_H1)) && ((mode == `MODE_scatter@QUAD))) -> (((vecidx == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'idxsize': result['REGISTERS']['IDXSIZE']['U4_H0'], 'mode': result['REGISTERS']['MODE_scatter']['QUAD'], 'vecidx':0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && [ || [ == idxsize `IDXSIZE@U4_H0 ] [ == idxsize `IDXSIZE@U4_H1 ] ] [ [ == mode `MODE_scatter@QUAD ] ] ] [ [ [ == vecidx 0 ] ] ]')

    e_str = '(((idxsize == `IDXSIZE@U8)) && ((mode == `MODE_scatter@QUAD))) -> (((vecidx == 0) || (vecidx == 1) || (vecidx == 2) || (vecidx == 3) || (vecidx == 4) || (vecidx == 5) || (vecidx == 6) || (vecidx == 7) || (vecidx == 8) || (vecidx == 9) || (vecidx == 10) || (vecidx == 11) || (vecidx == 12) || (vecidx == 13) || (vecidx == 14) || (vecidx == 15)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'idxsize': result['REGISTERS']['IDXSIZE']['U8'], 'mode': result['REGISTERS']['MODE_scatter']['QUAD'], 'vecidx':0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && [ [ == idxsize `IDXSIZE@U8 ] ] [ [ == mode `MODE_scatter@QUAD ] ] ] [ [ || || || || || || || || || || || || || || || [ == vecidx 0 ] [ == vecidx 1 ] [ == vecidx 2 ] [ == vecidx 3 ] [ == vecidx 4 ] [ == vecidx 5 ] [ == vecidx 6 ] [ == vecidx 7 ] [ == vecidx 8 ] [ == vecidx 9 ] [ == vecidx 10 ] [ == vecidx 11 ] [ == vecidx 12 ] [ == vecidx 13 ] [ == vecidx 14 ] [ == vecidx 15 ] ] ]')

    e_str = '(Sb_addr & 0x3) == 0'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['sel__RCR_RCR'].eval)
    res = expr( Isolator.unpack_args( {'Sb_addr': int('0b100',2)}))
    # f = (oo.Op_LBrace, oo.Op_Alias, oo.Op_BAnd, oo.Op_Int, oo.Op_RBrace, oo.Op_Equal, oo.Op_Int)
    assert(res == True)
    assert(expr.preorder_str == '== [ & Sb_addr 0x3 ] 0')

    e_str = '((scoreboard_list & (1 << sbidx)) == 0)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['depbar__LE'].eval)
    res = expr( Isolator.unpack_args( {'scoreboard_list': int('0b101',2), 'sbidx': 1 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_BAnd, oo.Op_LBrace, oo.Op_Int, oo.Op_LShift, oo.Op_Alias, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ == [ & scoreboard_list [ << 1 sbidx ] ] 0 ]')

    e_str = '((Sb == 3088))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['ide_'].eval)
    res = expr( Isolator.unpack_args( {'Sb': 3088 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ [ == Sb 3088 ] ]')

    for Sb_bank,Sb_addr,r in zip([25,20,25],[200,200,260],[True,True,False]):
        e_str = '(Sb_bank >= 24 && Sb_bank <= 31) -> (Sb_addr <= 255)'
        expr:SASS_Expr = SASS_Expr(e_str, *args)
        expr, evaled = expr.finalize(all_format['dfma__RCR_RCR'].eval)
        res = expr( Isolator.unpack_args( {'Sb_bank': Sb_bank, 'Sb_addr': Sb_addr }))
        # f = (oo.Op_LBrace, oo.Op_Alias, oo.Op_GreaterOrEqual, oo.Op_Int, oo.Op_And, oo.Op_Alias, oo.Op_SmallerOrEqual, oo.Op_Int, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_Alias, oo.Op_SmallerOrEqual, oo.Op_Int, oo.Op_RBrace)
        assert(res == r)
        assert(expr.preorder_str == '-> [ && >= Sb_bank 24 <= Sb_bank 31 ] [ <= Sb_addr 255 ]')
        
    result, all_enc_inds, all_format, args = Isolator.parse_sm(90)
    regs = result['REGISTERS']
    e_str = '(((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 11) || (mdidx == 10) || (mdidx == 13) || (mdidx == 12) || (mdidx == 14) || (mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 9) || (mdidx == 8)) && ((vecidx6 == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args({'num': regs['NUM_GROUPS']['1G'], 'idxsize': regs['IDXSIZE']['U2'], 'seq': regs['SEQ']['SEQ'], 'mdidx': 12, 'vecidx6': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@1G ] ] [ [ == idxsize `IDXSIZE@U2 ] ] [ [ == seq `SEQ@SEQ ] ] ] [ && [ || || || || || || || || || || || || || || [ == mdidx 11 ] [ == mdidx 10 ] [ == mdidx 13 ] [ == mdidx 12 ] [ == mdidx 14 ] [ == mdidx 1 ] [ == mdidx 0 ] [ == mdidx 3 ] [ == mdidx 2 ] [ == mdidx 5 ] [ == mdidx 4 ] [ == mdidx 7 ] [ == mdidx 6 ] [ == mdidx 9 ] [ == mdidx 8 ] ] [ [ == vecidx6 0 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq))) -> (((mdidx == 11) || (mdidx == 10) || (mdidx == 12) || (mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 9) || (mdidx == 8)) && ((vecidx6 == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['2G'], 'idxsize': regs['IDXSIZE']['U2'], 'seq': regs['SEQ']['noseq'], 'mdidx': 12, 'vecidx6': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@2G ] ] [ [ == idxsize `IDXSIZE@U2 ] ] [ [ == seq `SEQ@noseq ] ] ] [ && [ || || || || || || || || || || || || [ == mdidx 11 ] [ == mdidx 10 ] [ == mdidx 12 ] [ == mdidx 1 ] [ == mdidx 0 ] [ == mdidx 3 ] [ == mdidx 2 ] [ == mdidx 5 ] [ == mdidx 4 ] [ == mdidx 7 ] [ == mdidx 6 ] [ == mdidx 9 ] [ == mdidx 8 ] ] [ [ == vecidx6 0 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U2)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 7) || (mdidx == 6) || (mdidx == 8)) && ((vecidx6 == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['4G'], 'idxsize': regs['IDXSIZE']['U2'], 'seq': regs['SEQ']['noseq'], 'mdidx': 2, 'vecidx6': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@4G ] ] [ [ == idxsize `IDXSIZE@U2 ] ] [ [ == seq `SEQ@noseq ] ] ] [ && [ || || || || || || || || [ == mdidx 1 ] [ == mdidx 0 ] [ == mdidx 3 ] [ == mdidx 2 ] [ == mdidx 5 ] [ == mdidx 4 ] [ == mdidx 7 ] [ == mdidx 6 ] [ == mdidx 8 ] ] [ [ == vecidx6 0 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 5) || (mdidx == 4) || (mdidx == 6)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['1G'], 'idxsize': regs['IDXSIZE']['U4'], 'seq': regs['SEQ']['noseq'], 'mdidx': 3, 'vecidx6': 2 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@1G ] ] [ [ == idxsize `IDXSIZE@U4 ] ] [ [ == seq `SEQ@SEQ ] ] ] [ && [ || || || || || || [ == mdidx 1 ] [ == mdidx 0 ] [ == mdidx 3 ] [ == mdidx 2 ] [ == mdidx 5 ] [ == mdidx 4 ] [ == mdidx 6 ] ] [ || || || [ == vecidx6 1 ] [ == vecidx6 0 ] [ == vecidx6 3 ] [ == vecidx6 2 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 4)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['2G'], 'idxsize': regs['IDXSIZE']['U4'], 'seq': regs['SEQ']['noseq'], 'mdidx': 3, 'vecidx6': 3 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@2G ] ] [ [ == idxsize `IDXSIZE@U4 ] ] [ [ == seq `SEQ@noseq ] ] ] [ && [ || || || || [ == mdidx 1 ] [ == mdidx 0 ] [ == mdidx 3 ] [ == mdidx 2 ] [ == mdidx 4 ] ] [ || || || [ == vecidx6 1 ] [ == vecidx6 0 ] [ == vecidx6 3 ] [ == vecidx6 2 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@noseq))) -> (((mdidx == 0)) && ((vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['4G'], 'idxsize': regs['IDXSIZE']['U4'], 'seq': regs['SEQ']['noseq'], 'mdidx': 0, 'vecidx6': 3 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@4G ] ] [ [ == idxsize `IDXSIZE@U4 ] ] [ [ == seq `SEQ@noseq ] ] ] [ && [ [ == mdidx 0 ] ] [ || || || [ == vecidx6 1 ] [ == vecidx6 0 ] [ == vecidx6 3 ] [ == vecidx6 2 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@1G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 2)) && ((vecidx6 == 56) || (vecidx6 == 54) || (vecidx6 == 42) || (vecidx6 == 48) || (vecidx6 == 43) || (vecidx6 == 60) || (vecidx6 == 61) || (vecidx6 == 62) || (vecidx6 == 63) || (vecidx6 == 49) || (vecidx6 == 52) || (vecidx6 == 53) || (vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 46) || (vecidx6 == 47) || (vecidx6 == 44) || (vecidx6 == 45) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 40) || (vecidx6 == 41) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 51) || (vecidx6 == 39) || (vecidx6 == 38) || (vecidx6 == 59) || (vecidx6 == 58) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30) || (vecidx6 == 37) || (vecidx6 == 36) || (vecidx6 == 35) || (vecidx6 == 34) || (vecidx6 == 33) || (vecidx6 == 55) || (vecidx6 == 32) || (vecidx6 == 57) || (vecidx6 == 50)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['1G'], 'idxsize': regs['IDXSIZE']['U8'], 'seq': regs['SEQ']['SEQ'], 'mdidx': 1, 'vecidx6': 56 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@1G ] ] [ [ == idxsize `IDXSIZE@U8 ] ] [ [ == seq `SEQ@SEQ ] ] ] [ && [ || || [ == mdidx 1 ] [ == mdidx 0 ] [ == mdidx 2 ] ] [ || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || [ == vecidx6 56 ] [ == vecidx6 54 ] [ == vecidx6 42 ] [ == vecidx6 48 ] [ == vecidx6 43 ] [ == vecidx6 60 ] [ == vecidx6 61 ] [ == vecidx6 62 ] [ == vecidx6 63 ] [ == vecidx6 49 ] [ == vecidx6 52 ] [ == vecidx6 53 ] [ == vecidx6 24 ] [ == vecidx6 25 ] [ == vecidx6 26 ] [ == vecidx6 27 ] [ == vecidx6 20 ] [ == vecidx6 21 ] [ == vecidx6 22 ] [ == vecidx6 23 ] [ == vecidx6 46 ] [ == vecidx6 47 ] [ == vecidx6 44 ] [ == vecidx6 45 ] [ == vecidx6 28 ] [ == vecidx6 29 ] [ == vecidx6 40 ] [ == vecidx6 41 ] [ == vecidx6 1 ] [ == vecidx6 0 ] [ == vecidx6 3 ] [ == vecidx6 2 ] [ == vecidx6 5 ] [ == vecidx6 4 ] [ == vecidx6 7 ] [ == vecidx6 6 ] [ == vecidx6 9 ] [ == vecidx6 8 ] [ == vecidx6 51 ] [ == vecidx6 39 ] [ == vecidx6 38 ] [ == vecidx6 59 ] [ == vecidx6 58 ] [ == vecidx6 11 ] [ == vecidx6 10 ] [ == vecidx6 13 ] [ == vecidx6 12 ] [ == vecidx6 15 ] [ == vecidx6 14 ] [ == vecidx6 17 ] [ == vecidx6 16 ] [ == vecidx6 19 ] [ == vecidx6 18 ] [ == vecidx6 31 ] [ == vecidx6 30 ] [ == vecidx6 37 ] [ == vecidx6 36 ] [ == vecidx6 35 ] [ == vecidx6 34 ] [ == vecidx6 33 ] [ == vecidx6 55 ] [ == vecidx6 32 ] [ == vecidx6 57 ] [ == vecidx6 50 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@noseq))) -> (((mdidx == 0)) && ((vecidx6 == 56) || (vecidx6 == 54) || (vecidx6 == 42) || (vecidx6 == 48) || (vecidx6 == 43) || (vecidx6 == 60) || (vecidx6 == 61) || (vecidx6 == 62) || (vecidx6 == 63) || (vecidx6 == 49) || (vecidx6 == 52) || (vecidx6 == 53) || (vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 46) || (vecidx6 == 47) || (vecidx6 == 44) || (vecidx6 == 45) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 40) || (vecidx6 == 41) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 51) || (vecidx6 == 39) || (vecidx6 == 38) || (vecidx6 == 59) || (vecidx6 == 58) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30) || (vecidx6 == 37) || (vecidx6 == 36) || (vecidx6 == 35) || (vecidx6 == 34) || (vecidx6 == 33) || (vecidx6 == 55) || (vecidx6 == 32) || (vecidx6 == 57) || (vecidx6 == 50)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['2G'], 'idxsize': regs['IDXSIZE']['U8'], 'seq': regs['SEQ']['noseq'], 'mdidx': 0, 'vecidx6': 56 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@2G ] ] [ [ == idxsize `IDXSIZE@U8 ] ] [ [ == seq `SEQ@noseq ] ] ] [ && [ [ == mdidx 0 ] ] [ || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || [ == vecidx6 56 ] [ == vecidx6 54 ] [ == vecidx6 42 ] [ == vecidx6 48 ] [ == vecidx6 43 ] [ == vecidx6 60 ] [ == vecidx6 61 ] [ == vecidx6 62 ] [ == vecidx6 63 ] [ == vecidx6 49 ] [ == vecidx6 52 ] [ == vecidx6 53 ] [ == vecidx6 24 ] [ == vecidx6 25 ] [ == vecidx6 26 ] [ == vecidx6 27 ] [ == vecidx6 20 ] [ == vecidx6 21 ] [ == vecidx6 22 ] [ == vecidx6 23 ] [ == vecidx6 46 ] [ == vecidx6 47 ] [ == vecidx6 44 ] [ == vecidx6 45 ] [ == vecidx6 28 ] [ == vecidx6 29 ] [ == vecidx6 40 ] [ == vecidx6 41 ] [ == vecidx6 1 ] [ == vecidx6 0 ] [ == vecidx6 3 ] [ == vecidx6 2 ] [ == vecidx6 5 ] [ == vecidx6 4 ] [ == vecidx6 7 ] [ == vecidx6 6 ] [ == vecidx6 9 ] [ == vecidx6 8 ] [ == vecidx6 51 ] [ == vecidx6 39 ] [ == vecidx6 38 ] [ == vecidx6 59 ] [ == vecidx6 58 ] [ == vecidx6 11 ] [ == vecidx6 10 ] [ == vecidx6 13 ] [ == vecidx6 12 ] [ == vecidx6 15 ] [ == vecidx6 14 ] [ == vecidx6 17 ] [ == vecidx6 16 ] [ == vecidx6 19 ] [ == vecidx6 18 ] [ == vecidx6 31 ] [ == vecidx6 30 ] [ == vecidx6 37 ] [ == vecidx6 36 ] [ == vecidx6 35 ] [ == vecidx6 34 ] [ == vecidx6 33 ] [ == vecidx6 55 ] [ == vecidx6 32 ] [ == vecidx6 57 ] [ == vecidx6 50 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 1) || (mdidx == 0) || (mdidx == 3) || (mdidx == 2) || (mdidx == 4)) && ((vecidx6 == 1) || (vecidx6 == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['2G'], 'idxsize': regs['IDXSIZE']['U4'], 'seq': regs['SEQ']['noseq'], 'mdidx': 0, 'vecidx6': 1 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@2G ] ] [ [ == idxsize `IDXSIZE@U4 ] ] [ [ == seq `SEQ@SEQ ] ] ] [ && [ || || || || [ == mdidx 1 ] [ == mdidx 0 ] [ == mdidx 3 ] [ == mdidx 2 ] [ == mdidx 4 ] ] [ || [ == vecidx6 1 ] [ == vecidx6 0 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@4G)) && ((idxsize == `IDXSIZE@U4)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 0)) && ((vecidx6 == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['4G'], 'idxsize': regs['IDXSIZE']['U4'], 'seq': regs['SEQ']['SEQ'], 'mdidx': 0, 'vecidx6': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@4G ] ] [ [ == idxsize `IDXSIZE@U4 ] ] [ [ == seq `SEQ@SEQ ] ] ] [ && [ [ == mdidx 0 ] ] [ [ == vecidx6 0 ] ] ]')

    e_str = '(((num == `NUM_GROUPS@2G)) && ((idxsize == `IDXSIZE@U8)) && ((seq == `SEQ@SEQ))) -> (((mdidx == 0)) && ((vecidx6 == 24) || (vecidx6 == 25) || (vecidx6 == 26) || (vecidx6 == 27) || (vecidx6 == 20) || (vecidx6 == 21) || (vecidx6 == 22) || (vecidx6 == 23) || (vecidx6 == 28) || (vecidx6 == 29) || (vecidx6 == 1) || (vecidx6 == 0) || (vecidx6 == 3) || (vecidx6 == 2) || (vecidx6 == 5) || (vecidx6 == 4) || (vecidx6 == 7) || (vecidx6 == 6) || (vecidx6 == 9) || (vecidx6 == 8) || (vecidx6 == 11) || (vecidx6 == 10) || (vecidx6 == 13) || (vecidx6 == 12) || (vecidx6 == 15) || (vecidx6 == 14) || (vecidx6 == 17) || (vecidx6 == 16) || (vecidx6 == 19) || (vecidx6 == 18) || (vecidx6 == 31) || (vecidx6 == 30)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['genmetadata_'].eval)
    res = expr( Isolator.unpack_args( {'num': regs['NUM_GROUPS']['2G'], 'idxsize': regs['IDXSIZE']['U8'], 'seq': regs['SEQ']['SEQ'], 'mdidx': 0, 'vecidx6': 24 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == num `NUM_GROUPS@2G ] ] [ [ == idxsize `IDXSIZE@U8 ] ] [ [ == seq `SEQ@SEQ ] ] ] [ && [ [ == mdidx 0 ] ] [ || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || [ == vecidx6 24 ] [ == vecidx6 25 ] [ == vecidx6 26 ] [ == vecidx6 27 ] [ == vecidx6 20 ] [ == vecidx6 21 ] [ == vecidx6 22 ] [ == vecidx6 23 ] [ == vecidx6 28 ] [ == vecidx6 29 ] [ == vecidx6 1 ] [ == vecidx6 0 ] [ == vecidx6 3 ] [ == vecidx6 2 ] [ == vecidx6 5 ] [ == vecidx6 4 ] [ == vecidx6 7 ] [ == vecidx6 6 ] [ == vecidx6 9 ] [ == vecidx6 8 ] [ == vecidx6 11 ] [ == vecidx6 10 ] [ == vecidx6 13 ] [ == vecidx6 12 ] [ == vecidx6 15 ] [ == vecidx6 14 ] [ == vecidx6 17 ] [ == vecidx6 16 ] [ == vecidx6 19 ] [ == vecidx6 18 ] [ == vecidx6 31 ] [ == vecidx6 30 ] ] ]')

    e_str = '(((sparse == `SPARSE@SP)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_B3))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'sparse': regs['SPARSE']['SP'], 'mode': regs['MODE_scatter']['THREAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U4_B3'], 'vecidx': 3 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && && [ [ == sparse `SPARSE@SP ] ] [ [ == mode `MODE_scatter@THREAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U4_B3 ] ] ] [ [ || || || [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] ] ]')

    e_str = '(((sparse == `SPARSE@SP)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 56) || (vecidx == 54) || (vecidx == 42) || (vecidx == 48) || (vecidx == 43) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 49) || (vecidx == 52) || (vecidx == 53) || (vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 28) || (vecidx == 29) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 51) || (vecidx == 39) || (vecidx == 38) || (vecidx == 59) || (vecidx == 58) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 33) || (vecidx == 55) || (vecidx == 32) || (vecidx == 57) || (vecidx == 50)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'sparse': regs['SPARSE']['SP'], 'mode': regs['MODE_scatter']['THREAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U4_B3'], 'vecidx': 56 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && && [ [ == sparse `SPARSE@SP ] ] [ [ == mode `MODE_scatter@THREAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || [ == vecidx 56 ] [ == vecidx 54 ] [ == vecidx 42 ] [ == vecidx 48 ] [ == vecidx 43 ] [ == vecidx 60 ] [ == vecidx 61 ] [ == vecidx 62 ] [ == vecidx 63 ] [ == vecidx 49 ] [ == vecidx 52 ] [ == vecidx 53 ] [ == vecidx 24 ] [ == vecidx 25 ] [ == vecidx 26 ] [ == vecidx 27 ] [ == vecidx 20 ] [ == vecidx 21 ] [ == vecidx 22 ] [ == vecidx 23 ] [ == vecidx 46 ] [ == vecidx 47 ] [ == vecidx 44 ] [ == vecidx 45 ] [ == vecidx 28 ] [ == vecidx 29 ] [ == vecidx 40 ] [ == vecidx 41 ] [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] [ == vecidx 5 ] [ == vecidx 4 ] [ == vecidx 7 ] [ == vecidx 6 ] [ == vecidx 9 ] [ == vecidx 8 ] [ == vecidx 51 ] [ == vecidx 39 ] [ == vecidx 38 ] [ == vecidx 59 ] [ == vecidx 58 ] [ == vecidx 11 ] [ == vecidx 10 ] [ == vecidx 13 ] [ == vecidx 12 ] [ == vecidx 15 ] [ == vecidx 14 ] [ == vecidx 17 ] [ == vecidx 16 ] [ == vecidx 19 ] [ == vecidx 18 ] [ == vecidx 31 ] [ == vecidx 30 ] [ == vecidx 37 ] [ == vecidx 36 ] [ == vecidx 35 ] [ == vecidx 34 ] [ == vecidx 33 ] [ == vecidx 55 ] [ == vecidx 32 ] [ == vecidx 57 ] [ == vecidx 50 ] ] ]')

    e_str = '(((sparse == `SPARSE@SP)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'sparse': regs['SPARSE']['SP'], 'mode': regs['MODE_scatter']['THREAD'], 'elsize':regs['ELSIZE']['U8'], 'idxsize': regs['IDXSIZE_scatter']['U8_H1'], 'vecidx': 2 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && && [ [ == sparse `SPARSE@SP ] ] [ [ == mode `MODE_scatter@QUAD ] ] [ [ == elsize `ELSIZE@U8 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] [ == vecidx 5 ] [ == vecidx 4 ] [ == vecidx 7 ] [ == vecidx 6 ] ] ]')

    e_str = '(((sparse == `SPARSE@nosparse)) && ((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 0) || (vecidx == 4) || (vecidx == 8) || (vecidx == 119) || (vecidx == 120) || (vecidx == 121) || (vecidx == 122) || (vecidx == 123) || (vecidx == 124) || (vecidx == 125) || (vecidx == 126) || (vecidx == 127) || (vecidx == 118) || (vecidx == 59) || (vecidx == 58) || (vecidx == 55) || (vecidx == 54) || (vecidx == 57) || (vecidx == 56) || (vecidx == 51) || (vecidx == 50) || (vecidx == 53) || (vecidx == 52) || (vecidx == 115) || (vecidx == 114) || (vecidx == 88) || (vecidx == 89) || (vecidx == 111) || (vecidx == 110) || (vecidx == 113) || (vecidx == 112) || (vecidx == 82) || (vecidx == 83) || (vecidx == 80) || (vecidx == 81) || (vecidx == 86) || (vecidx == 87) || (vecidx == 84) || (vecidx == 85) || (vecidx == 3) || (vecidx == 7) || (vecidx == 108) || (vecidx == 109) || (vecidx == 102) || (vecidx == 103) || (vecidx == 100) || (vecidx == 101) || (vecidx == 106) || (vecidx == 107) || (vecidx == 104) || (vecidx == 105) || (vecidx == 39) || (vecidx == 38) || (vecidx == 33) || (vecidx == 32) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 64) || (vecidx == 65) || (vecidx == 66) || (vecidx == 67) || (vecidx == 68) || (vecidx == 69) || (vecidx == 2) || (vecidx == 6) || (vecidx == 99) || (vecidx == 98) || (vecidx == 91) || (vecidx == 90) || (vecidx == 93) || (vecidx == 92) || (vecidx == 95) || (vecidx == 94) || (vecidx == 97) || (vecidx == 96) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 117) || (vecidx == 116) || (vecidx == 48) || (vecidx == 49) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 42) || (vecidx == 43) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 5) || (vecidx == 9) || (vecidx == 77) || (vecidx == 76) || (vecidx == 75) || (vecidx == 74) || (vecidx == 73) || (vecidx == 72) || (vecidx == 71) || (vecidx == 70) || (vecidx == 79) || (vecidx == 78)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'sparse': regs['SPARSE']['nosparse'], 'mode': regs['MODE_scatter']['THREAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U8_H1'], 'vecidx': 24 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && && [ [ == sparse `SPARSE@nosparse ] ] [ [ == mode `MODE_scatter@THREAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || [ == vecidx 24 ] [ == vecidx 25 ] [ == vecidx 26 ] [ == vecidx 27 ] [ == vecidx 20 ] [ == vecidx 21 ] [ == vecidx 22 ] [ == vecidx 23 ] [ == vecidx 28 ] [ == vecidx 29 ] [ == vecidx 0 ] [ == vecidx 4 ] [ == vecidx 8 ] [ == vecidx 119 ] [ == vecidx 120 ] [ == vecidx 121 ] [ == vecidx 122 ] [ == vecidx 123 ] [ == vecidx 124 ] [ == vecidx 125 ] [ == vecidx 126 ] [ == vecidx 127 ] [ == vecidx 118 ] [ == vecidx 59 ] [ == vecidx 58 ] [ == vecidx 55 ] [ == vecidx 54 ] [ == vecidx 57 ] [ == vecidx 56 ] [ == vecidx 51 ] [ == vecidx 50 ] [ == vecidx 53 ] [ == vecidx 52 ] [ == vecidx 115 ] [ == vecidx 114 ] [ == vecidx 88 ] [ == vecidx 89 ] [ == vecidx 111 ] [ == vecidx 110 ] [ == vecidx 113 ] [ == vecidx 112 ] [ == vecidx 82 ] [ == vecidx 83 ] [ == vecidx 80 ] [ == vecidx 81 ] [ == vecidx 86 ] [ == vecidx 87 ] [ == vecidx 84 ] [ == vecidx 85 ] [ == vecidx 3 ] [ == vecidx 7 ] [ == vecidx 108 ] [ == vecidx 109 ] [ == vecidx 102 ] [ == vecidx 103 ] [ == vecidx 100 ] [ == vecidx 101 ] [ == vecidx 106 ] [ == vecidx 107 ] [ == vecidx 104 ] [ == vecidx 105 ] [ == vecidx 39 ] [ == vecidx 38 ] [ == vecidx 33 ] [ == vecidx 32 ] [ == vecidx 31 ] [ == vecidx 30 ] [ == vecidx 37 ] [ == vecidx 36 ] [ == vecidx 35 ] [ == vecidx 34 ] [ == vecidx 60 ] [ == vecidx 61 ] [ == vecidx 62 ] [ == vecidx 63 ] [ == vecidx 64 ] [ == vecidx 65 ] [ == vecidx 66 ] [ == vecidx 67 ] [ == vecidx 68 ] [ == vecidx 69 ] [ == vecidx 2 ] [ == vecidx 6 ] [ == vecidx 99 ] [ == vecidx 98 ] [ == vecidx 91 ] [ == vecidx 90 ] [ == vecidx 93 ] [ == vecidx 92 ] [ == vecidx 95 ] [ == vecidx 94 ] [ == vecidx 97 ] [ == vecidx 96 ] [ == vecidx 11 ] [ == vecidx 10 ] [ == vecidx 13 ] [ == vecidx 12 ] [ == vecidx 15 ] [ == vecidx 14 ] [ == vecidx 17 ] [ == vecidx 16 ] [ == vecidx 19 ] [ == vecidx 18 ] [ == vecidx 117 ] [ == vecidx 116 ] [ == vecidx 48 ] [ == vecidx 49 ] [ == vecidx 46 ] [ == vecidx 47 ] [ == vecidx 44 ] [ == vecidx 45 ] [ == vecidx 42 ] [ == vecidx 43 ] [ == vecidx 40 ] [ == vecidx 41 ] [ == vecidx 1 ] [ == vecidx 5 ] [ == vecidx 9 ] [ == vecidx 77 ] [ == vecidx 76 ] [ == vecidx 75 ] [ == vecidx 74 ] [ == vecidx 73 ] [ == vecidx 72 ] [ == vecidx 71 ] [ == vecidx 70 ] [ == vecidx 79 ] [ == vecidx 78 ] ] ]')

    e_str = '(((sparse == `SPARSE@SP)) && ((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_B3))) -> (((vecidx == 1) || (vecidx == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'sparse': regs['SPARSE']['SP'], 'mode': regs['MODE_scatter']['PAIR'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U4_B3'], 'vecidx': 1 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && && [ [ == sparse `SPARSE@SP ] ] [ [ == mode `MODE_scatter@PAIR ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U4_B3 ] ] ] [ [ || [ == vecidx 1 ] [ == vecidx 0 ] ] ]')

    e_str = '(((sparse == `SPARSE@SP)) && ((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'sparse': regs['SPARSE']['SP'], 'mode': regs['MODE_scatter']['PAIR'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U8_H1'], 'vecidx': 27 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && && [ [ == sparse `SPARSE@SP ] ] [ [ == mode `MODE_scatter@PAIR ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || [ == vecidx 24 ] [ == vecidx 25 ] [ == vecidx 26 ] [ == vecidx 27 ] [ == vecidx 20 ] [ == vecidx 21 ] [ == vecidx 22 ] [ == vecidx 23 ] [ == vecidx 28 ] [ == vecidx 29 ] [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] [ == vecidx 5 ] [ == vecidx 4 ] [ == vecidx 7 ] [ == vecidx 6 ] [ == vecidx 9 ] [ == vecidx 8 ] [ == vecidx 11 ] [ == vecidx 10 ] [ == vecidx 13 ] [ == vecidx 12 ] [ == vecidx 15 ] [ == vecidx 14 ] [ == vecidx 17 ] [ == vecidx 16 ] [ == vecidx 19 ] [ == vecidx 18 ] [ == vecidx 31 ] [ == vecidx 30 ] ] ]')

    e_str = '(((sparse == `SPARSE@SP)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_B3))) -> (((vecidx == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'sparse': regs['SPARSE']['SP'], 'mode': regs['MODE_scatter']['QUAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U4_B3'], 'vecidx': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && && [ [ == sparse `SPARSE@SP ] ] [ [ == mode `MODE_scatter@QUAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U4_B3 ] ] ] [ [ [ == vecidx 0 ] ] ]')

    e_str = '(((sparse == `SPARSE@SP)) && ((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'sparse': regs['SPARSE']['SP'], 'mode': regs['MODE_scatter']['QUAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U8_H1'], 'vecidx': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && && [ [ == sparse `SPARSE@SP ] ] [ [ == mode `MODE_scatter@QUAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || || || || || || || || || [ == vecidx 11 ] [ == vecidx 10 ] [ == vecidx 13 ] [ == vecidx 12 ] [ == vecidx 15 ] [ == vecidx 14 ] [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] [ == vecidx 5 ] [ == vecidx 4 ] [ == vecidx 7 ] [ == vecidx 6 ] [ == vecidx 9 ] [ == vecidx 8 ] ] ]')

    e_str = '(((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_B3))) -> (((vecidx == 1) || (vecidx == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'mode': regs['MODE_scatter']['PAIR'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U4_B3'], 'vecidx': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == mode `MODE_scatter@PAIR ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U4_B3 ] ] ] [ [ || [ == vecidx 1 ] [ == vecidx 0 ] ] ]')

    e_str = '(((mode == `MODE_scatter@PAIR)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 28) || (vecidx == 29) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'mode': regs['MODE_scatter']['PAIR'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U8_H1'], 'vecidx': 20 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == mode `MODE_scatter@PAIR ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || [ == vecidx 24 ] [ == vecidx 25 ] [ == vecidx 26 ] [ == vecidx 27 ] [ == vecidx 20 ] [ == vecidx 21 ] [ == vecidx 22 ] [ == vecidx 23 ] [ == vecidx 28 ] [ == vecidx 29 ] [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] [ == vecidx 5 ] [ == vecidx 4 ] [ == vecidx 7 ] [ == vecidx 6 ] [ == vecidx 9 ] [ == vecidx 8 ] [ == vecidx 11 ] [ == vecidx 10 ] [ == vecidx 13 ] [ == vecidx 12 ] [ == vecidx 15 ] [ == vecidx 14 ] [ == vecidx 17 ] [ == vecidx 16 ] [ == vecidx 19 ] [ == vecidx 18 ] [ == vecidx 31 ] [ == vecidx 30 ] ] ]')

    e_str = '(((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_B3))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'mode': regs['MODE_scatter']['THREAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U4_B3'], 'vecidx': 3 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == mode `MODE_scatter@THREAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U4_B3 ] ] ] [ [ || || || [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] ] ]')

    e_str = '(((mode == `MODE_scatter@THREAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 56) || (vecidx == 54) || (vecidx == 42) || (vecidx == 48) || (vecidx == 43) || (vecidx == 60) || (vecidx == 61) || (vecidx == 62) || (vecidx == 63) || (vecidx == 49) || (vecidx == 52) || (vecidx == 53) || (vecidx == 24) || (vecidx == 25) || (vecidx == 26) || (vecidx == 27) || (vecidx == 20) || (vecidx == 21) || (vecidx == 22) || (vecidx == 23) || (vecidx == 46) || (vecidx == 47) || (vecidx == 44) || (vecidx == 45) || (vecidx == 28) || (vecidx == 29) || (vecidx == 40) || (vecidx == 41) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8) || (vecidx == 51) || (vecidx == 39) || (vecidx == 38) || (vecidx == 59) || (vecidx == 58) || (vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 17) || (vecidx == 16) || (vecidx == 19) || (vecidx == 18) || (vecidx == 31) || (vecidx == 30) || (vecidx == 37) || (vecidx == 36) || (vecidx == 35) || (vecidx == 34) || (vecidx == 33) || (vecidx == 55) || (vecidx == 32) || (vecidx == 57) || (vecidx == 50)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'mode': regs['MODE_scatter']['THREAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U8_H1'], 'vecidx': 42 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == mode `MODE_scatter@THREAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || || [ == vecidx 56 ] [ == vecidx 54 ] [ == vecidx 42 ] [ == vecidx 48 ] [ == vecidx 43 ] [ == vecidx 60 ] [ == vecidx 61 ] [ == vecidx 62 ] [ == vecidx 63 ] [ == vecidx 49 ] [ == vecidx 52 ] [ == vecidx 53 ] [ == vecidx 24 ] [ == vecidx 25 ] [ == vecidx 26 ] [ == vecidx 27 ] [ == vecidx 20 ] [ == vecidx 21 ] [ == vecidx 22 ] [ == vecidx 23 ] [ == vecidx 46 ] [ == vecidx 47 ] [ == vecidx 44 ] [ == vecidx 45 ] [ == vecidx 28 ] [ == vecidx 29 ] [ == vecidx 40 ] [ == vecidx 41 ] [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] [ == vecidx 5 ] [ == vecidx 4 ] [ == vecidx 7 ] [ == vecidx 6 ] [ == vecidx 9 ] [ == vecidx 8 ] [ == vecidx 51 ] [ == vecidx 39 ] [ == vecidx 38 ] [ == vecidx 59 ] [ == vecidx 58 ] [ == vecidx 11 ] [ == vecidx 10 ] [ == vecidx 13 ] [ == vecidx 12 ] [ == vecidx 15 ] [ == vecidx 14 ] [ == vecidx 17 ] [ == vecidx 16 ] [ == vecidx 19 ] [ == vecidx 18 ] [ == vecidx 31 ] [ == vecidx 30 ] [ == vecidx 37 ] [ == vecidx 36 ] [ == vecidx 35 ] [ == vecidx 34 ] [ == vecidx 33 ] [ == vecidx 55 ] [ == vecidx 32 ] [ == vecidx 57 ] [ == vecidx 50 ] ] ]')

    e_str = '(((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U4_B3))) -> (((vecidx == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'mode': regs['MODE_scatter']['QUAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U4_B3'], 'vecidx': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == mode `MODE_scatter@QUAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U4_B3 ] ] ] [ [ [ == vecidx 0 ] ] ]')

    e_str = '(((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U16)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 11) || (vecidx == 10) || (vecidx == 13) || (vecidx == 12) || (vecidx == 15) || (vecidx == 14) || (vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6) || (vecidx == 9) || (vecidx == 8)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'mode': regs['MODE_scatter']['QUAD'], 'elsize':regs['ELSIZE']['U16'], 'idxsize': regs['IDXSIZE_scatter']['U8_H1'], 'vecidx': 11 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == mode `MODE_scatter@QUAD ] ] [ [ == elsize `ELSIZE@U16 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || || || || || || || || || [ == vecidx 11 ] [ == vecidx 10 ] [ == vecidx 13 ] [ == vecidx 12 ] [ == vecidx 15 ] [ == vecidx 14 ] [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] [ == vecidx 5 ] [ == vecidx 4 ] [ == vecidx 7 ] [ == vecidx 6 ] [ == vecidx 9 ] [ == vecidx 8 ] ] ]')

    e_str = '(((mode == `MODE_scatter@QUAD)) && ((elsize == `ELSIZE@U8)) && ((idxsize == `IDXSIZE_scatter@U8_H1))) -> (((vecidx == 1) || (vecidx == 0) || (vecidx == 3) || (vecidx == 2) || (vecidx == 5) || (vecidx == 4) || (vecidx == 7) || (vecidx == 6)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['scatter_'].eval)
    res = expr( Isolator.unpack_args( {'mode': regs['MODE_scatter']['QUAD'], 'elsize':regs['ELSIZE']['U8'], 'idxsize': regs['IDXSIZE_scatter']['U8_H1'], 'vecidx': 3 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '-> [ && && [ [ == mode `MODE_scatter@QUAD ] ] [ [ == elsize `ELSIZE@U8 ] ] [ [ == idxsize `IDXSIZE_scatter@U8_H1 ] ] ] [ [ || || || || || || || [ == vecidx 1 ] [ == vecidx 0 ] [ == vecidx 3 ] [ == vecidx 2 ] [ == vecidx 5 ] [ == vecidx 4 ] [ == vecidx 7 ] [ == vecidx 6 ] ] ]')

    e_str = '(((Sb == 0)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['hadd2_F32i_'].eval)
    res = expr( Isolator.unpack_args( {'Sb': 0 }))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res == True)
    assert(expr.preorder_str == '[ [ [ == Sb 0 ] ] ]')

    result, all_enc_inds, all_format, args = Isolator.parse_sm(120)
    regs = result['REGISTERS']

    e_str = 'Pg -> e'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['atomg_int__RaNonRZ'].eval)
    res1 = expr( Isolator.unpack_args( {'Pg': 1, 'e': 1 }))
    assert(res1 == True)
    res2 = expr( Isolator.unpack_args( {'Pg': 1, 'e': 0 }))
    assert(res2 == False)
    res3 = expr( Isolator.unpack_args( {'Pg': 0, 'e': 1 }))
    assert(res3 == True)
    res4 = expr( Isolator.unpack_args( {'Pg': 0, 'e': 0 }))
    assert(res4 == True)

    e_str = 'TABLES_mem_0(sem,sco,private)'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['atomg_int__RaNonRZ'].eval)
    res1 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {2}, 'sco':{5}, 'private': {1}} ))
    assert(res1 == 10)
    res2 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {3}, 'sco':{5}, 'private': {0}} ))
    assert(res2 == 12)
    res3 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {2}, 'sco':{3}, 'private': {0}} ))
    assert(res3 == 7)

    e_str = '(DEFINED TABLES_mem_0(sem,sco,private)) && ((TABLES_mem_0(sem,sco,private) != 10) && (TABLES_mem_0(sem,sco,private) != 12))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['atomg_int__RaNonRZ'].eval)
    res1 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {2}, 'sco':{5}, 'private': {1}} ))
    assert(res1 == False)
    res2 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {3}, 'sco':{5}, 'private': {0}} ))
    assert(res2 == False)
    res3 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {2}, 'sco':{3}, 'private': {0}} ))
    assert(res3 == True)

    e_str = '(((op == `OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD@SAFEADD)))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['atomg_int__RaNonRZ'].eval)
    res1 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['ADD'], 'sem': {2}, 'sco':{5}, 'private': {1}} ))
    assert(res1 == False)
    res2 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['MIN'], 'sem': {3}, 'sco':{5}, 'private': {0}} ))
    assert(res2 == False)
    res3 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {2}, 'sco':{3}, 'private': {0}} ))
    assert(res3 == True)

    e_str = '(((op == `OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD@SAFEADD))) -> (((DEFINED TABLES_mem_0(sem,sco,private)) && ((TABLES_mem_0(sem,sco,private) != 10) && (TABLES_mem_0(sem,sco,private) != 12))))'
    expr:SASS_Expr = SASS_Expr(e_str, *args)
    expr, evaled = expr.finalize(all_format['atomg_int__RaNonRZ'].eval)
    res1 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {2}, 'sco':{5}, 'private': {1}} ))
    assert(res1 == False)
    res2 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {3}, 'sco':{5}, 'private': {0}} ))
    assert(res2 == False)
    res3 = expr( Isolator.unpack_args( {'op': regs['OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD']['SAFEADD'], 'sem': {2}, 'sco':{3}, 'private': {0}} ))
    # f = (oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_And, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Register, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace, oo.Op_Implication, oo.Op_LBrace, oo.Op_LBrace, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_Or, oo.Op_LBrace, oo.Op_Alias, oo.Op_Equal, oo.Op_Int, oo.Op_RBrace, oo.Op_RBrace, oo.Op_RBrace)
    assert(res3 == True)
    assert(expr.preorder_str == '-> [ [ [ == op `OP_ADD_MIN_MAX_INC_DEC_AND_OR_XOR_EXCH_SAFEADD@SAFEADD ] ] ] [ [ && [ DEFINED TABLES_mem_0 [ sem ] [ sco ] [ private ] ] [ && [ != TABLES_mem_0 [ sem ] [ sco ] [ private ] 10 ] [ != TABLES_mem_0 [ sem ] [ sco ] [ private ] 12 ] ] ] ]')
