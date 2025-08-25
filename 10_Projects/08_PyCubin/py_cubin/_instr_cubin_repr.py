from __future__ import annotations
import termcolor as tc
import typing
import itertools as itt
from py_sass import SM_SASS
from py_sass import SM_Latency
from py_sass import SM_XX_Instr_Desc
from py_sass import SASS_Class
from py_sass_ext import SASS_Bits
from py_sass_ext import BitVector
from . import _config as sp
from ._instr_cubin import Instr_CuBin
from ._instr_cubin_repr_lib import Instr_CuBin_Repr_Lib
from ._instr_cubin_repr_classes import *
from ._instr_cubin_db_proxy import Db_InstrClassDef_Proxy, Db_InstrLatency_Proxy, Db_Instr_Proxy, Db_Universe_Proxy

"""
This file contains Instr_CuBin_Repr which is the main class that can contain one
decoded instruction.
"""

class Instr_CuBin_Repr:
    @staticmethod
    def create_from_enc_vals(sass:SM_SASS, instr_index:int, bin_offset_hex:str, kernel_offset_hex:str, class_name:str, enc_vals:dict) -> Instr_CuBin_Repr:
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_index, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bin_offset_hex, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(kernel_offset_hex, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)

        bv:BitVector = Instr_CuBin.instr_assemble_to_bv(sass, class_name, enc_vals)
        return Instr_CuBin_Repr.create_from_bits(sass, instr_index, bin_offset_hex, kernel_offset_hex, bv, class_name)
    
    @staticmethod
    def create_from_bits(sass:SM_SASS, instr_index:int, bin_offset_hex:str, kernel_offset_hex:str, bv:BitVector, class_name:str|None = None) -> Instr_CuBin_Repr:
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_index, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bin_offset_hex, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(kernel_offset_hex, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bv, BitVector): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_name, str|None): raise Exception(sp.CONST__ERROR_ILLEGAL)

        # If we really create directly from bits, we have to figure out which instruction class we are creating
        # class_name is ideally None if this method is called from create_from_enc_vals, because to assemble an instruction from enc_vals
        # we need the class_name.
        cn:str|None = class_name
        if cn is None: 
            cn = Instr_CuBin.instr_bits_to_class([bv], sass, [])[0]
        i:int = instr_index
        u = Instr_CuBin_Repr("{0}-{1}".format(Instr_CuBin_Repr_Lib.create_id('i'), i), sass, i, bin_offset_hex, kernel_offset_hex, bv, cn)
        u.compute_instr_universes(sass)
        u.all_enc_vals
        return u

    def __init__(self, id, sass:SM_SASS, instr_index:int, bin_offset_hex:str, kernel_offset_hex:str, instr_bits:BitVector, class_name:str): #, enc_vals:dict={}):
        self.__instr_index = instr_index
        self.__instr_bits = instr_bits
        self.__class_name = class_name
        self.__head_only = True
        self.__class:SASS_Class = sass.sm.classes_dict[class_name]
        self.__misc = Instr_CuBin_Misc(instr_index, int(bin_offset_hex, 16), int(kernel_offset_hex, 16), class_name, instr_bits, sass)
        self.__universes = sorted(self.__class.ENCODING, key=lambda x: Instr_CuBin_Repr_Lib.sortby_encs(x['alias']))
        self.__id = id
        self.__kernel_offset_hex = kernel_offset_hex
        self.__used_regs = dict()
        self.__used_alias = dict()

        instr_code:str = self.__class.get_opcode_instr()
        if instr_code in sass.sm.all_instr_desc: desc = sass.sm.all_instr_desc[instr_code]
        else: desc = "N/A"

        self.__desc:SM_XX_Instr_Desc|str = desc
        self.__instr_code = instr_code
        # self.__used_enc_vals = True if enc_vals != {} else False
        # self.__input_enc_vals = enc_vals
        self.__all_enc_vals = []
        self.__all_enc_vals_augmentations = []

    @property
    def instr_index(self): return self.__instr_index
    @property
    def instr_bits(self): return self.__instr_bits
    @property
    def class_name(self): return self.__class_name
    @property
    def universes(self): return self.__universes
    @property
    def head(self): return self.__head_only
    @property
    def class_(self) -> SASS_Class: return self.__class
    @property
    def desc(self) -> SM_XX_Instr_Desc|str: return self.__desc
    @property
    def misc(self): return self.__misc
    @property
    def id(self): return self.__id
    @property
    def kernel_offset_hex(self): return self.__kernel_offset_hex
    @property
    def enc_vals__used_regs(self): return self.__used_regs
    @property
    def enc_vals__used_alias(self): return self.__used_alias
    @property
    def all_enc_vals(self): return self.__all_enc_vals
    @property
    def all_enc_vals_augmentations(self): return self.__all_enc_vals_augmentations

    def new_with_instr_index(self, sass:SM_SASS, instr_index:int, bin_offset_hex:str, kernel_offset_hex:str) -> Instr_CuBin_Repr:
        new:Instr_CuBin_Repr = self.__new__(self.__class__)
        new.__instr_index = instr_index
        new.__instr_bits = self.__instr_bits
        new.__class_name = self.__class_name
        new.__head_only = self.__head_only
        new.__class = self.__class
        # create a new one of these
        new.__misc = Instr_CuBin_Misc(instr_index, int(bin_offset_hex, 16), int(kernel_offset_hex, 16), new.__class_name, new.__instr_bits, sass)
        
        new.__universes = self.__universes
        new.__id = self.__id
        new.__kernel_offset_hex = kernel_offset_hex
        new.__used_regs = self.__used_regs
        new.__used_alias = self.__used_alias
        new.__desc = self.__desc
        new.__instr_code = self.__instr_code
        new.__all_enc_vals = self.__all_enc_vals
        new.__all_enc_vals_augmentations = self.__all_enc_vals_augmentations

        return new

    def compute_enc_vals(self) -> typing.Tuple[list, list]:
        all_enc_vals = []
        all_enc_vals_augmentations = []
        for u in self.__universes:
            enc_vals = dict()
            enc_vals_augmentations = dict()
            if u[Instr_CuBin_Repr_Lib.PRED] is not None:
                enc_vals |= u[Instr_CuBin_Repr_Lib.PRED].enc_vals()
            enc_vals |= u[Instr_CuBin_Repr_Lib.OPCODE].enc_vals()
            for r in u[Instr_CuBin_Repr_Lib.REGS]: enc_vals |= r.enc_vals()
            c:Instr_CuBin_Cash
            for c in u[Instr_CuBin_Repr_Lib.CASHS]: 
                enc_vals |= c.enc_vals()
                enc_vals_augmentations |= c.enc_vals_augmentations()

            all_enc_vals.append(enc_vals)
            all_enc_vals_augmentations.append(enc_vals_augmentations)
        self.__all_enc_vals = all_enc_vals
        self.__all_enc_vals_augmentations = all_enc_vals_augmentations
        return all_enc_vals, all_enc_vals_augmentations

    def compute_instr_universes(self, sass:SM_SASS) -> typing.Tuple[dict, dict]:
        if not self.__head_only == True: return self.__used_regs, {}
        self.__universes = Instr_CuBin_Repr_Lib.create_universe_bodies(self.__instr_index, sass, self.__class_name, self.__instr_bits, self.__universes)
        self.__head_only = False
        all_u_regs = []

        for u in self.__universes:
            regs = u[Instr_CuBin_Repr_Lib.REGS]
            all_u_regs.append([r.reg() for r in regs])
        all_u_regs = list(itt.chain.from_iterable(all_u_regs))

        used_regs = dict()
        used_alias = dict()
        for u_regs in all_u_regs:
            ur:Instr_Reg
            for ur in u_regs:
                if not ur: continue
                reg_name = ur.value_name
                
                if reg_name not in used_regs: used_regs[reg_name] = set()
                # sb: SASS_Bits, v: int
                used_regs[reg_name].add(ur.sass_bits)
                
                if reg_name not in used_alias: used_alias[reg_name] = set()
                used_alias[reg_name].add(ur.alias)
        self.__used_regs = used_regs
        self.__used_alias = used_alias

        self.compute_enc_vals()
        return self.__used_regs, self.__used_alias

    def __str__(self):
        desc:SM_XX_Instr_Desc|str = self.__desc
        if not isinstance(desc, str): desc = desc.doc()

        res = "Class: " +  self.class_name + "\n"
        for ind,u in enumerate(self.universes):
            res += "U" + str(ind) + ": "
            if u[Instr_CuBin_Repr_Lib.PRED]: res += str(u[Instr_CuBin_Repr_Lib.PRED]) + " "
            res += str(u[Instr_CuBin_Repr_Lib.OPCODE])
            res += " " + ", ".join(str(r) for r in u[Instr_CuBin_Repr_Lib.REGS])
            res += "\n      " + ", ".join(str(c) for c in u[Instr_CuBin_Repr_Lib.CASHS])
            if u[Instr_CuBin_Repr_Lib.CONSTS]: res += "\n      " + ", ".join(str(c) for c in u[Instr_CuBin_Repr_Lib.CONSTS])
            res += "\n      " + str(self.__misc)
            res += "\n      " + desc
            if ind < len(self.universes)-1: res += "\n"
        return res
    
    def to_db(self, sass:SM_SASS) -> Db_Instr_Proxy:
        if not isinstance(self.__desc, str): 
            class_desc = self.__desc.desc
            class_cat:str = self.__desc.category
        else: 
            class_desc = self.__desc
            class_cat:str = "Not documented"

        universes = []
        instr_codes = set()
        class_:SASS_Class = self.__class
        for ind,u in enumerate(self.universes):
            if u[Instr_CuBin_Repr_Lib.PRED]: u_pred:Instr_CuBin_Pred|None = u[Instr_CuBin_Repr_Lib.PRED]
            else: u_pred:Instr_CuBin_Pred|None = None
            u_opcode:Instr_CuBin_Opcode = u[Instr_CuBin_Repr_Lib.OPCODE]
            u_regs:typing.List[Instr_CuBin_Param_L|Instr_CuBin_Param_RF|Instr_CuBin_Param_Attr] = u[Instr_CuBin_Repr_Lib.REGS]
            u_cashs:typing.List[Instr_CuBin_Cash] = u[Instr_CuBin_Repr_Lib.CASHS]
            u_consts:typing.List[Instr_CuBin_Const] = u[Instr_CuBin_Repr_Lib.CONSTS]
            u_eval:Instr_CuBin_Eval = u[Instr_CuBin_Repr_Lib.EVAL]

            instr_parts = []
            if u_pred: instr_parts.append(u_pred.to_db(class_))
            instr_parts.append(u_opcode.to_db(class_))
            reg:Instr_CuBin_Param_L|Instr_CuBin_Param_RF|Instr_CuBin_Param_Attr
            for reg in u_regs: instr_parts.append(reg.to_db(class_))
            cash:Instr_CuBin_Cash
            for cash in u_cashs: instr_parts.append(cash.to_db(class_))
            const:Instr_CuBin_Const
            for const in u_consts: instr_parts.append(const.to_db(class_))

            instr_eval = u_eval.to_db(class_)

            universes.append(Db_Universe_Proxy.create(ind, "", instr_parts, instr_eval, ''))
            instr_codes.add(u_opcode.instr_code)

        indent = 3
        instr_class_def = [
            Db_InstrClassDef_Proxy.create(Db_InstrClassDef_Proxy.Type_format, 0, class_.format_to_str(indent), 'The FORMAT part of the instruction class'),
            Db_InstrClassDef_Proxy.create(Db_InstrClassDef_Proxy.Type_conditions, 1, class_.conditions_to_str(indent), 'The CONDITIONS part of the instruction class'),
            Db_InstrClassDef_Proxy.create(Db_InstrClassDef_Proxy.Type_properties, 2, class_.properties_to_str(indent), 'The PROPERTIES part of the instruction class'),
            Db_InstrClassDef_Proxy.create(Db_InstrClassDef_Proxy.Type_predicates, 3, class_.predicates_to_str(indent), 'The PREDICATES part of the instruction class'),
            Db_InstrClassDef_Proxy.create(Db_InstrClassDef_Proxy.Type_opcodes, 4, class_.opcodes_to_str(indent), 'The OPCODES part of the instruction class'),
            Db_InstrClassDef_Proxy.create(Db_InstrClassDef_Proxy.Type_encoding, 5, class_.encoding_to_str(), 'The ENCODING part of the instruction class')
        ]
        latencies = Db_InstrLatency_Proxy.create(SM_Latency.matches_to_table(sass.latencies.match(class_), lambda x: True))

        misc = self.misc.to_db(class_)
        instr = Db_Instr_Proxy.create(
            self.instr_index, self.__instr_code, self.class_name, class_desc, class_cat, '', 
            universes, instr_class_def, latencies, misc)

        return instr
