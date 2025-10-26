import re
import typing
import itertools as itt
from . import _config as sp
from ._sass_expression_ops import Op_Constant, Op_ConstBankAddress2, Op_ConstBankAddress0
from ._tt_instruction import TT_Instruction
if not sp.SWITCH__USE_PROPS_EXT:
    from ._tt_terms import TT_Opcode, TT_Param, TT_List, TT_Reg, TT_Ext
    from ._tt_terms import TT_Func
else:
    from py_sass_ext import TT_Opcode, TT_Param, TT_List, TT_Reg, TT_Ext
    from py_sass_ext import TT_Func, TT_AttrParam
from .sm_cu_details import SM_Cu_Details

class SASS_Class_Props:
    def __init__(self, format_tt:TT_Instruction, opcode:str, opcode_set:set, properties:dict, predicates:dict, encoding:list, is_alternate:bool, details:SM_Cu_Details):
        # these are a bunch of things that make this one easier and nicer
        self.__format_tt = format_tt
        self.__opcode = opcode
        self.__opcode_set = opcode_set
        self.__details = details
        self.__properties = properties
        self.__predicates = predicates
        self.__op_predicates:list = details.OPERATION.PREDICATES # type: ignore
        self.__op_properties:list = details.OPERATION.PROPERTIES # type: ignore
        self.__encoding = encoding
        
        # if class_.class_name == 'AL2P':
        #     pass
        self.__has_pred:bool = False
        self.__has_dst:bool = False
        self.__has_src:bool = False
        self.__has_list_arg:bool = False
        self.__has_attr_arg:bool = False
        self.__has_imm:bool = False
        self.__has_reuse:bool = False
        self.__is_alternate:bool = is_alternate
        self.__nr_dst:int = 0
        self.__nr_src:int = 0
        self.__dst_preds = set()
        self.__src_preds = set()
        
        # Find out what the alias for the cash bits is because they may vary slightly.
        # They cab be used by the set_RD/WR/USCHED_INFO/... in py_cubin.SM_CuBin_File to modify
        # the specific fields.
        self.__rd_alias = None
        self.__wr_alias = None
        self.__wr_early_alias = None
        self.__req_alias = None
        self.__usched_info_alias = None
        self.__batch_t_alias = None
        self.__pm_pred_alias = None

        # set a flag for easy filtering
        self.__has_rd = False
        self.__has_wr = False
        self.__has_wr_early = False
        self.__has_req = False
        self.__has_usched_info = False
        self.__has_batch_t = False
        self.__has_pm_pred = False

        # Check each cash entry for which one it is and set a flag if present
        for x in format_tt.cashs:
            xx = str(x)
            if xx.find('WR')>=0:
                self.__wr_alias = str(x.values[-1].alias)
                self.__has_wr = True
            elif xx.find('RD')>=0:
                self.__rd_alias = str(x.values[-1].alias)
                self.__has_rd = True
            elif xx.find('WR_EARLY')>=0:
                self.__wr_early_alias = str(x.values[-1].alias)
                self.__has_wr_early = True
            elif xx.find('REQ')>=0:
                self.__req_alias = str(x.values[-1].alias)
                self.__has_req = True
            elif xx.find('BATCH_T')>=0:
                self.__batch_t_alias = str(x.values[-1].alias)
                self.__has_batch_t = True
            elif xx.find('USCHED_INFO')>=0:
                self.__usched_info_alias = str(x.values[-1].alias)
                self.__has_usched_info = True
            elif xx.find('PM_PRED')>=0:
                self.__pm_pred_alias = str(x.values[-1].alias)
                self.__has_pm_pred = True
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        self.__has_variable_predicates = any(i.get_alias_names_set() != set() for i in self.__predicates.values())

        # Register aliases if they have a REUSE extension
        # These are also contained in __alias_regs
        self.__alias_reuse = set()

        self.__alias_pred = set()
        self.__alias_funcs = set()
        self.__alias_regs = set()
        self.__alias_exts = set()
        self.__alias_all = set()
        self.__alias_ops = set()
        # self.__alias_added_defaults = set()
        self.__tt_exts = dict()
        self.__tt_pred = dict()
        self.__tt_funcs = dict()
        self.__tt_regs = dict()
        self.__tt_reuse = dict()
        self.__list_rf_alias:typing.List[typing.Dict] = list()
        self.instr_properties()
        self.__alias_cashs = set([str(kk.alias) for kk in k.values if isinstance(kk, TT_Param)][-1] for k in format_tt.cashs)

        if not self.__alias_all == self.__check_alias(): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        self.__dst_types = dict()
        self.__dst_size = dict()
        self.__dst_operands = dict()
        self.__src_types = dict()
        self.__src_size = dict()
        self.__src_operands = dict()
        self.__src_names = dict()
        self.__dst_names = dict()
        self.__alias_and_size = dict()
        self.resolve_size_mappings()

        self.__const_bank_address:dict = {ind:i['alias'].get_sequenced_alias_names() for ind,i in enumerate(self.__encoding) if i['alias'].startswith_ConstBankAddressX()}
        

    def __check_alias(self):
        return self.__alias_cashs.union(self.__alias_regs).union(self.__alias_exts).union(self.__alias_funcs).union(self.__alias_ops).union(self.__alias_pred)

    @property
    def alias_and_size(self) -> dict:
        """This one contains the sizes of all operands, identified by their alias. The size is either an integer or a SASS_Expr.\\
        
        The SASS_Expr version has to be evaluated with a valid set of encoding values!

        :return: a dictionary with alias:size_expression pairs where the size_expression is either an int or a SASS_Expr.
        :rtype: dict
        """
        return self.__alias_and_size

    @property
    def const_bank_address(self) -> dict:
        """This one contains the index of the ENCODING entry and the aliases of the expression if the instruction
        class has either of
        * ConstBankAddress2
        * ConstBankAddress0

        For example:\\
        * ConstBankAddress2(Sc_bank,Sc_addr) => {9: ['Sc_addr', 'Sc_bank']}
        
        :return: dictionary with index into the ENCODINGS list and aliases of const bank address ENCODINGS
        :rtype: dict
        """
        return self.__const_bank_address
    @property
    def has_barrier(self) -> bool:
        """Contains True if the instruction class has RD, WR or WR_EARLY or multiple of them.

        :return: True if the instruction class has some kind of barrier
        :rtype: bool
        """
        return self.__has_rd or self.__has_wr or self.__has_wr_early
    @property
    def has_pred(self) -> bool: 
        """Usually instruction classes have a predicate '@[!]Predicate(PT):Pg'

        :return: True if the instruction class has a predicate, False otherwise
        :rtype: bool
        """        
        return self.__has_pred
    @property
    def has_dst(self) -> bool: 
        """Most instruction classes have one or more destination registers 'Register:Rd' (or similar).

        :return: True if the instruction class has at least one destination register, False otherwise
        :rtype: bool
        """        
        return self.__has_dst
    @property
    def has_src(self) -> bool:
        """Most instruction classes have one or more source registers 'Register:Ra', 'NonZeroRegister:Ra' (or similar).

        :return: True if the instruction class has at least one source register, False otherwise
        :rtype: bool
        """        
        return self.__has_src
    @property
    def has_list_arg(self) -> bool: 
        """Some instruction classes have lists. Usually they are associated with memory or register movements.

        For example:
        * [ NonZeroRegister:Ra + SImm(32/0)*:Ra_offset ]
        
        :return: True if the instruction class has some kind of list in the definition, False otherwise
        :rtype: bool
        """        
        return self.__has_list_arg
    @property
    def has_attr_arg(self) -> bool: 
        """Some instruction classes have attributes. Usually they are associated with memory or register movements.

        For example:
        * A:srcAttr[ NonZeroRegister:Ra ]
        * C:Sb[UImm(5/0*):Sb_bank]*[SImm(17)*:Sb_addr]
        * DESC:memoryDescriptor[UniformRegister:Ra_URc][Register:Ra /ONLY64:input_reg_sz_64_dist+SImm(24/0)*:Ra_offset]
        
        :return: True if the instruction class has some kind of list in the definition, False otherwise
        :rtype: bool
        """        
        return self.__has_list_arg
    @property
    def has_imm(self) -> bool: 
        """Many instruction classes use immediate values. They are designated with 'UImm', 'Imm', 'F16Imm', 'RSImm', etc
        
        For example
        * CX:Sb[UniformRegister:URb][UImm(16)*:Sb_offset]
        * RSImm(50)*:Ra_offset
        * F64Imm(64):Sc

        NOTE: the cash definitions for WR and RD barriers always contains an UImm. Cash definitions are not included in this property.
        
        :return: True if the instruction class contains an immediate value in the **operands**, False otherwise.
        :rtype: bool
        """        
        return self.__has_imm
    @property
    def has_reuse(self) -> bool: 
        """Many instruction classes have 'reuse/noreuse' extensions for registers.

        For example:
        * [-] [||] Register:Ra {/REUSE("noreuse"):reuse_src_a}

        :return: True if one or more operands have a reuse/noreuse extension, False otherwise
        :rtype: bool
        """        
        return self.__has_reuse

    @property
    def nr_dst(self) -> int: 
        """Most instruction classes have destination registers as operands. Usually they have an alias ending in '..d'.

        For example:
        * Rd
        * URd

        :return: the number of destination operands.
        :rtype: int
        """        
        return self.__nr_dst
    @property
    def nr_src(self) -> int: 
        """Most instruction classes have source registers. Usually they have aliases ending in '..a/b/c', depending on the SM version, up to '..e', leaving out '..d'.

        For example:
        * Ra
        * URc

        :return: the number of source operands
        :rtype: int
        """        
        return self.__nr_src
    @property
    def dst_preds(self) -> set: 
        """All instruction classes have a PREDICATES definition. For example

        PREDICATES 
            IDEST_SIZE = 32; 
            IDEST2_SIZE = 0; 
            ISRC_B_SIZE = 32; 
            ISRC_C_SIZE = 0; 
            ISRC_E_SIZE = 0; 
            ISRC_A_SIZE = 0; 

        This property contains as set with the destination names of the predicates. For example:
        * IDEST_SIZE
        * IDEST2_SIZE

        :return: a set with all destination names of the PREDICATES
        :rtype: set
        """        
        return self.__dst_preds
    @property
    def src_preds(self): 
        """All instruction classes have a PREDICATES definition. For example

        PREDICATES 
            IDEST_SIZE = 32; 
            IDEST2_SIZE = 0; 
            ISRC_B_SIZE = 32; 
            ISRC_C_SIZE = 0; 
            ISRC_E_SIZE = 0; 
            ISRC_A_SIZE = 0; 

        This property contains as set with the source names of the predicates. For example:
        * ISRC_B_SIZE
        * ISRC_E_SIZE

        :return: a set with all source names of the PREDICATES
        :rtype: set
        """  
        return self.__src_preds
    @property
    def is_alternate(self) -> bool: 
        """Some instruction classes are defined as ALTERNATES for other classes.

        For example:
        * ALTERNATE CLASS "depbar_all_"

        :return: True if the instruction class is an alternate, False otherwise
        :rtype: bool
        """        
        return self.__is_alternate
    
    @property
    def alias_cashs(self) -> set: 
        """All instruction classes have cash definitions in the FORMAT. This property contains their aliases.

        For example:
        * {'usched_info', 'batch_t', 'src_rel_sb', 'pm_pred', 'dst_wr_sb', 'req_bit_set'}

        :return: a set with all cash aliases
        :rtype: set
        """        
        return self.__alias_cashs
    @property
    def alias_funcs(self) -> set: 
        """Some instruction classes use immediate values in their operans. For example 'SImm(11)*:Ra_offset'. This property contains a set with all immediate value aliases.

        For example:
        * Ra_offset

        NOTE: it is called '_funcs' because the immediate values, for example SImm(11) look like functions.

        :return: a set with all immediate value aliases
        :rtype: set
        """        
        return self.__alias_funcs
    @property
    def tt_funcs(self) -> dict:
        """Some instruction classes use immediate values in their operans. For example 'SImm(11)*:Ra_offset'. This property contains a dict with all immediate value aliases-tt_object pairs.

        For example:
        * Ra_offset:TT_Func(...)

        NOTE: it is called '_funcs' because the immediate values, for example SImm(11) look like functions.

        :return: a dict with all immediate value aliases-tt_object pairs
        :rtype: dict
        """    
        return self.__tt_funcs
    @property
    def alias_regs(self) -> set: 
        """Most instruction classes use registers in their operands. For exaple 'Register:Ra'. This property contains a set with all register aliases.

        For example:
        * Ra

        :return: a set with all register operand aliases
        :rtype: set
        """        
        return self.__alias_regs
    @property
    def tt_regs(self) -> dict:
        """Most instruction classes use registers in their operands. For exaple 'Register:Ra'. This property contains a dict with all register aliases-tt_object pairs.

        For example:
        * Ra:TT_Reg

        :return: a dict with all register operand aliases-tt_object pairs
        :rtype: dict
        """        
        return self.__tt_regs
    @property
    def alias_pred(self) -> set: 
        """Most instruction classes have a predicate, for example '@[!]Predicate(PT):Pg'. This property contains a set {'Pg'}.

        For example:
        * Pg

        :return: a set with the predicate alias
        :rtype: set
        """        
        return self.__alias_pred
    @property
    def tt_pred(self) -> dict:
        """Most instruction classes have a predicate, for example '@[!]Predicate(PT):Pg'. This property contains a dict {'Pg':TT_Reg(...)}.

        For example:
        * Pg

        :return: a dict with the predicate tt object
        :rtype: dict
        """        
        return self.__tt_pred
    @property
    def list_rf_alias(self) -> list:
        """Instructions that have operands that are lists, for example if they access memory at some offset,
        return a non-empty list for this property.

        For example an instruction with a typical C:Sc[bank][addr] construct contains
        * [
            {'tt': <py_sass._tt_terms.TT_List object at 0x7ea7d7031f40>, 'a': {'Ra_URc': 'reg'}, 'type': 'attr_0.0'},
            {'tt': <py_sass._tt_terms.TT_List object at 0x7ea7d7032090>, 'a': {'Ra': 'reg', 'Ra_offset': 'func'}, 'type': 'attr_0.1'} \
          ]
        
        For example an instruction with a single [Reg, UReg, SImm] type operand contains
        * [
            {'tt': <py_sass._tt_terms.TT_List object at 0x7ea7d6fce960>, 'a': {'Ra': 'reg', 'Ra_URc': 'reg', 'Ra_offset': 'func'}, 'type': 'list_0'}
          ]

        For single and double attribute operands, the 'type' field contains things like 'attr_0.0' and 'attr_0.1'. The first
        index is the operand index, the second index is the attribute list index.

        For regular list operands, the 'type' field contains things like 'list_0' where the index is the
        operand index.

        :return: a list with the aliases of the registers and functions that are inside of lists
        :rtype: list
        """
        return self.__list_rf_alias
    @property
    def alias_ops(self) -> set: 
        """Most instruction classes contain operations, for example '[!], [-] or [~]'. This property contains their aliases.

        For example:
        * Pg@not ([!])
        * Ra@negate ([-])

        :return: a set with the operation aliases
        :rtype: set
        """  
        return self.__alias_ops
    @property
    def alias_exts(self) -> set: 
        """Most instruction classes have extensions to configure the instruction. This property contains a set with their aliases.

        For example:
        * {'io', 'sz'}

        :return: a set with the extension aliases
        :rtype: set
        """  
        return self.__alias_exts
    @property
    def tt_exts(self) -> dict:
        """Most instruction classes have extensions to configure the instruction. This property contains a dictionary with their alias and TT_Ext object.

        For example:
        * {'io':TT_Ext(...), 'sz':TT_Ext(...)}

        These can be used, for example to get the domains of individual extensions as well as other properties.

        :return: a list with the extension aliases and their TT_Ext objects
        :rtype: dict
        """  
        return self.__tt_exts
    @property
    def alias_reuse(self) -> set: 
        """Some instruction classes have a reuse/noreuse extension for some operands. This property contains a set with the aliases of the REGISTERS with those extensions.

        For example:
        * {'Ra', 'Rb'} for "Register:Ra /REUSE(noreuse):reuse_src_a" and "Register:Rb /REUSE(noreuse):reuse_src_b"

        :return: a set with the aliases of operands with REUSE capability
        :rtype: set
        """  
        return self.__alias_reuse
    @property
    def tt_reuse(self) -> dict:
        """Some instruction classes have a reuse/noreuse extension for some operands. This property contains a dict with the aliases-tt_object pairs of the REGISTERS with those extensions.

        For example:
        * {'Ra':TT_Reg(...), 'Rb':TT_Reg(...)} for "Register:Ra /REUSE(noreuse):reuse_src_a" and "Register:Rb /REUSE(noreuse):reuse_src_b"

        :return: a dict with the aliases-tt_object pairs of operands with REUSE capability
        :rtype: dict
        """  
        return self.__tt_reuse
    @property
    def alias_added_defaults(self) -> set: 
        """This property contains aliases of added cash definitions if "SASS_Class_Cash_Aug" is used.

        NOTE: the mechanism around "SASS_Class_Cash_Aug" doesn't work, but it's still in the code for reference.

        :return: an empty set unless "SASS_Class_Cash_Aug" is used
        :rtype: set
        """       
        raise Exception(sp.CONST__ERROR_DEPRECATED) 
        return self.__alias_added_defaults
    @property
    def alias_all(self) -> set: 
        """This property contains a set with all aliases used in the FORMAT section of the instruction class definition.

        It fullfills the condition:
        * alias_all == alias_cashs.union(alias_regs).union(alias_exts).union(alias_funcs).union(alias_ops).union(alias_pred)

        :return: a set with all FORMAT aliases
        :rtype: set
        """        
        return self.__alias_all

    @property
    def cash_has__wr(self) -> bool: 
        """Some instruction classes have a write barrier WR.
        * $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$

        :return: True if the instruction class has a WR barrier, False otherwise
        :rtype: bool
        """        
        return self.__has_wr
    @property
    def cash_alias__wr(self) -> str|None: 
        """If the instruction class has a write barrier, this property contains the main alias.

        For example, if $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ is defined
        * {'dst_wr_sb'}

        :return: alias of the WR barrier if present, None otherwise
        :rtype: str|None
        """        
        return self.__wr_alias
    @property
    def cash_has__wr_early(self) -> bool: 
        """In SM 90 and above, some instruction classes have a write early barrier WR_EARLY.
        * $( { & WR_EARLY:wr_early = UImm(3/0x7):src_rel_sb } )$

        :return: True if the instruction class has a WR_EARLY barrier, False otherwise
        :rtype: bool
        """        
        return self.__has_wr_early
    @property
    def cash_alias__wr_early(self) -> str|None: 
        """If the instruction class has a write early barrier, this property contains the main alias.

        For example, if $( { & WR_EARLY:wr_early = UImm(3/0x7):src_rel_sb } )$ is defined
        * {'src_rel_sb'}

        :return: alias of the WR_EARLY barrier if present, None otherwise
        :rtype: str|None
        """        
        return self.__wr_early_alias
    @property
    def cash_has__rd(self) -> bool: 
        """Some instruction classes have a read barrier WR.
        * $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$

        :return: True if the instruction class has a RD barrier, False otherwise
        :rtype: bool
        """   
        return self.__has_rd
    @property
    def cash_alias__rd(self) -> str|None: 
        """If the instruction class has a read barrier, this property contains the main alias.

        For example, if $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ is defined
        * {'src_rel_sb'}

        :return: alias of the RD barrier if present, None otherwise
        :rtype: str|None
        """  
        return self.__rd_alias
    @property
    def cash_has__batch_t(self) -> bool: 
        """All instruction classes from SM 70 upwards have a BATCH_T definition
        * $( { ? BATCH_T(NOP):batch_t } )$

        :return: True if the instruction class has a BATCH_T barrier, False otherwise
        :rtype: bool
        """ 
        return self.__has_batch_t
    @property
    def cash_alias__batch_t(self) -> str|None: 
        """If the instruction class has a batch_t definition, this property contains the main alias.

        For example, if $( { ? BATCH_T(NOP):batch_t } )$ is defined
        * {'batch_t'}

        :return: alias of the batch_t definition if present, None otherwise
        :rtype: str|None
        """  
        return self.__batch_t_alias
    @property
    def cash_has__req(self) -> bool: 
        """All instruction classes have a REQ definition
        * $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$

        :return: True if the instruction class has a REQ definition, False otherwise
        :rtype: bool
        """ 
        return self.__has_req
    @property
    def cash_alias__req(self) -> str|None: 
        """All instruction classes have a REQ definition, this property contains the main alias.

        For example, if $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ is defined
        * {'req_bit_set'}

        :return: alias of the REQ definition if present, None otherwise
        :rtype: str|None
        """  
        return self.__req_alias
    @property
    def cash_has__usched_info(self) -> bool: 
        """All instruction classes have an USCHED_INFO definition
        * $( { ? USCHED_INFO(DRAIN):usched_info } )$

        :return: True if the instruction class has a USCHED_INFO definition, False otherwise
        :rtype: bool
        """ 
        return self.__has_usched_info
    @property
    def cash_alias__usched_info(self) -> str|None: 
        """All instruction classes have a USCHED_INFO definition, this property contains the main alias.

        For example, if $( { ? USCHED_INFO(DRAIN):usched_info } )$ is defined
        * {'usched_info'}

        :return: alias of the USCHED_INFO definition if present, None otherwise
        :rtype: str|None
        """  
        return self.__usched_info_alias
    @property
    def cash_has__pm_pred(self) -> bool: 
        """Some instruction classes from SM 86 upwards have a PM_PRED definition
        * $( { ? PM_PRED(PMN):pm_pred } )$

        :return: True if the instruction class has a PM_PRED definition, False otherwise
        :rtype: bool
        """ 
        return self.__has_pm_pred
    @property
    def cash_alias__pm_pred(self) -> str|None: 
        """If the instruction class has a PM_PRED definition, this property contains the main alias.

        For example, if $( { ? PM_PRED(PMN):pm_pred } )$ is defined
        * {'pm_pred'}

        :return: alias of the PM_PRED definition if present, None otherwise
        :rtype: str|None
        """  
        return self.__pm_pred_alias

    @property
    def has_variable_predicates(self) -> bool: 
        """Some instruction classes have PREDICATES that depend on some parameters, usually defined as extensions. They usually resolve to a multiple of 32.

        For example:
        * IDEST_SIZE = 32 + (((sz == `AInteger@64)) * 32 + ((sz == `AInteger@96)) * 64 + ((sz == `AInteger@128)) * 96)
        
        :return: True if the instruction class has at least one parameterized predicate, False otherwise
        :rtype: bool
        """        
        return self.__has_variable_predicates

    @property
    def lat_set(self) -> set: 
        """Every instruction class has some mapping into the latencies table. This property contains as set with the mapping keys.

        For example:
        * {'BMMA', 'BMMAint_pipe'}

        :return: set with the keys used to map into the latencies table
        :rtype: set
        """        
        return self.__opcode_set
    @property
    def opcode(self) -> str:
        """The opcode of the instruction class.

        For example:
        * IADD3
        * LEA
        * I2F
        * ...

        :return: the opcode of the instruction class
        :rtype: str
        """        
        return self.__opcode
    # @property
    # def register_set(self) -> set: 
    #     """Almost all instruction classes use registers in their FORMAT definition.

    #     This property contains a set with the aliases of all used register types. That includes for example 'Register' and 'UniformRegister'. For example:
    #     * {'Ra', 'Pg', 'Rc', 'Rd', 'Rb', 'UPp'}

    #     :return: a set with all used register types aliases
    #     :rtype: set
    #     """        
    #     return set(self.__format_tt.register_set)
    # @property
    # def extension_set(self) -> set: 
    #     """Almost all instruction classes have extensions. This property contains a set with the aliases of all extensions.
        
    #     NOTE: that the extensions have some duality in their ENCODING where sometimes they use the parent register name and sometimes the alias. This property contains the one that is used in the ENCODING section.

    #     For example:
    #     * {'ROWONLY', 'size', 'REUSE', 'reuse_src_a', 'row_A', 'LOGICAL_OP1_BMMA', 'POPCONLY', 'SIZE', 'op', 'reuse_src_b', 'accum', 'col_B', 'COLONLY'}

    #     :return: a set with all extension aliases as used in the ENCODING section of the instruction class
    #     :rtype: set
    #     """        
    #     return set(self.__format_tt.extension_set)
    @property
    def min_wait_needed(self) -> int:
        """Minimum number of cycles required as given by the instruction PROPERTIES. min_wait_needed = 0 means, it's a fixed latency instruction with no barriers.

        :return: minimum cycles to wait for the instruction dispatcher before the next instruction
        :rtype: int
        """
        return self.__min_wait_needed
    
    @property
    def dst_types(self) -> dict: 
        """This property returns indications related to the [**type**] of an instruction operand. It includes
        the alias as well as the tt object of an operand\\
        **NOTE**: these are available up until SM 90. SM 100 and SM 120 have a different system.

        The [**destination types**] are
        * {'IDEST': {'Rd': {'type': 'DOUBLE', 'tt': '<py_sass.tt_terms.TT_Reg..>'}}, 'IDEST2': {}}\\
        
        for an example instruction class [dadd__RRC_RC] on SM 86 with following
        * FORMAT PREDICATE @[!]Predicate(PT):Pg \\
                Opcode /Round1(RN):rnd \\
                    Register:Rd \\
                    ,[-][||]Register:Ra /REUSE(noreuse):reuse_src_a \\
                    ,[-][||]C:Sc[UImm(5/0*):Sc_bank]*[SImm(17)*:Sc_addr] \\
                $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ \\
                $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ \\
                $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ \\
                $( { ? USCHED_INFO(DRAIN):usched_info } )$ \\
                $( { ? BATCH_T(NOP):batch_t } )$ \\
                $( { ? PM_PRED(PMN):pm_pred } )$
        
        * PROPERTIES
            INSTRUCTION_TYPE = INST_TYPE_COUPLED_EMULATABLE;
            IERRORS = (1 << IERROR_ILLEGAL_INSTR_DECODING) + (1 << IERROR_INVALID_CONST_ADDR_LDC) + (1 << IERROR_MISALIGNED_ADDR) + (1 << IERROR_MISALIGNED_REG) + (1 << IERROR_OOR_REG) + (1 << IERROR_PC_WRAP) + 0;
            MIN_WAIT_NEEDED = 0;
            SIDL_NAME = `SIDL_NAMES@DADD_C;
            VALID_IN_SHADERS = ISHADER_ALL;
            IDEST_OPERAND_MAP = (1 << INDEX(Rd));
            IDEST_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            IDEST2_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            IDEST2_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_C_OPERAND_MAP = (1 << INDEX(Sc_bank)) + (1 << INDEX(Sc_addr));
            ISRC_C_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            ISRC_E_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_E_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_A_OPERAND_MAP = (1 << INDEX(Ra));
            ISRC_A_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
        
        * PREDICATES
            IDEST_SIZE = 64;
            IDEST2_SIZE = 0;
            ISRC_B_SIZE = 0;
            ISRC_C_SIZE = 64;
            ISRC_E_SIZE = 0;
            ISRC_A_SIZE = 64;
            VIRTUAL_QUEUE = $VQ_REDIRECTABLE;
            ILABEL_Ra_SIZE = 64;
        
        :return: a dictionary with the types of the destination operands.
        :rtype: dict
        """
        return self.__dst_types
    @property
    def dst_size(self) -> dict:
        """This property returns the [**size**] of an instruction operand. For example 32.\\
        **NOTE**: these are available at least up until SM 120.

        The [**destination sizes**] are
        * {'IDEST': '<py_sass.tt_terms.SASS_Expr..>', 'IDEST2': '<py_sass.tt_terms.SASS_Expr..>'}\\
        
        for an example instruction class [dadd__RRC_RC] on SM 86 with following
        * FORMAT PREDICATE @[!]Predicate(PT):Pg \\
                Opcode /Round1(RN):rnd \\
                    Register:Rd \\
                    ,[-][||]Register:Ra /REUSE(noreuse):reuse_src_a \\
                    ,[-][||]C:Sc[UImm(5/0*):Sc_bank]*[SImm(17)*:Sc_addr] \\
                $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ \\
                $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ \\
                $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ \\
                $( { ? USCHED_INFO(DRAIN):usched_info } )$ \\
                $( { ? BATCH_T(NOP):batch_t } )$ \\
                $( { ? PM_PRED(PMN):pm_pred } )$
        
        * PROPERTIES
            INSTRUCTION_TYPE = INST_TYPE_COUPLED_EMULATABLE;
            IERRORS = (1 << IERROR_ILLEGAL_INSTR_DECODING) + (1 << IERROR_INVALID_CONST_ADDR_LDC) + (1 << IERROR_MISALIGNED_ADDR) + (1 << IERROR_MISALIGNED_REG) + (1 << IERROR_OOR_REG) + (1 << IERROR_PC_WRAP) + 0;
            MIN_WAIT_NEEDED = 0;
            SIDL_NAME = `SIDL_NAMES@DADD_C;
            VALID_IN_SHADERS = ISHADER_ALL;
            IDEST_OPERAND_MAP = (1 << INDEX(Rd));
            IDEST_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            IDEST2_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            IDEST2_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_C_OPERAND_MAP = (1 << INDEX(Sc_bank)) + (1 << INDEX(Sc_addr));
            ISRC_C_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            ISRC_E_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_E_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_A_OPERAND_MAP = (1 << INDEX(Ra));
            ISRC_A_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
        
        * PREDICATES
            IDEST_SIZE = 64;
            IDEST2_SIZE = 0;
            ISRC_B_SIZE = 0;
            ISRC_C_SIZE = 64;
            ISRC_E_SIZE = 0;
            ISRC_A_SIZE = 64;
            VIRTUAL_QUEUE = $VQ_REDIRECTABLE;
            ILABEL_Ra_SIZE = 64;
        
        :return: a dictionary with the size of the destination operands.
        :rtype: dict
        """
        return self.__dst_size
    @property
    def dst_operands(self) -> dict: 
        """This property returns the [**full operand expressions**] of an instruction operand. For example 'Register:Rd'. \\
        **NOTE**: these are available at least up until SM 120.

        The [**destination operands**] are
        * {'IDEST': ['Register:Rd'], 'IDEST2': []} \\
        
        for an example instruction class [dadd__RRC_RC] on SM 86 with following
        * FORMAT PREDICATE @[!]Predicate(PT):Pg \\
                Opcode /Round1(RN):rnd \\
                    Register:Rd \\
                    ,[-][||]Register:Ra /REUSE(noreuse):reuse_src_a \\
                    ,[-][||]C:Sc[UImm(5/0*):Sc_bank]*[SImm(17)*:Sc_addr] \\
                $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ \\
                $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ \\
                $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ \\
                $( { ? USCHED_INFO(DRAIN):usched_info } )$ \\
                $( { ? BATCH_T(NOP):batch_t } )$ \\
                $( { ? PM_PRED(PMN):pm_pred } )$
        
        * PROPERTIES
            INSTRUCTION_TYPE = INST_TYPE_COUPLED_EMULATABLE;
            IERRORS = (1 << IERROR_ILLEGAL_INSTR_DECODING) + (1 << IERROR_INVALID_CONST_ADDR_LDC) + (1 << IERROR_MISALIGNED_ADDR) + (1 << IERROR_MISALIGNED_REG) + (1 << IERROR_OOR_REG) + (1 << IERROR_PC_WRAP) + 0;
            MIN_WAIT_NEEDED = 0;
            SIDL_NAME = `SIDL_NAMES@DADD_C;
            VALID_IN_SHADERS = ISHADER_ALL;
            IDEST_OPERAND_MAP = (1 << INDEX(Rd));
            IDEST_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            IDEST2_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            IDEST2_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_C_OPERAND_MAP = (1 << INDEX(Sc_bank)) + (1 << INDEX(Sc_addr));
            ISRC_C_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            ISRC_E_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_E_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_A_OPERAND_MAP = (1 << INDEX(Ra));
            ISRC_A_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
        
        * PREDICATES
            IDEST_SIZE = 64;
            IDEST2_SIZE = 0;
            ISRC_B_SIZE = 0;
            ISRC_C_SIZE = 64;
            ISRC_E_SIZE = 0;
            ISRC_A_SIZE = 64;
            VIRTUAL_QUEUE = $VQ_REDIRECTABLE;
            ILABEL_Ra_SIZE = 64;
        
        :return: a dictionary with the tt objects of the destination operands.
        :rtype: dict
        """
        return self.__dst_operands
    @property
    def src_types(self) -> dict:
        """This property returns indications related to the [**type**] of an instruction operand. It includes
        the alias as well as the tt object of an operand \\
        **NOTE**: these are available up until SM 90. SM 100 and SM 120 have a different system.

        The [**source types**] are
        * {'ISRC_B': {}, 'ISRC_C': {'Sc_bank': {'type': 'UImm(5/0*)', 'tt': '<py_sass.tt_terms.TT_Func..>'}, 'Sc_addr': {'type': 'SImm(17)*', 'tt': '<py_sass.tt_terms.TT_Func..>'}}, 'ISRC_E': {}, 'ISRC_A': {'Ra': {'type': 'DOUBLE', 'tt': '<py_sass.tt_terms.TT_Reg..>'}}} \\

        for an example instruction class [dadd__RRC_RC] on SM 86 with following
        * FORMAT PREDICATE @[!]Predicate(PT):Pg \\
                Opcode /Round1(RN):rnd \\
                    Register:Rd \\
                    ,[-][||]Register:Ra /REUSE(noreuse):reuse_src_a \\
                    ,[-][||]C:Sc[UImm(5/0*):Sc_bank]*[SImm(17)*:Sc_addr] \\
                $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ \\
                $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ \\
                $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ \\
                $( { ? USCHED_INFO(DRAIN):usched_info } )$ \\
                $( { ? BATCH_T(NOP):batch_t } )$ \\
                $( { ? PM_PRED(PMN):pm_pred } )$
        
        * PROPERTIES
            INSTRUCTION_TYPE = INST_TYPE_COUPLED_EMULATABLE;
            IERRORS = (1 << IERROR_ILLEGAL_INSTR_DECODING) + (1 << IERROR_INVALID_CONST_ADDR_LDC) + (1 << IERROR_MISALIGNED_ADDR) + (1 << IERROR_MISALIGNED_REG) + (1 << IERROR_OOR_REG) + (1 << IERROR_PC_WRAP) + 0;
            MIN_WAIT_NEEDED = 0;
            SIDL_NAME = `SIDL_NAMES@DADD_C;
            VALID_IN_SHADERS = ISHADER_ALL;
            IDEST_OPERAND_MAP = (1 << INDEX(Rd));
            IDEST_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            IDEST2_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            IDEST2_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_C_OPERAND_MAP = (1 << INDEX(Sc_bank)) + (1 << INDEX(Sc_addr));
            ISRC_C_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            ISRC_E_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_E_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_A_OPERAND_MAP = (1 << INDEX(Ra));
            ISRC_A_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
        
        * PREDICATES
            IDEST_SIZE = 64;
            IDEST2_SIZE = 0;
            ISRC_B_SIZE = 0;
            ISRC_C_SIZE = 64;
            ISRC_E_SIZE = 0;
            ISRC_A_SIZE = 64;
            VIRTUAL_QUEUE = $VQ_REDIRECTABLE;
            ILABEL_Ra_SIZE = 64;
        
        :return: a dictionary with the types of the source operands.
        :rtype: dict
        """
        return self.__src_types
    @property
    def src_size(self) -> dict:
        """This property returns the [**size**] of an instruction operand. For example 32. \\
        **NOTE**: these are available at least up until SM 120.

        The [**source sizes**] are
        * {'ISRC_B': '<py_sass.tt_terms.SASS_Expr..>', 'ISRC_C': '<py_sass.tt_terms.SASS_Expr..>', 'ISRC_E': '<py_sass.tt_terms.SASS_Expr..>', 'ISRC_A': '<py_sass.tt_terms.SASS_Expr..>'} \\
        
        for an example instruction class [dadd__RRC_RC] on SM 86 with following
        * FORMAT PREDICATE @[!]Predicate(PT):Pg \\
                Opcode /Round1(RN):rnd \\
                    Register:Rd \\
                    ,[-][||]Register:Ra /REUSE(noreuse):reuse_src_a \\
                    ,[-][||]C:Sc[UImm(5/0*):Sc_bank]*[SImm(17)*:Sc_addr] \\
                $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ \\
                $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ \\
                $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ \\
                $( { ? USCHED_INFO(DRAIN):usched_info } )$ \\
                $( { ? BATCH_T(NOP):batch_t } )$ \\
                $( { ? PM_PRED(PMN):pm_pred } )$
        
        * PROPERTIES
            INSTRUCTION_TYPE = INST_TYPE_COUPLED_EMULATABLE;
            IERRORS = (1 << IERROR_ILLEGAL_INSTR_DECODING) + (1 << IERROR_INVALID_CONST_ADDR_LDC) + (1 << IERROR_MISALIGNED_ADDR) + (1 << IERROR_MISALIGNED_REG) + (1 << IERROR_OOR_REG) + (1 << IERROR_PC_WRAP) + 0;
            MIN_WAIT_NEEDED = 0;
            SIDL_NAME = `SIDL_NAMES@DADD_C;
            VALID_IN_SHADERS = ISHADER_ALL;
            IDEST_OPERAND_MAP = (1 << INDEX(Rd));
            IDEST_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            IDEST2_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            IDEST2_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_C_OPERAND_MAP = (1 << INDEX(Sc_bank)) + (1 << INDEX(Sc_addr));
            ISRC_C_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            ISRC_E_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_E_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_A_OPERAND_MAP = (1 << INDEX(Ra));
            ISRC_A_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
        
        * PREDICATES
            IDEST_SIZE = 64;
            IDEST2_SIZE = 0;
            ISRC_B_SIZE = 0;
            ISRC_C_SIZE = 64;
            ISRC_E_SIZE = 0;
            ISRC_A_SIZE = 64;
            VIRTUAL_QUEUE = $VQ_REDIRECTABLE;
            ILABEL_Ra_SIZE = 64;
        
        :return: a dictionary with the size of the source operands.
        :rtype: dict
        """
        return self.__src_size
    @property
    def src_operands(self) -> dict:
        """This property returns the [**full operand expressions**] of an instruction operand. For example ['UImm(5/0*):Sc_bank', 'SImm(17)*:Sc_addr']. \\
        **NOTE**: these are available at least up until SM 120.

        The [**source operands**] are
        * {'ISRC_B': [], 'ISRC_C': ['UImm(5/0*):Sc_bank', 'SImm(17)*:Sc_addr'], 'ISRC_E': [], 'ISRC_A': ['Register:Ra']} \\
        
        for an example instruction class [dadd__RRC_RC] on SM 86 with following
        * FORMAT PREDICATE @[!]Predicate(PT):Pg \\
                Opcode /Round1(RN):rnd \\
                    Register:Rd \\
                    ,[-][||]Register:Ra /REUSE(noreuse):reuse_src_a \\
                    ,[-][||]C:Sc[UImm(5/0*):Sc_bank]*[SImm(17)*:Sc_addr] \\
                $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ \\
                $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ \\
                $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ \\
                $( { ? USCHED_INFO(DRAIN):usched_info } )$ \\
                $( { ? BATCH_T(NOP):batch_t } )$ \\
                $( { ? PM_PRED(PMN):pm_pred } )$
        
        * PROPERTIES
            INSTRUCTION_TYPE = INST_TYPE_COUPLED_EMULATABLE;
            IERRORS = (1 << IERROR_ILLEGAL_INSTR_DECODING) + (1 << IERROR_INVALID_CONST_ADDR_LDC) + (1 << IERROR_MISALIGNED_ADDR) + (1 << IERROR_MISALIGNED_REG) + (1 << IERROR_OOR_REG) + (1 << IERROR_PC_WRAP) + 0;
            MIN_WAIT_NEEDED = 0;
            SIDL_NAME = `SIDL_NAMES@DADD_C;
            VALID_IN_SHADERS = ISHADER_ALL;
            IDEST_OPERAND_MAP = (1 << INDEX(Rd));
            IDEST_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            IDEST2_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            IDEST2_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_C_OPERAND_MAP = (1 << INDEX(Sc_bank)) + (1 << INDEX(Sc_addr));
            ISRC_C_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            ISRC_E_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_E_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_A_OPERAND_MAP = (1 << INDEX(Ra));
            ISRC_A_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
        
        * PREDICATES
            IDEST_SIZE = 64;
            IDEST2_SIZE = 0;
            ISRC_B_SIZE = 0;
            ISRC_C_SIZE = 64;
            ISRC_E_SIZE = 0;
            ISRC_A_SIZE = 64;
            VIRTUAL_QUEUE = $VQ_REDIRECTABLE;
            ILABEL_Ra_SIZE = 64;
        
        :return: a dictionary with the tt objects of the source operands.
        :rtype: dict
        """
        return self.__src_operands
    @property
    def src_names(self) -> dict:
        """This property returns the [**names**] of an instruction operand. For example 'Ra'. \\
        **NOTE**: these are available at least up until SM 120.

        The [**source names*] are
        * {'Ra', 'Sc_addr', 'Sc_bank'} \\
        
        for an example instruction class [dadd__RRC_RC] on SM 86 with following
        * FORMAT PREDICATE @[!]Predicate(PT):Pg \\
                Opcode /Round1(RN):rnd \\
                    Register:Rd \\
                    ,[-][||]Register:Ra /REUSE(noreuse):reuse_src_a \\
                    ,[-][||]C:Sc[UImm(5/0*):Sc_bank]*[SImm(17)*:Sc_addr] \\
                $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ \\
                $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ \\
                $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ \\
                $( { ? USCHED_INFO(DRAIN):usched_info } )$ \\
                $( { ? BATCH_T(NOP):batch_t } )$ \\
                $( { ? PM_PRED(PMN):pm_pred } )$
        
        * PROPERTIES
            INSTRUCTION_TYPE = INST_TYPE_COUPLED_EMULATABLE;
            IERRORS = (1 << IERROR_ILLEGAL_INSTR_DECODING) + (1 << IERROR_INVALID_CONST_ADDR_LDC) + (1 << IERROR_MISALIGNED_ADDR) + (1 << IERROR_MISALIGNED_REG) + (1 << IERROR_OOR_REG) + (1 << IERROR_PC_WRAP) + 0;
            MIN_WAIT_NEEDED = 0;
            SIDL_NAME = `SIDL_NAMES@DADD_C;
            VALID_IN_SHADERS = ISHADER_ALL;
            IDEST_OPERAND_MAP = (1 << INDEX(Rd));
            IDEST_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            IDEST2_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            IDEST2_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_C_OPERAND_MAP = (1 << INDEX(Sc_bank)) + (1 << INDEX(Sc_addr));
            ISRC_C_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            ISRC_E_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_E_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_A_OPERAND_MAP = (1 << INDEX(Ra));
            ISRC_A_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
        
        * PREDICATES
            IDEST_SIZE = 64;
            IDEST2_SIZE = 0;
            ISRC_B_SIZE = 0;
            ISRC_C_SIZE = 64;
            ISRC_E_SIZE = 0;
            ISRC_A_SIZE = 64;
            VIRTUAL_QUEUE = $VQ_REDIRECTABLE;
            ILABEL_Ra_SIZE = 64;
        
        :return: a set with the types/alias of the source operands.
        :rtype: set
        """
        return self.__src_names
    @property
    def dst_names(self) -> dict:
        """This property returns the [**names**] of an instruction operand. For example 'Rd'. \\
        **NOTE**: these are available at least up until SM 120.

        The [**destination names**] are
        * {'Rd'} \\
        
        for an example instruction class [dadd__RRC_RC] on SM 86 with following
        * FORMAT PREDICATE @[!]Predicate(PT):Pg \\
                Opcode /Round1(RN):rnd \\
                    Register:Rd \\
                    ,[-][||]Register:Ra /REUSE(noreuse):reuse_src_a \\
                    ,[-][||]C:Sc[UImm(5/0*):Sc_bank]*[SImm(17)*:Sc_addr] \\
                $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$ \\
                $( { & RD:rd = UImm(3/0x7):src_rel_sb } )$ \\
                $( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$ \\
                $( { ? USCHED_INFO(DRAIN):usched_info } )$ \\
                $( { ? BATCH_T(NOP):batch_t } )$ \\
                $( { ? PM_PRED(PMN):pm_pred } )$
        
        * PROPERTIES
            INSTRUCTION_TYPE = INST_TYPE_COUPLED_EMULATABLE;
            IERRORS = (1 << IERROR_ILLEGAL_INSTR_DECODING) + (1 << IERROR_INVALID_CONST_ADDR_LDC) + (1 << IERROR_MISALIGNED_ADDR) + (1 << IERROR_MISALIGNED_REG) + (1 << IERROR_OOR_REG) + (1 << IERROR_PC_WRAP) + 0;
            MIN_WAIT_NEEDED = 0;
            SIDL_NAME = `SIDL_NAMES@DADD_C;
            VALID_IN_SHADERS = ISHADER_ALL;
            IDEST_OPERAND_MAP = (1 << INDEX(Rd));
            IDEST_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            IDEST2_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            IDEST2_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_B_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_C_OPERAND_MAP = (1 << INDEX(Sc_bank)) + (1 << INDEX(Sc_addr));
            ISRC_C_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
            ISRC_E_OPERAND_MAP = (1 << IOPERAND_MAP_NON_EXISTENT_OPERAND);
            ISRC_E_OPERAND_TYPE = (1 << IOPERAND_TYPE_NON_EXISTENT_OPERAND);
            ISRC_A_OPERAND_MAP = (1 << INDEX(Ra));
            ISRC_A_OPERAND_TYPE = (1 << IOPERAND_TYPE_DOUBLE);
        
        * PREDICATES
            IDEST_SIZE = 64;
            IDEST2_SIZE = 0;
            ISRC_B_SIZE = 0;
            ISRC_C_SIZE = 64;
            ISRC_E_SIZE = 0;
            ISRC_A_SIZE = 64;
            VIRTUAL_QUEUE = $VQ_REDIRECTABLE;
            ILABEL_Ra_SIZE = 64;
        
        :return: a set with the names/aliase of the destination operands.
        :rtype: set
        """
        return self.__dst_names

    def __str__(self):
        res = self.__format_tt.class_name
        res += "\n+    is_alt: {0}".format(self.__is_alternate)
        res += "\n+    opcode: {0}".format(self.__opcode)
        res += "\n+   has_imm: {0}".format(self.__has_imm)
        res += "\n+   has_lst: {0}".format(self.__has_list_arg)
        res += "\n+   has_att: {0}".format(self.__has_attr_arg)
        res += "\n+ has_reuse: {0}".format(self.__has_reuse)
        if self.__has_reuse: 
            res += "\n    - reuse_regs: {0}".format(self.alias_reuse)
        res += "\n+  has_pred: {0}".format(self.__has_pred)
        res += "\n+   has_dst: {0}".format(self.__has_dst)
        if self.__has_dst: 
            res += "\n    -     nr_dst: {0}".format(self.__nr_dst)
            res += "\n    -  dst_preds: {0}".format(self.__dst_preds)
        res += "\n+   has_src: {0}".format(self.__has_src)
        if self.__has_src: 
            res += "\n    -     nr_src: {0}".format(self.__nr_src)
            res += "\n    -  src_preds: {0}".format(self.__src_preds)
        return res

    def instr_properties(self):
        def add_ext(extensions:list, parent:TT_Param|TT_Opcode|TT_List):
            if not extensions: return
            if any(True for e in extensions if e.value.value == 'REUSE'): 
                if isinstance(parent, TT_Opcode): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                if isinstance(parent, TT_List): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                self.__has_reuse = True
                self.__alias_reuse.add(parent.alias.value)
                self.__tt_reuse[parent.alias.value] = parent.value
            e:TT_Ext
            for e in extensions:
                v = e.value.value
                a = e.alias.value
                if v in self.__alias_all: 
                    self.__alias_exts.add(v)
                    self.__tt_exts[v] = e
                elif a in self.__alias_all: 
                    self.__alias_exts.add(a)
                    self.__tt_exts[a] = e
        def add_reg(p:TT_Param, list_rf_alias:list|None):
            a = str(p.alias.value)
            v = p.value.value
            # There are registers like Bla:dummy => ignore them, they are not used in the encoding
            if not (a in self.__alias_all or v in self.__alias_all): return
            alias:str = a if a in self.__alias_all else v
            self.__alias_regs.add(alias)
            self.__tt_regs[alias] = p.value
            if list_rf_alias is not None:
                list_rf_alias[-1]['a'][alias] = 'reg'
        def add_func(p:TT_Param, list_rf_alias:list|None):
            a = str(p.alias.value)
            v = p.value.value
            # There are TT_Func with an @, like 'UImm(13)@:tid', ignore them, they are not used in the encoding
            if p.is_at_alias: return
            alias:str = a if a in self.__alias_all else v
            self.__alias_funcs.add(alias)
            self.__tt_funcs[alias] = p.value
            if list_rf_alias is not None:
                list_rf_alias[-1]['a'][alias] = 'func'

        self.__dst_preds = set(p for p,v in self.__predicates.items() if p in self.__details.dst_predicates and str(v) != '0')
        self.__nr_dst = len(self.__dst_preds)
        self.__has_dst = self.__nr_dst > 0
        self.__src_preds = set(p for p,v in self.__predicates.items() if p in self.__details.src_predicates and str(v) != '0')
        self.__nr_src = len(self.__src_preds)
        self.__has_src = self.__nr_src > 0

        # check if we have a predicate
        if self.__format_tt.pred is not None: 
            self.__has_pred = True
            self.__alias_pred.add(self.__format_tt.pred.alias.value)
            self.__alias_ops = self.__alias_ops.union(set([str(self.__format_tt.pred.op.alias)]))
            self.__tt_pred[self.__format_tt.pred.alias.value] = self.__format_tt.pred.value

        # self.__alias_added_defaults = set(self.__format_tt.default_enc_vals.keys())
        
        # The alias like 'uImm@sign' is a built in sign function for all TT_Func that is used up to SM 62.
        # Also, the entire framework just returns 1 not matter what for that built in function.
        # Thus, we ignore it here.
        self.__alias_all = set(itt.chain.from_iterable([a for a in e['alias'].get_alias_names_set() if not a.endswith('@sign')] for e in self.__encoding if not str(e['alias']).startswith('!')))

        if not self.__properties['MIN_WAIT_NEEDED'].startswith_int(): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        self.__min_wait_needed:int = self.__properties['MIN_WAIT_NEEDED'].get_first_value()

        add_ext(self.__format_tt.opcode.extensions, self.__format_tt.opcode)

        for i_ind, i in enumerate(self.__format_tt.regs):
            # The registers follow the following format:
            if isinstance(i, TT_List):
                # if we have a list, we have a memory access somewhere
                self.__has_list_arg = True

                # What kinds exactly?
                #  - all lists of stuff: [ZeroRegister(RZ):Ra + UImm(20/0)*:uImm]
                self.__list_rf_alias.append({'tt':i, 'a':dict(), 'type':'list_{0}'.format(i_ind)})
                for j in i.value:
                    # lists always contain TT_Param
                    if not isinstance(j, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    # TT_Param contain either TT_Reg or TT_Func
                    if isinstance(j.value, TT_Reg):
                        add_ext(j.extensions, j)
                        add_reg(j, self.__list_rf_alias)
                        self.__alias_ops = self.__alias_ops.union(set(str(e.alias) for e in j.ops))
                    elif isinstance(j.value, TT_Func):
                        self.__has_imm = True
                        add_ext(j.extensions, j)
                        add_func(j, self.__list_rf_alias)
                        self.__alias_ops = self.__alias_ops.union(set(str(e.alias) for e in j.ops if not str(e.alias).endswith('@sign')))
                add_ext(i.extensions, i)

            elif isinstance(i.value, TT_Reg):
                # What kinds exactly?
                #  - regular regusters: RegisterFAU:Rd
                #  - registers with attributs: C:srcConst[UImm(5/0*):constBank]*[ZeroRegister(RZ):Ra+SImm(17)*:immConstOffset]
                #  => in both instances RegisterFAU:Rd and C:srcConst are a [RegisterName]:[AliasName] pair
                # reg_vals[str(i.alias)] = set(int(x) for x in i.value.get_domain({}))
                # if (sp.SWITCH__USE_TT_EXT and isinstance(i, TT_AttrParam)) or (not sp.SWITCH__USE_TT_EXT):
                for attr_ind, attr in enumerate(i.attr):
                    # if we have an attribute, we have a memory access somewhere
                    self.__has_attr_arg = True
                    self.__list_rf_alias.append({'tt':attr, 'a':dict(), 'type':'attr_{0}.{1}'.format(i_ind, attr_ind)})

                    # attributs are always lists of things and the lists always contain TT_Param
                    if not isinstance(attr, TT_List): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    for a in attr.value:
                        if not isinstance(a, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                        # TT_Param contain either TT_Reg or TT_Func
                        if isinstance(a.value, TT_Reg):
                            add_ext(a.extensions, a)
                            add_reg(a, self.__list_rf_alias)
                            self.__alias_ops = self.__alias_ops.union(set(str(e.alias) for e in a.ops))
                        elif isinstance(a.value, TT_Func): 
                            self.__has_imm = True
                            add_ext(a.extensions, a)
                            add_func(a, self.__list_rf_alias)
                            self.__alias_ops = self.__alias_ops.union(set(str(e.alias) for e in a.ops if not str(e.alias).endswith('@sign')))

                add_ext(i.extensions, i)
                # if (sp.SWITCH__USE_TT_EXT and isinstance(i, TT_Param)): add_reg(i, None)
                # elif (not sp.SWITCH__USE_TT_EXT) and 
                if (not i.attr): add_reg(i, None)
                self.__alias_ops = self.__alias_ops.union(set(str(e.alias) for e in i.ops))
            elif isinstance(i.value, TT_Func): 
                self.__has_imm = True
                add_ext(i.extensions, i)
                add_func(i, None)
                self.__alias_ops = self.__alias_ops.union(set(str(e.alias) for e in i.ops if not str(e.alias).endswith('@sign')))
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    
    def resolve_size_mappings(self):
        # This method resolves the size mappings for all SM types
        #  - all variables are inside of class_.details.OPERATION.PREDICATES and class_.details.OPERATION.PROPERTIES
        # On the older models, the pattern is like this:
        #  - the PREDICATES and PROPERTIES contain terms in the form of 
        #    ISRC_[A-Z]+_SIZE, IDEST[0-9]*_OPERAND_MAP and IDEST[0-9]*_OPERAND_TYPE
        #  - the ..MAP terms contain the name of the operand alias that maps into the class FORMAT
        #  - the ..TYPE term contains a designation for the TYPE of the operand (this one doesn't seem to have any influence)
        #   PROPERTIES
        #       IDEST_OPERAND_TYPE = (1<<IOPERAND_TYPE_GENERIC);
        #       ISRC_A_OPERAND_TYPE = (1<<IOPERAND_TYPE_NON_EXISTENT_OPERAND);
        #       ISRC_B_OPERAND_TYPE = (1<<IOPERAND_TYPE_NON_EXISTENT_OPERAND);
        #       ISRC_C_OPERAND_TYPE = (1<<IOPERAND_TYPE_NON_EXISTENT_OPERAND);
        #       IDEST_OPERAND_MAP = (1<<INDEX(Rd));
        #       ISRC_A_OPERAND_MAP = (1<<IOPERAND_MAP_NON_EXISTENT_OPERAND);
        #       ISRC_B_OPERAND_MAP = (1<<IOPERAND_MAP_NON_EXISTENT_OPERAND);
        #       ISRC_C_OPERAND_MAP = (1<<IOPERAND_MAP_NON_EXISTENT_OPERAND);
        #   PREDICATES
        #       IDEST_SIZE = 32;
        #       ISRC_A_SIZE = 0;
        #       ISRC_B_SIZE = 0;
        #       ISRC_C_SIZE = 0;
        #
        # On the newer models (and there is some overlap for some that have both -.-)
        #  - there are some that follow the old scheme
        #  - there is a new scheme with RF indexes, for example with "RF:indexURb[UniformRegister:URb] ','UImm(4/0xf)*:PixMaskU04"
        #    where there is an entry like "ISRC_B_INDEX_RF_SIZE = 32;" in the PREDICATES
        #  - there are operands like "NonZeroRegister:Ra" that have an entry like "ILABEL_Ra_SIZE = 32;" and at the same time "ISRC_A_SIZE = 32;" in 
        #    the PREDICATES
        #  - the reason for this duality are probably the latency mappings that still use ISRC_A_SIZE and IDEST_SIZE. Assume that they may be scrapped
        #    in the future too
        #
        # How to map:
        #  1. if we have ISRC_B_OPERAND_MAP and ISRC_B_OPERAND_TYPE, they take precedence
        #      - assumption 1: if we have those, then they are correct because they are the proven aproach
        #      - assumption 2: if we have those, sometimes the labels are different from the maps
        #         => assume that they just wanted to test the new label notation which is why they both appear and
        #            are mostly identical but not always
        #  2. if there are both ISRC_A_SIZE and ILABEL_Ra_SIZE, or ISRC_B_SIZE and ILABEL_Rb_SIZE etc present, they must match
        #      => mapping is the letter [A] to R[a], [B] to R[b] etc
        #  3. if not both are present, throw an exception
        #  4. if an ^ISRC_[A-Z]+_INDEX_RF_SIZE$ term is present, there must be an RF:.. operand present in the FORMAT
        #  5. if an ^ILABEL_[a-zA-Z_]+_SIZE$ term is present, there must be an operand with alias that matches the middle part
        #      - there are labels like ILABEL_Rb_URc_SIZE. In this case, the middle part is Rb_URc and not Rb and URc!!
        #  6. if there is an ^IDEST_SIZE$ and no MAP, it matches Rd
        #  7. if there is an ^IDEST2_SIZE$ and no MAP, it matches Rd2
        #  8. if there is an ^ISRC_[A-Z]+_OPERAND_TYPE$ use that type designation, otherwise make something up:
        #      - for attribute operands like Reg:TAlias[..bla..][..bla..], TAlias is going to be the type
        #      - this matches the newer architectures where for example, we have an ISRC_C_INDEX_RF_SIZE that matches
        #        RF:indexURc[UniformRegister:URc] where we then say "indexURc" is the type
        #  9. if we have both ^ISRC_[A-Z]+_SIZE$ and matching ^ISRC_[A-Z]+_INDEX_RF_SIZE$, an operand like RF:indexURc[UniformRegister:URc] must exist
        #     where ^ISRC_[A-Z]+_SIZE$ match the stuff inside of [...] and ^ISRC_[A-Z]+_INDEX_RF_SIZE$ matches the stuff in front of it
        # 10. There are instruction classes with no operands. In this case some ISRC_[X]_SIZE are set to funny values like 4 or 12 to match
        #     the latencies later

        predicates_tt:dict = self.__predicates
        properties_tt:dict = self.__properties
        op_predicates:list = self.__op_predicates
        op_properties:list = self.__op_properties
        format_tt:TT_Instruction = self.__format_tt

        dst_re_map = re.compile('^IDEST[0-9]*_OPERAND_MAP$')
        dst_re_type = re.compile('^IDEST[0-9]*_OPERAND_TYPE$')
        dst_re_size = re.compile('^IDEST[0-9]*_SIZE$')
        dst_re_rf_size = re.compile('IDEST[0-9]*_INDEX_RF_SIZE')

        src_re_map = re.compile('^ISRC_[A-Z0-9]+_OPERAND_MAP$')
        src_re_type = re.compile('^ISRC_[A-Z0-9]+_OPERAND_TYPE$')
        src_re_size = re.compile('^ISRC_[A-Z0-9]+_SIZE$')
        src_re_rf_size = re.compile('^ISRC_[A-Z0-9]+_INDEX_RF_SIZE$')
        src_re_label_size = re.compile('^ILABEL_[a-zA-Z_]+_SIZE$')

        # map all OPERAND_MAP types
        dst_map = [(p,e) for p,e in properties_tt.items() if dst_re_map.match(p)]
        src_map = [(p,e) for p,e in properties_tt.items() if src_re_map.match(p)]

        # map all OPERAND_TYPE types
        dst_type = [(p,e) for p,e in properties_tt.items() if dst_re_type.match(p)]
        src_type = [(p,e) for p,e in properties_tt.items() if src_re_type.match(p)]
        
        # map all IDEST[0-9]*_SIZE types
        dst_size = [(p,e) for p,e in predicates_tt.items() if dst_re_size.match(p)]
        src_size = [(p,e) for p,e in predicates_tt.items() if src_re_size.match(p)]

        # map all rf size types
        dst_rf_size = [(p,e) for p,e in predicates_tt.items() if dst_re_rf_size.match(p)]
        src_rf_size = [(p,e) for p,e in predicates_tt.items() if src_re_rf_size.match(p)]

        # map all labels
        src_label_size = [(p,e) for p,e in predicates_tt.items() if src_re_label_size.match(p)]

        # group all mappigs together using assumptions 1 to 9
        # all operands are conveniently TT_Param => stuff the mapping into it's respective TT_Param component like TT_Reg, or TT_Func
        # because that is what we have access too in the decoder
        #  - for example, write: ISRC_A_SIZE(Ra, UImm(..)) = 32

        # if we have OPERAND_TYPEs, remove the ones from src_size and src_type where the type name is IOPERAND_TYPE_NON_EXISTENT_OPERAND
        ll_OPERAND_TYPE = len('_OPERAND_TYPE')
        ll_OPERAND_MAP = len('_OPERAND_MAP')
        ll_SIZE = len('_SIZE')
        dst_type_f = {p[:-ll_OPERAND_TYPE]:t for p,t in [(p,[str(ee) for ee in e.expr if isinstance(ee, Op_Constant) and not ee.value() == self.__details.CONSTANTS.IOPERAND_TYPE_NON_EXISTENT_OPERAND]) for p,e in dst_type] if t} # type: ignore
        src_type_f = {p[:-ll_OPERAND_TYPE]:t for p,t in [(p,[str(ee) for ee in e.expr if isinstance(ee, Op_Constant) and not ee.value() == self.__details.CONSTANTS.IOPERAND_TYPE_NON_EXISTENT_OPERAND]) for p,e in src_type] if t} # type: ignore
        dst_map_f = {p[:-ll_OPERAND_MAP]:e.get_alias_names_set() for p,e in dst_map if not any([isinstance(ee, Op_Constant) and ee.value() == self.__details.CONSTANTS.IOPERAND_MAP_NON_EXISTENT_OPERAND for ee in e.expr])} # type: ignore
        src_map_f = {p[:-ll_OPERAND_MAP]:e.get_alias_names_set() for p,e in src_map if not any([isinstance(ee, Op_Constant) and ee.value() == self.__details.CONSTANTS.IOPERAND_MAP_NON_EXISTENT_OPERAND for ee in e.expr])} # type: ignore
        dst_size_f = {p[:-ll_SIZE]:e for p,e in dst_size if str(e) != '0'}
        src_size_f = {p[:-ll_SIZE]:e for p,e in src_size if str(e) != '0'}

        if not len(dst_type_f) == len(dst_map_f): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not len(src_type_f) == len(src_map_f): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # These assumptions DON'T hold. The reason is that there are some instructions that don't have operators and they need to
        # be mapped to latencies as well
        #  - if not len(dst_type_f) == len(dst_size_f): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        #  - if not len(src_type_f) == len(src_size_f): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not all(a[0]==b[0] for a,b in zip(dst_type_f.items(), dst_map_f.items())): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not all(a[0]==b[0] for a,b in zip(src_type_f.items(), src_map_f.items())): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # These assumptions DON'T hold. The reason is that there are some instructions that don't have operators and they need to
        # be mapped to latencies as well
        #  - if not all(a[0]==b[0] for a,b in zip(dst_type_f, dst_size_f)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        #  - if not all(a[0]==b[0] for a,b in zip(src_type_f, src_size_f)): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # if we have ILABEL entries, extract their aliases

        ll_ILABEL_ = len('ILABEL_')
        src_label_size_f = {l:(set([l[ll_ILABEL_:-ll_SIZE]]), e) for l,e in src_label_size}
        # if not len(src_label_size_f) == len(src_size_f): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if src_map_f != dict() and src_label_size_f != dict():
            # if we have old-fashioned maps, use the maps and ignore the aliases
            # To verify this assumption, make sure that every present label contains at most a subset of the map notation
            #  => this seems to hold up
            if not all(len(l[1][0]) <= len(s[1]) for l,s in itt.product(src_label_size_f.items(), src_map_f.items()) if len(l[1][0].intersection(s[1]))>0): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif src_map_f == dict() and src_label_size_f == dict():
            # these are instructions where all sizes are 0
            # the assumption is that they all map to the same latency
            pass
        elif src_map_f == dict() and src_label_size_f:
            # in this case we expect an exact overlap between the old ISRC_[X]_SIZE notation and the new
            # ILABEL_[Rx]+_SIZE notation
            if not all(len(l[1][0]) == len(s[1]) for l,s in itt.product(src_label_size_f.items(), src_map_f.items()) if len(l[1][0].intersection(s[1]))>0): 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # Since we know this is always the case, emulate the same data structure as with the other case
            # Matches are one size with the label that has the same equation
            # There are some funny variations:
            #  - Sometimes we have only one size but two labels, for example with Ra and Ra_URc. This is actually a valid case
            #    and we use both sizes
            #   ISRC_A_SIZE = 32 + ((e==`E@E))*32;
            #   ILABEL_Ra_SIZE = 32;
            #   ILABEL_Ra_URc_SIZE = 32 + ((e==`E@E))*32;
            pass
        elif src_map_f != dict() and src_label_size_f == dict():
            # this is the regular old case
            # We get stuff like this:
            # print(' # src_map_f=',src_map_f,'\n', '# src_size_f=',src_size_f,'\n', '# src_type_f=',src_type_f,'\n', '# dst_map_f=',dst_map_f,'\n', '# dst_size_f=',dst_size_f,'\n', '# dst_type_f=',dst_type_f)
            #    src_map_f= {'ISRC_B': {'Sb_bank', 'Sb_addr'}} 
            #    src_size_f= {'ISRC_B': <_sass_expression.SASS_Expr object at 0x756b61d13500>} 
            #    src_type_f= {'ISRC_B': ['IOPERAND_TYPE_INTEGER']} 
            #    dst_map_f= {'IDEST': {'Rd'}} 
            #    dst_size_f= {'IDEST': <_sass_expression.SASS_Expr object at 0x756b61d133e0>} 
            #    dst_type_f= {'IDEST': ['IOPERAND_TYPE_INTEGER']}
            pass
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # if class_.class_name == 'ald_UR__LOGICAL_URa_default':
        #     pass

        dst_p = [(p,e) for p,e in properties_tt.items() if dst_re_map.match(p)]
        dst_t = [(p,e) for p,e in properties_tt.items() if dst_re_type.match(p)]
        dst_operand_type = [(t[0][:-len('_OPERAND_TYPE')], [str(e) for e in t[1].expr if isinstance(e, Op_Constant)]) for t in dst_t]
        if any(len(b)!=1 for a,b in dst_operand_type): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        dst_re = re.compile('^IDEST[0-9]*_SIZE$')
        dst_operand_type = dict([(a,b[0]) for a,b in dst_operand_type])
        dst_operand_size = {p[:-len('_SIZE')]:e for p,e in predicates_tt.items() if dst_re.match(p)}
        dst_operand_term = {t[0][:-len('_OPERAND_MAP')]:{a:v.value() for a,v in t[1].get_alias().items()} for t in dst_p}

        src_re_map = re.compile('^ISRC_[A-Z]_OPERAND_MAP$')
        src_re_type = re.compile('^ISRC_[A-Z]_OPERAND_TYPE$')
        src_p = [(p,e) for p,e in properties_tt.items() if src_re_map.match(p)]
        src_t = [(p,e) for p,e in properties_tt.items() if src_re_type.match(p)]
        src_operand_type = [(t[0][:-len('_OPERAND_TYPE')], [str(e) for e in t[1].expr if isinstance(e, Op_Constant)]) for t in src_t]
        if any(len(b)!=1 for a,b in src_operand_type): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        src_re = re.compile('^ISRC_[A-Z]_SIZE$')
        src_operand_type = dict([(a,b[0]) for a,b in src_operand_type])
        src_operand_size = {p[:-len('_SIZE')]:e for p,e in predicates_tt.items() if src_re.match(p)}
        src_operand_term = {t[0][:-len('_OPERAND_MAP')]:{a:v.value() for a,v in t[1].get_alias().items()} for t in src_p}

        self.__dst_types = self.map_types(dst_operand_term, dst_operand_type) # type: ignore
        self.__dst_size = dst_operand_size # type: ignore
        self.__dst_operands = {k : ["{0}:{1}".format(str(tt),kk) for kk,tt in t.items()] for k,t in dst_operand_term.items()} # type: ignore
        self.__src_types = self.map_types(src_operand_term, src_operand_type) # type: ignore
        self.__src_size = src_operand_size # type: ignore
        self.__src_operands = {k : ["{0}:{1}".format(str(tt),kk) for kk,tt in t.items()] for k,t in src_operand_term.items()} # type: ignore

        self.__src_names = set(itt.chain.from_iterable(s[1].get_alias_names() for s in src_p)) # type: ignore
        self.__dst_names = set(itt.chain.from_iterable(s[1].get_alias_names() for s in dst_p)) # type: ignore

        bla_sizes = [(i, j) for i,j in src_operand_size.items()] + [(i, j) for i,j in dst_operand_size.items()] 
        bla_maps = {b[-1]:(int(s) if isinstance(s, str) else s) for b,s in bla_sizes}
        src_end_mapping = {'a':'A', 'b':'B', 'c':'C', 'e':'E', 'f':'F'}
        src_end_mapping = {k:v for k,v in src_end_mapping.items() if v in bla_maps}
        dst_end_mapping = {'d':'T', '2':'2'}
        dst_end_mapping = {k:v for k,v in dst_end_mapping.items() if v in bla_maps}
        alias_and_size = {}
        label_sizes = {l[len('ILABEL_'):-len('_SIZE')]:e for l,e in src_label_size}
        for alias,tt in self.__tt_regs.items():
            reg_type = tt.value
            if alias[-1] in src_end_mapping:
                # source register
                alias_and_size[alias] = bla_maps[src_end_mapping[alias[-1]]]
            elif alias[-1] in dst_end_mapping:
                # destination register
                alias_and_size[alias] = bla_maps[dst_end_mapping[alias[-1]]]
            elif 'Predicate' in reg_type:
                # predicate operand
                alias_and_size[alias] = 1
            else:
                # estimate = len(bin(max(list(itt.chain.from_iterable(getattr(self._SASS_Class_Props__details.REGISTERS, tt.value).values()))))[2:])
                # These are unknown sizes
                alias_and_size[alias] = 0

            # This one is an 'if' on purpose. It overwrites some but adds others!!!
            if alias in label_sizes:
                # Visual inspection yields, that these are always the same
                # They are two different ways of expressing the same thing, it seems...
                # NOTE: there is a check around line 1389 of this skript that checks exactly this overlap
                ee = label_sizes[alias]
                alias_and_size[alias] = int(ee) if isinstance(ee, str) else ee
            
        self.__alias_and_size = alias_and_size


    def map_types(self, op_term:dict, op_type:dict):
        res = dict()
        for i,t in zip(op_term.items(), op_type.items()):
            if not i[0] in res: res[i[0]] = dict()
            res[i[0]] |= {x[0] : {'type' : t[1][len('IOPERAND_TYPE_'):] if isinstance(x[1], TT_Reg) else str(x[1]), 'tt': x[1]} for x in i[1].items()}
        return res