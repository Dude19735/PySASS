from __future__ import annotations
import os
import datetime
import random
import itertools as itt
from py_sass import py_sass_parse_cash_str
from py_sass import SASS_Expr
from py_sass import SASS_Expr_Dec
from py_sass import TT_Instruction
from py_sass import TT_Param, TT_Cash, TT_Opcode, TT_List
from py_sass import SM_SASS
from py_sass import SM_Cu_Details
from py_sass import SASS_Class
from py_sass_ext import BitVector
from . import _config as sp
from ._instr_cubin_repr_classes import *

"""
This file contains a bunch of library methods for Instr_CuBin_Repr.
"""

class Instr_CuBin_Repr_Lib:
    PRED:str = 'pred'
    OPCODE:str = 'opcode'
    REGS:str = 'regs'
    CASHS:str = 'cashs'
    CONSTS:str = 'consts'
    EVAL:str = 'eval'

    # Replacement cashes for the ones that are encoded as fixed values
    CASH_REPS = {
        "req_bit_set": "& REQ:req = BITSET(6/0x0000):req_bit_set",
        "src_rel_sb": "& RD:rd = UImm(3/0x7):src_rel_sb",
        "dst_wr_sb": "& WR:wr = UImm(3/0x7):dst_wr_sb",
        "usched_info": "? USCHED_INFO:usched_info",
        "batch_t": "? BATCH_T(NOP):batch_t",
        "pm_pred": "? PM_PRED(PMN):pm_pred"
    }

    @staticmethod
    def create_id(prefix:str):
        t1 = datetime.datetime.now().timestamp()
        random.seed(datetime.datetime.now().timestamp())
        t2 = random.randint(0,999999)
        random.seed(datetime.datetime.now().timestamp())
        t3 = random.randint(0,999999)
        id = "{0}{1}-{2}-{3}".format(prefix, str(t1).replace('.','-'), t2, t3)
        return id

    @staticmethod
    def sort_by(entry:list|SASS_Expr_Dec):
        if isinstance(entry,list): 
            if isinstance(entry[0], list): return 1000 + len(entry)
            else: return len(entry)
        return 0

    @staticmethod
    def create_universe_bodies(instr_index:int, sass:SM_SASS, class_name:str, instr_bits:BitVector, s_encs:list):
        class_:SASS_Class = sass.sm.classes_dict[class_name]
        enc_vals = dict()
        res = []
        for encs in s_encs:
            expr:SASS_Expr = encs['alias']
            enc_ind:list = encs['code_ind']
            if expr.startswith_notEnc(): continue
            cur = expr.inv(sass.sm.details, instr_bits, enc_ind, enc_vals, encs['code_name'])
            enc_vals = Instr_CuBin_Repr_Lib.add_to_enc_vals(cur, enc_vals)        
            if isinstance(cur, list) and not isinstance(cur[0], list):
                if len(cur) != 2: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                res.append(cur[0])
                res.append(cur[1])
            elif isinstance(cur, list):
                res.append(cur)
            elif isinstance(cur, SASS_Expr_Dec):
                res.append(cur)
            else:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # sort such that lists are last and in ascending order with respect to length
        sres = sorted(res, key=lambda x:Instr_CuBin_Repr_Lib.sort_by(x))

        # Calculate all the different universes
        universes = []
        # regular stuff
        regs = [i for i in sres if not isinstance(i,list)]
        c99 = list(itt.product(*[i for i in sres if isinstance(i,list)]))
        # add a regs to each c99
        for hunter in c99:
            full_regiment = []
            full_regiment.extend(regs)
            for omega in hunter:
                for tec in omega:
                    full_regiment.append(tec)
            universes.append(full_regiment)

        tt_format:TT_Instruction = class_.FORMAT
        pred_a = []
        if tt_format.pred: pred_a.extend(tt_format.pred.get_enc_alias())
        
        opcode_a:list = tt_format.opcode.get_enc_alias()
        if not isinstance(opcode_a, list): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        r:TT_Param
        param_a = []
        for r in tt_format.regs: param_a.extend(r.get_enc_alias())

        c:TT_Cash
        cash_a = []
        for c in tt_format.cashs: cash_a.extend(c.get_enc_alias())

        t_universes = []
        for universe in universes:
            new_universe = Instr_CuBin_Repr_Lib.transform_universe(sass, class_name, pred_a, opcode_a, param_a, cash_a, universe)
            
            # collect all extensions for later
            extension_collection:list = list(new_universe[Instr_CuBin_Repr_Lib.OPCODE].ext)
            for x in new_universe[Instr_CuBin_Repr_Lib.REGS]:
                extension_collection.extend(x.ext)
                if isinstance(x, Instr_CuBin_Param_L) or isinstance(x, Instr_CuBin_Param_Attr):
                    extension_collection.extend(list(itt.chain.from_iterable(i.ext for i in x.param1)))
                    extension_collection.extend(list(itt.chain.from_iterable(i.ext for i in x.param2)))
            new_universe[Instr_CuBin_Repr_Lib.EVAL] = Instr_CuBin_Eval(instr_index, class_name, sass, enc_vals, new_universe[Instr_CuBin_Repr_Lib.PRED], new_universe[Instr_CuBin_Repr_Lib.REGS], new_universe[Instr_CuBin_Repr_Lib.CASHS], new_universe[Instr_CuBin_Repr_Lib.CONSTS], extension_collection, new_universe[Instr_CuBin_Repr_Lib.OPCODE])
            t_universes.append(new_universe)

        # Check if all universes have the same sized src and dst
        src_sizes = {42} #set(tuple(sorted([(k,v) for k,v in u['eval'].evaled_src_sizes.items()], key=lambda x:x[0])) for u in t_universes)
        dst_sizes = {42} #set(tuple(sorted([(k,v) for k,v in u['eval'].evaled_dst_sizes.items()], key=lambda x:x[0])) for u in t_universes)
        if not len(src_sizes) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not len(dst_sizes) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return t_universes

    @staticmethod
    def transform_universe(sass:SM_SASS, class_name:str, pred_a:list, opcode_a:list, param_a:list, cash_a:list, universe:list):
        class_:SASS_Class = sass.sm.classes_dict[class_name]
        tt_format:TT_Instruction = class_.FORMAT
        instr_code:str = class_.get_opcode_instr()
        details:SM_Cu_Details = sass.sm.details
        mm:int = sass.max_config_fields_for_sm
        config_bits:dict = sass.config_bits

        const = [i for i in universe if i.is_const()]
        alias = [i for i in universe if i.is_alias()]
        opcode = [i for i in universe if i.is_opcode()]
        
        pred_a_vals = {i.alias():i for i in alias if i.alias() in pred_a}
        opcode_a_vals = {i.alias():i for i in alias if i.alias() in opcode_a}
        param_a_vals = {i.alias():i for i in alias if i.alias() in param_a}
        cash_a_vals = {i.alias():i for i in alias if i.alias() in cash_a}

        enc_vals_alias = set(itt.chain.from_iterable(e['alias'].get_alias_names_set() for e in class_.ENCODING))
        pred = None
        if tt_format.pred: pred = Instr_CuBin_Pred(tt_format.pred, pred_a_vals, details, enc_vals_alias)
        
        opcode = Instr_CuBin_Opcode(opcode[0], tt_format.opcode, instr_code, opcode_a_vals, details, enc_vals_alias, class_)
        regs = []
        p:TT_Param
        for index,p in enumerate(tt_format.regs):
            if isinstance(p, TT_List): regs.append(Instr_CuBin_Param_L(p, param_a_vals, index, details, enc_vals_alias, class_))
            elif p.attr == []: regs.append(Instr_CuBin_Param_RF(p, param_a_vals, index, details, enc_vals_alias, class_))
            else: regs.append(Instr_CuBin_Param_Attr(p, param_a_vals, index, details, enc_vals_alias, class_))

        cashs = []
        for c_ind,c in enumerate(tt_format.cashs): cashs.append(Instr_CuBin_Cash(c, cash_a_vals, c_ind, details, enc_vals_alias))

        consts = []
        for c_ind,c in enumerate(const): consts.append(Instr_CuBin_Const(c, c_ind, details, enc_vals_alias))

        # Check if we are missing some cash configs. If we are, search for the corresponding values
        # in the consts and create cashes from them.
        # NOTE: if some cashes are missing, they have to be defined as constant values. Otherwise it's a bug
        # For example:
        #   BITS_6_121_116_req_bit_set=req_bit_set;
        #   BITS_3_115_113_src_rel_sb=VarLatOperandEnc(src_rel_sb);
        #   BITS_3_112_110_dst_wr_sb=7;
        #   BITS_8_124_122_109_105_opex=TABLES_opex_0(batch_t,usched_info);
        # => BITS_3_112_110_dst_wr_sb is 7 and will show up here in the consts list. It has to be transfered to a cash
        # containing a WR
        if len(cashs) < mm:
            index_offset = len(cashs)
            enc_names = set(enc['code_name'] for enc in class_.ENCODING)
            outer_res = details.as_dict()
            to_rem = []
            cash_local_vals = {}
            
            if not enc_names.intersection(config_bits): raise Exception(sp.CONST__ERROR_UNEXPECTED)

            cash_strs = []
            cash_consts = []
            for c in consts:
                if c.code_name in config_bits:
                    to_rem.append(c)
                    enc_vals_name = config_bits[c.code_name]
                    cash_strs.append(Instr_CuBin_Repr_Lib.CASH_REPS[enc_vals_name])
                    cash_consts.append(c)
                    cash_local_vals[enc_vals_name] = c.value

            cash_str = "$( { " + " } )$ $( { ".join(cash_strs) + " } )$"
            tt_terms:list = py_sass_parse_cash_str(class_.class_name, cash_str, outer_res)
            tt_cashs = [TT_Cash(class_.class_name, tt_term, details) for tt_term in tt_terms]
            
            tt_const:Instr_CuBin_Const
            for tt_ind,(tt_cash,tt_const) in enumerate(zip(tt_cashs, cash_consts)):
                new_cash = Instr_CuBin_Cash(tt_cash, cash_local_vals, tt_ind+index_offset, details, enc_vals_alias, augment=True, const_link=tt_const)
                cashs.append(new_cash)
                tt_const.add_cash_link(new_cash)

            # Make sure we have a full set of cash configs now
            if not len(cashs) == mm: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            for r in to_rem: consts.remove(r)

        return {Instr_CuBin_Repr_Lib.PRED:pred, Instr_CuBin_Repr_Lib.OPCODE:opcode, Instr_CuBin_Repr_Lib.REGS:regs, Instr_CuBin_Repr_Lib.CASHS:cashs, Instr_CuBin_Repr_Lib.CONSTS:consts}

    @staticmethod
    def __add_to_enc_vals(cur:SASS_Expr_Dec, enc_vals:dict):
        if cur.is_const():
            enc_vals[cur.code_name] = cur.sb
        # Add stuff we could use in .inv to enc_vals
        if cur.is_alias():
            enc_vals[cur.alias()] = cur.sb
        # ... deal with duality for the extensions where sometimes the alias 
        # and sometimes the register name is use din the encoding
        if cur.has_parent_register():
            parent = cur.parent_register()
            # Don't use register parents like 'Register', 'Predicate' or 'NonZeroRegister'
            # because they are only used for real register operands, never for extensions
            if not parent in NON_FUNC_REG:
                enc_vals[cur.parent_register()] = cur.sb
        return enc_vals
    
    @staticmethod
    def add_to_enc_vals(cur:SASS_Expr_Dec|list, enc_vals:dict):
        if isinstance(cur, SASS_Expr_Dec):
            enc_vals = Instr_CuBin_Repr_Lib.__add_to_enc_vals(cur, enc_vals)
        elif isinstance(cur, list):
            for c in cur:
                if isinstance(c, list):
                    for v in c: enc_vals = Instr_CuBin_Repr_Lib.__add_to_enc_vals(v, enc_vals)
                else: enc_vals = Instr_CuBin_Repr_Lib.__add_to_enc_vals(c, enc_vals)
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)
        return enc_vals

    @staticmethod
    def sortby_encs(expr:SASS_Expr) -> int:
        val = 0
        if expr.startswith_register(): return val
        val += 1
        if expr.startswith_int(): return val
        val += 1
        if expr.startswith_constant(): return val
        val += 1
        if expr.is_scale(): return val
        val += 1
        if expr.startswith_alias(): return val
        val += 1
        if expr.startswith_atOp(): return val
        val += 1
        if expr.startswith_identical(): return val
        val += 1
        if expr.startswith_table(): return val
        val += 1
        if expr.startswith_ConstBankAddressX(): return val
        val += 1
        if expr.startswith_convertFloat(): return val
        return val
    