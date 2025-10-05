from __future__ import annotations
import typing, sqlite3, os, sys, inspect
import itertools as itt
from py_sass import SM_SASS
from py_sass import SASS_Expr_Dec
from py_sass import TT_Param, TT_Ext, TT_Cash, TT_Opcode, TT_Pred, TT_List, TT_Base
from py_sass import TT_OpAtNegate, TT_OpAtNot, TT_OpAtInvert, TT_OpAtSign, TT_OpAtAbs
from . import _config as sp
from ._instr_cubin_db import DbTable

class ProxyHelpers:
    @staticmethod
    def persist(obj:object, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int, self_parent:bool, ):
        if not isinstance(obj, object): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(db_con, sqlite3.Connection):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(types, dict):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_table_name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_id, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(self_parent, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)

        t_col_names, links, refs = DbTable.get_col_names(obj)
        t,pid = DbTable(obj,
            parent_table_name=parent_table_name,
            col_names_t=t_col_names,
            db_con=db_con,
            self_parent=self_parent).create_if_not_exists()
        
        obj.persist_id = t.insert(**(DbTable.get_insert_args(obj, t, types, pid=pid, parent_id=parent_id, refs=refs))) # type: ignore

        for link in links:
            for l in link:
                l.persist(db_con, types, t.table_name, obj.persist_id) # type: ignore

class Db_InstrMisc_Proxy:
    Type_BinOffset = 'BinOffset'
    Type_CubinOffset = 'CubinOffset'
    Type_InstrOffset = 'InstrOffset'
    Type_ClassName = 'ClassName'
    Type_InstrBits = 'InstrBits'

    def __init__(self, SeqNr:int, TypeName:str, MiscValue:str, AdditionalInfo:str):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(TypeName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(MiscValue, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr__:int = SeqNr
        self.___0X_Type___:str = TypeName
        self.___01_MiscValue___:str = MiscValue
        self.___02_AdditionalInfo___:str = AdditionalInfo

    def __str__(self):
        res = "TypeName: {TypeName}\n   SeqNr: {SeqNr}\n   MiscValue: {MiscValue}\n   AdditionalInfo: {AdditionalInfo}".format(
            TypeName = self.___0X_Type___,
            SeqNr = self.___00_SeqNr__,
            MiscValue = self.___01_MiscValue___,
            AdditionalInfo = self.___02_AdditionalInfo___
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(type_proxy:str, seq_nr:int, misc_value:str, additional_info:str):
        # ook
        if not isinstance(type_proxy, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(misc_value, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_InstrMisc_Proxy(seq_nr, type_proxy, misc_value, additional_info)
    
class Db_InstrClassDef_Proxy:
    Type_format = 'format'
    Type_encoding = 'encoding'
    Type_conditions = 'conditions'
    Type_properties = 'properties'
    Type_predicates = 'predicates'
    Type_opcodes = 'opcodes'
    Type_encoding = 'encoding'

    def __init__(self, SeqNr:int, TypeName:str, Content:str, AdditionalInfo:str):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(TypeName, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Content, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___0X_Type___:str = TypeName
        self.___01_Content___:str = Content
        self.___02_AdditionalInfo___:str = AdditionalInfo

    def __str__(self):
        res = "TypeName: {TypeName}\n   SeqNr: {SeqNr}\n   Content: {Content}\n   AdditionalInfo: {AdditionalInfo}".format(
            TypeName = self.___0X_Type___,
            SeqNr = self.___00_SeqNr___,
            Content = self.___01_Content___,
            AdditionalInfo = self.___02_AdditionalInfo___
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(type_proxy:str, seq_nr:int, def_str:str, additional_info:str) -> Db_InstrClassDef_Proxy:
        # ook
        if not isinstance(type_proxy, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(def_str, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        def_str = "".join(def_str.split("'"))
        return Db_InstrClassDef_Proxy(seq_nr, type_proxy, def_str, additional_info)

class Db_InstrLatency_Proxy:
    def __init__(self, SeqNr:int, Type:str, Input:str, Table:str, Row:str, Col:str, Cross:str, Val:int):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Type, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Input, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Table, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Row, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Col, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Cross, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Val, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_TypeName___:str = Type
        self.___02_Input___:str = Input
        self.___03_TableName___:str = Table
        self.___04_Row___:str = Row
        self.___05_Col___:str = Col
        self.___06_Cross___:str = Cross
        self.___07_Val___:int = Val

    def __str__(self):
        res = "TypeName: Latencies\n   SeqNr: {SeqNr}\n   Type: {Type}\n   Input: {Input}\n   Table: {Table}\n   Row: {Row}\n   Col: {Col}\n   Cross: {Cross}\n   Val: {Val}".format(
            SeqNr = self.___00_SeqNr___,
            Type = self.___01_TypeName___,
            Input = self.___02_Input___,
            Table = self.___03_TableName___,
            Row = self.___04_Row___,
            Col = self.___05_Col___,
            Cross = self.___06_Cross___,
            Val = self.___07_Val___
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(def_table:typing.List[list]) -> typing.List[Db_InstrLatency_Proxy]:
        # ook
        if not isinstance(def_table, list): raise Exception(sp.CONST__ERROR_ILLEGAL)

        res = []
        for ind,def_t in enumerate(def_table[1:]):
            # Need to remove all single quotes for the data base
            def_tt = [t.replace('\'','') if isinstance(t,str) else t for t in def_t]
            res.append(Db_InstrLatency_Proxy(ind, def_tt[0], def_tt[1], def_tt[2], def_tt[3], def_tt[4], def_tt[5], int(def_tt[6])))
        return res

class Db_UniverseComponent_Proxy:
    Type_op = 'op'
    Type_pred = 'pred'
    Type_opcode = 'opcode'
    Type_src_reg = 'src_reg'
    Type_dst_reg = 'dst_reg'
    Type_func = 'func'
    Type_attr = 'attr'
    Type_list = 'list'
    Type_larg = 'larg' # lists and attrs have largs as their arguments, for example Sa[...][...] has two larg children where each larg contains the respective list arguments
    Type_ext = 'ext'
    Type_cash = 'cash'
    Type_const = 'const'
    Type_none = 'none'

    def __init__(self, SeqNr:int, TypeName:str, InstrFieldAlias:str, BitFrom:int, BitTo:int, SassBits:str, ValueName:str, ValueType:str, ClassDef:str, AdditionalInfo:str, children:typing.List[Db_UniverseComponent_Proxy]):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(TypeName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(InstrFieldAlias, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(BitFrom, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(BitTo, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(SassBits, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ValueName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ValueType, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ClassDef, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_UniverseComponent_Proxy) for c in children):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___0X_Type___:str = TypeName
        self.___01_InstrFieldAlias___:str = InstrFieldAlias
        self.___02_BitFrom___:int = BitFrom
        self.___03_BitTo___:int = BitTo
        self.___04_SassBits___:str = SassBits
        self.___05_ValueName___:str = ValueName
        self.___06_ValueType___:str = ValueType
        self.___07_ClassDef___:str = ClassDef
        self.___08_AdditionalInfo___:str = AdditionalInfo
        self.___L0_children___:list = children

    def __str__(self):
        res = "TypeName: {TypeName}\n   SeqNr: {SeqNr}\n   InstrFieldAlias: {InstrFieldAlias}\n   BitFrom: {BitFrom}\n   BitTo: {BitTo}\n   SassBits: {SassBits}\n   ValueName: {ValueName}\n   ValueType: {ValueType}\n   ClassDef: {ClassDef}\n   AdditionalInfo: {AdditionalInfo}\n   n[children]: {nchildren}".format(
            TypeName = self.___0X_Type___,
            SeqNr = self.___00_SeqNr___,
            InstrFieldAlias = self.___01_InstrFieldAlias___,
            BitFrom = self.___02_BitFrom___,
            BitTo = self.___03_BitTo___,
            SassBits = self.___04_SassBits___,
            ValueName = self.___05_ValueName___,
            ValueType = self.___06_ValueType___,
            ClassDef = self.___07_ClassDef___,
            AdditionalInfo = self.___08_AdditionalInfo___,
            nchildren = len(self.___L0_children___)
        )
        if len(self.___L0_children___) > 0:
            res += "\n   " + "\n   ".join(str(i).replace('\n', '\n   ') for i in self.___L0_children___)
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=True)

    @staticmethod
    def create(type_proxy:str, seq_nr:int, instr_field_alias:str|None, dec_value:SASS_Expr_Dec|None, value_name:str, value_type:str, class_def:TT_Base, additional_info:str, children:typing.List[Db_UniverseComponent_Proxy]):
        # ook
        if not isinstance(type_proxy, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if type_proxy == Db_UniverseComponent_Proxy.Type_list: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_field_alias, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(dec_value, SASS_Expr_Dec|None):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(value_name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(value_type, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_def, TT_Ext|TT_Opcode|TT_Pred|TT_Param|TT_List|TT_OpAtNegate|TT_OpAtNot|TT_OpAtInvert|TT_OpAtAbs):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_UniverseComponent_Proxy) for c in children): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        if dec_value is not None:
            # This is to cover stuff like
            #   BITS_0_Sb = Sb;
            # from SM 86 upwards
            if len(dec_value.enc_ind) == 0:
                bit_from = 0
                bit_to = 0
            else:
                bit_from = min(dec_value.enc_ind)
                bit_to = max(dec_value.enc_ind)
            sass_bits_str = str(dec_value.sb)
        else:
            bit_from = -1
            bit_to = -1
            sass_bits_str = 'N/A'
        return Db_UniverseComponent_Proxy(seq_nr, type_proxy, instr_field_alias, bit_from, bit_to, sass_bits_str, value_name, value_type, str(class_def), additional_info, children)

    @staticmethod
    def create_attr(type_proxy:str, seq_nr:int, instr_field_alias:str|None, param1:typing.List[Db_UniverseComponent_Proxy], param2:typing.List[Db_UniverseComponent_Proxy], additional_info:str, children:typing.List[Db_UniverseComponent_Proxy]):
        # ook
        if not isinstance(type_proxy, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if type_proxy not in [Db_UniverseComponent_Proxy.Type_attr, Db_UniverseComponent_Proxy.Type_list]: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_field_alias, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(param1, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_UniverseComponent_Proxy) for c in param1): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(param2, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_UniverseComponent_Proxy) for c in param2): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_UniverseComponent_Proxy) for c in children): raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        # if instr_field_alias == '': instr_field_alias = 'N/A'
        params = [Db_UniverseComponent_Proxy(0, Db_UniverseComponent_Proxy.Type_larg, '', -1, -1, "N/A", "N/A", "N/A", "N/A", "param1 of larg", param1)]
        if param2 != []: params.append(Db_UniverseComponent_Proxy(0, Db_UniverseComponent_Proxy.Type_larg, '', -1, -1, "N/A", "N/A", "N/A", "N/A", "param2 of larg", param2))
        return Db_UniverseComponent_Proxy(seq_nr, type_proxy, instr_field_alias, -1, -1, "N/A", "N/A", "N/A", "N/A", additional_info, params + children)


    @staticmethod
    def create_cash(type_proxy:str, seq_nr:int, instr_field_alias:str|None, dec_value:SASS_Expr_Dec|None, value_name:str, value_type:str, class_def:TT_Cash, additional_info:str, augment:bool):
        # ook
        if not isinstance(type_proxy, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if type_proxy != Db_UniverseComponent_Proxy.Type_cash: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_field_alias, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(dec_value, SASS_Expr_Dec):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(value_name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(value_type, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_def, TT_Cash):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(augment, bool):raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        if dec_value is not None:
            bit_from = min(dec_value.enc_ind)
            bit_to = max(dec_value.enc_ind)
            sass_bits_str = str(dec_value.sb)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        children = []
        if class_def.added_later:
            value_name = value_name + "**"
        if augment:
            value_name = value_name + "[A]"
        return Db_UniverseComponent_Proxy(seq_nr, type_proxy, instr_field_alias, bit_from, bit_to, sass_bits_str, value_name, value_type, str(class_def), additional_info, children)

    @staticmethod
    def create_const(type_proxy:str, seq_nr:int, instr_field_alias:str|None, dec_value:SASS_Expr_Dec|None, additional_info:str):
        # ook
        if not isinstance(type_proxy, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if type_proxy != Db_UniverseComponent_Proxy.Type_const: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_field_alias, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(dec_value, SASS_Expr_Dec):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        if dec_value is not None:
            bit_from = min(dec_value.enc_ind)
            bit_to = max(dec_value.enc_ind)
            sass_bits_str = str(dec_value.sb)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return Db_UniverseComponent_Proxy(seq_nr, type_proxy, instr_field_alias, bit_from, bit_to, sass_bits_str, "N/A", "N/A", "N/A", additional_info, [])

class Db_UniverseEvalRegisters_Proxy:
    def __init__(self, SeqNr:int, ParentName:str, ValueName:str, Alias:str, Value:int, SassBitsStr:str, InstrProxy:Db_UniverseComponent_Proxy, AdditionalInfo:str, children:list):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ParentName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ValueName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Alias, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Value, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(SassBitsStr, str):raise Exception(sp.CONST__ERROR_ILLEGAL)    
        if not isinstance(InstrProxy, Db_UniverseComponent_Proxy|type):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_ParentName___:str = ParentName
        self.___02_ValueName___:str = ValueName
        self.___03_Alias___:str = Alias
        self.___04_Value___:int = Value
        self.___05_SassBitsStr___:str = SassBitsStr
        self.___06_AdditionalInfo___:str = AdditionalInfo
        self.___RR0_instr_proxy___:Db_UniverseComponent_Proxy|type = InstrProxy
        self.___L0_children___:list = children

    def __str__(self):
        res = "SeqNr: {SeqNr}\n   ParentName: {ParentName}\n   ValueName: {ValueName}\n   Alias: {Alias}\n   Value: {Value}\n   SassBits: {SassBits}\n   AdditionalInfo: {AdditionalInfo}\n   InstrProxy: {InstrProxy}\n   n[children]: {nchildren}".format(
            SeqNr = self.___00_SeqNr___,
            ParentName = self.___01_ParentName___,
            ValueName = self.___02_ValueName___,
            Alias = self.___03_Alias___,
            Value = self.___04_Value___,
            SassBits = self.___05_SassBitsStr___,
            InstrProxy = "\n   " + str(self.___RR0_instr_proxy___).replace('\n','\n   ') if self.___RR0_instr_proxy___ is not None else '-',
            AdditionalInfo = self.___06_AdditionalInfo___ if self.___06_AdditionalInfo___ else '-',
            nchildren = len(self.___L0_children___)
        )
        if len(self.___L0_children___) > 0:
            res += "\n   " + "\n   ".join(str(i).replace('\n', '\n   ') for i in self.___L0_children___)
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(index:int, parent_name:str, value_name:str, alias:str, value:int, sass_bits_str:str, proxy:Db_UniverseComponent_Proxy, additional_info:str, children:typing.List[Db_UniverseEvalEncoding_Proxy]):
        # ook
        if not isinstance(index, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(value_name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(alias, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(value, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sass_bits_str, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(proxy, Db_UniverseComponent_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_UniverseEvalRegisters_Proxy(index, parent_name, value_name, alias, value, sass_bits_str, proxy, additional_info, children)

class Db_UniverseEvalEncoding_Proxy:
    Type_fixed = 'fixed'
    Type_dynamic = 'dynamic'
    Type_table = 'table'
    Type_func = 'func'

    def __init__(self, SeqNr:int, TypeName:str, Expr:str, BitFrom:int, BitTo:int, SassBitsStr:str, InstrProxy:Db_UniverseComponent_Proxy|type, AdditionalInfo:str, children:list):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(TypeName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Expr, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(BitFrom, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(BitTo, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(SassBitsStr, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(InstrProxy, Db_UniverseComponent_Proxy|type):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___0X_Type___:str = TypeName
        self.___01_Expr___:str = Expr
        self.___02_SassBitsStr___:str = SassBitsStr
        self.___03_BitFrom___:int = BitFrom
        self.___04_BitTo___:int = BitTo
        self.___RR0_instr_proxy___:Db_UniverseComponent_Proxy|type = InstrProxy
        self.___05_AdditionalInfo___:str = AdditionalInfo
        self.___L0_children___:list = children

    def __str__(self):
        res = "TypeName: {TypeName}\n   SeqNr: {SeqNr}\n   Expr: {Expr}\n   BitFrom: {BitFrom}\n   BitTo: {BitTo}\n   SassBits: {SassBits}\n   AdditionalInfo: {AdditionalInfo}\n   InstrProxy: {InstrProxy}\n   n[children]: {nchildren}".format(
            TypeName = self.___0X_Type___,
            SeqNr = self.___00_SeqNr___,
            Expr = self.___01_Expr___,
            BitFrom = self.___03_BitFrom___,
            BitTo = self.___04_BitTo___,
            SassBits = self.___02_SassBitsStr___,
            InstrProxy = "\n   " + str(self.___RR0_instr_proxy___).replace('\n','\n   ') if self.___RR0_instr_proxy___ is not None else '-',
            AdditionalInfo = self.___05_AdditionalInfo___ if self.___05_AdditionalInfo___ else '-',
            nchildren = len(self.___L0_children___)
        )
        if len(self.___L0_children___) > 0:
            res += "\n   " + "\n   ".join(str(i).replace('\n', '\n   ') for i in self.___L0_children___)
        return res
    
    def add_ref(self, ref:Db_UniverseComponent_Proxy):
        if not isinstance(ref, Db_UniverseComponent_Proxy): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___RR0_instr_proxy___ = ref
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=True)

    @staticmethod
    def create(type_proxy:str, seq_nr:int, expr_str:str, proxy:Db_UniverseComponent_Proxy, additional_info:str, children:typing.List[Db_UniverseEvalEncoding_Proxy]):
        # ook
        if not isinstance(type_proxy, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(expr_str, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(proxy, Db_UniverseComponent_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_UniverseEvalEncoding_Proxy(seq_nr, type_proxy, expr_str, proxy.___02_BitFrom___, proxy.___03_BitTo___, proxy.___04_SassBits___, proxy, additional_info, children)

    @staticmethod
    def create_raw(type_proxy:str, seq_nr:int, expr_str:str, sass_bits_str:str, bit_from:int, bit_to:int, additional_info:str, children:typing.List[Db_UniverseEvalEncoding_Proxy]):
        # ook
        if not isinstance(type_proxy, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(expr_str, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sass_bits_str, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bit_from, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bit_to, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)

        # If we don't have a real proxy, still pass the type so that we can construct the db later
        proxy:type = Db_UniverseComponent_Proxy
        return Db_UniverseEvalEncoding_Proxy(seq_nr, type_proxy, expr_str, bit_from, bit_to, sass_bits_str, proxy, additional_info, children)

    @staticmethod
    def create_raw_w_proxy(type_proxy:str, seq_nr:int, expr_str:str, proxy:Db_UniverseComponent_Proxy, sass_bits_str:str, bit_from:int, bit_to:int, additional_info:str, children:typing.List[Db_UniverseEvalEncoding_Proxy]):
        # ook
        if not isinstance(type_proxy, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(expr_str, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(proxy, Db_UniverseComponent_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(sass_bits_str, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bit_from, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bit_to, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_UniverseEvalEncoding_Proxy(seq_nr, type_proxy, expr_str, bit_from, bit_to, sass_bits_str, proxy, additional_info, children)

class Db_UniverseEvalPredicate_Proxy:
    def __init__(self, SeqNr:int, PredicateName:str, PredicateValue:int, InstrProxy:Db_UniverseComponent_Proxy, SourceType:str, SourceOperand:str, AdditionalInfo:str, children:list):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(PredicateName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(PredicateValue, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(InstrProxy, Db_UniverseComponent_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(SourceType, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(SourceOperand, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_PredicateName___:str = PredicateName
        self.___RR0_instr_proxy___:Db_UniverseComponent_Proxy = InstrProxy
        self.___02_SourceType___:str = SourceType
        self.___03_PredicateValue___:int = PredicateValue
        self.___04_SourceOperand___:str = SourceOperand
        self.___05_AdditionalInfo___:str = AdditionalInfo
        self.___L0_children___:list = children

    def __str__(self):
        res = "TypeName: EvalPredicate\n   SeqNr: {SeqNr}\n   PredicateName: {PredicateName}\n   PredicateValue: {PredicateValue}\n   InstrProxy: {InstrProxy}\n   SourceType: {SourceType}\n   SourceOperand: {SourceOperand}\n   AdditionalInfo: {AdditionalInfo}\n   n[children]: {nchildren}".format(
            SeqNr = self.___00_SeqNr___,
            PredicateName = self.___01_PredicateName___,
            PredicateValue = self.___03_PredicateValue___,
            InstrProxy = "\n   " + str(self.___RR0_instr_proxy___).replace('\n','\n   ') if self.___RR0_instr_proxy___ is not None else '-',
            SourceType = self.___02_SourceType___,
            SourceOperand = self.___04_SourceOperand___,
            AdditionalInfo = self.___05_AdditionalInfo___,
            nchildren = len(self.___L0_children___)
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(seq_nr:int, size_field:str, size_val:int, source_decode:Db_UniverseComponent_Proxy, source_type:str, source_operand:str, additional_info:str, children:typing.List[Db_UniverseEvalPredicate_Proxy]):
        # ook
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(size_field, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(size_val, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(source_decode, Db_UniverseComponent_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(source_type, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(source_operand, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(children, list):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_UniverseEvalPredicate_Proxy(seq_nr, size_field, size_val, source_decode, source_type, source_operand, additional_info, children)

class Db_UniverseEval_Proxy:
    Type_predicate = 'predicate'
    Type_encoding = 'encoding'
    Type_registers = 'registers'

    def __init__(self, SeqNr:int, AdditionalInfo:str, Predicates:typing.List[Db_UniverseEvalPredicate_Proxy], Encodings:typing.List[Db_UniverseEvalEncoding_Proxy], EvalRegisters:typing.List[Db_UniverseEvalRegisters_Proxy]):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Predicates, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_UniverseEvalPredicate_Proxy) for i in Predicates): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Encodings, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_UniverseEvalEncoding_Proxy) for i in Encodings): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(EvalRegisters, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_UniverseEvalRegisters_Proxy) for i in EvalRegisters): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_AdditionalInfo___:str = AdditionalInfo
        self.___L0_predicates___:list = Predicates
        self.___L1_encodings___:list = Encodings
        self.___L2_eval_registers___:list = EvalRegisters

    def __str__(self):
        res = "TypeName: UniverseEval\n   SeqNr: {SeqNr}\n   Predicates: {Predicates}\n   Encodings: {Encodings}\n   EvalRegisters: {EvalRegisters}\n   AdditionalInfo: {AdditionalInfo}".format(
            SeqNr = self.___00_SeqNr___,
            AdditionalInfo = self.___01_AdditionalInfo___,
            Predicates = "\n      " + "\n      ".join(str(e).replace('\n', '\n      ') for e in self.___L0_predicates___),
            Encodings = "\n      " + "\n      ".join(str(e).replace('\n', '\n      ') for e in self.___L1_encodings___),
            EvalRegisters = "\n      " + "\n      ".join(str(e).replace('\n', '\n      ') for e in self.___L2_eval_registers___)
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)
    
    @staticmethod
    def create(seq_nr:int, predicates:typing.List[Db_UniverseEvalPredicate_Proxy], encodings:typing.List[Db_UniverseEvalEncoding_Proxy], eval_regs:typing.List[Db_UniverseEvalRegisters_Proxy], additional_info:str):
        # ook
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(predicates, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_UniverseEvalPredicate_Proxy) for i in predicates): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(encodings, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_UniverseEvalEncoding_Proxy) for i in encodings): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(eval_regs, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_UniverseEvalRegisters_Proxy) for i in eval_regs): raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_UniverseEval_Proxy(seq_nr, additional_info, predicates, encodings, eval_regs)

class Db_Universe_Proxy:
    def __init__(self, SeqNr:int, Props:str, AdditionalInfo:str, instr_parts:typing.List[Db_UniverseComponent_Proxy], instr_eval:Db_UniverseEval_Proxy):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Props, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_parts, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_UniverseComponent_Proxy) for i in instr_parts): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_eval, Db_UniverseEval_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_Props___:str = Props
        self.___02_AdditionalInfo___:str = AdditionalInfo
        self.___L0_instr_parts___:list = instr_parts
        self.___L1_instr_eval___:typing.List[Db_UniverseEval_Proxy] = [instr_eval] # make into link...

    def __str__(self):
        res = "TypeName: Universe\n   SeqNr: {SeqNr}\n   Props: {Props}\n   AdditionalInfo: {AdditionalInfo}\n   InstrParts: {InstrParts}\n   InstrEval: {InstrEval}".format(
            SeqNr = self.___00_SeqNr___,
            Props = self.___01_Props___,
            AdditionalInfo = self.___02_AdditionalInfo___,
            InstrParts = "\n      " + "\n      ".join(str(e).replace('\n', '\n      ') for e in self.___L0_instr_parts___),
            InstrEval = "\n      " + str(self.___L1_instr_eval___).replace('\n', '\n      ')
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(seq_nr:int, props:str, instr_parts:typing.List[Db_UniverseComponent_Proxy], instr_eval:Db_UniverseEval_Proxy, additional_info:str):
        # ook
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(props, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_parts, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_UniverseComponent_Proxy) for i in instr_parts): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_eval, Db_UniverseEval_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_Universe_Proxy(seq_nr, props, additional_info, instr_parts, instr_eval)
    
class Db_Instr_Proxy:
    def __init__(self, 
                 SeqNr:int, 
                 Code:str,
                 Class:str,
                 Desc:str,
                 TypeDesc:str,
                 AdditionalInfo:str,
                 universes:typing.List[Db_Universe_Proxy],
                 instr_class_def:typing.List[Db_InstrClassDef_Proxy], 
                 instr_latencies:typing.List[Db_InstrLatency_Proxy],
                 instr_misc:typing.List[Db_InstrMisc_Proxy]):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Code, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Class, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Desc, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(TypeDesc, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(universes, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_Universe_Proxy) for i in universes): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_class_def, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_InstrClassDef_Proxy) for i in instr_class_def): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_latencies, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_InstrLatency_Proxy) for i in instr_latencies): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_misc, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_InstrMisc_Proxy) for i in instr_misc): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_Code___:str = Code
        self.___02_Class___:str = Class
        self.___03_Desc___:str = Desc
        self.___04_TypeDesc___:str = TypeDesc
        self.___05_AdditionalInfo___:str = AdditionalInfo
        self.___L0_universes___:list = universes
        self.___L1_instr_class_def___:list = instr_class_def
        self.___L2_instr_latencies___:list = instr_latencies
        self.___L3_instr_misc___:list = instr_misc

    def __str__(self):
        res = "TypeName: Instr\n   SeqNr: {SeqNr}\n   Code: {Code}\n   Class: {Class}\n   Desc: {Desc}\
            \n   TypeDesc: {TypeDesc}\n   AdditionalInfo: {AdditionalInfo}\n   n[Universes]: {n_Universes}\n   Universes: {Universes}\
            \n   InstrClassDef: {InstrClassDef}\n   InstrLatencies: {InstrLatencies}\n   InstrMisc: {InstrMisc}".format(
            SeqNr = self.___00_SeqNr___,
            Code = self.___01_Code___,
            Class = self.___02_Class___,
            Desc = self.___03_Desc___,
            TypeDesc = self.___04_TypeDesc___,
            AdditionalInfo = self.___05_AdditionalInfo___,
            n_Universes = len(self.___L0_universes___),
            Universes = "\n      " + "\n      ".join(str(e).replace('\n', '\n      ') for e in self.___L0_universes___),
            InstrClassDef = "\n      " + "\n      ".join(str(e)[:-1].replace('\n', '\n      ') for e in self.___L1_instr_class_def___),
            InstrLatencies = "\n      " + "\n      ".join(str(e).replace('\n', '\n      ') for e in self.___L2_instr_latencies___),
            InstrMisc = "\n      " + "\n      ".join(str(e).replace('\n', '\n      ') for e in self.___L3_instr_misc___),
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(seq_nr:int, code:str, class_name:str, desc:str, type_desc:str, additional_info:str,
               universes:typing.List[Db_Universe_Proxy],
               instr_class_def:typing.List[Db_InstrClassDef_Proxy], 
               instr_latencies:typing.List[Db_InstrLatency_Proxy],
               instr_misc:typing.List[Db_InstrMisc_Proxy]):
        # ook
        if not isinstance(seq_nr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(code, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(desc, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(type_desc, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(universes, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_Universe_Proxy) for i in universes): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_class_def, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_InstrClassDef_Proxy) for i in instr_class_def): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_latencies, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_InstrLatency_Proxy) for i in instr_latencies): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_misc, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(i, Db_InstrMisc_Proxy) for i in instr_misc): raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_Instr_Proxy(seq_nr, code, class_name, desc, type_desc, additional_info, universes, instr_class_def, instr_latencies, instr_misc)

class Db_GraphNode_Proxy:
    def __init__(self, 
                 SeqNr:int,
                 ParentLabel:str,
                 Label:str,
                 InstrProxy:Db_Instr_Proxy|type,
                 CycleProxy:Db_GraphCycle_Proxy|type,
                 AdditionalInfo:str):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ParentLabel, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Label, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(InstrProxy, Db_Instr_Proxy|type):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(CycleProxy, Db_GraphCycle_Proxy|type):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr # sequence number of the instruction inside the current kernel
        self.___01_ParentLabel___:str = ParentLabel # label of the superimposed node (like .L_x_0)
        self.___02_Label___:str = Label # the instruction code that comes out of the disasm tool
        self.___03_AdditionalInfo___:str = AdditionalInfo
        self.___RR0_instr___:Db_Instr_Proxy|type = InstrProxy # translation from the instr_offset
        self.___RR1_cycle___:Db_GraphCycle_Proxy|type = CycleProxy # translation from the instr_offset

    def __str__(self):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(seq_nr:int, parent_label:str, label:str, instr_proxy:Db_Instr_Proxy, cycle_proxy:Db_GraphCycle_Proxy|type, additional_info:str):
        # ook
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_label, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(label, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_proxy, Db_Instr_Proxy|type):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cycle_proxy, Db_GraphCycle_Proxy|type):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_GraphNode_Proxy(seq_nr, parent_label, label, instr_proxy, cycle_proxy, additional_info)
    
class Db_GraphEdge_Proxy:
    def __init__(self, 
                 AdditionalInfo:str,
                 GraphNodeProxyFrom:Db_GraphNode_Proxy, 
                 GraphNodeProxyTo:Db_GraphNode_Proxy):
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(GraphNodeProxyFrom, Db_GraphNode_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(GraphNodeProxyTo, Db_GraphNode_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        self.___00_AdditionalInfo___:str = AdditionalInfo
        self.___RR0_graph_node_proxy_from___:Db_GraphNode_Proxy|type = GraphNodeProxyFrom
        self.___RR1_graph_node_proxy_to___:Db_GraphNode_Proxy|type = GraphNodeProxyTo

    def __str__(self):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(additional_info:str,
               graph_node_proxy_from:Db_GraphNode_Proxy, 
               graph_node_proxy_to:Db_GraphNode_Proxy):
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(graph_node_proxy_from, Db_GraphNode_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(graph_node_proxy_to, Db_GraphNode_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_GraphEdge_Proxy(additional_info, graph_node_proxy_from, graph_node_proxy_to)

class Db_GraphCondition_Proxy:
    def __init__(self, 
                 Edge:Db_GraphEdge_Proxy,
                 Condition:Db_Instr_Proxy,
                 AdditionalInfo:str):
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Edge, Db_GraphEdge_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Condition, Db_Instr_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        self.___00_AdditionalInfo___:str = AdditionalInfo
        self.___RR0_edge___:Db_GraphEdge_Proxy|type = Edge
        self.___RR1_condition___:Db_Instr_Proxy|type = Condition

    def __str__(self):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(edge:Db_GraphEdge_Proxy,
               condition:Db_Instr_Proxy,
               additional_info:str):
        if not isinstance(edge, Db_GraphEdge_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(condition, Db_Instr_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_GraphCondition_Proxy(edge, condition, additional_info)

class Db_GraphCycle_Proxy:
    def __init__(self, 
                 Cycle:int,
                 FirstInstruction:Db_Instr_Proxy,
                 Condition:Db_Instr_Proxy,
                 AdditionalInfo:str):
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Cycle, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(FirstInstruction, Db_Instr_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Condition, Db_Instr_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_cycle___:int|type = Cycle
        self.___01_AdditionalInfo___:str = AdditionalInfo
        self.___RR0_condition___:Db_Instr_Proxy|type = FirstInstruction
        self.___RR1_condition___:Db_Instr_Proxy|type = Condition

    def __str__(self):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(cycle:int,
               first_instruction:Db_Instr_Proxy,
               condition:Db_Instr_Proxy,
               additional_info:str):
        if not isinstance(cycle, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(first_instruction, Db_Instr_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(condition, Db_Instr_Proxy):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_GraphCycle_Proxy(cycle, first_instruction, condition, additional_info)

class Db_KernelGraph_Proxy:
    def __init__(self, SeqNr:int, 
                 AdditionalInfo:str, 
                 nodes:typing.List[Db_GraphNode_Proxy], 
                 edges:typing.List[Db_GraphEdge_Proxy],
                 conditions:typing.List[Db_GraphCondition_Proxy],
                 cycles:typing.List[Db_GraphCycle_Proxy]):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(nodes, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_GraphNode_Proxy) for c in nodes): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(edges, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_GraphEdge_Proxy) for c in edges): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(conditions, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_GraphCondition_Proxy) for c in conditions): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cycles, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_GraphCycle_Proxy) for c in cycles): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_AdditionalInfo___:str = AdditionalInfo
        self.___L0_cycles___:list = cycles
        self.___L1_nodes___:list = nodes
        self.___L2_edges___:list = edges
        self.___L3_conditions___:list = conditions

    def __str__(self):
        raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(seq_nr:int, 
               nodes:typing.List[Db_GraphNode_Proxy], 
               edges:typing.List[Db_GraphEdge_Proxy], 
               conditions:typing.List[Db_GraphCondition_Proxy],
               cycles:typing.List[Db_GraphCycle_Proxy],
               additional_info:str):
        # ook
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(nodes, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_GraphNode_Proxy) for c in nodes): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(edges, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_GraphEdge_Proxy) for c in edges): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(conditions, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_GraphCondition_Proxy) for c in conditions): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(cycles, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_GraphCycle_Proxy) for c in cycles): raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_KernelGraph_Proxy(seq_nr, additional_info, nodes, edges, conditions, cycles)

class Db_KernelMisc_Proxy:
    Type_WebId = 'WebId'
    Type_UsedRegs = 'UsedRegs'
    Type_UsedAlias = 'UsedAlias'
    Type_InstrOffset = 'InstrOffset'
    Type_KernelOffset = 'KernelOffset'
    Type_BinOffset = 'BinOffset'
    Type_UsedRegNames = 'UsedRegNames'
    Type_KernelDecoded = 'KernelDecoded'

    def __init__(self, SeqNr:int, TypeName:str, MiscValue:str, AdditionalInfo:str):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(TypeName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(MiscValue, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr__:int = SeqNr
        self.___0X_Type___:str = TypeName
        self.___01_MiscValue___:str = MiscValue
        self.___02_AdditionalInfo___:str = AdditionalInfo

    def __str__(self):
        res = "TypeName: {TypeName}\n   SeqNr: {SeqNr}\n   MiscValue: {MiscValue}\n   AdditionalInfo: {AdditionalInfo}".format(
            TypeName = self.___0X_Type___,
            SeqNr = self.___00_SeqNr__,
            MiscValue = self.___01_MiscValue___,
            AdditionalInfo = self.___02_AdditionalInfo___
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(type_proxy:str, seq_nr:int, misc_value:str, additional_info:str):
        # ook
        if not isinstance(type_proxy, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(misc_value, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        # remove all '..' from arguments
        if type_proxy in [Db_KernelMisc_Proxy.Type_UsedAlias, Db_KernelMisc_Proxy.Type_UsedRegs]:
            # These can be entries like this:
            #   {'Register': {'Ra', 'Rc', 'Rd', 'Rb'}, 'SpecialRegister': {'SRa'}, 'Predicate': {'Pp', 'Pq'}}
            # Can't have the many quotes for the database...
            misc_value = misc_value.replace("'", "")
        return Db_KernelMisc_Proxy(seq_nr, type_proxy, misc_value, additional_info)

class Db_Kernel_Proxy:
    def __init__(self, 
                 SeqNr:int, 
                 Name:str, 
                 AdditionalInfo:str, 
                 instr_list:typing.List[Db_Instr_Proxy], 
                 kernel_misc:typing.List[Db_KernelMisc_Proxy]):
                #  kernel_graph:typing.List[Db_KernelGraph_Proxy]):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_list, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_Instr_Proxy) for c in instr_list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(kernel_misc, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_KernelMisc_Proxy) for c in kernel_misc): raise Exception(sp.CONST__ERROR_ILLEGAL)
        # if not isinstance(kernel_graph, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        # if not all(isinstance(c, Db_KernelGraph_Proxy) for c in kernel_graph): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_Name___:str = Name
        self.___02_AdditionalInfo___:str = AdditionalInfo
        self.___L0_instr_list___:list = instr_list
        self.___L1_kernel_misc___:list = kernel_misc
        # self.___L2_kernel_graph___:list = kernel_graph

    def __str__(self):
        res = "TypeName: Kernel\n   SeqNr: {SeqNr}\n   Name: {Name}\n   AdditionalInfo: {AdditionalInfo}\n   len[InstrList]: {l_InstrList}\n   InstrList: {InstrList}\n len[KernelMisc]: {l_KernelMisc}\n   KernelMisc: {KernelMisc}".format(
            SeqNr = self.___00_SeqNr___,
            Name = self.___01_Name___,
            AdditionalInfo = self.___02_AdditionalInfo___,
            l_InstrList = len(self.___L0_instr_list___),
            InstrList = "\n   " + "\n   ".join(str(i).replace('\n', '\n   ') for i in self.___L0_instr_list___),
            l_KernelMisc = len(self.___L1_kernel_misc___),
            KernelMisc = "\n   " + "\n   ".join(str(i).replace('\n', '\n   ') for i in self.___L1_kernel_misc___)
        )
        return res

    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(seq_nr:int, 
               kernel_name:str, 
               instr_list:typing.List[Db_Instr_Proxy], 
               kernel_misc:typing.List[Db_KernelMisc_Proxy], 
            #    kernel_graph:typing.List[Db_KernelGraph_Proxy], 
               additional_info:str):
        # ook
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(kernel_name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(instr_list, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_Instr_Proxy) for c in instr_list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(kernel_misc, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_KernelMisc_Proxy) for c in kernel_misc): raise Exception(sp.CONST__ERROR_ILLEGAL)
        # if not isinstance(kernel_graph, list):raise Exception(sp.CONST__ERROR_ILLEGAL)
        # if not all(isinstance(c, Db_KernelGraph_Proxy) for c in kernel_graph): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str):raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_Kernel_Proxy(seq_nr, kernel_name, additional_info, instr_list, kernel_misc) #, kernel_graph)

class Db_BinaryMisc_Proxy:
    Type_Version = 'Version'
    Type_EncW = 'EncW'
    Type_WordSize = 'WordSize'
    Type_TestRun = 'TestRun'
    Type_FullName = 'FullName'
    Type_BinaryDecoded = 'BinaryDecoded'

    def __init__(self, SeqNr:int, TypeName:str, MiscValue:str, AdditionalInfo:str):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(TypeName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(MiscValue, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr__:int = SeqNr
        self.___0X_Type___:str = TypeName
        self.___01_MiscValue___:str = MiscValue
        self.___02_AdditionalInfo___:str = AdditionalInfo

    def __str__(self):
        res = "TypeName: {TypeName}\n   SeqNr: {SeqNr}\n   MiscValue: {MiscValue}\n   AdditionalInfo: {AdditionalInfo}".format(
            TypeName = self.___0X_Type___,
            SeqNr = self.___00_SeqNr__,
            MiscValue = self.___01_MiscValue___,
            AdditionalInfo = self.___02_AdditionalInfo___
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        ProxyHelpers.persist(self, db_con, types, parent_table_name, parent_id, self_parent=False)

    @staticmethod
    def create(type_proxy:str, seq_nr:int, misc_value:str, additional_info:str):
        # ook
        if not isinstance(type_proxy, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(misc_value, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_BinaryMisc_Proxy(seq_nr, type_proxy, misc_value, additional_info)
    
class Db_BinaryData_Proxy:
    Type_BinHead = 'BinHead'
    Type_BinTail = 'BinTail'
    Type_CubinHead = 'CubinHead'
    Type_CubinTail = 'CubinTail'

    def __init__(self, SeqNr:int, TypeName:str, Data:bytes, AdditionalInfo:str):
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(TypeName, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Data, bytes):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(AdditionalInfo, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___0X_Type___:str = TypeName
        self.___01_Data___:bytes = Data
        self.___02_AdditionalInfo___:str = AdditionalInfo

    def __str__(self):
        res = "TypeName: {TypeName}\n   SeqNr: {SeqNr}\n   AdditionalInfo: {AdditionalInfo}\n   len[Data]: {l_Data}".format(
            TypeName = self.___0X_Type___,
            SeqNr = self.___00_SeqNr___,
            AdditionalInfo = self.___02_AdditionalInfo___,
            l_Data = len(self.___01_Data___)
        )
        return res
    
    def persist(self, db_con:sqlite3.Connection, types:dict, parent_table_name:str, parent_id:int):
        # NOTE: this is almost the same as in **ProxyHelpers.persist** but not exactly it
        if not isinstance(db_con, sqlite3.Connection):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(types, dict):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_table_name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(parent_id, int):raise Exception(sp.CONST__ERROR_ILLEGAL)

        t_col_names, links, refs = DbTable.get_col_names(self)
        t,pid = DbTable(
            self,
            parent_table_name=parent_table_name,
            col_names_t=t_col_names,
            db_con=db_con).create_if_not_exists()
        
        table_name = t.table_name
        args = DbTable.get_insert_args(self, t, types, pid=pid, parent_id=parent_id, refs=refs)
        # This is inserting byte data into the data base. To achieve that, we need an unnamed, parameterized
        # insert. This is less robust than the regular way with dictionaries because the sequence of the parameters
        # can't be arbitrary at this stage!!!
        t.insert_np((parent_id, types[table_name][self.___0X_Type___], args['SeqNr'], args['Data'], args['AdditionalInfo']))

    @staticmethod
    def create(type_proxy:str, seq_nr:int, data:bytes, additional_info:str):
        # ook
        if not isinstance(type_proxy, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(data, bytes): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_BinaryData_Proxy(seq_nr, type_proxy, data, additional_info)

class Db_Type_Proxy:
    # A proxy can contain Types.
    # Tables that have these also need a ___0X_Type___ column to effectively use them.
    # The table Db_Type_Proxy will collect all of these 'Type_...' fields automatically into a Type table.
    # The types are passed as a Python dict to all 'persist' methods (=> types:dict param)
    def __init__(self, db_con:sqlite3.Connection):
        types_table,_ = DbTable(self, 
            parent_table_name=None, 
            col_names_t=['Category text', 'Name text', 'AdditionalInfo text'], 
            db_con=db_con).create_if_not_exists()
        
        def get_args(tt:type):
            cat = DbTable.get_table_name_t(tt.__name__)
            return [{'Category':cat, 'Name':getattr(tt, i), 'AdditionalInfo':''} for i in dir(tt) if i.startswith('Type_')]
        
        # Isolate all Type_... fields from all Db_..._Proxy classes and create insert arguments for them
        args = list(itt.chain.from_iterable(get_args(o) for n,o in inspect.getmembers(sys.modules[__name__]) if inspect.isclass(o) if n.startswith('Db_') and n.endswith('_Proxy')))
        # Insert all of them into the Type Table
        for arg in args:
            types_table.insert(**arg)
        # Load all of them with their respective db ids
        all_types_n, all_types_r = types_table.select() # type: ignore
        # Group all of them such that we have a dictionary like {Category1:{Name1:id1, Name2:id2, ...}, ..., CategoryN:{Name1:idX, ... }}
        # ... then pass all_types to every persistance call and use it's id to reference the Types table instead of writing a cumbersome name
        self.__all_types = {g:{gg:[mmm[0] for mmm in mm][0] for gg,mm in itt.groupby([mm for mm in m], key=lambda x:x[2])} for g,m in itt.groupby(all_types_r, key=lambda x:x[1])}

    @property
    def all_types(self): return self.__all_types

class Db_Binary_Proxy:
    # This is the top-level table proxy:
    #   - Every table has it's own proxy class
    #   - A proxy can be persisted into an sqlite db
    #   - The entire db is connected with parent-child relations and references
    #      - there is one single top-level table Db_Binary_Proxy with no parent
    #      - Db_Binary_Proxy is the output of calling 'to_db()' on an SM_Cubin_File 
    #      - an in-memory db is the output of calling 'persist()' on a Db_Binary_Proxy
    #      - there are utility methods in SM_Cubin_Db like 
    #         1. 'SM_Cubin_Db.file_to_db()'
    #         2. 'SM_Cubin_Db.db_con_to_mem()'
    #         3. 'SM_Cubin_Db.db_mem_to_con()'
    #         4. 'SM_Cubin_Db.db_con_to_file()'
    #      - which covers all required work steps:
    #         - the server does 'SM_Cubin_Db.file_to_db()' and returns the result of 'SM_Cubin_Db.db_con_to_mem()'
    #         - the client applies 'SM_Cubin_Db.db_mem_to_con()' and then does 'SM_Cubin_Db.db_con_to_file()'
    def __init__(self, SeqNr:int, Name:str, Arch:int, kernel_list:typing.List[Db_Kernel_Proxy], binary_data:typing.List[Db_BinaryData_Proxy], binary_misc:typing.List[Db_BinaryMisc_Proxy], AdditionalInfo:str):
        # All db fields start and end with ___
        # ___0X_Type___:
        #    Reference to a type in the 'Type' table
        # ___00/01/..._[ColumnName]___:
        #    This is a column with fixed sequence number
        #    (without sequence number, Python sorts the columns alphabetically, which is not desirable)
        # ___RR_[ColumnName]___:
        #    This is a reference to an entry in another table. The entry must already exist and is referenced with the ID. 
        #    Tables that have a reference but nothing to reference can pass the Python 'type' of the referenced table (allow to construct the name of the field without needing an existing db entry)
        #    The column name is Ref_[referenced_table_name]_Id
        # ___L0/1/...___:
        #    List of children with a parent/child relation to the current table
        if not isinstance(SeqNr, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Name, str):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(Arch, int):raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(kernel_list, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_Kernel_Proxy) for c in kernel_list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(binary_data, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_BinaryData_Proxy) for c in binary_data): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(binary_misc, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_BinaryMisc_Proxy) for c in binary_misc): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___00_SeqNr___:int = SeqNr
        self.___01_Name___:str = Name
        self.___02_Arch___:int = Arch
        self.___03_AdditionalInfo___:str = AdditionalInfo
        self.___L0_kernel_list___:list = kernel_list
        self.___L1_binary_data___:list = binary_data
        self.___L2_binary_misc___:list = binary_misc

    def __str__(self):
        res = "TypeName: Binary\n   SeqNr: {SeqNr}\n   Name: {Name}\n   AdditionalInfo: {AdditionalInfo}\n   len[KernelList]: {l_KernelList}\n   KernelList: {KernelList}\n   len[BinaryData]: {l_BinaryData}\n   BinaryData: {BinaryData}\n len[BinaryMisc]: {l_BinaryMisc}\n   BinaryMisc: {BinaryMisc}".format(
            SeqNr = self.___00_SeqNr___,
            Name = self.___01_Name___,
            AdditionalInfo = self.___03_AdditionalInfo___,
            l_KernelList = len(self.___L0_kernel_list___),
            KernelList = "\n   " + "\n   ".join(str(i).replace('\n', '\n   ') for i in self.___L0_kernel_list___),
            l_BinaryData = len(self.___L1_binary_data___),
            BinaryData = "\n   " + "\n   ".join(str(i).replace('\n', '\n   ') for i in self.___L1_binary_data___),
            l_BinaryMisc = len(self.___L2_binary_misc___),
            BinaryMisc = "\n   " + "\n   ".join(str(i).replace('\n', '\n   ') for i in self.___L2_binary_misc___)
        )
        return res
    
    def add_binary_data(self, binary_data:typing.List[Db_BinaryData_Proxy]):
        if not isinstance(binary_data, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.___L1_binary_data___.extend(binary_data)

    def __persist(self, db_con:sqlite3.Connection, types:dict) -> sqlite3.Connection:
        # This is the starting point for all persistence...
        
        t_col_names, links, refs = DbTable.get_col_names(self)
        t,_ = DbTable(self,
            parent_table_name=None,
            col_names_t=t_col_names,
            db_con=db_con).create_if_not_exists()
        self.persist_id = t.insert(**DbTable.get_insert_args(self, t, types, refs=refs))

        for link in links:
            for l in link:
                l.persist(db_con, types, t.table_name, self.persist_id)

        return db_con
    
    @staticmethod
    def persist(bins:typing.List[Db_Binary_Proxy]) -> sqlite3.Connection:
        if not isinstance(bins, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_Binary_Proxy) for c in bins): raise Exception(sp.CONST__ERROR_ILLEGAL)

        # This is the starting point for all persistence...
        db_con:sqlite3.Connection = sqlite3.connect(':memory:')
        t_prox = Db_Type_Proxy(db_con)
        types = t_prox.all_types
        
        bin:Db_Binary_Proxy
        for bin in bins:
            bin.__persist(db_con, types)

        db_con.commit()
        return db_con

    @staticmethod
    def create(sass:SM_SASS, seq_nr:int, binary_name:str, kernel_list:typing.List[Db_Kernel_Proxy], binary_data:typing.List[Db_BinaryData_Proxy], binary_misc:typing.List[Db_BinaryMisc_Proxy], additional_info:str):
        # ook
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(binary_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(seq_nr, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(kernel_list, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_Kernel_Proxy) for c in kernel_list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(binary_data, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_BinaryData_Proxy) for c in binary_data): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(binary_misc, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(c, Db_BinaryMisc_Proxy) for c in binary_misc): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(additional_info, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

        return Db_Binary_Proxy(seq_nr, binary_name, sass.sm_nr, kernel_list, binary_data, binary_misc, additional_info)