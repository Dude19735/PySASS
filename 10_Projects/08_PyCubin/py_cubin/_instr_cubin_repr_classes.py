from __future__ import annotations
import itertools as itt
import termcolor as tc
import typing
from py_sass import Op_AtAbs, Op_AtInvert, Op_AtNegate, Op_AtNot, Op_AtSign
from py_sass import SASS_Expr
from py_sass import SASS_Expr_Dec
from py_sass import TT_Reg, TT_Func, TT_Param, TT_Ext, TT_Cash, TT_Opcode, TT_Pred, TT_List, TT_Base
from py_sass import TT_OpAtNegate, TT_OpAtNot, TT_OpAtInvert, TT_OpAtSign, TT_OpAtAbs
from py_sass import SM_SASS
from py_sass import SM_Cu_Details
from py_sass import SASS_Class
from py_sass_ext import BitVector
from py_sass_ext import SASS_Bits
from . import _config as sp
from ._instr_reg import Instr_Reg
from ._instr_cubin_db_proxy import Db_UniverseComponent_Proxy, Db_UniverseEvalEncoding_Proxy, Db_UniverseEvalRegisters_Proxy
from ._instr_cubin_db_proxy import Db_UniverseEvalPredicate_Proxy, Db_InstrMisc_Proxy, Db_UniverseEval_Proxy

"""
This file contains all classes that are necessary to generate one
Instr_CuBin_Repr.
"""

if 'NON_FUNC_REG' not in locals(): 
    NON_FUNC_REG = {'Predicate', 'UniformPredicate', 'Register','SpecialRegister','Predicate','BarrierRegister','NonZeroRegister','ZeroRegister', 'UniformRegister', 'NonZeroUniformRegister', 'ZeroUniformRegister'}

class Instr_CuBin_B:
    """Base class for a decoded field.
    """    
    MODE__HEX = 0
    MODE__BIN = 1
    MODE__DEC = 2
    def __init__(self, value, name, tt, index:int, details:SM_Cu_Details, enc_vals_alias:set):
        self.__value:SASS_Expr_Dec = value
        self.__name:str = name
        self.__tt:TT_Base = tt
        self.__index:int = index
        self.__mode:int = Instr_CuBin_B.MODE__HEX

    @property
    def value(self) -> SASS_Expr_Dec: 
        """Contains all decoded values as decimal and SASS_Bits as well as misc information such as the parent_register, type and attributes of a decoded field.

        :return: the raw decoding information for one instruction field.
        :rtype: SASS_Expr_Dec
        """        
        return self.__value
    @property
    def name(self) -> str: 
        """Contains the name of a decoded field.
        
        Usually this is the encoding name used in the ENCODINGS stage of an instruction class. If it's an opcode, the name is the opcode.

        For example:
        * Pg@not, Pg
        * LO, fmt, Rd, reuse_src_a, REQ, USCHED_INFO
        * IMAD
        * Sc_bank, Sc_addr, Sc

        Sometimes the name is empty. For example, if the current field represents a list or an attribute of something.

        :return: a string that either contains a name as outlined in the examples or ''
        :rtype: str
        """        
        return self.__name
    @property
    def tt(self) -> TT_Base: 
        """Usually contains the associated TT_Pred, TT_Cash, TT_Reg, ... out of tt_terms.py with all attached information. In some cases, it's None

        :return: associated object out of tt_terms.py or None
        :rtype: TT_Base
        """        
        return self.__tt
    @property
    def index(self) -> int: 
        """Always contains the index of the current field, relative to the hierarchy the field is in.

        For example:
        * if the current field is part of a list, the index is relative to the list (i.e. the first elem of the list has index 0)
        * if the current field is a source/dest register, the index is relative to the operands, meaning, the destination register (if present) has index 0

        :return: an integer with the index of the current field relative to the containing structure
        :rtype: int
        """        
        return self.__index
    @property
    def mode(self) -> int: 
        """Contains a value that is always Instr_CuBin_B.MODE__HEX and generally not used and irrelevant.

        :return: always Instr_CuBin_B.MODE__HEX
        :rtype: int
        """        
        return self.__mode

    def reg(self) -> typing.List[Instr_Reg]:
        if self.tt is None: return []
        if not isinstance(self.tt.value, TT_Reg): return [] # type: ignore
        tt:TT_Reg = self.tt.value # type: ignore
        reg_name = str(tt.value)
        reg_alias = str(tt.alias)
        if reg_name not in NON_FUNC_REG: return []
        return [Instr_Reg(index=self.__index, value_name=reg_name, alias=reg_alias, parent_name=self.value.parent_register(), value_d=self.value.d, sass_bits=self.value.sb)]

    def set_mode(self, mode:int):
        if not mode in (Instr_CuBin_B.MODE__HEX, Instr_CuBin_B.MODE__BIN, Instr_CuBin_B.MODE__DEC): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__mode = mode

    def enc_vals(self):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

class Instr_CuBin_Ext(Instr_CuBin_B):
    """Base class (on top of Instr_CuBin_B) for an extension of a part of an instruction.

    Extensions are for example in IMAD.LO.32 the two designations '.LO' and '.32'.
    """
    def __init__(self, ext:TT_Ext, enc_vals:dict, index:int, details:SM_Cu_Details, enc_vals_alias:set):
        if ext.alias.value in enc_vals_alias:
            self.__enc_alias = ext.alias.value
        elif ext.value.value in enc_vals_alias:
            self.__enc_alias = ext.value.value
        else: self.__enc_alias = None
        if not ext.alias.value in enc_vals:
            # NOTE: at this point we already have the correct instruction class, thus we know all the possible
            # extensions it can have.
            # We have an extension that is only in the instruction definition but not in the encodings
            reg_val = getattr(details.REGISTERS, ext.value.value, False)
            if reg_val == False:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if len(reg_val) == 1: # type: ignore
                super().__init__(None, next(iter(reg_val)), ext, index, details, enc_vals_alias) # type: ignore
            elif ext.value.value == 'ONLY32':
                # some register extension that shows up in the instruction def but not in encoding
                super().__init__(None, "32", ext, index, details, enc_vals_alias)
            elif ext.value.value in ['ONLY64', 'ONLY64_bmov', 'ONLY64_syncs']:
                # some register extension that shows up in the instruction def but not in encoding
                super().__init__(None, "64", ext, index, details, enc_vals_alias)
            elif ext.value.value == 'PSEUDO_OPCODE':
                # some register extension that shows up in the instruction def but not in encoding
                super().__init__(None, "nopseudo_opcode", ext, index, details, enc_vals_alias)
            elif ext.value.value == 'PSEUDO_OP':
                super().__init__(None, "nopseudo_op", ext, index, details, enc_vals_alias)
            elif ext.value.value in ('ONLY256', 'ONLY256_ldcu'):
                super().__init__(None, "256", ext, index, details, enc_vals_alias)
            elif ext.value.value in ('ONLY16832'):
                super().__init__(None, "16832", ext, index, details, enc_vals_alias)
            elif ext.value.value in ('ONLY16864'):
                super().__init__(None, "16864", ext, index, details, enc_vals_alias)
            elif ext.value.value in ('ONLY168128'):
                super().__init__(None, "168128", ext, index, details, enc_vals_alias)
            elif ext.value.value in ('ONLY1X'):
                super().__init__(None, "1X", ext, index, details, enc_vals_alias)
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else:
            super().__init__(enc_vals[ext.alias.value], ext.alias.value, ext, index, details, enc_vals_alias)

        self.__db_proxy = self.__to_db()
        
    @property
    def db_proxy(self): return self.__db_proxy
    @property
    def enc_alias(self): return self.enc_alias
    def enc_vals(self): # type: ignore
        if self.__enc_alias is not None: return {self.__enc_alias:self.value.sb}
        return dict()
        # raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    def __str__(self):
        msg = "/{0}"
        if self.value is not None:
            ext = self.value.register()
            if len(ext) == 1: ext = next(iter(ext))
        else: ext = self.name
        return msg.format(ext)
    def __to_db(self) -> Db_UniverseComponent_Proxy:
        if self.value is not None:
            ext = self.value.register()
            if len(ext) == 1: ext = next(iter(ext))
            else: 
                ext = "{{{0}}}".format(",".join(str(e) for e in ext))
            alias = self.value.alias()
        else: 
            ext = str(self.name)
            alias = str(self.tt.alias) # type: ignore
        return Db_UniverseComponent_Proxy.create(Db_UniverseComponent_Proxy.Type_ext, self.index, alias, self.value, ext, str(self.tt.value.value), self.tt, '', []) # type: ignore

    def to_db(self, class_:SASS_Class) -> Db_UniverseComponent_Proxy:
        return self.__db_proxy

class Instr_CuBin_Op(Instr_CuBin_B):
    """This is the base class for operations (on top of Instr_CuBin_B).

    An operation is for example in [!]Predicate:Pg, the '[!]'. Some source registers have negations '[-]' or abs operators '[||]'.

    Operations are generally encoded with their parent alias and the operation itself, split by an @. For example:
    * [!]Predicate:Pg => '[!]' is encoded as Pg@not
    * [-]Register:Ra => '[-]' is encoded as Ra@negate
    """
    def __init__(self, op:TT_OpAtNegate|TT_OpAtNot|TT_OpAtInvert|TT_OpAtSign|TT_OpAtAbs, enc_vals:dict, index:int, details:SM_Cu_Details, enc_vals_alias:set):
        if not op.alias in enc_vals: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        super().__init__(enc_vals[op.alias], op.alias, op, index, details, enc_vals_alias)
        self.__db_proxy = self.__to_db()
    @property
    def db_proxy(self): return self.__db_proxy
    def __str__(self):
        if self.value.d == 1: return "[{0}]".format(str(self.tt))
        else: return ""
    def __to_db(self) -> Db_UniverseComponent_Proxy|None:
        if self.value.d == 1: return Db_UniverseComponent_Proxy.create(Db_UniverseComponent_Proxy.Type_op, self.index, self.value.alias(), self.value, str(self.tt), self.tt.value, self.tt, '', []) # type: ignore
        else: return None
    def to_db(self, class_:SASS_Class) -> Db_UniverseComponent_Proxy|None:
        return self.__db_proxy

class Instr_CuBin_BE(Instr_CuBin_B):
    """This one represents an instruction part with a base and an extension (B,E).

    For example a register Register:Ra/smd/sz...
    """
    def __init__(self, value, name, tt, ext, index:int, details:SM_Cu_Details, enc_vals_alias:set):
        super().__init__(value, name, tt, index, details, enc_vals_alias)
        self.__ext = ext
    @property
    def ext(self) -> typing.List[Instr_CuBin_Ext]: return self.__ext

class Instr_CuBin_BEO(Instr_CuBin_BE):
    """This represents an instruction part with a base, an extension and an operation (B,E,O).

    For example a register [-]Register:Ra/smd/sz
    """
    def __init__(self, value, name, tt, ext, ops, index:int, details:SM_Cu_Details, enc_vals_alias:set):
        super().__init__(value, name, tt, ext, index, details, enc_vals_alias)
        self.__ops = ops
    @property
    def ops(self) -> typing.List[Instr_CuBin_Op]: return self.__ops

    def reg(self) -> typing.List[Instr_Reg]:
        if self.tt is None: return []
        if not isinstance(self.tt.value, TT_Reg): return [] # type: ignore
        tt:TT_Reg = self.tt.value # type: ignore
        if self.value is not None:
            # This is the usual case
            reg_name:str = self.value.parent_register()
            reg_value_name:str = sorted(self.value.register(), key=lambda x: len(x), reverse=True)[0]
            value_d:int = self.value.d
            sass_bits:SASS_Bits = self.value.sb
        else:
            # But every now and then, we have a value, decoded as register, that is not actually encoded in the ENCODINGS stage.
            #  => get the relevant data from the tt object
            reg_name:str = tt.value
            if tt.arg_default is not None:
                reg_value_name:str = tt.arg_default.value
            else:
                reg_value_name:str = '[None available]'
            value_d = 0
            sass_bits = SASS_Bits.from_int(0)
        reg_alias = str(tt.alias)
        if reg_name not in NON_FUNC_REG: return []
        return [Instr_Reg(index=self.index, value_name=reg_value_name, alias=reg_alias, parent_name=reg_name, value_d=value_d, sass_bits=sass_bits)]

class Instr_CuBin_Opcode(Instr_CuBin_BE):
    """This represents an Opcode field. It has a base part and an extension (B,E).

    For example IMAD/smd/sz would be Opcode/smd/sz.
    """
    def __init__(self, opcode_dec:SASS_Expr_Dec, opcode:TT_Opcode, instr_code:str, enc_vals:dict, details:SM_Cu_Details, enc_vals_alias:set, class_:SASS_Class):
        ext = []
        for index,e in enumerate(opcode.extensions):
            ext.append(Instr_CuBin_Ext(e, enc_vals, index, details, enc_vals_alias))
        super().__init__(opcode_dec, instr_code, opcode, ext, 0, details, enc_vals_alias)
        self.__db_proxy = self.__to_db(class_)
    
    @property
    def db_proxy(self): return self.__db_proxy
    @property
    def instr_code(self): return self.name
    def enc_vals(self): # type: ignore
        return dict(itt.chain.from_iterable(e.enc_vals().items() for e in self.ext))
    def __str__(self):
        msg = "[{0}]{1}"
        ext = "".join(str(e) for e in self.ext)
        return msg.format(self.name, ext)
    def __to_db(self, class_:SASS_Class) -> Db_UniverseComponent_Proxy:
        mm = Db_UniverseComponent_Proxy.create(Db_UniverseComponent_Proxy.Type_opcode, self.index, 'Opcode', self.value, class_.get_opcode_instr(), self.name, self.tt, '', children=[e.db_proxy for e in self.ext])
        return mm
    def to_db(self, class_:SASS_Class) -> Db_UniverseComponent_Proxy:
        return self.__db_proxy

class Instr_CuBin_Pred(Instr_CuBin_BEO):
    """This represents the omnipresent predicate that almost every instruction has. It has a base, and an operation.

    For example:
    * @[!]Predicate:Pg
    * @[!]UniformPredicate:UPg

    NOTE: the predicate never has an extension, even if this one is based on Instr_CuBin_BEO! The reason for being
    based on Instr_CuBin_BEO is that this is also a register type representation and should be based on the same as
    Instr_CuBin_RF.
    """
    def __init__(self, pred:TT_Pred, enc_vals:dict, details:SM_Cu_Details, enc_vals_alias:set):
        ops = []
        for index,op in enumerate(pred.ops):
            # leave out special stuff that is really not important
            if op.op_name() == '@sign': continue
            ops.append(Instr_CuBin_Op(op, enc_vals, index, details, enc_vals_alias))
        if not pred.alias.value in enc_vals: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        super().__init__(enc_vals[pred.alias.value], pred.alias.value, pred, [], ops, 0, details, enc_vals_alias)
        self.__db_proxy = self.__to_db()
    @property
    def db_proxy(self): return self.__db_proxy
    def enc_vals(self): # type: ignore
        return {o.name:o.value.sb for o in self.ops} | {self.name:self.value.sb}
    def __str__(self):
        msg = "@{0}{1}"
        op = "".join(str(o) for o in self.ops)
        reg = self.value.register()
        if len(reg) == 1: reg = next(iter(reg))
        return msg.format(op, reg)
    def __to_db(self) -> Db_UniverseComponent_Proxy:
        op = [o for o in [o.db_proxy for o in self.ops] if o is not None]
        reg = self.value.register()
        if len(reg) == 1: reg = next(iter(reg))
        mm = Db_UniverseComponent_Proxy.create(Db_UniverseComponent_Proxy.Type_pred, self.index, self.value.alias(), self.value, reg, self.tt.value.value, self.tt, '', children=op) # type: ignore
        return mm
    def to_db(self, class_:SASS_Class) -> Db_UniverseComponent_Proxy:
        return self.__db_proxy

class Instr_CuBin_Param_RF(Instr_CuBin_BEO):
    """This one represents an instruction operand that is a register or a function (R,F). For example
    * [-]Register:Ra
    * [||]NonZeroRegister:Rb
    * UImm(0x0)
    * SImm(0x60)
    * F32Imm(0x40080000)

    It has a base, may have an operator and extensions. Functions never have operators or extensions.

    In additon to the initializations of Instr_CuBin_BEO, this one takes care of correctly assigning a name to a decoded register
    and differentiates between register operands and function operands.
    """
    def __init__(self, param:TT_Param, enc_vals:dict, index:int, details:SM_Cu_Details, enc_vals_alias:set, class_:SASS_Class):
        ops = []
        for op_ind,op in enumerate(param.ops):
            # leave out special stuff that is really not important
            if op.op_name() == '@sign': continue
            ops.append(Instr_CuBin_Op(op, enc_vals, op_ind, details, enc_vals_alias))
        ext = []
        for ext_ind,e in enumerate(param.extensions):
            ext.append(Instr_CuBin_Ext(e, enc_vals, ext_ind, details, enc_vals_alias))
        name = param.alias.value
        if not name in enc_vals:
            if isinstance(param.value, TT_Reg): 
                if param.value.arg_default is not None:
                    super().__init__(None, param.value.arg_default.value, param, ext, ops, index, details, enc_vals_alias)
                else:
                    reg_val = getattr(details.REGISTERS, param.value.value, False)
                    if reg_val == False: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    elif len(reg_val) == 1: # type: ignore
                        super().__init__(None, next(iter(reg_val)), param, ext, ops, index, details, enc_vals_alias) # type: ignore
                    else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            elif isinstance(param.value, TT_Func):
                if param.is_at_alias:
                    super().__init__(None, str(param.value) + "@", param, ext, ops, index, details, enc_vals_alias)
                else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else:
            super().__init__(enc_vals[name], name, param, ext, ops, index, details, enc_vals_alias)

        self.__db_proxy = self.__to_db(class_)
    @property
    def db_proxy(self): return self.__db_proxy
    def enc_vals(self): # type: ignore
        return ({self.name:self.value.sb} if self.value else {}) | dict(itt.chain.from_iterable(e.enc_vals().items() for e in self.ext)) | {o.name:o.value.sb for o in self.ops if o.value}
    def __str__(self):
        msg = "{op}{fr}{ext}"
        op = "".join(str(o) for o in self.ops)
        ext = "".join(str(e) for e in self.ext)
        if isinstance(self.tt.value, TT_Reg): # type: ignore
            if self.value is None: reg = self.name
            else: reg = self.value.register()
            if len(reg) == 1: reg = next(iter(reg))
            return msg.format(op=op, fr=reg, ext=ext)
        elif isinstance(self.tt.value, TT_Func): # type: ignore
            func_name = self.tt.value.value # type: ignore
            if self.value is None: return msg.format(op=op, fr=self.name, ext=ext)
            elif self.mode == Instr_CuBin_B.MODE__BIN: func_val = "{0}({1})".format(func_name, self.value.b)
            elif self.mode == Instr_CuBin_B.MODE__HEX: func_val = "{0}({1})".format(func_name, self.value.h)
            elif self.mode == Instr_CuBin_B.MODE__DEC: func_val = "{0}({1})".format(func_name, self.value.d)
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            return msg.format(op=op, fr=func_val, ext=ext)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    
    def __to_db(self, class_:SASS_Class) -> Db_UniverseComponent_Proxy:
        op = [o for o in [o.db_proxy for o in self.ops] if o is not None]
        ext = [e.db_proxy for e in self.ext]

        if isinstance(self.tt.value, TT_Reg): # type: ignore
            if self.name in class_.props.dst_names: f_type = Db_UniverseComponent_Proxy.Type_dst_reg
            else: f_type = Db_UniverseComponent_Proxy.Type_src_reg
            
            if self.value is None: 
                reg = self.name
                alias = str(self.tt.alias) # type: ignore
                parent = str(self.tt.value) # type: ignore
            else: 
                reg = self.value.register()
                parent = self.value.parent_register()
                alias = self.value.alias()
                if len(reg) == 1: reg = next(iter(reg))
                else:
                    special = [r for r in reg if r.startswith('SR_')]
                    if special:
                        s = sorted([(ind,len(r)) for ind,r in enumerate(special)], key=lambda x:x[1], reverse=True)
                        reg = special[s[0][0]]
                    else:    
                        reg = "{{{0}}}".format(",".join(str(r) for r in reg))
            return Db_UniverseComponent_Proxy.create(f_type, self.index, alias, self.value, reg, parent, self.tt, '', op+ext)
        elif isinstance(self.tt.value, TT_Func): # type: ignore
            f_type = Db_UniverseComponent_Proxy.Type_func
            if self.value is None: 
                alias = str(self.tt.alias) # type: ignore
                func_value = str(self.tt.value.arg_default) # type: ignore
                value_type = self.tt.value.value # type: ignore
                return Db_UniverseComponent_Proxy.create(f_type, self.index, alias, None, func_value, value_type, self.tt, '', op+ext) 
            elif self.mode == Instr_CuBin_B.MODE__BIN: func_value = str(self.value.b)
            elif self.mode == Instr_CuBin_B.MODE__HEX: func_value = str(self.value.h)
            elif self.mode == Instr_CuBin_B.MODE__DEC: func_value = str(self.value.d)
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        alias = self.value.alias()
        value_type = self.tt.value.value # type: ignore
        func = Db_UniverseComponent_Proxy.create(f_type, self.index, alias, self.value, func_value, value_type, self.tt, '', op+ext)
        return func
    def to_db(self, class_:SASS_Class) -> Db_UniverseComponent_Proxy:
        return self.__db_proxy

class Instr_CuBin_Param_BEOA(Instr_CuBin_BEO):
    """This one represents an operand with attributes or a list. For example:
    * Sc[UImm(0x0)][SImm(0x160)]
    * memoryDescriptor[UR4][R2.64, SImm(0x58)]
    * [RZ,UR4,UImm(32)]

    param1 always contains something. param2 only contains something if an operand with an attribute is represented.
    """
    def __init__(self, param1:list, param2:list, name, ext, ops, index:int, details:SM_Cu_Details, enc_vals_alias:set):
        super().__init__(None, name, None, ext, ops, index, details, enc_vals_alias)
        self.__param1 = param1
        self.__param2 = param2

        self.__db_proxy = self.__to_db()
    @property
    def db_proxy(self): return self.__db_proxy
    @property
    def param1(self) -> typing.List[Instr_CuBin_Param_RF]: return self.__param1
    @property
    def param2(self) -> typing.List[Instr_CuBin_Param_RF]: return self.__param2

    def __str__(self):
        msg = "{op}{reg}{param1}{param2}{ext}"
        op = "".join(str(o) for o in self.ops)
        ext = "".join(str(e) for e in self.ext)
        param1 = ", ".join(str(p) for p in self.param1)
        param2 = ", ".join(str(p) for p in self.param2)
        if param1 != "": param1 = "[" + param1 + "]"
        if param2 != "": param2 = "[" + param2 + "]"
        return msg.format(op=op, reg=self.name, param1=param1, param2=param2, ext=ext)
    
    def __to_db(self):
        op = [o for o in [o.db_proxy for o in self.ops] if o is not None]
        ext = [e.db_proxy for e in self.ext]
        param1 = [p.db_proxy for p in self.param1]
        param2 = [p.db_proxy for p in self.param2]
        if self.name:
            if self.value is not None:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if self.tt is not None:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            return Db_UniverseComponent_Proxy.create_attr(Db_UniverseComponent_Proxy.Type_attr, self.index, self.name, param1, param2, '', op+ext)
        else:
            return Db_UniverseComponent_Proxy.create_attr(Db_UniverseComponent_Proxy.Type_list, self.index, "", param1, param2, '', op+ext)

    def to_db(self, class_:SASS_Class):
        return self.__db_proxy
    
    def reg(self) -> typing.List[Instr_Reg]:
        res = []
        if self.__param1: res.extend([p.reg() for p in self.__param1])
        if self.__param2: res.extend([p.reg() for p in self.__param2])
        return list(itt.chain.from_iterable(res))

class Instr_CuBin_Param_Attr(Instr_CuBin_Param_BEOA):
    """This one represents an operand with attributes. For example:
    * Sc[UImm(0x0)][SImm(0x160)]
    * memoryDescriptor[UR4][R2.64, SImm(0x58)]
    """
    def __init__(self, param:TT_Param, enc_vals:dict, index:int, details:SM_Cu_Details, enc_vals_alias:set, class_:SASS_Class):
        ops = []
        for op_ind,op in enumerate(param.ops):
            # leave out special stuff that is really not important
            if op.op_name() == '@sign': continue
            ops.append(Instr_CuBin_Op(op, enc_vals, op_ind, details, enc_vals_alias))
        ext = []
        for e_ind,e in enumerate(param.extensions):
            ext.append(Instr_CuBin_Ext(e, enc_vals, e_ind, details, enc_vals_alias))
        name = param.alias.value
        if name in ['srcConst', 'Sb', 'Sa', 'Sc', 'memoryDescriptor']:
            vv = [p.value for p in param.attr]
            if not len(vv) == 2: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            param1 = [Instr_CuBin_Param_RF(v, enc_vals, seqNr, details, enc_vals_alias, class_) for seqNr,v in enumerate(vv[0])]
            param2 = [Instr_CuBin_Param_RF(v, enc_vals, seqNr, details, enc_vals_alias, class_) for seqNr,v in enumerate(vv[1])]
        elif name in ['srcAttr', 'indexURd', 'indexURc', 'indexURb', 'ttuAddr', 'gdesc', 'desc', 'tmemA', 'tmemB', 'tmemC', 'tmemE', 'gdescA', 'gdescB', 'idesc', 'tmemI']:
            vv = [p.value for p in param.attr]
            if not len(vv) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            vv = vv[0]
            param1 = [Instr_CuBin_Param_RF(v, enc_vals, seqNr, details, enc_vals_alias, class_) for seqNr,v in enumerate(vv)]
            param2 = []
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        super().__init__(param1, param2, name, ext, ops, index, details, enc_vals_alias)
    def enc_vals(self): # type: ignore
        return dict(itt.chain.from_iterable(e.enc_vals().items() for e in self.ext)) | {o.name:o.value.sb for o in self.ops} | dict(itt.chain.from_iterable(p.enc_vals().items() for p in self.param1)) | dict(itt.chain.from_iterable(p.enc_vals().items() for p in self.param2))

class Instr_CuBin_Param_L(Instr_CuBin_Param_BEOA):
    """This one represents an operand with attributes or a list. For example:
    * [RZ,UR4,UImm(32)]
    """
    def __init__(self, param:TT_List, enc_vals:dict, index:int, details:SM_Cu_Details, enc_vals_alias:set, class_:SASS_Class):
        ext = []
        for e_ind,e in enumerate(param.extensions):
            ext.append(Instr_CuBin_Ext(e, enc_vals, e_ind, details, enc_vals_alias))
        vv = [p for p in param.value]
        param1 = [Instr_CuBin_Param_RF(v, enc_vals, seqNr, details, enc_vals_alias, class_) for seqNr,v in enumerate(vv)]
        super().__init__(param1, [], "", ext, [], index, details, enc_vals_alias)
    def enc_vals(self): # type: ignore
        return dict(itt.chain.from_iterable(e.enc_vals().items() for e in self.ext)) | {o.name:o.value.sb for o in self.ops} | dict(itt.chain.from_iterable(p.enc_vals().items() for p in self.param1))

class Instr_CuBin_Const(Instr_CuBin_B):
    """This one represents a constant entry in the ENCODINGS section of an instruction. For example:
    * BITS_3_115_113_src_rel_sb =* 7;
    * BITS_3_112_110_dst_wr_sb =* 7;

    These values sometimes can't be matched to any tt_terms.py type. Thus they are represented as constants. With cash
    values, like WR, RD and REQ, the decoder attempts to match constants to their corresponding cash type.
    """
    def __init__(self, const, index:int, details:SM_Cu_Details, enc_vals_alias:set):
        self.__from_b = min(const.enc_ind)
        self.__to_b = max(const.enc_ind)
        super().__init__(const, "", None, index, details, enc_vals_alias)
        self.__cash_link = None
        self.__db_proxy = self.__to_db()

    @property
    def from_b(self): return self.__from_b
    @property
    def to_b(self): return self.__to_b
    @property
    def code_name(self) -> str: return self.value.code_name
    @property
    def db_proxy(self): return self.__db_proxy
    def add_cash_link(self, cash_link:Instr_CuBin_Cash):
        if not isinstance(cash_link, Instr_CuBin_Cash): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__cash_link = cash_link
    def __str__(self):
        msg = "C[{f}:{t}]={val}"
        if self.mode == Instr_CuBin_B.MODE__BIN:
            return msg.format(f=self.from_b, t=self.to_b, val=self.value.b)
        elif self.mode == Instr_CuBin_B.MODE__HEX:
            return msg.format(f=self.from_b, t=self.to_b, val=self.value.h)
        elif self.mode == Instr_CuBin_B.MODE__DEC:
            return msg.format(f=self.from_b, t=self.to_b, val=self.value.d)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __to_db(self):
        return Db_UniverseComponent_Proxy.create_const(Db_UniverseComponent_Proxy.Type_const, self.index, "C", self.value, '')
    def to_db(self, class_:SASS_Class):
        return self.__db_proxy
    
class Instr_CuBin_Cash(Instr_CuBin_B):
    """This one represents all cash bits. They include (depending on the SM type)
    * RD (read barrier)
    * WR (write barrier)
    * REQ (wait-for barrier)
    * USCHED_INFO (wait cycles after instruction dispatch)
    * PM_PRED (??)
    * BATCH_T (??)
    """
    def __init__(self, cash:TT_Cash, enc_vals:dict, index:int, details:SM_Cu_Details, enc_vals_alias:set, augment=False, const_link:Instr_CuBin_Const|None=None):
        bla = [(i.value.value, i.alias.value) for i in cash.values if isinstance(i, TT_Param)]
        if not bla[-1][-1] in enc_vals: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        value = enc_vals[bla[-1][-1]]
        name = bla[0][0]
        enc_alias = bla[-1][-1]
        self.__augment = augment
        self.__const_link = const_link

        if isinstance(cash.values[-1].value, TT_Func): cash_type = 'f'
        elif isinstance(cash.values[-1].value, TT_Reg): cash_type = 'r'
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        if cash_type == 'r':
            reg_cands = getattr(details.REGISTERS, name, False)
            if reg_cands == False: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            elif not isinstance(reg_cands, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
            cash_names = {k for k,v in reg_cands.items() if value.d in v}
        else:
            cash_names = {cash.values[-1].value.value}

        super().__init__(value, name, cash, index, details, enc_vals_alias)
        self.__cash_type = cash_type
        self.__cash_names = cash_names
        self.__enc_alias = enc_alias
        self.__db_proxy = self.__to_db()

    @property
    def db_proxy(self): return self.__db_proxy
    @property
    def cash_type(self): return self.__cash_type
    @property
    def cash_names(self): return self.__cash_names
    @property
    def enc_alias(self): return self.__enc_alias
    @property
    def augment(self): return self.__augment
    @property
    def const_link(self): return self.__const_link
    def enc_vals(self): # type: ignore
        # Some instructions can't encode all cash values because they have fixed values. For these, we don't
        # return an enc_vals set
        if self.__augment: return dict()
        return {self.enc_alias:self.value.sb}
    def enc_vals_augmentations(self):
        # This one returns all cash values that are augmented by the decoding process
        if not self.__augment: return dict()
        return {self.enc_alias:self.value.sb}
    def __str__(self):
        msg = "${0}:[{1}]={2}"
        if self.mode == Instr_CuBin_B.MODE__BIN:
            return msg.format(self.name, self.cash_names, self.value.b)
        elif self.mode == Instr_CuBin_B.MODE__HEX:
            return msg.format(self.name, self.cash_names, self.value.h)
        elif self.mode == Instr_CuBin_B.MODE__DEC:
            return msg.format(self.name, self.cash_names, self.value.d)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

    def __to_db(self):
        if len(self.cash_names) == 1: cash = next(iter(self.cash_names))
        else:
            cashes = list(self.cash_names)
            cashes = sorted(cashes, key=lambda x: len(x), reverse=True)
            cash = cashes[0]

        if self.augment: alias = str(self.tt.values[1].alias) # type: ignore
        else: alias = self.value.alias()
        if not isinstance(self.tt, TT_Cash): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if self.cash_type == 'r': return Db_UniverseComponent_Proxy.create_cash(Db_UniverseComponent_Proxy.Type_cash, self.index, alias, self.value, self.name, cash, self.tt, '', self.augment)
        else: return Db_UniverseComponent_Proxy.create_cash(Db_UniverseComponent_Proxy.Type_cash, self.index, alias, self.value, self.name, cash, self.tt, '', self.augment)

    def to_db(self, class_:SASS_Class):
        return self.__db_proxy

class Instr_CuBin_Misc(Instr_CuBin_B):
    """This one contains all sorts of additional information, collected during the decoding process. It doesn't represent
    a specific part of an instruction.

    For example:
    * instruction offsets (in entire binary, only inside of cuda part, only inside of the instructions)
    * decoded SM number
    * instruction index
    * instruction class name
    """
    def __init__(self, instr_index:int, bin_start_offset_dec:int, kernel_offset_dec:int, class_name:str, instr_bits:BitVector, sass:SM_SASS):
        sm = int(sass.sm.details.SM_XX.split('_')[-1]) # type: ignore
        real_offset = 0
        relative_offset = 0
        if sm <= 62:
            if instr_index%3 == 0: pass
            if instr_index%3 == 1: pass
            if instr_index%3 == 2: pass
            real_offset = hex(kernel_offset_dec + (((instr_index+1) // 3 + instr_index) * 8))
            relative_offset = hex((((instr_index+1) // 3 + instr_index) * 8))
            total_offset = hex(bin_start_offset_dec + kernel_offset_dec + (((instr_index+1) // 3 + instr_index) * 8))
        else:
            real_offset = hex(kernel_offset_dec + (instr_index * 16))
            relative_offset = hex((instr_index * 16))
            total_offset = hex(bin_start_offset_dec + kernel_offset_dec + (instr_index * 16))
        
        self.__value_b:str = "0b" + "".join([str(i) for i in instr_bits])
        self.__value_d:int = int(self.__value_b,2)
        self.__value_h:str = hex(self.__value_d)
        self.__real_offset:str = real_offset
        self.__relative_offset:str = relative_offset
        self.__total_offset:str = total_offset
        self.__class_name:str = class_name
        self.__class_def:SASS_Class = sass.sm.classes_dict[class_name]
        self.__encw:int = sass.sm.details.FUNIT.encoding_width # type: ignore
        self.__sm_nr:int = sm
        self.__mode:int = Instr_CuBin_B.MODE__HEX
        self.__instr_index:int = instr_index

        self.__db_proxy:typing.List[Db_InstrMisc_Proxy] = self.__to_db()

    def set_mode(self, mode:int):
        if not mode in (Instr_CuBin_B.MODE__HEX, Instr_CuBin_B.MODE__BIN, Instr_CuBin_B.MODE__DEC): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__mode = mode
    
    @property
    def mode(self) -> int: 
        """[DEPRECATED] This is not used anymore!

        :return: return the decoding mode of a file
        :rtype: int
        """
        return self.__mode
    @property
    def value(self) -> str|int:
        """Not relevant for this Class

        :return: the value of the decoded field.
        :rtype: str|int
        """
        if self.mode == Instr_CuBin_B.MODE__BIN: return self.__value_b
        elif self.mode == Instr_CuBin_B.MODE__HEX: return self.__value_h
        elif self.mode == Instr_CuBin_B.MODE__DEC: return self.__value_d
    @property
    def real_offset(self) -> str: 
        """This is the [byte] offset between the start of the Cuda binary and the instruction.

        This is the middle-sized offset.
        
        :return: a hex string containing the offset
        :rtype: str
        """
        return self.__real_offset
    @property
    def relative_offset(self) -> str: 
        """This is the [byte] offset between the start of the instructions and the current instruction.

        This is the smallest offset.

        :return: a hex string containing the offset
        :rtype: str
        """
        return self.__relative_offset
    @property
    def total_offset(self) -> str: 
        """This is the [byte] offset between the start of the c++ binary and the current instruction.

        This is the largest offset.

        :return: a hex string containing the offset
        :rtype: str
        """
        return self.__total_offset
    @property
    def class_name(self) -> str: 
        """The class name of the decoded instruction

        :return: a string containing the instruction class name
        :rtype: str
        """
        return self.__class_name
    @property
    def class_def(self) -> SASS_Class: 
        """The SASS_Class definition for the decoded instruction.

        :return: return SASS_Class representing the decoded instruction
        :rtype: SASS_Class
        """
        return self.__class_def
    @property
    def encw(self) -> int: 
        """An integer containing the encoding with for the used SM.

        This is either 88 for SMs 50 to 62 or 128 for SMs 70 upwards.

        :return: an integer with the encoding with of the used SM
        :rtype: int
        """
        return self.__encw
    @property
    def sm_nr(self) -> int: 
        """The SM number. For example 86 for Ampere.

        :return: an integer with the number of the used SM
        :rtype: int
        """
        return self.__sm_nr
    @property
    def instr_index(self) -> int: 
        """The index of the instruction. The first instruction has index 0.

        :return: an integer with the index of the decoded instruction
        :rtype: int
        """
        return self.__instr_index

    def __str__(self):
        msg = "[{linenr}]: SM[{sm_nr}], ENCW[{encw}], INSTR[{val}]"
        linenr = self.real_offset
        sm_nr = self.sm_nr
        encw = self.encw
        value = self.value
        return msg.format(linenr=linenr, sm_nr=sm_nr, encw=encw, val=value)
    
    def __to_db(self) -> typing.List[Db_InstrMisc_Proxy]:
        return [
            Db_InstrMisc_Proxy.create(Db_InstrMisc_Proxy.Type_BinOffset, 0, self.__total_offset, 'Offset between start of the binary and the instruction'),
            Db_InstrMisc_Proxy.create(Db_InstrMisc_Proxy.Type_CubinOffset, 1, self.__real_offset, 'Offset between the start of the cuda binary and the instruction'),
            Db_InstrMisc_Proxy.create(Db_InstrMisc_Proxy.Type_InstrOffset, 2, self.__relative_offset, 'Offset between the start of the cuda instructions and the current instruction'),
            Db_InstrMisc_Proxy.create(Db_InstrMisc_Proxy.Type_ClassName, 3, str(self.__class_name), 'The instruction class name from instructions.txt'),
            Db_InstrMisc_Proxy.create(Db_InstrMisc_Proxy.Type_InstrBits, 4, str(self.__value_b[2:]), 'The actual instruction bits as 0/1 string')
        ]
    
    def to_db(self, class_:SASS_Class):
        return self.__db_proxy

class Instr_CuBin_Eval:
    """This one contains all information regarding how a given instruction's binary code is decoded. The information
    is presented in the 'Class Eval' section of the decoder visualization.
    """
    def __init__(self, instr_index:int, class_name:str, sass:SM_SASS, enc_vals:dict, pred:Instr_CuBin_Pred|None, regs:list, cashs:list, consts:list, extensions:list, opcode:Instr_CuBin_Opcode):
        class_:SASS_Class = sass.sm.classes_dict[class_name]
        self.__instr_index = instr_index
        
        regs_match = dict()
        used_instr_regs = []
        for ind,i in enumerate(regs):
            if isinstance(i, Instr_CuBin_Param_RF):
                regs_match |= {ind: [str(i.tt.alias)]} # type: ignore
                used_instr_regs.extend(i.reg())
            elif isinstance(i, Instr_CuBin_Param_Attr):
                regs_match |= {ind : [str(p.tt.alias) for p in i.param1] + [str(p.tt.alias) for p in i.param2]} # type: ignore
                used_instr_regs.extend(i.reg())
            elif isinstance(i, Instr_CuBin_Param_L):
                regs_match |= {ind : [str(p.tt.alias) for p in i.param1] + [str(p.tt.alias) for p in i.param2]} # type: ignore
                used_instr_regs.extend(i.reg())
            else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        reg_alias_ind = dict(itt.chain.from_iterable([(vv,k) for vv in v] for k,v in regs_match.items()))
        # Some registers also have alias or register name in the encodings (-.-)
        reg_alias_ind |= {str(class_.FORMAT.eval[i].value):reg_alias_ind[i] for i in reg_alias_ind if isinstance(class_.FORMAT.eval[i], TT_Reg) and str(class_.FORMAT.eval[i]) not in NON_FUNC_REG}

        if pred is not None:
            used_instr_regs.extend(pred.reg())

        self.__used_instr_regs:typing.List[Instr_Reg] = used_instr_regs

        self.__has_ncp = False #not (class_.non_const_preds == dict())
        if sass.sm_nr < 100:
            self.__evaled_src_sizes = {s[0]:int(s[1](enc_vals)) for s in class_.props.src_size.items() if class_.props.src_types[s[0]]}
            self.__evaled_dst_sizes = {s[0]:int(s[1](enc_vals)) for s in class_.props.dst_size.items() if class_.props.dst_types[s[0]]}
            self.__src_reg_ind = dict(itt.chain.from_iterable([(i,ind) for i,t in class_.props.src_types.items() if any(tk_nr in m for tk_nr in t)] for ind,m in regs_match.items()))
            self.__dst_reg_ind = dict(itt.chain.from_iterable([(i,ind) for i,t in class_.props.dst_types.items() if any(tk_nr in m for tk_nr in t)] for ind,m in regs_match.items()))
        else:
            self.__evaled_src_sizes = dict()
            self.__evaled_dst_sizes = dict()
            self.__src_reg_ind = dict()
            self.__dst_reg_ind = dict()

        ext_names = dict()
        for i in extensions:
            ext_names |= {i.tt.value.value : i, i.tt.alias.value : i, i.name : i}

        self.__encoding = []
        at_ops_tt = dict()
        for enc in class_.ENCODING:
            if enc['code_name'].startswith('!'): continue
            ex:SASS_Expr = enc['alias']
            a_names = ex.get_alias_names_set()
            is_opcode = False
            is_table = False
            is_encf = False
            is_identical = False
            if ex.startswith_opcode():
                code_name = 'Opcode'
                is_opcode = True
                bits = ["".join(str(i) for i in class_.get_opcode_bin())]
            elif ex.startswith_alias():
                code_name = str(ex)
                bits = [str(enc_vals[a]) for a in a_names]
            elif ex.is_constant() or ex.is_int() or ex.is_register():
                code_name = enc['code_name']
                bits = [str(enc_vals[code_name])]
            elif ex.startswith_atOp():
                code_name = str(ex)
                bits = [str(enc_vals[code_name])]
                at_ops_tt[code_name] = ex.get_first_op().value() # type: ignore
            elif ex.startswith_table():
                is_table = True
                code_name = ""
                # tables can have at_ops as args
                at_ops_tt |= {str(i):i.value() for i in ex.expr if isinstance(i, Op_AtAbs|Op_AtInvert|Op_AtNegate|Op_AtNot|Op_AtSign)}
                bits = [(a,str(enc_vals[a])) for a in a_names]
            elif ex.startswith_ConstBankAddressX() or ex.startswith_identical() or ex.startswith_convertFloat():
                is_encf = True
                code_name = ""
                bits = [(a,str(enc_vals[a])) for a in a_names]
            else:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            self.__regs = regs
            self.__encoding.append({
                'is_opcode': is_opcode,
                'is_table': is_table,
                'is_encf': is_encf,
                'is_identical': is_identical,
                'encoding' : "{0} = {1}".format(enc['code_name'], str(ex)), 
                'bits' : bits,
                'inv' : {'is_opcode': is_opcode, 'code_name': code_name, 'pred': pred, 'regs': regs, 'cashs': {c.value.alias() if c.value.is_alias() else "Const" + str(ind):c for ind,c in enumerate(cashs)}, 'consts':consts, 'reg_alias_ind': reg_alias_ind, 'a_names': a_names, 'ext_names': ext_names, 'at_ops_tt': at_ops_tt, 'opcode': opcode}, 
                'pattern' : enc['code'], 'pattern_inds' : enc['code_ind']})
        
        self.__db_proxy = self.__to_db(class_)

    @property
    def has_ncp(self): return self.__has_ncp
    @property
    def evaled_src_sizes(self): return self.__evaled_src_sizes
    @property
    def evaled_dst_sizes(self): return self.__evaled_dst_sizes
    @property
    def src_reg_ind(self): return self.__src_reg_ind
    @property
    def dst_reg_ind(self): return self.__dst_reg_ind
    @property
    def regs(self): return self.__regs
    @property
    def encoding(self): return self.__encoding
    
    def __inv_to_db(self, index:int, class_:SASS_Class, encoding_str:str, bits:list, pattern_inds:list, is_opcode:bool, code_name:str, pred:Instr_CuBin_Pred|None, regs:list, cashs:dict, consts:list, reg_alias_ind:dict, a_names:set, ext_names:dict, at_ops_tt:dict, opcode:Instr_CuBin_Opcode) -> Db_UniverseEvalEncoding_Proxy:
        if is_opcode: 
            return Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, index, encoding_str, opcode.db_proxy, '', [])
        elif code_name in ext_names: 
            instr_ext:Instr_CuBin_Ext = ext_names[code_name]
            return Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, index, encoding_str, instr_ext.db_proxy, '', [])
        else:
            if len(a_names) > 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            for a in a_names:
                if a in reg_alias_ind: 
                    # NOTE: this type is just for autocompletion. There can be different types but all of them representing a register
                    reg:Instr_CuBin_Param_RF = regs[reg_alias_ind[a]]
                    return Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, index, encoding_str, reg.db_proxy, '', [])
                elif a in at_ops_tt: 
                    from_bit = min(pattern_inds[0])
                    to_bit = max(pattern_inds[0])
                    return Db_UniverseEvalEncoding_Proxy.create_raw(Db_UniverseEvalEncoding_Proxy.Type_dynamic, index, encoding_str, bits[0], from_bit, to_bit, '', [])
                elif pred and pred.name == a: return Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, index, encoding_str, pred.db_proxy, '', [])
                elif a in cashs:
                    cash:Instr_CuBin_Cash = cashs[a]
                    return Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, index, encoding_str, cash.db_proxy, '', [])
                elif a.startswith('Const'):
                    pass
                else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            
            from_bit = min(pattern_inds[0])
            to_bit = max(pattern_inds[0])
            # Maybe we can find some made-up cash that fits this entry?
            # NOTE: This is about the cashs that are not contained in the instruction class FORMAT definition but are included in the ENCODING portion.
            #       For those, we manually create a cash entry, so that we can show it. But we would also like to link it to the correct encoding bits.
            #       Since those bits are not linked to any FORMAT entry, we can't really do that here unless we check the bit range. Luckily, we added
            #       a reference to the correct, artificial cash when we create it :-) and we can use it here.
            maybe_cash_link = [c for k,c in cashs.items() if k.startswith('Const') and c.const_link is not None and c.const_link.from_b >= from_bit and c.const_link.to_b <= to_bit]
            if maybe_cash_link:
                if len(maybe_cash_link) > 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                cash_link:Instr_CuBin_Cash = maybe_cash_link[0]
                return Db_UniverseEvalEncoding_Proxy.create_raw_w_proxy(Db_UniverseEvalEncoding_Proxy.Type_fixed, index, encoding_str, cash_link.db_proxy, bits[0], from_bit, to_bit, '', [])
            else:
                return Db_UniverseEvalEncoding_Proxy.create_raw(Db_UniverseEvalEncoding_Proxy.Type_fixed, index, encoding_str, bits[0], from_bit, to_bit, '', [])

    def __table_to_db(self, index:int, class_:SASS_Class, encoding_str:str, bits:list, pattern_inds:list, is_opcode:bool, code_name:str, pred:Instr_CuBin_Pred|None, regs:list, cashs:dict, consts:list, reg_alias_ind:dict, a_names:set, ext_names:dict, at_ops_tt:dict, opcode:Instr_CuBin_Opcode) -> Db_UniverseEvalEncoding_Proxy:
        table_res = []
        for ind,(a,b) in enumerate(bits):
            if a in reg_alias_ind: 
                # NOTE: this type is just for autocompletion. There can be different types but all of them representing a register
                reg:Instr_CuBin_Param_RF = regs[reg_alias_ind[a]]
                table_res.append(Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, reg.db_proxy, '', []))
            elif a in ext_names: 
                instr_ext:Instr_CuBin_Ext = ext_names[a]
                table_res.append(Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, instr_ext.db_proxy, '', []))
            elif a in at_ops_tt: 
                from_bit = min(pattern_inds[0])
                to_bit = max(pattern_inds[0])
                table_res.append(Db_UniverseEvalEncoding_Proxy.create_raw(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, b, from_bit, to_bit, '', []))
            elif a in cashs:
                cash:Instr_CuBin_Cash = cashs[a]
                table_res.append(Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, cash.db_proxy, '', []))
            elif pred and pred.name == a:  table_res.append(Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, pred.db_proxy, '', []))
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return Db_UniverseEvalEncoding_Proxy.create_raw(Db_UniverseEvalEncoding_Proxy.Type_table, index, encoding_str, "N/A", -1, -1, '', table_res)
    
    def __encf_to_db(self, index:int, class_:SASS_Class, encoding_str:str, bits:list, pattern_inds:list, is_opcode:bool, code_name:str, pred:Instr_CuBin_Pred|None, regs:list, cashs:dict, consts:list, reg_alias_ind:dict, a_names:set, ext_names:dict, at_ops_tt:dict, opcode:Instr_CuBin_Opcode) -> Db_UniverseEvalEncoding_Proxy:
        # this is a table
        encf_res = []
        for ind,(a,b) in enumerate(bits):
            # prequel = [Instr_CuBin_Html.span_split(), Instr_CuBin_Html.span_eval_entry_b(a), Instr_CuBin_Html.span_split(), Instr_CuBin_Html.span_eval_entry(b), Instr_CuBin_Html.span_split()]
            if a in reg_alias_ind: 
                reg:Instr_CuBin_Param_RF = regs[reg_alias_ind[a]]
                encf_res.append(Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, reg.db_proxy, '', []))
            elif a in ext_names: 
                instr_ext:Instr_CuBin_Ext = ext_names[a]
                encf_res.append(Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, instr_ext.db_proxy, '', []))
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # return Instr_CuBin_Html.html_table(Instr_CuBin_Html.span_eval_entry_b(encoding_str), "<br>".join(encf_res))  
        return Db_UniverseEvalEncoding_Proxy.create_raw(Db_UniverseEvalEncoding_Proxy.Type_func, index, encoding_str, "N/A", -1, -1, '', encf_res)
    
    def __size_to_db(self, class_:SASS_Class) -> typing.List[Db_UniverseEvalPredicate_Proxy]:
        sizes = []
        added_dst = set()
        index1 = 0
        for index1,(dst,ind) in enumerate(self.dst_reg_ind.items()):
            dst_types = class_.props.dst_types[dst]
            if isinstance(self.regs[ind], Instr_CuBin_Param_Attr|Instr_CuBin_Param_L):
                param1 = ", ".join("{0}:{1}".format(t,a) for a,t in zip([str(p.tt.alias) for p in self.regs[ind].param1], [dst_types[str(p.tt.alias)]['type'] for p in self.regs[ind].param1]))
                param2 = ", ".join("{0}:{1}".format(t,a) for a,t in zip([str(p.tt.alias) for p in self.regs[ind].param2], [dst_types[str(p.tt.alias)]['type'] for p in self.regs[ind].param2]))
                source_types = "{0}[{1}]".format(self.regs[ind].name, param1)
                # types = "{0}".format(param1)
                if param2: source_types = "{0}[{1}]".format(source_types, param2)

                source1 = ", ".join("{0}:{1}".format(t,a) for a,t in zip([str(p.tt.alias) for p in self.regs[ind].param1], [dst_types[str(p.tt.alias)]['tt'] for p in self.regs[ind].param1]))
                source2 = ", ".join("{0}:{1}".format(t,a) for a,t in zip([str(p.tt.alias) for p in self.regs[ind].param2], [dst_types[str(p.tt.alias)]['tt'] for p in self.regs[ind].param2]))
                source_operands = "{0}[{1}]".format(self.regs[ind].name, source1)
                if source2: source_operands = "{0}[{1}]".format(source_operands, source2)

            elif isinstance(self.regs[ind], Instr_CuBin_Param_RF):
                source_types = dst_types[str(self.regs[ind].tt.alias)]['type']
                source_operands = self.regs[ind].name
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            size_field = dst
            size_val = self.evaled_dst_sizes[dst]
            sizes.append(Db_UniverseEvalPredicate_Proxy.create(index1, size_field, size_val, self.regs[ind].db_proxy, source_types, source_operands, '', []))
            added_dst.add(dst)

        if len(added_dst) != len(self.evaled_dst_sizes): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        added_src = set()
        for index2,(src,ind) in enumerate(self.src_reg_ind.items()):
            src_types = class_.props.src_types[src]
            if isinstance(self.regs[ind], Instr_CuBin_Param_Attr|Instr_CuBin_Param_L):
                param1 = ", ".join("{0}:{1}".format(t,a) for a,t in zip([str(p.tt.alias) for p in self.regs[ind].param1], [src_types[str(p.tt.alias)]['type'] for p in self.regs[ind].param1]))
                param2 = ", ".join("{0}:{1}".format(t,a) for a,t in zip([str(p.tt.alias) for p in self.regs[ind].param2], [src_types[str(p.tt.alias)]['type'] for p in self.regs[ind].param2]))
                source_types = "{0}[{1}]".format(self.regs[ind].name, param1)
                if param2: source_types = "{0}[{1}]".format(source_types, param2)

                source1 = ", ".join("{0}:{1}".format(t,a) for a,t in zip([str(p.tt.alias) for p in self.regs[ind].param1], [src_types[str(p.tt.alias)]['tt'] for p in self.regs[ind].param1]))
                source2 = ", ".join("{0}:{1}".format(t,a) for a,t in zip([str(p.tt.alias) for p in self.regs[ind].param2], [src_types[str(p.tt.alias)]['tt'] for p in self.regs[ind].param2]))
                source_operands = "{0}[{1}]".format(self.regs[ind].name, source1)
                if source2: source_operands = "{0}[{1}]".format(source_operands, source2)

            elif isinstance(self.regs[ind], Instr_CuBin_Param_RF):
                source_types = src_types[str(self.regs[ind].tt.alias)]['type']
                source_operands = self.regs[ind].name
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            size_field = src
            size_val = self.evaled_src_sizes[src]
            sizes.append(Db_UniverseEvalPredicate_Proxy.create(index1+index2, size_field, size_val, self.regs[ind].db_proxy, source_types, source_operands, '', []))
            added_src.add(src)

        if len(added_src) != len(self.evaled_src_sizes): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return sizes
    
    def __eval_regs_to_db(self, index:int, class_:SASS_Class, encoding_str:str, bits:list, pattern_inds:list, is_opcode:bool, code_name:str, pred:Instr_CuBin_Pred|None, regs:list, cashs:dict, consts:list, reg_alias_ind:dict, a_names:set, ext_names:dict, at_ops_tt:dict, opcode:Instr_CuBin_Opcode) -> typing.List[Db_UniverseEvalRegisters_Proxy]:
        res = []
        # for ind,(a,b) in enumerate(bits):
        #     # prequel = [Instr_CuBin_Html.span_split(), Instr_CuBin_Html.span_eval_entry_b(a), Instr_CuBin_Html.span_split(), Instr_CuBin_Html.span_eval_entry(b), Instr_CuBin_Html.span_split()]
        #     if a in reg_alias_ind: 
        #         reg:Instr_CuBin_Param_RF = regs[reg_alias_ind[a]]
        #         encf_res.append(Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, reg.db_proxy, '', []))
        #     elif a in ext_names: 
        #         instr_ext:Instr_CuBin_Ext = ext_names[a]
        #         encf_res.append(Db_UniverseEvalEncoding_Proxy.create(Db_UniverseEvalEncoding_Proxy.Type_dynamic, ind, a, instr_ext.db_proxy, '', []))
        #     else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        for reg in self.__used_instr_regs:
            if reg.alias in reg_alias_ind:
                proxy = regs[reg_alias_ind[reg.alias]].db_proxy
            elif class_.FORMAT.pred is not None and class_.FORMAT.pred.alias.value == reg.alias:
                if pred is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                proxy = pred.db_proxy
            else:
                raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
            res.append(Db_UniverseEvalRegisters_Proxy.create(reg.index, reg.parent_name, reg.value_name, reg.alias, reg.value_d, str(reg.sass_bits), proxy, "", []))            

        return res
    
    def __to_db(self, class_:SASS_Class) -> Db_UniverseEval_Proxy:
        encodings = []
        collapsibles = []
        ind=0
        for ind, e in enumerate(self.__encoding):
            if e['is_table']:
                collapsibles.append(self.__table_to_db(ind, class_, e['encoding'], e['bits'], e['pattern_inds'], **e['inv']))
            elif e['is_encf']:
                collapsibles.append(self.__encf_to_db(ind, class_, e['encoding'], e['bits'], e['pattern_inds'], **e['inv']))
            else:
                inv = self.__inv_to_db(ind, class_, e['encoding'], e['bits'], e['pattern_inds'], **e['inv'])
                encodings.append(inv)

        sizes = self.__size_to_db(class_)
        eval_regs = self.__eval_regs_to_db(ind, class_, e['encoding'], e['bits'], e['pattern_inds'], **e['inv']) # type: ignore
        return Db_UniverseEval_Proxy.create(self.__instr_index, sizes, collapsibles + encodings, eval_regs, 'Eval for {0}'.format(class_.class_name))
    
    def to_db(self, class_:SASS_Class):
        return self.__db_proxy
