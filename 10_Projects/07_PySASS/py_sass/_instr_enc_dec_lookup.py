from __future__ import annotations
from . import _config as sp
from py_sass_ext import BitVector
from .sm_cu import SM_XX_Instr_Desc

class Instr_EncDec_Lookup:
    class MInstr:
        def __init__(self, class_name:str, is_alternate:bool, d_set:set, params:dict, desc:SM_XX_Instr_Desc|None, funit:list):
            self.class_name = class_name
            self.is_alternate = is_alternate
            self.d_set = d_set
            self.params = params
            self.deciders = sorted([(i['code_ind'][0], params[i['code_name']]) for i in funit if i['code_name'] in params], key=lambda x: len(x[0]), reverse=True)
            self.same_class = []
            self.same_class_alternate = []
            self.desc = desc
        @staticmethod
        def to_str(obj:Instr_EncDec_Lookup.MInstr, indent:str):
            res = indent + obj.class_name + (' [ALTERNATE]' if obj.is_alternate else "") + "\n"
            if obj.same_class: 
                for c,a in zip(obj.same_class, obj.same_class_alternate):
                    res += indent + "   " + ('[ALTERNATE] ' if a else '[DUPLICATE] ') + c + "\n"
            res += indent + "    [DECIDERS] [" + ", ".join(obj.params.keys()) + "]"
            if obj.desc is not None: res += "\n" + indent + "   [INSTR_DOC] " + obj.desc.doc()
            return res
        @staticmethod
        def to_json(obj:Instr_EncDec_Lookup.MInstr):
            res = dict()
            res['class_name'] = obj.class_name
            res['sad'] = 'A' if obj.is_alternate else 'S'
            res['alternates'] = []

            if obj.same_class: 
                for c,a in zip(obj.same_class, obj.same_class_alternate):
                    res['alternates'].append({
                        'class_name': c,
                        'sad' : 'A' if a else 'D'
                    })
            res['deciders'] = {k:["".join(str(vvv) for vvv in vv) for vv in v] for k,v in obj.params.items()}
            return res
        @staticmethod
        def get_others(obj:Instr_EncDec_Lookup.MInstr):
            res = {obj.class_name: []}
            if obj.same_class: 
                for c,a in zip(obj.same_class, obj.same_class_alternate):
                    res[obj.class_name].append(c)
            return res

        @staticmethod
        def get_main_class(obj:Instr_EncDec_Lookup.MInstr) -> str:
            return obj.class_name
        @staticmethod
        def match(obj:Instr_EncDec_Lookup.MInstr, instr_bits:BitVector):
            for d in obj.deciders:
                enc_bits = tuple(instr_bits[i] for i in d[0])
                if not enc_bits in d[1]: return False
            return True
        
    class SInstr:
        def __init__(self, class_name:str, is_alternate:bool, desc:SM_XX_Instr_Desc|None):
            self.class_name = class_name
            self.is_alternate = is_alternate
            self.desc = desc
        @staticmethod
        def to_str(obj:Instr_EncDec_Lookup.SInstr, indent:str):
            res = indent + obj.class_name + (' [S] [ALTERNATE]' if obj.is_alternate else " [S]")
            if obj.desc is not None: res += "\n" + indent + "   [INSTR_DOC] " + obj.desc.doc()
            return res
        @staticmethod
        def to_json(obj:Instr_EncDec_Lookup.SInstr):
            res = dict()
            res['class_name'] = obj.class_name
            res['sad'] = 'A' if obj.is_alternate else 'S'
            res['alternates'] = []
            res['deciders'] = {}
            return res
        @staticmethod
        def get_others(obj:Instr_EncDec_Lookup.SInstr):
            return {obj.class_name: []}
        @staticmethod
        def get_main_class(obj:Instr_EncDec_Lookup.SInstr) -> str:
            return obj.class_name
        @staticmethod
        def match(obj:Instr_EncDec_Lookup.SInstr, instr_bits:BitVector): return True

    def __init__(self):
        self.instr_dict = dict()
        self.opcode_bin = tuple()

    @staticmethod
    def to_json(obj:Instr_EncDec_Lookup):
        opcode_key = "".join(str(i) for i in obj.opcode_bin)
        res = {opcode_key : []}
        for i in obj.instr_dict.values():
            if isinstance(i, Instr_EncDec_Lookup.SInstr):
                p = Instr_EncDec_Lookup.SInstr.to_json(i)
            else:
                p = Instr_EncDec_Lookup.MInstr.to_json(i)
            res[opcode_key].append(p)
        return res
    
    @staticmethod
    def get_others(obj:Instr_EncDec_Lookup):
        res = dict()
        for i in obj.instr_dict.values():
            if isinstance(i, Instr_EncDec_Lookup.SInstr):
                p = Instr_EncDec_Lookup.SInstr.get_others(i)
            else:
                p = Instr_EncDec_Lookup.MInstr.get_others(i)
            for k,v in p.items():
                if k in res: res[k].extend(v)
                else: res[k] = v
        return res

    @staticmethod
    def to_str(obj:Instr_EncDec_Lookup):
        res = ["".join(str(i) for i in obj.opcode_bin)]
        indent = 3*" "
        for i in obj.instr_dict.values():
            if isinstance(i, Instr_EncDec_Lookup.SInstr):
                res.append( Instr_EncDec_Lookup.SInstr.to_str(i, indent))
            else:
                res.append( Instr_EncDec_Lookup.MInstr.to_str(i, indent))
        return "\n".join(res)
    
    @staticmethod
    def get_main_classes(lu:dict) -> set:
        result = set()
        obj:Instr_EncDec_Lookup
        for obj in lu.values():
            for i in obj.instr_dict.values():
                if isinstance(i, Instr_EncDec_Lookup.SInstr):
                    result.add(Instr_EncDec_Lookup.SInstr.get_main_class(i))
                else:
                    result.add(Instr_EncDec_Lookup.MInstr.get_main_class(i))
        return result

    @staticmethod
    def get(obj:Instr_EncDec_Lookup, instr_bits:BitVector, target_class_name:str|None=None):
        instr:Instr_EncDec_Lookup.MInstr|Instr_EncDec_Lookup.SInstr
        instr_candidates = []
        for instr in obj.instr_dict.values():
            match=False
            if isinstance(instr, Instr_EncDec_Lookup.MInstr):
                match = Instr_EncDec_Lookup.MInstr.match(instr, instr_bits)
            else:
                match = Instr_EncDec_Lookup.SInstr.match(instr, instr_bits)
            if match:
                # If in test mode, try all matches. If we get more than one, raise Exception
                if target_class_name is not None:
                    instr_candidates.append(instr)
                else: return instr.class_name, ""

        if target_class_name is None: 
            return None, "Target class name for [{0}] not found: target_class_name == None!".format(type(instr).__name__) # type: ignore

        # If we find no match, raise Exception
        main_c = 0
        success = False
        for i in instr_candidates:
            if not i.is_alternate: main_c += 1
            if i.class_name == target_class_name:
                success = True
            elif target_class_name in i.same_class:
                success = True
        if not success: 
            return None, "Target class name for [{0}] not found: success == False!".format(type(instr).__name__) # type: ignore
        if main_c > 1:
            return None, "Target class name for [{0}] not found: main_c > 1!".format(type(instr).__name__) # type: ignore
        return target_class_name, ""

    @staticmethod
    def from_multiples(opcode_bin:tuple, group_lookup:list, group_classes:list, classes_dict:dict, desc:dict):
        if not isinstance(opcode_bin, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(group_lookup, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(group_classes, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not len(group_lookup) == len(group_classes): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(classes_dict, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(desc, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)

        mm = Instr_EncDec_Lookup()
        mm.instr_dict = dict()
        mm.opcode_bin = opcode_bin
        for og, class_name in zip(group_lookup, group_classes):
            instr = classes_dict[class_name].get_opcode_instr()
            if instr in desc: d:SM_XX_Instr_Desc|None = desc[instr]
            else: d:SM_XX_Instr_Desc|None = None
            Instr_EncDec_Lookup.insert_alts(og, class_name, mm.instr_dict, classes_dict, d)
        return mm

    @staticmethod
    def from_singles(opcode_bin:tuple, class_name:str, classes_dict:dict, desc:dict):
        if not isinstance(opcode_bin, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(classes_dict, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(desc, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)

        mm = Instr_EncDec_Lookup()
        instr = classes_dict[class_name].get_opcode_instr()
        d = desc[instr] if instr in desc else None
        mm.instr_dict = {class_name: Instr_EncDec_Lookup.SInstr(class_name, classes_dict[class_name].IS_ALTERNATE, d)}
        mm.opcode_bin = opcode_bin
        return mm

    @staticmethod
    def insert_alts(og:dict, class_name:str, instr_dict:dict, classes_dict:dict, desc:SM_XX_Instr_Desc|None):
        d_set = set((i[0], tuple(i[1])) for i in og.items())
        is_alternate = classes_dict[class_name].IS_ALTERNATE
        # Check if we already have an exact, indistinguishable equivalent instruction class
        v:Instr_EncDec_Lookup.MInstr
        for c,v in instr_dict.items():
            if d_set == v.d_set:
                # NOTE: the non-alternate classes always come first. If we find a duplicate and it's not an
                # ALTERNATE, it's a bug.
                if not is_alternate: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                # If it's an ALTERNATE, we have to make sure that it has the same number of CASHS as it's parent. If this is not
                # the case and for example, the parent has more cash definitions than it's child, the decode post processing will
                # augment the cash definitions wrongly.
                if not (len(classes_dict[c].FORMAT.cashs) == len(classes_dict[class_name].FORMAT.cashs)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                # if not classes_dict[class_name].get_opcode_instr() == classes_dict[c].get_opcode_instr(): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                v.same_class.append(class_name)
                v.same_class_alternate.append(is_alternate)
                return
        instr_dict[class_name] = Instr_EncDec_Lookup.MInstr(class_name, is_alternate, d_set, og, desc, classes_dict[class_name].ENCODING)        
