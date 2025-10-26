"""
This is the big one: it parses one instruction class in the instructions.txt like the following example.

CLASS "TLD"
    FORMAT PREDICATE @[!]Predicate(PT):Pg Opcode
             /LOD1:lod /TOFF1(noTOFF):toff /MS(noMS):ms
             /CL(noCL):clamp /NODEP(noNODEP):ndp
             /TPhase(noPhase):phase
             Register:Rd
             ',' Register:Ra ',' Register(RZ):Rb
',' UImm(16)*:tid ',' ParamA:paramA ',' UImm(4/15/PRINT):wmsk
     $( { '&' REQ:req '=' BITSET(6/0x0000):req_bit_set } )$
         $( { '&' RD:rd '=' UImm(3/0x7):src_rel_sb } )$
         $( { '&' WR:wr '=' UImm(3/0x7):dst_wr_sb } )$
     $( { '?' USCHED_INFO:usched_info } )$
             ;
    CONDITIONS
            MISALIGNED_REG_ERROR
                ((((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)) > 2) -> ((((Rd)+((Rd)==255)) & 0x3) == 0) :
                "Register D should be aligned to 4 if sz is greater than 64"
            MISALIGNED_REG_ERROR
                ((((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)) == 2) -> ((((Rd)+((Rd)==255)) & 0x1) == 0) :
                "Register D should be aligned to 2 if sz is 64"
            OOR_REG_ERROR
                (((Rd)==`Register@RZ)||((Rd)<=%MAX_REG_COUNT-(((wmsk & 0x1) != 0) + ((wmsk & 0x2) != 0) + ((wmsk & 0x4) != 0) + ((wmsk & 0x8) != 0)))) :
                "Register D is out of range"
            MISALIGNED_REG_ERROR
                (( (ParamA == `ParamA@"_1D") + (ParamA == `ParamA@RECT) * 2 + (ParamA == `ParamA@CUBE) * 3 + (ParamA == `ParamA@"_3D") * 3 + (ParamA == `ParamA@ARRAY_1D) * 2 + (ParamA == `ParamA@ARRAY_RECT) * 3 + (ParamA == `ParamA@ARRAY_3D) * 4 + (ParamA == `ParamA@ARRAY_CUBE) * 4 ) > 2 ) -> ((((Ra)+((Ra)==255)) & 0x3) == 0) :
                "Register A should be aligned to 4 if the number of coordinates is > 2"
            MISALIGNED_REG_ERROR
                (( (ParamA == `ParamA@"_1D") + (ParamA == `ParamA@RECT) * 2 + (ParamA == `ParamA@CUBE) * 3 + (ParamA == `ParamA@"_3D") * 3 + (ParamA == `ParamA@ARRAY_1D) * 2 + (ParamA == `ParamA@ARRAY_RECT) * 3 + (ParamA == `ParamA@ARRAY_3D) * 4 + (ParamA == `ParamA@ARRAY_CUBE) * 4 ) == 2) -> ((((Ra)+((Ra)==255)) & 0x1) == 0) :
                "Register A should be aligned to 2 if the number of coordinates is == 2"
            OOR_REG_ERROR
                (((Ra)==`Register@RZ)||((Ra)<=%MAX_REG_COUNT-( (ParamA == `ParamA@"_1D") + (ParamA == `ParamA@RECT) * 2 + (ParamA == `ParamA@CUBE) * 3 + (ParamA == `ParamA@"_3D") * 3 + (ParamA == `ParamA@ARRAY_1D) * 2 + (ParamA == `ParamA@ARRAY_RECT) * 3 + (ParamA == `ParamA@ARRAY_3D) * 4 + (ParamA == `ParamA@ARRAY_CUBE) * 4 ))) :
                "Register A is out of range"
            MISALIGNED_REG_ERROR
                (( (TOFF1 == `TOFF1@AOFFI) + ( MS == `MS@MS) + (LOD1 == `LOD1@LL) ) > 2 ) -> ((((Rb)+((Rb)==255)) & 0x3) == 0) :
                "Register B should be aligned to 4 if the number of coordinates is > 2"
            MISALIGNED_REG_ERROR
                (( (TOFF1 == `TOFF1@AOFFI) + ( MS == `MS@MS) + (LOD1 == `LOD1@LL) ) == 2) -> ((((Rb)+((Rb)==255)) & 0x1) == 0) :
                "Register B should be aligned to 2 if the number of coordinates is == 2"
            OOR_REG_ERROR
                (((Rb)==`Register@RZ)||((Rb)<=%MAX_REG_COUNT-( (TOFF1 == `TOFF1@AOFFI) + ( MS == `MS@MS) + (LOD1 == `LOD1@LL) ))) :
                "Register B is out of range"
            ILLEGAL_INSTR_ENCODING_ERROR
                (phase != `TPhase@INVALIDPHASE3):
                "Invalid TPhase (phase) field value INVALIDPHASE3"
        ILLEGAL_INSTR_ENCODING_ERROR (ParamA != `ParamA@CUBE):
                "Illegal instruction encoding: CUBE is not supported "
                ILLEGAL_INSTR_ENCODING_ERROR (ParamA != `ParamA@ARRAY_CUBE) :
                "Illegal instruction encoding: ARRAY_3D is not supported"
                ILLEGAL_INSTR_ENCODING_ERROR (ParamA != `ParamA@ARRAY_3D) :
                "Illegal instruction encoding: ARRAY_CUBE is not supported"
                ILLEGAL_INSTR_ENCODING_ERROR (MS == `MS@MS) -> (LOD1 == `LOD1@LZ):
                "Illegal instruction encoding: .MS can only be used with the .LZ LOD option"
                ILLEGAL_INSTR_ENCODING_ERROR (MS == `MS@MS) -> (CL != `CL@CL):
                "Illegal instruction encoding: .MS can not be used with the CL option"
                ILLEGAL_INSTR_ENCODING_ERROR (MS == `MS@MS) -> (ParamA == `ParamA@"2D" || ParamA == `ParamA@ARRAY_2D):
                "Illegal instruction encoding: .MS can only be used with 2D/ARRAY_2D textures"
        ILLEGAL_INSTR_ENCODING_ERROR
            ((( (ParamA == `ParamA@"_1D") + (ParamA == `ParamA@RECT) * 2 + (ParamA == `ParamA@CUBE) * 3 + (ParamA == `ParamA@"_3D") * 3 + (ParamA == `ParamA@ARRAY_1D) * 2 + (ParamA == `ParamA@ARRAY_RECT) * 3 + (ParamA == `ParamA@ARRAY_3D) * 4 + (ParamA == `ParamA@ARRAY_CUBE) * 4 ) >0 ) -> (Ra != `Register@RZ)) :
            "Illegal instruction encoding: If the number of coordinates of Ra is > 0, then Ra cannot be RZ"
        ILLEGAL_INSTR_ENCODING_ERROR
            ((( (TOFF1 == `TOFF1@AOFFI) + ( MS == `MS@MS) + (LOD1 == `LOD1@LL) ) >0 ) -> (Rb != `Register@RZ)) :
            "Illegal instruction encoding: If the number of coordinates of Rb is > 0, then Rb cannot be RZ"
    PROPERTIES
         OPERATION_TYPE = MEMORY_LOAD;
         VALID_IN_SHADERS = ISHADER_ALL;
              INSTRUCTION_TYPE = INST_TYPE_DECOUPLED_RD_WR_SCBD;
              MIN_WAIT_NEEDED = 1;
         IERRORS = (1<<IERROR_PC_WRAP)
                   + (1<<IERROR_ILLEGAL_INSTR_DECODING)
                   + (1<<IERROR_MISALIGNED_REG)
                   + (1<<IERROR_OOR_REG)
                   ;
         IDEST_OPERAND_TYPE = (1<<IOPERAND_TYPE_FLOAT);
         ISRC_A_OPERAND_TYPE = (1<<IOPERAND_TYPE_TEX);
         ISRC_B_OPERAND_TYPE = (1<<IOPERAND_TYPE_TEX);
         ISRC_C_OPERAND_TYPE = (1<<IOPERAND_TYPE_NON_EXISTENT_OPERAND);
         IDEST_OPERAND_MAP = (1<<INDEX(Rd));
         ISRC_A_OPERAND_MAP = (1<<INDEX(Ra));
         ISRC_B_OPERAND_MAP = (1<<INDEX(Rb));
         ISRC_C_OPERAND_MAP = (1<<IOPERAND_MAP_NON_EXISTENT_OPERAND);
    PREDICATES
         IDEST_SIZE = ( (((wmsk)&0x1) + ((wmsk>>1)&0x1) + ((wmsk>>2)&0x1) + ((wmsk>>3)&0x1)) ) * 32;
         ISRC_A_SIZE = (( (ParamA == `ParamA@"_1D") + (ParamA == `ParamA@RECT) * 2 + (ParamA == `ParamA@CUBE) * 3 + (ParamA == `ParamA@"_3D") * 3 + (ParamA == `ParamA@ARRAY_1D) * 2 + (ParamA == `ParamA@ARRAY_RECT) * 3 + (ParamA == `ParamA@ARRAY_3D) * 4 + (ParamA == `ParamA@ARRAY_CUBE) * 4 )) * 32;
         ISRC_B_SIZE = (( (TOFF1 == `TOFF1@AOFFI) + ( MS == `MS@MS) + (LOD1 == `LOD1@LL) )) * 32;
         ISRC_C_SIZE = 0;
         DOES_READ_CC = 0;
         VIRTUAL_QUEUE = $VQ_TEX;
    OPCODES
        TLDmio_pipe =  0b110_11100;
        TLD =  0b110_11100;
    ENCODING
      Opcode8 = Opcode;
      Pred = Pg;
      PredNot = Pg@not;
      Dest = Rd;
      RegA = Ra;
      RegB = Rb;
TidB = tid MULTIPLY 4 SCALE 4;
      Wmsk = wmsk;
      LOD1 = LOD1;
      TOFF1 = TOFF1;
      MS = MS;
      CL = CL;
      NODEP = NODEP;
      PredDst = `Predicate@PT;
      ParamA = ParamA;
      OEUSchedInfo = usched_info;
       OEWaitOnSb = req_bit_set;
           OEVarLatDest = VarLatOperandEnc( dst_wr_sb );
           OEVarLatSrc = VarLatOperandEnc( src_rel_sb );
           OETexPhase = TPhase;
       !OEReserved;
   !OEReserved1;
"""
from __future__ import annotations
import re
import itertools as itt
from . import _config as sp
from ._sass_expression_ops import Op_Constant
from ._sass_expression import SASS_Expr
from ._sass_expression_domain_contract import SASS_Expr_Domain_Contract
from ._tt_term import TT_Term
if not sp.SWITCH__USE_TT_EXT:
    from ._tt_terms import TT_Func, TT_Reg, TT_List, TT_Param, TT_Pred, TT_Cash
else:
    from py_sass_ext import TT_Func, TT_Reg, TT_List, TT_Param, TT_Pred, TT_Cash
from ._tt_instruction import TT_Instruction
from py_sass_ext import TT_Instruction as cTT_Instruction
from ._sass_class import _SASS_Class
from ._iterator import Iterator
from .sm_cu_details import SM_Cu_Details
from .sass_class_props import SASS_Class_Props
from py_sass_ext import SASS_Bits

class SASS_Class:
    def __init__(self, class_name, class_:dict, details:SM_Cu_Details):
        if sp.CONST_NAME__SKIP in class_.keys(): return
        self.__deprecated_by_nvidia = False
        self.__deprecated_reason = ''

        for param in class_.keys(): setattr(self, param, class_[param])
        self.class_name = class_name
        self.details = details

        if not sp.CONST_NAME__FORMAT in class_.keys(): raise Exception("Class {0} has no format block".format(self.class_name))
        else: self.FORMAT = self.FORMAT # fake auto-completion
        if not sp.CONST_NAME__FORMAT_ALIAS in class_.keys(): self.FORMAT_ALIAS = []
        if not sp.CONST_NAME__CONDITIONS in class_.keys(): self.CONDITIONS = []
        if not sp.CONST_NAME__PROPERTIES in class_.keys(): self.PROPERTIES = {}
        if not sp.CONST_NAME__PREDICATES in class_.keys(): self.PREDICATES = {}
        if not sp.CONST_NAME__OPCODES in class_.keys(): raise Exception("Class {0}: has no opcode block".format(self.class_name))
        else: self.OPCODES = self.OPCODES # fake auto-completion
        if not sp.CONST_NAME__ENCODING in class_.keys(): raise Exception("Class {0}: has no encoding block".format(self.class_name))
        else: self.ENCODING = self.ENCODING # fake auto-completion
        if not sp.CONST_NAME__REMAP in class_.keys(): self.REMAP = []
        if not sp.CONST_NAME__IS_ALTERNATE in class_.keys(): self.IS_ALTERNATE = False
        else: self.IS_ALTERNATE = self.IS_ALTERNATE # fake auto-completion

        # finalize format: replace all TT_Term with more expressive ones
        format_tt:TT_Instruction
        format_tt = self.FORMAT
        format_tt.finalize(details)

        # add the operation binary code to the format abstraction of the instruction
        bin_ind_l = [i for i in self.ENCODING if str(i['alias']) == 'Opcode']
        if len(bin_ind_l) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        format_tt.add_opcode_bin(self.OPCODES, bin_ind_l[0]['code_ind'])

        self.__used_regs, self.__reuse_regs =  format_tt.get_used_regs_and_reuse(details)
        
        # Transform the objects to their CPP equivalents
        # format_tt2:cTT_Instruction
        # format_tt2 = format_tt.to_cpp()
        # print(self.class_name, "...................")
        cformat_tt:cTT_Instruction = format_tt.to_cpp()
        # print("...................", "ok")
        # self.FORMAT = format_tt2

        # finalize the conditions: replace all remaining Op_Value with other stuff
        cond_types = details.ARCHITECTURE.CONDITION['TYPES'] # type: ignore
        for x in self.CONDITIONS:
            if not x['code'] in cond_types.keys():
                raise Exception("Class {0}: condition type {1} not defined".format(class_name, x))
            expr:SASS_Expr = x['expr']
            expr.finalize(format_tt.eval)
            if expr.is_int() and expr.get_first_value() == 0:
                # there are a few instructions that have one condition that looks like this (or something like it)
                # ILLEGAL_INSTR_ENCODING_SASS_ONLY_ERROR
                #   0:
                #   "OUT with constat with immediate address for Sb is deprecated (Errata 24)"
                # => need to remove those from consideration XD
                self.__deprecated_by_nvidia = True
                self.__deprecated_reason = x['msg']

        op_props = set(details.OPERATION.PROPERTIES) # type: ignore
        for x in self.PROPERTIES:
            if not x in op_props: raise Exception("Class {0}: property {1} not defined".format(class_name, x))
            expr:SASS_Expr = self.PROPERTIES[x]
            expr.finalize(format_tt.eval)

        op_preds = set(details.OPERATION.PREDICATES) # type: ignore
        for x in self.PREDICATES:
            if not x in op_preds: raise Exception("Class {0}: predicates {1} not defined".format(class_name, x))
            expr:SASS_Expr = self.PREDICATES[x]
            expr.finalize(format_tt.eval)

        for ee in self.ENCODING:
            x = ee['code_name']
            if x.startswith('!'):
                if not x[1:] in details.FUNIT.encoding.keys(): raise Exception("Class {0}: funit encoding {1} not defined".format(class_name, x)) # type: ignore
            elif x.find(',') > 0:
                xx = [i.strip() for i in x.split(',')]
                for xx1 in xx:
                    if not xx1 in details.FUNIT.encoding.keys(): raise Exception("Class {0}: funit encoding {1} not defined".format(class_name, x))       # type: ignore
            elif not x in details.FUNIT.encoding.keys(): raise Exception("Class {0}: funit encoding {1} not defined".format(class_name, x)) # type: ignore
            if isinstance(ee['alias'], SASS_Expr):
                expr:SASS_Expr = ee['alias']
                res = expr.finalize(format_tt.eval)
        
        # Calculate some convenience short-cuts
        self.enc_alias_expr = [(i['alias'], [tuple(ind for ind,j in enumerate(c) if j=='1') for c in i['code']]) for i in self.ENCODING]
        self.enc_alias = [(str(i['alias']), [tuple(ind for ind,j in enumerate(c) if j=='1') for c in i['code']]) for i in self.ENCODING]
        alias_dom = {}
        # self.encoding_priority_sorted = self.sort_encodings_by_priorities()

        self.funit_mask = details.FUNIT.encoding_width * [1] # type: ignore
        self.funit_mask_str = details.FUNIT.encoding_width * '1' # type: ignore
        for ee in self.ENCODING:
            k = ee['code_name']
            v = ee
            if k.startswith('!'):
                for o in v['code_ind']:
                    for i in o:
                        self.funit_mask[i] = 0
        self.funit_mask_str = "".join([str(i) for i in self.funit_mask])
        self.table_names = set([i for i in dir(details.TABLES) if not i.startswith('__')])
        self.alias_dom = alias_dom
        self.funit_mask_hash = self.funit_mask_str.__hash__()

        # get all modifiers that have unique values
        opc_mod = [(str(ext.alias), str(ext.value.value)) for ext in format_tt.opcode.extensions]
        self.opc_mod = SASS_Class.mod_to_useful(self, opc_mod)

        reg_mod = list(itt.chain.from_iterable([[(str(ext.alias), str(ext.value.value)) for ext in reg.extensions] for reg in format_tt.regs if reg.extensions]))
        self.reg_mod = SASS_Class.mod_to_useful(self, reg_mod)
        self.__pt = SASS_Class.get_PT(False, self.details, self.ENCODING, format_tt)
        self.__not_pt = SASS_Class.get_PT(True, self.details, self.ENCODING, format_tt)
        self.__const_size_order, self.__const_size_sizes = SASS_Class.calculate_const_size_sets(self.class_name, self.PREDICATES, self.ENCODING)

        # SASS_Class.resolve_size_mappings(self)
        # self.__non_const_preds = self.get_non_const_preds()
        # if class_name == 'arrives_':
        #     pass
        self.__props = SASS_Class_Props(
            format_tt, 
            self.OPCODES['opcode']['i'], self.OPCODES['set'],
            self.PROPERTIES, self.PREDICATES, self.ENCODING, self.IS_ALTERNATE,
            self.details)
        
    def __iter__(self):
        self.__iter = iter([i for i in dir(self) if not i.startswith('_') and i[0].isupper()])
        return self
    def __next__(self): return next(self.__iter)
    def __str__(self):
        class_name = self.class_name
        is_alternate = self.IS_ALTERNATE
        res = 'CLASS "' + class_name + '"\n'
        if is_alternate: res = 'ALTERNATE ' + res

        indent = 3
        res += self.format_to_str(indent)

        if self.FORMAT_ALIAS:
            res += self.FORMAT_ALIAS[0] + "\n"
        res += self.conditions_to_str(indent)
        res += self.properties_to_str(indent)
        res += self.predicates_to_str(indent)
        res += self.opcodes_to_str(indent)
        res += self.encoding_to_str()

        if self.REMAP: res += self.REMAP[0] + "\n"
        return res

    @property
    def props(self) -> SASS_Class_Props: return self.__props

    @property
    def enc_vals__const_size_order(self) -> list: 
        """If an instruction class has PREDICATES with parameters, this property will contain the names of the parameterized properties.
        The sequence matches property 'enc_vals__const_size_sizes'

        :return: the names of the parameterized predicates. For example ['IDEST_SIZE].
        :rtype: list
        """                
        return self.__const_size_order
    @property
    def enc_vals__const_size_sizes(self) -> dict:    
        """If an instruction class has PREDICATES with parameters, this property will contain a dictionary
        with the size of the predicate, combined with a list of dictionaries that will produce that size.

        The dictionaries can be used directly to feed the instruction generator as fixed enc_vals_ankers.
        * sass.encdom.fix(class_name, enc_vals_ankers)

        For example: 
        * \\{ 
            (32,): [{'sz': {SASS_Bits_1}}], 
            (64,): [{'sz': {SASS_Bits_2}}], 
            (96,): [{'sz': {SASS_Bits_3}}], 
            (128,): [{'sz': {SASS_Bits_4}}]
          \\} 

        The keys of the dict are a tuple with the sizes the value lists will produce.

        :return: a {tuple:list} dictionary where the keys are tuples with sizes and the values are lists with sets that produce those values.
        :rtype: dict
        """        
        return self.__const_size_sizes
    @property
    def enc_vals__pt(self) -> dict: 
        """Almost every instruction class has a predicate. For example '@[!]Predicate(PT):Pg'. To make an instruction be executed in a Cuda kernel, the predicate has to be equivalent to 'True'.
        
        This property contains a dictionary with encode values for PT with no inversion, which corresponds to True. For example:
        * {'Pg@not': {SASS_Bits(0x0)}, 'Pg': {SASS_Bits(0x7)}} == PT

        This is the inverse of property 'enc_vals__not_pt'

        :return: dictionary with encoding values for PT
        :rtype: dict
        """        
        return self.__pt
    @property
    def enc_vals__not_pt(self): 
        """Almost every instruction class has a predicate. For example '@[!]Predicate(PT):Pg'. To make an instruction be executed in a Cuda kernel, the predicate has to be equivalent to 'True'.
        
        This property contains a dictionary with encode values for !PT with inversion, which corresponds to False. For example:
        * {'Pg@not': {SASS_Bits(0x1)}, 'Pg': {SASS_Bits(0x7)}} == !PT

        This is the inverse of property 'enc_vals__pt'
        
        :return: dictionary with encoding values for !PT
        :rtype: dict
        """  
        return self.__not_pt
    @property
    def enc_vals__used_regs(self) -> dict: 
        """Almost every instruction class uses registers. For example Register:Rd, Register:Ra or Register(RZ):Rb.

        This property contains a dictionary with all used register aliases (for example Ra, Rb, Rd, etc) and their parent type (for example 'Register' or 'UniformRegister') and their domains. For example:
        * {'Register': {'Rd': {...}, 'Ra': {...}, 'Rb': {...}, 'Rc': {...}}}

        :return: a dictionary with the used registers, their parent type and domains
        :rtype: dict
        """        
        return self.__used_regs
    
    @property
    def enc_vals__reuse_regs(self) -> dict:
        """Some instruction classes contain 'REUSE/NOREUSE' extensions. This property contains a dictionary that is non-empty if an instruction class has such extensions.

        If the property is non-empty, it contains a dictionary with the register alias, the alias of the reuse extension and the encoding values to set either reuse or no-reuse. For example:
        * {'Ra': {'a': 'reuse_src_a', 'd': {'reuse': <SASS_Bits>, 'noreuse': <SASS_Bits>}}, 'Rb': {'a': 'reuse_src_b', 'd': {'reuse': <SASS_Bits>, 'noreuse': <SASS_Bits>}}}

        :return: dictionary containing reuse/no-reuse encoding values
        :rtype: dict
        """        
        return self.__reuse_regs
    @property
    def deprecated_by_nvidia(self) -> bool: 
        """Some instruction classes are designated 'deprecated' in some way. For example using an unsatisfiable CONDITION (for example 0) or by other means.

        :return: True if the instruction class is deprecated, False otherwise
        :rtype: bool
        """        
        return self.__deprecated_by_nvidia
    @property
    def deprecated_reason(self) -> str: 
        """Sometimes it's possible to know why an instruction class is deprecated. In that case this property will contain a non-empty string. It's mostly empty, though.

        :return: reason for deprecation, if available
        :rtype: str
        """        
        return self.__deprecated_reason

    # @property
    # def non_const_preds(self): return self.__non_const_preds
    
    @property
    def default_enc_vals(self) -> dict: return self.FORMAT.default_enc_vals

    def enc_vals__exceptions(self, kernel_used_regs:dict):
        if not isinstance(kernel_used_regs, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return SASS_Class.get_enc_vals_exceptions(self.__used_regs, kernel_used_regs, self.details)

    def set_deprecated_reason(self, reason:str):
        self.__deprecated_reason = reason

    @staticmethod
    def conditions_to_string(conds): return _SASS_Class.conditions_to_string(conds)
    @staticmethod
    def properties_to_string(props): return _SASS_Class.conditions_to_string(props)
    @staticmethod
    def predicates_to_string(preds): return _SASS_Class.predicates_to_string(preds)
    @staticmethod
    def opcodes_to_string(opcodes): return _SASS_Class.opcodes_to_string(opcodes)
    @staticmethod
    def format_to_string(format): return _SASS_Class.format_to_string(format)
    @staticmethod
    def encoding_to_string(encodings): return _SASS_Class.encoding_to_string(encodings)
    @staticmethod
    def parse(lines_iter:Iterator, local_res:dict, tt:dict, is_alternate:bool): return _SASS_Class.parse(lines_iter, local_res, tt, is_alternate)

    def get_opcode_instr(self): return self.OPCODES['opcode']['i']
    def get_opcode_bin(self): return self.FORMAT.get_opcode_bin()
    def get_opcode_encoding(self):
        val = [(i['code'], self) for i in self.ENCODING if str(i['alias']) == 'Opcode']
        if len(val) != 1:
            raise Exception("Class {0} has no Opcode encoding".format(self.class_name))
        if len(val[0][0]) != 1:
            raise Exception("Class {0} has no Opcode encoding".format(self.class_name))
        cc = tuple([ind for ind,i in enumerate(val[0][0][0]) if i=='1'])
        return (cc, val[0][1])

    def format_to_str(self, indent:int):
        i = indent*' '
        return i + str(self.FORMAT).replace('\n','\n' + i) + '\n'
    
    def opcodes_to_str(self, indent:int):
        i = indent*' '
        res = ""
        res += sp.CONST_NAME__OPCODES + '\n'
        res += i + SASS_Class.opcodes_to_string(self.OPCODES).replace('\n','\n'+i) + "\n"
        return res
    
    def encoding_to_str(self):
        res = ""
        res += sp.CONST_NAME__ENCODING + '\n'
        res += SASS_Class.encoding_to_string(self.ENCODING)
        return res

    def conditions_to_str(self, indent:int):
        i = indent*' '
        res = ""
        if self.CONDITIONS:
            res += sp.CONST_NAME__CONDITIONS + "\n"
            for cond in self.CONDITIONS:
                res += "\n".join([1*i + cond['code'], 2*i + str(cond['expr']) + " :", 2*i + cond['msg'] + ";\n"])
        return res
    
    def properties_to_str(self, indent:int):
        i = indent*' '
        res = ""
        if self.PROPERTIES:
            res += sp.CONST_NAME__PROPERTIES +"\n"
            for p in self.PROPERTIES.items():
                prop_str = 1*i + p[0] + (' = ' if str(p[1]) else '') + str(p[1]) + ";"
                res += prop_str + "\n"
        return res
    
    def predicates_to_str(self, indent:int):
        i = indent*' '
        res = ""
        if self.PREDICATES:
            res += sp.CONST_NAME__PREDICATES + "\n"
            for p in self.PREDICATES.items():
                pred_str = 1*i + p[0] + ' = ' + str(p[1]) + ";"
                res += pred_str + "\n"
        return res
    
    def augment_enc_vals(self, enc_vals:dict):
        res = dict()
        ll = ['Register','SpecialRegister','Predicate','BarrierRegister','AtOp','NonZeroRegister']
        for e in enc_vals.keys():
            if isinstance(self.FORMAT.eval[e], TT_Func): continue
            reg_n = str(self.FORMAT.eval[e].value)
            aaa_n = str(self.FORMAT.eval[e].alias)
            res[e] = enc_vals[e]
            if e == reg_n:
                res[aaa_n] = enc_vals[e]
            elif e == aaa_n and reg_n not in ll:
                res[reg_n] = enc_vals[e]
        return res
    
    def test_all_conditions(self, enc_vals:dict):
        aug_vals = self.augment_enc_vals(enc_vals)
        if not isinstance(enc_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        res = []
        for cond in self.CONDITIONS:
            # if str(cond['expr']) == '(p == `POnly@P) -> (Rb == `Register@RZ)':
            #     pass
            aug_vals = self.augment_enc_vals(enc_vals)
            res.append(cond['expr'](aug_vals))

        return all(res)
    
    def get_operand_alias(self):
        alias_names = []
        for i in self.FORMAT.regs:
            # The registers follow the following format:
            if isinstance(i, TT_List):
                # What kinds exactly?
                #  - all lists of stuff: [ZeroRegister(RZ):Ra + UImm(20/0)*:uImm]
                for j in i.value:
                    # lists always contain TT_Param
                    if not isinstance(j, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    # TT_Param contain either TT_Reg or TT_Func
                    if isinstance(j.value, TT_Reg):
                        alias_names.append(str(j.alias))

            elif isinstance(i.value, TT_Reg):
                # What kinds exactly?
                #  - regular regusters: RegisterFAU:Rd
                #  - registers with attributs: C:srcConst[UImm(5/0*):constBank]*[ZeroRegister(RZ):Ra+SImm(17)*:immConstOffset]
                #  => in both instances RegisterFAU:Rd and C:srcConst are a [RegisterName]:[AliasName] pair
                # reg_vals[str(i.alias)] = set(int(x) for x in i.value.get_domain({}))
                for attr in i.attr:
                    # attributs are always lists of things and the lists always contain TT_Param
                    if not isinstance(attr, TT_List): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    for a in attr.value:
                        if not isinstance(a, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                        # TT_Param contain either TT_Reg or TT_Func
                        if isinstance(a.value, TT_Reg):
                            alias_names.append(str(a.alias))
                alias_names.append(str(i.alias))
        
        if self.FORMAT.pred:
            alias_names.append(str(self.FORMAT.pred.alias))

        return set(alias_names)
    
    @staticmethod
    def get_PT(invert:bool, details:SM_Cu_Details, ENCODING:list, tt_format:TT_Instruction):
        if tt_format.pred is None: return dict()

        pred:TT_Pred = tt_format.pred
        op_alias = str(pred.op.alias)
        reg_alias = str(pred.value.alias)
        
        encs = {str(i['alias']): len(i['code_ind'][0]) for i in ENCODING}
        if op_alias not in encs: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if reg_alias not in encs: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        pt = next(iter(details.REGISTERS.Predicate['PT'])) # type: ignore
        res = {
            op_alias: {SASS_Bits.from_int(1 if invert else 0, encs[op_alias], signed=0)}, 
            reg_alias: {SASS_Bits.from_int(pt, encs[reg_alias], signed=0)}
        }

        return res

    @staticmethod
    def mod_to_useful(class_:SASS_Class, mod_list:list):
        registers_tt = class_.details.REGISTERS
        mod_valid_l = [(i[0], i[1], set(itt.chain.from_iterable(v for k,v in getattr(registers_tt, i[1]).items() if not str(k).startswith('INVALID')))) for i in mod_list]
        mod_invalid_l = [(i[0], i[1], set(itt.chain.from_iterable(v for k,v in getattr(registers_tt, i[1]).items() if str(k).startswith('INVALID')))) for i in mod_list]
        mod_all_l = [(i[0], i[1], set(itt.chain.from_iterable(v for k,v in getattr(registers_tt, i[1]).items()))) for i in mod_list]
        unique_mod = dict(itt.chain.from_iterable([[(i[0],i[-1]), ((i[1],i[-1]))] for i in mod_valid_l if len(i[-1]) == 1]))
        valid_mod = dict(itt.chain.from_iterable([[(i[0],i[-1]), ((i[1],i[-1]))] for i in mod_valid_l]))
        invalid_mod = dict(itt.chain.from_iterable([[(i[0],i[-1]), ((i[1],i[-1]))] for i in mod_invalid_l if i[-1]]))
        all_mod = dict(itt.chain.from_iterable([[(i[0],i[-1]), ((i[1],i[-1]))] for i in mod_all_l if i[-1]]))

        return {'invalid': invalid_mod, 'valid': valid_mod, 'unique': unique_mod, 'all': all_mod}

    @staticmethod
    def enc_set_to_enc_val(enc_vals:dict):
        ii = list(enc_vals.items())
        k = [i[0] for i in ii]
        v = [i[1] for i in ii]
        return [{kk:pp for kk,pp in zip(k,p)} for p in itt.product(*v)]
    
    @staticmethod
    def get_enc_vals_exceptions(class_used_regs:dict, kernel_used_regs:dict, sm_details:SM_Cu_Details):
        # The following regular registers don't contribute to exceptions because the values signify the constant '0'==255 or 'True'==7:
        #   Register['RZ'] = 255
        #   UniformRegister['URZ'] = 255
        #   SpecialRegister['SRZ'] = 255
        #   Predicate['PT'] = 7
        # ZeroUniformRegister and ZeroRegister are always URZ or RZ and don't contribute to exceptions
        # NonZeroUniformRegister and NonZeroRegister don't contain values that can't be exceptions
        
        REGISTER = 'Register'
        UNIFORM_REGISTER = 'UniformRegister'
        SPECIAL_REGISTER = 'SpecialRegister'
        PREDICATE = 'Predicate'
        NON_ZERO_UNIFORM_REGISTER = 'NonZeroUniformRegister'
        NON_ZERO_REGISTER = 'NonZeroRegister'

        exceptions = dict()
        if REGISTER in kernel_used_regs and REGISTER in class_used_regs:
            uv = kernel_used_regs[REGISTER].difference(sm_details.REGISTERS.Register['RZ']) # type: ignore
            cur = class_used_regs[REGISTER]
            exceptions |= {k:cur[k].intersection(uv) for k in cur}
        if UNIFORM_REGISTER in kernel_used_regs and UNIFORM_REGISTER in class_used_regs:
            uv = kernel_used_regs[UNIFORM_REGISTER].difference(sm_details.REGISTERS.UniformRegister['URZ']) # type: ignore
            cur = class_used_regs[UNIFORM_REGISTER]
            exceptions |= {k:cur[k].intersection(uv) for k in cur}
        if SPECIAL_REGISTER in kernel_used_regs and SPECIAL_REGISTER in class_used_regs:
            uv = kernel_used_regs[SPECIAL_REGISTER].difference(sm_details.REGISTERS.SpecialRegister['SRZ']) # type: ignore
            cur = class_used_regs[SPECIAL_REGISTER]
            exceptions |= {k:cur[k].intersection(uv) for k in cur}
        if PREDICATE in kernel_used_regs and PREDICATE in class_used_regs:
            uv = kernel_used_regs[PREDICATE].difference(sm_details.REGISTERS.Predicate['PT']) # type: ignore
            cur = class_used_regs[PREDICATE]
            exceptions |= {k:cur[k].intersection(uv) for k in cur}
        if NON_ZERO_REGISTER in kernel_used_regs and NON_ZERO_REGISTER in class_used_regs:
            uv = kernel_used_regs[NON_ZERO_REGISTER]
            cur = class_used_regs[NON_ZERO_REGISTER]
            exceptions |= {k:cur[k].intersection(uv) for k in cur}
        if NON_ZERO_UNIFORM_REGISTER in kernel_used_regs and NON_ZERO_UNIFORM_REGISTER in class_used_regs:
            uv = kernel_used_regs[NON_ZERO_UNIFORM_REGISTER]
            cur = class_used_regs[NON_ZERO_UNIFORM_REGISTER]
            exceptions |= {k:cur[k].intersection(uv) for k in cur}

        return exceptions

    @staticmethod
    def calculate_const_size_sets(class_name:str, PREDICATES:dict, ENCODING:list):
        """
        This method calculates the input configurations that make an instruction have constant
        size predicates. This is needed for the instruction generator to get the set of configuration
        values that can be varied and the one that has to stay fixed.
        """
        non_const = [(k, v) for k,v in PREDICATES.items() if (not v.is_fixed_val()) and (k.startswith('ISRC') or k.startswith('IDEST'))]
        if non_const:
            # Get values from aliases that make a size not constant
            nc_sizes = {c:{'expr':e, 'enc_vals':{a:t.value().get_domain({}) for a,t in e.get_alias().items()}} for c,e in non_const}
            # Match aliases with corresponding register names
            nc_aliases = set(itt.chain.from_iterable(i['enc_vals'] for i in nc_sizes.values()))
            encodings = list(itt.chain.from_iterable(
                [(k, str(v.value().value), str(v.value().alias)) for k,v in i['alias'].get_alias().items()] 
                for i in ENCODING 
                if not (i['code_name'].startswith('!') or str(i['alias'])=='Opcode' or i['alias'].is_fixed_val())
            ))
            # This is a list of tripples where the first entry is the name used in the ENCODIGS stage and the remaining ones
            # are register name and alias name respectively
            #   {'size': ('AInteger', 'AInteger', 'size')}
            relevant_encodings = {(i[1] if i[1] in nc_aliases else i[2]):i for i in encodings if (i[1] in nc_aliases or i[2] in nc_aliases)}

            # Group the aliases such that the result is a dictionary where the key is a tuple with all sizes
            # ordered as nc_sizes_contracted, for example
            #    ['IDEST_SIZE', 'ISRC_A_SIZE', 'ISRC_B_SIZE']                
            # and nc_sizes_contracted_2 is a dictionary that can be accessed like
            #    nc_sizes_contracted_2[(0,32,32)]
            # where the entries in (0,32,32) corresponds to ['IDEST_SIZE', 'ISRC_A_SIZE', 'ISRC_B_SIZE'] respectively
            # and
            #    nc_sizes_contracted_2[(0,32,32)] == [({...}, {...}, {...}), ({...}, {...}, {...}), ({...}, {...}, {...})]
            # and
            #    nc_sizes_contracted_2[(0,32,32)][0] == ({'wmsk': {...}}, {'ParamA': {...}}, {'DC': {...}, 'LOD': {...}, 'TOFF1': {...}})
            # which represents one variant for an enc_vals set that makes the sizes of this particular instruction be
            #    IDEST_SIZE = 0, ISRC_A_SIZE = 32, ISRC_B_SIZE = 32
            nc_sizes_expr = [(s,v['expr'],SASS_Class.enc_set_to_enc_val(v['enc_vals'])) for s,v in nc_sizes.items()]
            nc_sizes_vals = {i[0]:[(int(i[1](enc_vals)),enc_vals) for enc_vals in i[2]] for i in nc_sizes_expr}
            nc_sizes_groups = {k:{ii[0]:[] for ii in i} for k,i in nc_sizes_vals.items()}
            for k,g in nc_sizes_vals.items():
                for gg in g:
                    nc_sizes_groups[k][gg[0]].append(gg[1])
            # print("==================================================", class_name)
            # if class_name == 'TEXS':
            #     pass
            # print(nc_sizes_groups)
            nc_sizes_contracted = [(s,[(k,SASS_Expr_Domain_Contract.group(x)) for k,x in ncg.items()]) for s,ncg in nc_sizes_groups.items()]
            s_order = [i[0] for i in nc_sizes_contracted]
            nc_sizes_contracted_2 = {tuple(v[i][0] for i in range(len(s_order))): [p for p in itt.product(*[v[i][1] for i in range(len(s_order))])] for v in itt.product(*[i for s,i in nc_sizes_contracted])}

            if len(nc_sizes) > 1 and any(len(i['enc_vals'].keys())>1 for k,i in nc_sizes.items()):
                pass

            # While nc_sizes_contracted_2[(0,32,32)][0] == ({'wmsk': {...}}, {'ParamA': {...}}, {'DC': {...}, 'LOD': {...}, 'TOFF1': {...}})
            # this following bit of code turns it into one dictionary, like
            #    {'wmsk': {...}, 'ParamA': {...}, 'DC': {...}, 'LOD': {...}, 'TOFF1': {...}}
            flat_ll = [(k,[list(itt.chain.from_iterable([list(iii.items()) for iii in ii])) for ii in i]) for k,i in nc_sizes_contracted_2.items()]
            nc_sizes_reduced = dict()
            for kk,ff in flat_ll:
                kk_res = []
                for ll in ff:
                    res = dict()
                    for k,v in ll:
                        rk = relevant_encodings[k][0]
                        if rk in res: res[rk] = res[rk].union(v)
                        else: res[rk] = v
                    kk_res.append(res)
                nc_sizes_reduced[kk] = kk_res
            return s_order, nc_sizes_reduced
        else:
            return [], dict()
