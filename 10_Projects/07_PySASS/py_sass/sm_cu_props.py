import functools as ft
import itertools as itt
from . import _config as sp
from ._instr_enc_dec_lookup import Instr_EncDec_Lookup
from .sm_cu import SM_Cu
from .sm_latency import SM_Latency
from .sass_class import SASS_Class
from .sass_class import SASS_Class_Props

class SM_Cu_Props:
    def __init__(self, sm_nr:int, latencies:SM_Latency, sm:SM_Cu, lu:dict, to_file:bool=False):
        cid = set(i for i,d in sm.all_instr_desc.items() if d.category == 'Control Instructions')
        bru = set(i for i in latencies.op_sets['BRU_OPS'] if not i.endswith('_pipe'))
        # From SM70 onwards RPCMOV (program counter register move) is a control instruction but not in BRU_OPS
        # From SM90 onwards CGAERRBAR (CGA Error Barrier) is a control instruction but not in BRU_OPS
        if not cid.difference(bru) in [set(), {'RPCMOV'}, {'RPCMOV','CGAERRBAR'}]: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        control_classes:set = set(k for k,v in sm.classes_dict.items() if v.OPCODES if v.OPCODES['opcode']['i'] in bru)
        self.__control_instr_opcodes:set = bru
        self.__instr_cat__control_all:set = control_classes
        
        # Get all instructions designated as load/store
        lsld_instr_codes = {i for i,d in sm.all_instr_desc.items() if d.category.find('Load/Store Instructions') >= 0}
        lsld_instr_classes = {i for i,c in sm.classes_dict.items() if c.props.opcode in lsld_instr_codes}
        self.__instr_cat__load_store_all:set = lsld_instr_classes

        # SM 50 to 120 have
        #   INST_TYPE_MATH = 0
        #   INST_TYPE_COUPLED_MATH = 0
        #   INST_TYPE_MIO_RD_SCBD = 1
        #   INST_TYPE_DECOUPLED_RD_SCBD = 1
        #   INST_TYPE_MIO_RD_WR_SCBD = 2
        #   INST_TYPE_DECOUPLED_RD_WR_SCBD = 2
        #   INST_TYPE_COUPLED_EMULATABLE = 3
        #   INST_TYPE_DECOUPLED_BRU_DEPBAR_RD_SCBD = 4
        # SM 70 to 120 additionally have
        #   INST_TYPE_DECOUPLED_WR_SCBD = 5
        #   INST_TYPE_DECOUPLED_RD_NOREQ_SCBD = 6
        #   INST_TYPE_DECOUPLED_WR_NOREQ_SCBD = 7
        #   INST_TYPE_DECOUPLED_BRU_DEPBAR_RD_NOREQ_SCBD= 8
        # SM 100 to 120 additionall have
        #   INST_TYPE_COUPLED_EMULATABLE_NORD_SCBD = 9
        #   INST_TYPE_COUPLED_EMULATABLE_NOWR_SCBD = 10
        #   INST_TYPE_COUPLED_EMULATABLE_NORD_NOWR_SCBD = 11

        # Test conformity
        no_inst_type_inst = [(k,v) for k,v in sm.classes_dict.items() if not 'INSTRUCTION_TYPE' in v.PROPERTIES]
        if no_inst_type_inst: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        inst_types = {k:v for k,v in sm.details.CONSTANTS_DICT.items() if k.startswith('INST_TYPE')}
        # Split instruction classes based on pipes
        inst_split = {t:
                      [{
                          'c':k, 
                          'o':i.OPCODES['opcode']['i'], 
                          'p':i.OPCODES['pipes'][0]['i'],
                          's':[str(x) if x.is_fixed_val() else 'NC' for p,x in i.PREDICATES.items() if p.endswith('SIZE')],
                          'n':[str(x) for p,x in i.PROPERTIES.items() if p=='SIDL_NAME'],
                        } for k,i in sm.classes_dict.items() if str(i.PROPERTIES['INSTRUCTION_TYPE']) == t]
                      for t in inst_types}
        inst_split = {k:
                      [j | {'l':set(s for s,x in latencies.op_sets.items() 
                                    if ((j['o'] in x or j['p'] in x) and s!='ALL_OPS'))}
                                    for j in i] 
                      for k,i in inst_split.items()}
        
        # check..
        if not (sum(len(v) for v in inst_split.values()) == len(sm.classes_dict)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if to_file: SM_Cu_Props.inst_split_to_file(sm_nr, inst_split)

        self.__instr_split = inst_split
        self.__instr_types = inst_types

        # do an instruction class classification based on available cash bits and control properties
        # control instructions
        ci_rd = set()
        ci_wr = set()
        ci_rdwr = set()
        ci_wrearly = set()
        ci_no_barrier = set()
        # load/store instructions
        lsi_rd = set()
        lsi_wr = set()
        lsi_rdwr = set()
        lsi_wrearly = set()
        lsi_no_barrier = set()
        # all other instructions
        i_rd = set()
        i_wr = set()
        i_rdwr = set()
        i_wrearly = set()
        i_no_barrier = set()

        def classify(p:SASS_Class_Props, rd:set, wr:set, rdwr:set, wrearly:set, no_barrier:set):
            if p.cash_has__wr_early:
                # all instructions with WR_EARLY have a WR barrier, non have an RD barrer
                # => make sure this is really always the case
                if p.cash_has__rd: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                if not p.cash_has__wr: raise Exception(sp.CONST__ERROR_UNEXPECTED)

                # Don't add to any category => do that later. In here we just make sure that the assumptions
                # of these kinds of instructions hold
                if sm_nr < 90: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            if p.cash_has__rd and not p.cash_has__wr:
                # control and just RD
                rd.add(ic.class_name)
            elif p.cash_has__wr and not p.cash_has__rd:
                # control and just WR
                wr.add(ic.class_name)
                if p.cash_has__wr_early:
                    # maybe WR_EARLY...?
                    wrearly.add(ic.class_name)
            elif p.cash_has__wr and p.cash_has__rd:
                # control and WR and RD
                rdwr.add(ic.class_name)
            elif not (p.cash_has__wr or p.cash_has__rd):
                # no barrier
                no_barrier.add(ic.class_name)
            else: 
                # otherwise we are screeeewed ^^
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        # This is a local function to check if the union of all sets containing barrier instructions is the same
        # as the cd set
        def check_barrier_sets(cd:set, rd:set, wr:set, rdwr:set, wrearly:set, no_barrier:set) -> bool:
            got_all:bool = cd == rd.union(wr).union(rdwr).union(no_barrier)
            bla = wrearly.difference(wr) == set()
            return got_all and bla

        # Categorize all instructions based on if they have barriers and what kind of barriers
        ic:SASS_Class
        for ic in sm.classes_dict.values():
            p:SASS_Class_Props = ic.props
            # control instructions
            if ic.class_name in self.__instr_cat__control_all:
                classify(p, ci_rd, ci_wr, ci_rdwr, ci_wrearly, ci_no_barrier)
            # memory access instructions
            elif ic.class_name in self.__instr_cat__load_store_all:
                classify(p, lsi_rd, lsi_wr, lsi_rdwr, lsi_wrearly, lsi_no_barrier)
            # all other instructions
            else:
                classify(p, i_rd, i_wr, i_rdwr, i_wrearly, i_no_barrier)

        # Make sure we got all control instructions categorized
        ci_check:bool = check_barrier_sets(self.__instr_cat__control_all, ci_rd, ci_wr, ci_rdwr, ci_wrearly, ci_no_barrier)
        if not ci_check: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # Make sure we got all load/store instructions
        lsi_check:bool = check_barrier_sets(self.__instr_cat__load_store_all, lsi_rd, lsi_wr, lsi_rdwr, lsi_wrearly, lsi_no_barrier)
        if not lsi_check: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # Make sure we got all regular instructions categorized
        i_check:bool = check_barrier_sets(set(sm.classes_dict.keys()).difference(self.__instr_cat__control_all).difference(self.__instr_cat__load_store_all), i_rd, i_wr, i_rdwr, i_wrearly, i_no_barrier)
        if not i_check: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # If we have load/store instructions with no barrier => we don't like that: load/store instructions need at least one barrier, otherwise the whole thing
        #  => this one doesn't hold!!!
        # For example on SM 86, lsi_no_barrier = {'cctlt__IVALL', 'cctl__IVALL_WBALL_D_U_noSrc', 'cctl__IVALL_WBALL_I_noSrc', 'cctl__IVALL_WBALL_C_noSrc', 'errbar_', 'cctll__IVALL_WBALL_D_U_noSrc'}
        # if len(lsi_no_barrier): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # All constrol instructions
        self.__instr_cat__control_rd = ci_rd
        self.__instr_cat__control_wr = ci_wr
        self.__instr_cat__control_rdwr = ci_rdwr
        self.__instr_cat__control_wrearly = ci_wrearly
        # All load/store instructions
        self.__instr_cat__load_store_rd = lsi_rd
        self.__instr_cat__load_store_wr = lsi_wr
        self.__instr_cat__load_store_rdwr = lsi_rdwr
        self.__instr_cat__load_store_wrearly = lsi_wrearly
        self.__instr_cat__load_store_no_barrier = lsi_no_barrier
        self.__instr_cat__load_store_with_any_barrier = self.__instr_cat__load_store_rd.union(self.__instr_cat__load_store_wr).union(self.__instr_cat__load_store_rdwr).union(self.__instr_cat__load_store_wrearly)
        # All other instructions
        self.__instr_cat__rd = i_rd
        self.__instr_cat__wr = i_wr
        self.__instr_cat__rdwr = i_rdwr
        self.__instr_cat__wrearly = i_wrearly
        self.__instr_cat__with_any_barrier = self.__instr_cat__rd.union(self.__instr_cat__rdwr).union(self.__instr_cat__wr).union(self.__instr_cat__wrearly)

        # split no-barrier instructions into parameterized and non-parameterized fixed latency
        ci_ff_vared = set()
        ci_ff_fixed = set()
        i_ff_vared = set()
        i_ff_fixed = set()
        
        for x in ci_no_barrier:
            if sm.classes_dict[x].props.has_variable_predicates: ci_ff_vared.add(x)
            else: ci_ff_fixed.add(x)
        for x in i_no_barrier:
            if sm.classes_dict[x].props.has_variable_predicates: i_ff_vared.add(x)
            else: i_ff_fixed.add(x)

        # these vared/fixed relate to the size of the operands (NOTE: not relevant anymore => disproved, so-to-speak...)
        self.__instr_cat__control_ff_vared = ci_ff_vared
        self.__instr_cat__control_ff_fixed = ci_ff_fixed
        self.__instr_cat__ff_vared = i_ff_vared
        self.__instr_cat__ff_fixed = i_ff_fixed

        # Verify?: no control instruction has a barrier
        # if not (ci_no_barrier == self.__instr_cat__control_all): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # => does NOT hold for SM 70++!!!

        # All control instructions with fixed latency (no req barrier)
        self.__measure__control__fixed_lat = ci_no_barrier
        # All control instructions with variable latency (exist on SM 70++)
        self.__measure__control__vared_lat = self.instr_cat__control_all.difference(ci_no_barrier)

        # This finds all instruction classes that have something to do with real synchronization barriers, for example
        #  - BAR (barrier synchronization), DEPBAR (dependency barrier), ....
        # Mostly, these instructions are part of either control instructions or miscellaneous instructions
        measure__sync__all = {i for i,ic in sm.classes_dict.items() if (not (i in self.instr_cat__control_all)) and ((ic.props.opcode in sm.all_instr_desc and sm.all_instr_desc[ic.props.opcode].desc.find('Barrier') >= 0) or ic.props.opcode.lower().find('bar') >= 0)}

        # All synchronization instructions with fixed latency
        self.__measure__sync__fixed_lat = measure__sync__all.intersection(i_no_barrier.union(lsi_no_barrier))
        # All synchronization instructions with variable latency
        self.__measure__sync__vared_lat = measure__sync__all.intersection(self.__instr_cat__with_any_barrier.union(self.__instr_cat__load_store_with_any_barrier))

        # All load/store instructions with fixed latency
        self.__measure__load_store__fixed_lat = self.__instr_cat__load_store_no_barrier.difference(self.__measure__sync__fixed_lat)
        # All load/store instructions with variable latency
        self.__measure__load_store__vared_lat = self.__instr_cat__load_store_with_any_barrier.difference(measure__sync__all)

        # All regular data instructions with fixed latency
        self.__measure__data__fixed_lat = i_no_barrier.difference(self.__measure__sync__fixed_lat)
        # All regular data instructions with variable latency (i.e. with a req barrier)
        self.__measure__data__vared_lat = self.__instr_cat__with_any_barrier.difference(self.__measure__sync__vared_lat)

        # Combine all fixed latency instructions inside of one giant category
        self.__measure__all__fixed_lat = self.__measure__control__fixed_lat.union(self.__measure__sync__fixed_lat).union(self.__measure__load_store__fixed_lat).union(self.__measure__data__fixed_lat)

        # Checks:
        # Verify that the union of all "__measure__" sets indeed yields all instruction classes.
        # Use self.__measure__all__fixed_lat to make sure that we don't 'forget' any instructions in this category
        measure__all = self.__measure__sync__fixed_lat.union(self.__measure__sync__vared_lat)\
                                                      .union(self.__measure__control__vared_lat)\
                                                      .union(self.__measure__data__vared_lat)\
                                                      .union(self.__measure__load_store__vared_lat)\
                                                      .union(self.__measure__all__fixed_lat)
        if not (measure__all == set(sm.classes_dict.keys())): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # Make sure that all sets are distinct
        x = self.__measure__sync__fixed_lat, self.__measure__sync__vared_lat, self.__measure__control__fixed_lat, self.__measure__control__vared_lat, self.__measure__data__fixed_lat, self.__measure__data__vared_lat, self.__measure__load_store__fixed_lat, self.__measure__load_store__vared_lat
        if any(i[0].intersection(i[1]) for i in itt.combinations(x, 2)): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # Verify that for sync and control groups with variable latency, we have a non-zero min_wait_needed
        #  => holds
        if not all(sm.classes_dict[i].props.min_wait_needed != 0 for i in self.__measure__control__vared_lat): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not all(sm.classes_dict[i].props.min_wait_needed != 0 for i in self.__measure__sync__vared_lat): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # This one also holds. NOTE, though, that the same is NOT true for self.__measure__load_store__fixed_lat
        if not all(sm.classes_dict[i].props.min_wait_needed != 0 for i in self.__measure__load_store__vared_lat): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # Now, we may have instruction classes that are ALTERNATES of others. We don't need to measure the ALTERNATES because
        # the decoder will default to the main class anyways => remove them from the measured sets
        # This one gets all classes that are not ALTERNATES of other ones or if there are duplicates, takes the one
        # that appears first in the instructions file.
        main_classes = Instr_EncDec_Lookup.get_main_classes(lu)
        self.__measure__control__fixed_lat = self.__measure__control__fixed_lat.intersection(main_classes)
        self.__measure__control__vared_lat = self.__measure__control__vared_lat.intersection(main_classes)
        self.__measure__sync__fixed_lat = self.__measure__sync__fixed_lat.intersection(main_classes)
        self.__measure__sync__vared_lat = self.__measure__sync__vared_lat.intersection(main_classes)
        self.__measure__load_store__fixed_lat = self.__measure__load_store__fixed_lat.intersection(main_classes)
        self.__measure__load_store__vared_lat = self.__measure__load_store__vared_lat.intersection(main_classes)
        self.__measure__data__fixed_lat = self.__measure__data__fixed_lat.intersection(main_classes)
        self.__measure__data__vared_lat = self.__measure__data__vared_lat.intersection(main_classes)
        self.__measure__all__fixed_lat = self.__measure__all__fixed_lat.intersection(main_classes)

        if not all('VALID_IN_SHADERS' in c.PROPERTIES for n,c in sm.classes_dict.items()): raise Exception(sp.CONST__ERROR_UNEXPECTED)

    @property
    def measure__control__fixed_lat(self) -> set:
        """Benchmarking/Measurement: All instruction classes related to control flow with a fixed latency (no rd/wr barrier).

        For example the instruction classes of opcodes:
        * BRA, CALL, EXIT
        * WARPSYNC, RET, JMP

        The latencies of these instructions can be extracted from USCHED_INFO.

        The UNION of all self.measure__... properties contains all instruction classes.

        :return: a set with the instruction classes related to control flow that have a fixed latency
        :rtype: set
        """
        return self.__measure__control__fixed_lat
    @property
    def measure__control__vared_lat(self) -> set:
        """Benchmarking/Measurement: All instruction classes related to control flow with a variable latency, that feature an rd, wr or both barriers.

        For example the instruction classes related to opcodes:
        * NANOTRAP, BMOV

        A baseline for the latencies of these instructions is 'min_wait_needed'.

        The UNION of all self.measure__... properties contains all instruction classes.

        :return: a set with all control flow instruction classes with rd, wr or both barriers
        :rtype: set
        """
        return self.__measure__control__vared_lat
    @property
    def measure__sync__fixed_lat(self) -> set:
        """Benchmarking/Measurement: All instruction classes related to synchronization with a fixed latency (no rd/wr barrier).

        For example the instruction classes related to opcodes:
        * DEPBAR, ERRBAR

        The latencies of these instructions can be extracted from USCHED_INFO.

        The UNION of all self.measure__... properties contains all instruction classes.

        :return: a set with the instruction classes related to synchronization that have a fixed latency
        :rtype: set
        """
        return self.__measure__sync__fixed_lat
    @property
    def measure__sync__vared_lat(self) -> set:
        """Benchmarking/Measurement: All instruction classes related to synchronization with a variable latency (featuring rd, wr or both barriers).

        For example the instruction classes related to opcodes:
        * R2B, B2R
        * BAR, MEMBAR

        A baseline for the latencies of these instructions is 'min_wait_needed'.

        The UNION of all self.measure__... properties contains all instruction classes.

        :return: a set with the instruction classes related to synchronization that have a variable latency
        :rtype: set
        """
        return self.__measure__sync__vared_lat
    @property
    def measure__load_store__fixed_lat(self) -> set:
        """Benchmarking/Measurement: All instruction classes related to load/store with a fixed latency.

        For example the instruction classes related to opcodes:
        * CCTL, CCTLT
        * ERRBAR

        The UNION of all self.measure__... properties contains all instruction classes.

        :return: a set with the instruction classes related to memory access with fixed latency
        :rtype: set
        """
        return self.__measure__load_store__fixed_lat
    @property
    def measure__load_store__vared_lat(self) -> set:
        """Benchmarking/Measurement: All instruction classes related to load/store with a variable latency (featuring rd, wr or both barriers).

        For example the instruction classes related to opcodes:
        * LD, ST, LDC
        * ATOM, ATOMG

        A baseline for the latencies of these instructions is 'min_wait_needed'.

        The UNION of all self.measure__... properties contains all instruction classes.

        :return: a set with the instruction classes related to synchronization that have a variable latency
        :rtype: set
        """
        return self.__measure__load_store__vared_lat
    @property
    def measure__data__fixed_lat(self) -> set:
        """Benchmarking/Measurement: All instruction classes related to data flow with a fixed latency (no rd/wr barrier).

        For example the instruction classes related to opcodes:
        * SHL, LEA, IMAD
        * FFMA, ISETP

        The latencies of these instructions can be extracted from USCHED_INFO.

        The UNION of all self.measure__... properties contains all instruction classes.

        :return: a set with the instruction classes related to data flow that have a fixed latency
        :rtype: set
        """
        return self.__measure__data__fixed_lat
    @property
    def measure__data__vared_lat(self) -> set:
        """Benchmarking/Measurement: All instruction classes related to data flow with a variable latency (featuring rd, wr or both barriers).

        For example the instruction classes related to opcodes:
        * HMMA, F2F, STG
        * I2F, STG, LD

        The latencies of these instructions have to be benchmarked. Intersect with 
        * self.instr_cat__rd => all variable latency instructions to-be-benchmarked with an RD only barrier
        * self.instr_cat__wr => all variable latency instructions to-be-benchmarked with a WR only barrier
        * self.instr_cat__rdwr => all variable latency instructions to-be-benchmarked with both RD and WR barrier
        * self.instr_cat__wrearly => all variable latency instructions to-be-benchmarked with a WR_EARLY barrier (SM 90++). NOTE: this is a SUBSET of self.instr_cat__wr!!

        The UNION of all self.measure__... properties contains all instruction classes.

        :return: a set with the instruction classes related to data flow that have a variable latency
        :rtype: set
        """
        return self.__measure__data__vared_lat
    @property
    def measure__all__fixed_lat(self) -> set:
        """Benchmarking/Measurement: all instruction classes related to anything that have a fixed latency (including control, sync, memory, etc). Unfortunately
        fixed vs. variable latency doesn't really stop at category borders.

        For all of these, it is ok to use the USCHED_INFO value to gain insights into how many cycles they take.

        :return: a set with all fixed latency instruction classes.
        :rtype: set
        """
        return self.__measure__all__fixed_lat
    @property
    def instr_cat__control_rd(self) -> set:
        """Contains the instruction classes of control flow instructions that have an RD barrier only.
        
        * Control instruction classes influence the flow of a kernel.
        * These are variable latency instructions

        :return: a set with all control instruction classes with an RD barrier
        :rtype: set
        """
        return self.__instr_cat__control_rd
    @property
    def instr_cat__control_wr(self) -> set:
        """Contains the instruction classes of control flow instructions that have an WR barrier only.
        
        * Control instruction classes influence the flow of a kernel.
        * These are variable latency instructions

        :return: a set with all control instruction classes with an WR barrier
        :rtype: set
        """
        return self.__instr_cat__control_wr
    @property
    def instr_cat__control_rdwr(self) -> set:
        """Contains the instruction classes of control flow instructions that have both WR and RD barriers.
        
        * Control instruction classes influence the flow of a kernel.
        * These are variable latency instructions

        :return: a set with all control instruction classes with WR and RD barriers
        :rtype: set
        """
        return self.__instr_cat__control_rdwr
    @property
    def instr_cat__control_wrearly(self) -> set:
        """Contains the instruction classes of control flow instructions that have a WR_EARLY barrier AND a WR barrier.
        
        * Control instruction classes influence the flow of a kernel.
        * These are variable latency instructions
        * NOTE: WR_EARLY barriers only exist for SM90 and above and only in instructions that also have a WR barrier.
        * NOTE: instr_cat__control_wrearly is a **SUBSET** of instr_cat__control_wr!

        :return: a set with all control instruction classes with an WR_EARLY barrier
        :rtype: set
        """
        return self.__instr_cat__control_wrearly
    @property
    def instr_cat__load_store_rd(self) -> set:
        """Contains the instruction classes for load/store instructions that have an RD barrier only.

        * all instructions in this category have the instruction description category 'Load/Store Instructions'
        * all instructions in this category have an RD barrier only
        
        :return: a set with all load/store instruction classes with an RD barrier only
        :rtype: set
        """
        return self.__instr_cat__load_store_rd
    @property
    def instr_cat__load_store_wr(self) -> set:
        """Contains the instruction classes for load/store instructions that have a WR barrier only.

        * all instructions in this category have the instruction description category 'Load/Store Instructions'
        * all instructions in this category have a WR barrier only
        
        :return: a set with all load/store instruction classes with a WR barrier only
        :rtype: set
        """
        return self.__instr_cat__load_store_wr
    @property
    def instr_cat__load_store_rdwr(self) -> set:
        """Contains the instruction classes for load/store instructions that have an RD and a WR barrier.

        * all instructions in this category have the instruction description category 'Load/Store Instructions'
        * all instructions in this category have an RD barrier and a WR barrier
        
        :return: a set with all load/store instruction classes with RD and WR barriers
        :rtype: set
        """
        return self.__instr_cat__load_store_rdwr
    @property
    def instr_cat__load_store_wrearly(self) -> set:
        """Contains the instruction classes of load/store instructions that have a WR_EARLY barrier AND a WR barrier.
        
        * These are variable latency instructions
        * NOTE: WR_EARLY barriers only exist for SM90 and above and only in instructions that also have a WR barrier.
        * NOTE: instr_cat__load_store_wrearly is a **SUBSET** instr_cat__load_store_wr!

        :return: a set with all control instruction classes with an WR_EARLY barrier
        :rtype: set
        """
        return self.__instr_cat__load_store_wrearly
    @property
    def instr_cat__load_store_no_barrier(self) -> set:
        """Contains the instruction classes of load/store instructions that have no barrier at all.
        
        * These are fixed latency instructions
        
        For example, on SM 86 these are instruction classes
        * cctlt__IVALL, cctl__IVALL_WBALL_D_U_noSrc, cctl__IVALL_WBALL_I_noSrc, cctl__IVALL_WBALL_C_noSrc, errbar_, cctll__IVALL_WBALL_D_U_noSrc

        :return: a set with all control instruction classes with no barrier
        :rtype: set
        """
        return self.__instr_cat__load_store_no_barrier
    @property
    def instr_cat__rd(self) -> set:
        """Contains the instruction classes of regular instructions that have an RD barrier.
        
        * Regular instruction classes move or change data and don't directly influence the program flow.
        * These are variable latency instructions
        
        :return: a set with all regular instruction classes with an RD barrier
        :rtype: set
        """
        return self.__instr_cat__rd
    @property
    def instr_cat__wr(self) -> set:
        """Contains the instruction classes of regular instructions that have a WR barrier.
        
        * Regular instruction classes move or change data and don't directly influence the program flow.
        * These are variable latency instructions

        :return: a set with all regular instruction classes with a WR barrier
        :rtype: set
        """
        return self.__instr_cat__wr
    @property
    def instr_cat__rdwr(self) -> set:
        """Contains the instruction classes of regular instructions that have an RD and a WR barrier.
        
        * Regular instruction classes move or change data and don't directly influence the program flow.
        * These are variable latency instructions

        :return: a set with all regular instruction classes with an RD and a WR barrier
        :rtype: set
        """
        return self.__instr_cat__rdwr
    @property
    def instr_cat__wrearly(self) -> set:
        """Contains the instruction classes of regular instructions that have a WR_EARLY barrier.
        
        * Regular instruction classes move or change data and don't directly influence the program flow.
        * These are variable latency instructions
        * NOTE: WR_EARLY barriers only exist for SM90 and above and only in instructions that also have a WR barrier.
        * NOTE: instr_cat__wrearly is a **SUBSET** of instr_cat__wr!

        :return: a set with all control instruction classes with an WR_EARLY barrier
        :rtype: set
        """
        return self.__instr_cat__wrearly
    @property
    def instr_cat__control_ff_vared(self) -> set:
        """Contains the instruction classes of control instructions with fixed latency but parameterized PREDICATES.

        **NOTE: this mechanism is not relevant for the latencies**

        * Control instruction classes influence the flow of a kernel.
        * Parameterized PREDICATES are for example DEST_SIZE or ISRC_B_SIZE that depend on the configuration of the instruction. For example:
            * IDEST_SIZE = 32 + ((sz==`ATOMCASSZ@U64) || (sz==`ATOMCASSZ@"64"))*32;
        * Non-parameterized PREDICATES are fixed numbers. For example
            * IDEST_SIZE = 32;

        :return: a set with all control instructions with fixed latency but parameterized PREDICATES
        :rtype: set
        """
        return self.__instr_cat__control_ff_vared
    @property
    def instr_cat__control_ff_fixed(self) -> set:
        """Contains the instruction classes of fixed-latency control instructions.

        **NOTE: this mechanism is not relevant for the latencies**
        
        * Control instruction classes influence the flow of a kernel.
        * Parameterized PREDICATES are for example DEST_SIZE or ISRC_B_SIZE that depend on the configuration of the instruction. For example:
            * IDEST_SIZE = 32 + ((sz==`ATOMCASSZ@U64) || (sz==`ATOMCASSZ@"64"))*32;
        * Non-parameterized PREDICATES are fixed numbers. For example
            * IDEST_SIZE = 32;

        :return: a set with all fixed-latency control instructions
        :rtype: set
        """
        return self.__instr_cat__control_ff_fixed
    @property
    def instr_cat__ff_vared(self) -> set:
        """Contains the instruction classes of regular instructions with fixed latency but parameterized PREDICATES.

        **NOTE: this mechanism is not relevant for the latencies**
        
        * Regular instruction classes move or change data and don't directly influence the program flow.
        * Parameterized PREDICATES are for example DEST_SIZE or ISRC_B_SIZE that depend on the configuration of the instruction. For example:
            * IDEST_SIZE = 32 + ((sz==`ATOMCASSZ@U64) || (sz==`ATOMCASSZ@"64"))*32;
        * Non-parameterized PREDICATES are fixed numbers. For example
            * IDEST_SIZE = 32;

        :return: a set with all regular instructions with fixed latency but parameterized PREDICATES
        :rtype: set
        """
        return self.__instr_cat__ff_vared
    @property
    def instr_cat__ff_fixed(self) -> set:
        """Contains the instruction classes of fixed-latency, regular instructions.

        **NOTE: this mechanism is not relevant for the latencies**
        
        * Regular instruction classes move or change data and don't directly influence the program flow.
        * Parameterized PREDICATES are for example DEST_SIZE or ISRC_B_SIZE that depend on the configuration of the instruction. For example:
            * IDEST_SIZE = 32 + ((sz==`ATOMCASSZ@U64) || (sz==`ATOMCASSZ@"64"))*32;
        * Non-parameterized PREDICATES are fixed numbers. For example
            * IDEST_SIZE = 32;

        :return: a set with all regular, fixed-latency instructions
        :rtype: set
        """
        return self.__instr_cat__ff_fixed

    @property
    def control_instr_opcodes(self) -> set:
        """Control instructions govern the control flow of a Cuda kernel.

        :return: a set with all control instruction opcodes specified in SASS_Class.OPCODES['opcode']['i'].
        :rtype: set
        """        
        return self.__control_instr_opcodes
    @property
    def instr_cat__control_all(self) -> set:
        """Control instructions change the control flow of a Cuda kernel.

        :return: a set with all control instruction class names. Access the instruction class using an entry in this set.
        :rtype: set
        """        
        return self.__instr_cat__control_all
    @property
    def instr_cat__load_store_all(self) -> set:
        """Load/Store instructions access some kind of memory. All these instructions have at least one barrier.

        :return: a set with all load/store instruction class names.
        :rtype: _type_
        """
        return self.__instr_cat__load_store_all
    @property
    def instr_split(self) -> dict: 
        """Every instruction class is associated with several categories.

        * 'c': this is the class name as it appears in the class definition. It is unique to each instruction class.
        * 'o': this is the operation code as it appears in an instruction. Oftern, there are several instruction classes that share the same opcode.
        * 'p': this is the instruction pipe. It is a synonym for the opcode.
        * 's': these are the sizes of the operands
        * 'n': these are the SIDL names (no idea what that stands or is for)
        * 'l': this is a list of all latency sets the instruction class is part of. Latency sets are used in the latencies.txt to determine which latency numbers are associated with an instruction class.

        For example:
        * inst_split['INST_TYPE_COUPLED_MATH'][0] = {'c': 'bmsk__RCR_RCR', 'o': 'BMSK', 'p': 'BMSKint_pipe', 's': ['32', '0', '32', '0', '0', '32', '32'], 'n': ['`SIDL_NAMES@BMSK_C'], 'l': {'MATH_WITH_MMA', 'MATH_PRED_OPS', 'MATH_OPS_WITHOUT_RPCMOV', 'FXU_OPS', 'MATH_PRED_NO_FP16_FP64_OPS', 'MATH_OPS', 'ALL_OPS_WITHOUT_CBU', 'ALL_OPS_WITHOUT_BAR', 'FXU_WITH_IMMA', 'ALL_OPS_WITH_BMOV', 'int_pipe'}}
        
        :return: a dictionary with a categorization for every instruction class based on their instruction type
        :rtype: dict
        """        
        return self.__instr_split
    @property
    def instr_types(self) -> dict:
        """Instructions have types that are one of the following listed ones. Higher SM numbers have more types.

        Types are defined as sm.details.CONSTANTS, starting with 'INST_TYPE'.

        SM 50 to 120 have:
        * INST_TYPE_MATH = 0
        * INST_TYPE_COUPLED_MATH = 0
        * INST_TYPE_MIO_RD_SCBD = 1
        * INST_TYPE_DECOUPLED_RD_SCBD = 1
        * INST_TYPE_MIO_RD_WR_SCBD = 2
        * INST_TYPE_DECOUPLED_RD_WR_SCBD = 2
        * INST_TYPE_COUPLED_EMULATABLE = 3
        * INST_TYPE_DECOUPLED_BRU_DEPBAR_RD_SCBD = 4

        SM 70 to 120 additionally have:
        * INST_TYPE_DECOUPLED_WR_SCBD = 5
        * INST_TYPE_DECOUPLED_RD_NOREQ_SCBD = 6
        * INST_TYPE_DECOUPLED_WR_NOREQ_SCBD = 7
        * INST_TYPE_DECOUPLED_BRU_DEPBAR_RD_NOREQ_SCBD= 8

        SM 100 to 120 additionall have:
        * INST_TYPE_COUPLED_EMULATABLE_NORD_SCBD = 9
        * INST_TYPE_COUPLED_EMULATABLE_NOWR_SCBD = 10
        * INST_TYPE_COUPLED_EMULATABLE_NORD_NOWR_SCBD = 11

        :return: a dictionary with all types for the current SM
        :rtype: dict
        """        
        return self.__instr_types

    @staticmethod
    def inst_split_to_file(sm:int, inst_split:dict):
        """Dump instr_split dictionary into a file called 'sm_X_inst_split.autogen.txt'.

        :param sm: SM number (for example 50 or 86 or 90)
        :type sm: int
        :param inst_split: inst_split dictionary as contained in property self.instr_split
        :type inst_split: dict
        """        
        m_len = max(max(len(j['c']) for j in i) for i in inst_split.values() if i)
        with open('sm_{0}_inst_split.autogen.txt'.format(sm),'w') as f:
            for k,v in inst_split.items():
                s = [i['l'] for i in v]
                if s: common_sets = ft.reduce(lambda x,y: x.intersection(y), s)
                else: common_sets = set()
                f.write("### {0} ({1}) {2}\n".format(k, len(v), common_sets))
                for vv in v:
                    f.write("   {0} -> {1}\n".format(vv['c'].ljust(m_len+5), [x for x in vv['l'] if not x in common_sets]))
                    f.write("   {0}     -[{1}]-\n".format((m_len+5)*" ", vv['o']))
                    f.write("   {0}     {1}\n".format((m_len+5)*" ", vv['s']))
                    f.write("   {0}     {1}\n".format((m_len+5)*" ", vv['n']))
                f.write("\n")
