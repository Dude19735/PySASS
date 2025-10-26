import typing
import itertools as itt
from py_sass_ext import SASS_Bits
from py_sass_ext import TT_Instruction as cTT_Instruction
from py_sass_ext import TT_Pred as cTT_Pred
from py_sass_ext import TT_NoPred as cTT_NoPred
from py_sass_ext import TT_AttrParam as cTT_AttrParam
from py_sass_ext import TT_Param as cTT_Param
from py_sass_ext import TT_Opcode as cTT_Opcode
from py_sass_ext import TT_Cash as cTT_Cash
from py_sass_ext import OperandVector, CashVector
from . import _config as sp
from ._tt_term import TT_Term
from ._tt_terms import TT_Pred, TT_Opcode, TT_Param, TT_List, TT_Reg, TT_ICode
from ._tt_terms import TT_Func, TT_Cash
from ._tt_terms import TT_OpAtAbs, TT_OpAtInvert, TT_OpAtNegate, TT_OpAtNot, TT_OpAtSign
# from py_sass_ext import TT_Pred, TT_Opcode, TT_Param, TT_List, TT_Reg, TT_ICode
# from py_sass_ext import TT_Func, TT_Cash
# from py_sass_ext import TT_OpAtAbs, TT_OpAtInvert, TT_OpAtNegate, TT_OpAtNot, TT_OpAtSign
from .sm_cu_details import SM_Cu_Details

class TT_Instruction:
    """
    This one contains the components of a complete instruction:
     - predicate
     - opcode
     - dest reg
     - source regs
     - scheduler parts

    It also contains all the methods necessary to translate a list of TT_Terms into nicer TT_Param, TT_Opcode, TT_Predicate and TT_Cash
    """
    def __init__(self,pred, opcode, regs, cashs):
        self.class_name = "N/A" # This one is set in the parser manually because the class_name is not accessible at object creation time
        self.pred = pred
        self.opcode = opcode
        # self.dst = dst
        self.regs = regs
        self.cashs = cashs
        self.is_copy = False

        self.sm_details = None
        self.eval = {}
        self.eval_alias = {}
        self.operand_index = []
        self.parent = None

        self.__default_enc_vals = dict()
    
    @property
    def register_set(self):
        return set([str(i.alias) for i in self.regs] + [str(self.pred.alias)])

    @property
    def extension_set(self):
        reg_ext = list(itt.chain.from_iterable([[str(i.alias), i.value.value] for i in itt.chain.from_iterable([i.extensions for i in self.regs if i.extensions])]))
        opc_ext = list(itt.chain.from_iterable([[str(i.alias), i.value.value] for i in self.opcode.extensions if i]))
        return set(reg_ext + opc_ext)
    
    @property
    def default_enc_vals(self) -> dict: return self.__default_enc_vals

    def add_default_enc_vals(self, alias:str, default_val:SASS_Bits):
        raise Exception(sp.CONST__ERROR_DEPRECATED)
        if not isinstance(alias, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(default_val, SASS_Bits): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__default_enc_vals[alias] = default_val

    def to_param(self, param:TT_Term, sm_details:SM_Cu_Details) -> TT_Param|TT_List:
        """
        Convert a TT_Term to a TT_Param
        """
        old = str(param)
        # if old == '[Register(RZ):Rb+SImm(20/0)*:Rb_offset]/EXP_DESC(noexp_desc):e_desc':
        #     pass
        if param.tt == TT_List.tt():
            ll = []
            for i in param.val:
                ll.append(TT_Param(self.class_name, i, sm_details))
            res = TT_List(self.class_name, ll, param.ext, sm_details)
        elif param.tt in (TT_Reg.tt(), TT_Func.tt()):
            res = TT_Param(self.class_name, param, sm_details)
        else:
            raise Exception("Class {0}: invalid param type".format(self.class_name))
        
        if not old == str(param).replace(' ',''):
            raise Exception("Class {0}: TT_Param {1} benchmark compare error".format(self.class_name, old))
        
        return res
    
    def add_opcode_bin(self, opcodes:dict, bin_ind:typing.Tuple):
        """
        We get the opcode at a later stage than when we first parse an instruction class. This
        method puts the opcode in the correct place.

        There are also cases where we get a decimal number instead of a binary code and the binary code
        may be split by an underscore '_'. This method also takes care of this complication.
        """
        # if self.class_name == 'hadd2_32i_':
        #     pass
        bin_str_t = opcodes['opcode']['b']
        if not bin_str_t.startswith('0b'):
            # sometimes we just get numbers. SM 52's HADD2_32I instruction is one like that:
            #   OPCODES
            #     HADD2_32Ifp16g0_pipe = 22;
            #     HADD2_32Ifp16g1_pipe = 22;
            #     HADD2_32I = 22;
            val = int(bin_str_t)
            val_bin = bin(val)[2:].zfill(len(bin_ind[0]))
            last_ind = bin_ind[0][0]-1
            res = []
            for b,i in zip(val_bin, bin_ind[0]):
                if not i == last_ind+1:
                    res.append('_')
                res.append(b)
                last_ind = i
            bin_str = "".join(res)
            if not bin_str.replace('_','') == val_bin: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else:
            bin_str = bin_str_t[2:]
        opcode:TT_Opcode
        opcode = self.opcode
        # sometimes the bin code is shorter than the indexes -.-
        #  => fill with zeros
        bin_str = bin_str.zfill(len(bin_ind[0]))
        opcode.set_opcode_bin(bin_str, bin_ind)

    def get_opcode_bin(self):
        res = self.opcode.get_opcode_bin()
        if res is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return res
    
    def get_used_regs_and_reuse(self, sm_details:SM_Cu_Details):
        all_aliases = dict()
        reuse_aliases = dict()
        reuse = next(iter(sm_details.REGISTERS.REUSE['reuse'])) # type: ignore
        noreuse = next(iter(sm_details.REGISTERS.REUSE['noreuse'])) # type: ignore
        for i in self.regs:
            # The registers follow the following format:
            if isinstance(i, TT_List):
                # What kinds exactly?
                #  - all lists of stuff: [ZeroRegister(RZ):Ra + UImm(20/0)*:uImm]
                for j in i.value:
                    # lists always contain TT_Param
                    if not isinstance(j, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    # TT_Param contain either TT_Reg or TT_Func
                    if isinstance(j.value, TT_Reg):
                        category = j.value.value
                        if not category in sm_details.NON_FUNC_REG: continue
                        if not category in all_aliases: all_aliases[category] = dict()
                        alias = str(j.value.alias)
                        dom = j.value.get_domain({})
                        all_aliases[category][alias] = dom
                        extensions = j.extensions
                        if extensions:
                            aa = {alias:{'a':str(e.value.alias), 'd':e.value.get_domain({})} for e in extensions if e.value.value == 'REUSE'}
                            if aa:
                                aa[alias]['d'] = {'reuse' : [v for v in aa[alias]['d'] if v == reuse][0], 'noreuse' : [v for v in aa[alias]['d'] if v == noreuse][0]}
                                reuse_aliases |= aa

            elif isinstance(i.value, TT_Reg):
                # What kinds exactly?
                #  - regular regusters: RegisterFAU:Rd
                #  - registers with attributs: C:srcConst[UImm(5/0*):constBank]*[ZeroRegister(RZ):Ra+SImm(17)*:immConstOffset]
                #  => in both instances RegisterFAU:Rd and C:srcConst are a [RegisterName]:[AliasName] pair
                # reg_vals[str(i.alias)] = set(int(x) for x in i.value.get_domain({}))
                # if (sp.SWITCH__USE_TT_EXT and isinstance(i, cTT_AttrParam)) or (not sp.SWITCH__USE_TT_EXT):
                for attr in i.attr:
                    # attributs are always lists of things and the lists always contain TT_Param
                    if not isinstance(attr, TT_List): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    for a in attr.value:
                        if not isinstance(a, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                        # TT_Param contain either TT_Reg or TT_Func
                        if isinstance(a.value, TT_Reg):
                            category = a.value.value
                            if not category in sm_details.NON_FUNC_REG: continue
                            if not category in all_aliases: all_aliases[category] = dict()
                            alias = str(a.value.alias)
                            dom = a.value.get_domain({})
                            all_aliases[category][alias] = dom
                            extensions = a.extensions
                            if extensions:
                                aa = {alias:{'a':str(e.value.alias), 'd':e.value.get_domain({})} for e in extensions if e.value.value == 'REUSE'}
                                if aa:
                                    aa[alias]['d'] = {'reuse' : [v for v in aa[alias]['d'] if v == reuse][0], 'noreuse' : [v for v in aa[alias]['d'] if v == noreuse][0]}
                                    reuse_aliases |= aa

                category = i.value.value
                if not category in sm_details.NON_FUNC_REG: continue
                if not category in all_aliases: all_aliases[category] = dict()
                alias = str(i.value.alias)
                dom = i.value.get_domain({})
                all_aliases[category][alias] = dom
                extensions = i.extensions
                if extensions:
                    aa = {alias:{'a':str(e.value.alias), 'd':e.value.get_domain({})} for e in extensions if e.value.value == 'REUSE'}
                    if aa:
                        aa[alias]['d'] = {'reuse' : [v for v in aa[alias]['d'] if v == reuse][0], 'noreuse' : [v for v in aa[alias]['d'] if v == noreuse][0]}
                        reuse_aliases |= aa

        # Add predicate or not?        
        # if self.FORMAT.pred:
        #     alias_names.append(str(self.FORMAT.pred.alias))

        return all_aliases, reuse_aliases

    def finalize(self, sm_details:SM_Cu_Details):
        """
        Initially, when an instruction class is parsed, we get a list of TT_Term. This method
        translates an instruction class into the final structure made up of TT_Predicate, TT_Opcode, TT_Param and TT_Cash.
        """
        old = str(self)
        if self.pred:
            self.pred = TT_Pred(self.class_name, self.pred, sm_details)
            self.eval.update(self.pred.eval)
            self.eval_alias.update(self.pred.eval_alias)
            self.operand_index.extend(self.pred.operand_index)
            
        if not self.opcode:
            raise Exception("Class {0}: missing opcode".format(self.class_name))            
        self.opcode = TT_Opcode(self.class_name, self.opcode, sm_details)
        self.eval.update(self.opcode.eval)
        self.eval_alias.update(self.opcode.eval_alias)
        self.operand_index.extend(self.opcode.operand_index)
        
        if self.regs:
            regs = []
            for r in self.regs:
                reg:TT_Param|TT_List = self.to_param(r, sm_details)
                regs.append(reg)
                self.eval.update(reg.eval)
                self.eval_alias.update(reg.eval_alias)
                self.operand_index.extend(reg.operand_index)
            self.regs = regs

        if not self.cashs:
            raise Exception("Class {0}: missing cashs".format(self.class_name))            

        cashs = []
        for c in self.cashs:
             cashs.append(TT_Cash(self.class_name, c, sm_details))
             self.eval.update(cashs[-1].eval)
             self.eval_alias.update(cashs[-1].eval_alias)
             self.operand_index.extend(cashs[-1].operand_index)
        self.cashs = cashs

        eval_obj = set({TT_Reg, TT_Func, TT_OpAtAbs, TT_OpAtInvert, TT_OpAtNegate, TT_OpAtNot, TT_OpAtSign, TT_ICode})
        if not all([type(i) in eval_obj for i in self.eval.values()]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not all([isinstance(i,str) for i in self.operand_index]): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        old = old.replace(' ','')
        new = str(self).replace(' ','')
        if not old == new:
            raise Exception("Class {0}: TT_Opcode {1} benchmark compare error".format(self.class_name, old))

        self.sm_details = sm_details

    def to_cpp(self) -> cTT_Instruction:
        pred:cTT_Pred|cTT_NoPred
        if self.pred is not None: pred = self.pred.to_cpp()
        else: pred = cTT_NoPred()
        opcode = self.opcode.to_cpp()
        regs = [r.to_cpp() for r in self.regs]
        cashs = [c.to_cpp() for c in self.cashs]

        instr = cTT_Instruction(self.class_name, pred, opcode, OperandVector(regs), CashVector(cashs))

        str_old = str(self)
        str_new = str(instr)
        if not (str_old == str_new): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        eval_old = self.eval
        eval_new = instr.eval

        eval_old_str = {k:str(v) for k,v in sorted(eval_old.items())}
        eval_new_str = {k:str(v) for k,v in sorted(eval_new.items())}
        if not (eval_old_str == eval_new_str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        if self.pred:
            pred_old_enc_vals = sorted(self.pred.get_enc_alias())
            pred_new_enc_vals = sorted(instr.pred.get_enc_alias())
            if not (pred_old_enc_vals == pred_new_enc_vals): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        opcode_old_enc_vals = sorted(self.opcode.get_enc_alias())
        opcode_new_enc_vals = sorted(instr.opcode.get_enc_alias())
        if not (opcode_old_enc_vals == opcode_new_enc_vals): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        regs_old_enc_vals = [sorted(i.get_enc_alias()) for i in self.regs]
        regs_new_enc_vals = [sorted(i.get_enc_alias()) for i in instr.regs]
        if not (all(i==j for i,j in zip(regs_old_enc_vals, regs_new_enc_vals))): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        cashs_old_enc_vals = [sorted(i.get_enc_alias()) for i in self.cashs]
        cashs_new_enc_vals = [sorted(i.get_enc_alias()) for i in instr.cashs]
        if not (all(i==j for i,j in zip(cashs_old_enc_vals, cashs_new_enc_vals))): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        return instr

    def __str__(self):
        """
        This __str__ method should approximately ouptut the same as is in the instructions.txt file
        for each instruction class (barring whitespaces, ".." and other weird stuff).
        """
        val = ['FORMAT']
        if self.pred:
            val[-1] += ' PREDICATE ' + str(self.pred)

        val[-1] += (' ' + str(self.opcode))
        # if self.dst:
        #     val.append("   " + str(self.dst))
        if self.regs:
            for n,i in enumerate(self.regs):
                if n > 0: s = "   ,"
                else: s = "    "
                val.append(s + str(i))
        for i in self.cashs:
            val.append(str(i))

        return "\n".join(val)
    
    def to_other_kind_of_string(self, opcode:str):
        """
        This method outputs some fitting format for the search db. This is not the same as in the instructions.txt files
        """
        val = ['FORMAT']
        if self.pred:
            val[-1] += ' PREDICATE ' + str(self.pred)

        val[-1] += " " + str(self.opcode).replace('Opcode', opcode)

        if self.regs:
            for n,i in enumerate(self.regs):
                if n > 0: s = "   ,"
                else: s = "    "
                val.append(s + str(i))
        for i in self.cashs:
            val.append(str(i))

        return "\n".join(val)
