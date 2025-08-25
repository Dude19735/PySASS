import typing
import itertools as itt
import _config as sp
from py_sass import SM_Cu_Details
from py_sass_ext import SASS_Range
from py_sass_ext import SASS_Bits
from py_sass import TT_Instruction
from py_sass import SASS_Class
from py_sass import SM_SASS
from py_sass import SASS_Expr_Domain_Contract

class SASS_Expr_Domain_Limits:
    """
    Some variable types need to get their domains shrunk so that the calculations don't explode too much.

    This one takes care of that. There are two modes:
     - LARGE: this one limits very generically to make sure that Monta Carlo sampling works well without regard for any context
              of the register
     - SMALL: this one targets the automatic benchmarking. For example, it sets all the cash bits to their default values without
              variance and leaves the lower registers of any register type untouched.
    """
    
    @staticmethod
    def sm_50pp_reg_filter(reg_name:str) -> typing.Callable|None:
        if reg_name == 'ChkMode': 
            # The first is ok, all others are INVALIDCHKMODE..., pick the valid one and one of the rest
            return lambda x, m_x: [i for i in x if i<=2]
        elif (reg_name in ('GRF', 'Register', 'RegisterFAU')) or (reg_name[:5] in ('hfma2', 'hset2', 'hmul2', 'hadd2')): 
            # This is the same as the Registers, also including stuff like R00 and R0, R01 and R1, etc, mapping to the same values.
            # Pick values 30 to 50 and 255 for the random generator
            return lambda x, m_x: [i for i in x if (((i>=30) and (i<= 50)) or i==255)]
        elif reg_name in ('NonZeroRegister', 'NonZeroRegisterFAU'):
            # This is the same as the Registers excluding 255. Pick values 30 to 50.
            return lambda x, m_x: [i for i in x if ((i>=30) and (i<= 50))]
        elif reg_name == 'PNWord':
            # No idea what this is. It's used as uImm in older (<=62) architectures and not at all in the newer ones. Keep 0 and discard the rest
            return lambda x, m_x: [i for i in x if (i==0)]
        elif reg_name == 'SIDL_NAMES':
            # These are used only in the PROPERTIES sections => use 0 and ignore
            return lambda x, m_x: [i for i in x if (i==0)]
        elif reg_name == 'SpecialRegister':
            # "Warning: Only SR4..SR11 and SR72..SR83 are valid for CS2R"
            # "Warning: Only SR4..SR11 and SR72..SR83 are valid for CS2R"
            # "Special registers 84 and 85 should not be read in user mode"
            return lambda x, m_x: [i for i in x if ((i>=4 and i<=11) or (i>=72 and i<=83))]
        # NOTE: the following cover all SMs
        elif reg_name == 'BATCH_T':
            # Allways 0 for our purposes
            return lambda x, m_x: [i for i in x if i==0]
        elif reg_name == 'USCHED_INFO':
            # Use DRAIN=0, WAIT1=1 and TRANS1=17 => something for everyone...
            return lambda x, m_x: [i for i in x if i in (0, 1, 17)]
        elif reg_name == 'PM_PRED':
            # Allways 0 for our purposes
            return lambda x, m_x: [i for i in x if i==0]
        elif reg_name == 'REQ':
            # Wait for no barrier as default
            return lambda x, m_x: [i for i in x if i==0]
        elif reg_name == 'RD':
            # Set no barrier
            return lambda x, m_x: [i for i in x if i==7]
        elif reg_name == 'WR':
            # Set no barrier
            return lambda x, m_x: [i for i in x if i==7]
        elif reg_name == 'WR_EARLY':
            # Set no barrier
            return lambda x, m_x: [i for i in x if i==7]
        else: return None

    @staticmethod
    def sm_70pp_reg_filter(reg_name:str) -> typing.Callable|None:
        if reg_name == 'NP':
            # NP is some subset of PNWord. It's used only in one instruction (fswzadd_) with no condition limitations
            return lambda x, m_x: [i for i in x if i == 0]
        elif reg_name == 'BarrierRegister':
            # No single instruction explicitly uses this as a register type. Instructions that use barriers use a subset
            # of these called 'BD' that contains a subset of the registers in side of BarrierRegister:
            #  -> SM 70:  BD "B10"=10 , "B11"=11 , "B14"=14 , "B4"=4 , "B5"=5 , "B6"=6 , "B7"=7 , "B0"=0 , "B1"=1 , "B2"=2 , "B3"=3 , "B15"=15 , "B12"=12 , "B8"=8 , "B9"=9 , "B13"=13;
            #   ...
            #  -> SM 120: BD "B10"=10 , "B11"=11 , "B14"=14 , "B4"=4 , "B5"=5 , "B6"=6 , "B7"=7 , "B0"=0 , "B1"=1 , "B2"=2 , "B3"=3 , "B15"=15 , "B12"=12 , "B8"=8 , "B9"=9 , "B13"=13;
            return lambda x, m_x: [i for i in x if i == 0]
        else: return None

    @staticmethod
    def sm_75pp_reg_filter(reg_name:str, zero_uniform:int) -> typing.Callable|None:
        if reg_name == 'NonZeroUniformRegister':
            # This is the same as UniformRegister, excluding URZ=63
            return lambda x, m_x: [i for i in x if ((i>=30) and (i<= 50))]
        elif reg_name == 'UniformRegister':
            # Use 30 to 50 for the generator, reserve 0 to 29 for SASS boilerplate, add 63 for UZR
            return lambda x, m_x: [i for i in x if (((i>=30) and (i<= 50)) or i==zero_uniform)]
        else: return None

    def sm_90pp_reg_filter(reg_name:str, details:SM_Cu_Details) -> typing.Callable|None:
        if reg_name == 'MMA_SIZE': 
            return lambda x, m_x: [i for i in x if  i in {next(iter(details.REGISTERS.MMA_SIZE[x])) for x in [i for i in details.REGISTERS.MMA_SIZE if not (i.startswith('_') or i.startswith('INVALID'))]}]
        elif reg_name == 'CBU_STATE': 
            return lambda x, m_x: [i for i in x if i in {next(iter(details.REGISTERS.CBU_STATE[x])) for x in [i for i in details.REGISTERS.CBU_STATE]}]
        elif reg_name.startswith('SIZE_64'):
            return lambda x, m_x: [i for i in x if i in {next(iter(getattr(details.REGISTERS, reg_name)[x])) for x in [i for i in getattr(details.REGISTERS, reg_name)] if not (x.startswith('_'))}]
        else: return None
    
    @staticmethod
    def to_limit(details:SM_Cu_Details) -> typing.Dict[str, callable]:
        """
        Some domains are just too large to not be limited. Decide which ones should be limited in size in here.
        """
        xx = [(i, ([r for r in getattr(details.REGISTERS, i).values()]))
            for i in dir(details.REGISTERS)
            if not (i.startswith('__') and i.endswith('__')) and isinstance(getattr(details.REGISTERS, i), dict)]
        xx2 = [(x[0], len(set(itt.chain.from_iterable([list(s) for s in x[1]])))) for x in xx]
        to_limit = {i[0]:i[1] for i in xx2 if (i[1] > 32 or i[0] in ('BATCH_T', 'USCHED_INFO', 'PM_PRED', 'REQ', 'RD', 'WR', 'WR_EARLY'))}
        
        # For the large one, return the generaly limited one
        if sp.CONFIG__GEN_LARGE: 
            for k in to_limit:
                to_limit[k] = lambda x, m_x: [i for i in x if ((i<20) or (i>= (m_x/2-10) and i <= (m_x/2+10)) or (i>=m_x-20))]
            return to_limit

        # For the benchmarking one, choose a more targeted approach: for some registers, we can pick very few ones
        # for others we need the entire range, for example, because we need to cover all applicable sizes.
        if details.SM_XX in ('sm_50', 'sm_52', 'sm_53', 'sm_60', 'sm_61', 'sm_62'):
            for k in to_limit:
                b = SASS_Expr_Domain_Limits.sm_50pp_reg_filter(k)
                if b is not None: to_limit[k] = b
                else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif details.SM_XX in ('sm_70', 'sm_72'):
            for k in to_limit:
                b = SASS_Expr_Domain_Limits.sm_50pp_reg_filter(k)
                if b is not None: to_limit[k] = b
                else:
                    b = SASS_Expr_Domain_Limits.sm_70pp_reg_filter(k)
                    if b is not None: to_limit[k] = b
                    else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif details.SM_XX in ('sm_75', 'sm_80', 'sm_86'):
            for k in to_limit:
                b = SASS_Expr_Domain_Limits.sm_50pp_reg_filter(k)
                if b is not None: to_limit[k] = b
                else:
                    b = SASS_Expr_Domain_Limits.sm_70pp_reg_filter(k)
                    if b is not None: to_limit[k] = b
                    else:
                        b = SASS_Expr_Domain_Limits.sm_75pp_reg_filter(k, next(iter(details.REGISTERS.ZeroUniformRegister['URZ'])))
                        if b is not None: to_limit[k] = b
                        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif details.SM_XX in ('sm_90', 'sm_100', 'sm_120'):
            for k in to_limit:
                b = SASS_Expr_Domain_Limits.sm_50pp_reg_filter(k)
                if b is not None: to_limit[k] = b
                else:
                    b = SASS_Expr_Domain_Limits.sm_70pp_reg_filter(k)
                    if b is not None: to_limit[k] = b
                    else:
                        b = SASS_Expr_Domain_Limits.sm_75pp_reg_filter(k, next(iter(details.REGISTERS.ZeroUniformRegister['URZ'])))
                        if b is not None: to_limit[k] = b
                        else:
                            b = SASS_Expr_Domain_Limits.sm_90pp_reg_filter(k, details)
                            if b is not None: to_limit[k] = b
                            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else: raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        
        return to_limit
    
    @staticmethod
    def filter_domains(sass:SM_SASS, class_name:str, dom:typing.List[typing.Dict[str, SASS_Range|typing.Set[SASS_Bits]]]) -> typing.List[typing.Dict[str, SASS_Range|typing.Set[SASS_Bits]]]:
        """Filter domains for unwanted values if _config.CONFIG__GEN_SMALL = True, otherwise, does nothing.

        We need this additional filter because the domain generation is multi-stage.
        Some domain variables are simply generated, others are calculated using the CONDITIONS and the
        remaining ones are created in the ENCODINGS stage.

        This filter is called in all three locations.

        Currently filtered are:
        * Pg, Pg@not: set the predicate to PT and don't negate (allways run)
        * WR, RD, WR_EARLY: set all barriers to 0x7 (no barriers)
        * REQ: set REQ = 0x0 (wait for nothing)

        :param sass: SM_SASS for the current SM variant
        :type sass: SM_SASS
        :param class_name: the instruction class name currently being generated
        :type class_name: str
        :param dom: the unfiltered alias domains list
        :type dom: typing.List[typing.Dict[str, SASS_Range | typing.Set[SASS_Bits]]]
        :return: a filtered domain if _config.CONFIG__GEN_SMALL = True otherwise input == output
        :rtype: typing.List[typing.Dict[str, SASS_Range|typing.Set[SASS_Bits]]]
        """
        
        # If we don't want the small domains, do nothing, do not filter, don't even though the domains
        if not sp.CONFIG__GEN_SMALL: return dom

        # Otherwise, go nuts :-P
        new_dom = []
        for d in dom:
            if ('Pg' in d) or ('Pg@not' in d):
                # Make sure: if we have Pg, we also have Pg@not. They always come in pairs
                if not (('Pg' in d) and ('Pg@not' in d)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                # At this point, if we don't have the class, we really go nuts
                if not class_name in sass.sm.classes_dict: raise Exception(sp.CONST__ERROR_ILLEGAL)
                format_tt:TT_Instruction = sass.sm.classes_dict[class_name].FORMAT
                
                # Make sure we have a predicate. If we don't, this would be unexpected sinde Pg is always a predicate
                if format_tt.pred is None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                # Make sure the alias of the predicate we have is Pg. If not, this would be unexpected sinde Pg is always the alias of a predicate
                if not str(format_tt.pred.alias) == 'Pg': raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                # Filter Pg to PT (exclude P0 to P6)
                np = {i for i in d['Pg'] if int(i) == 0x7}
                # Make sure we have exactly PT in the set for the predicates
                if not (len(np) == 1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                d['Pg'] = np

                # Filter Pg@not to 0 (exclude Pg_negate == True)
                np = {i for i in d['Pg@not'] if int(i) == 0x0}
                if not (len(np) == 1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                d['Pg@not'] = np

            if class_name in sass.sm.classes_dict:
                # search for other stuff
                class_:SASS_Class = sass.sm.classes_dict[class_name]
                req_alias = class_.props.cash_alias__req if class_.props.cash_has__req else ''
                wr_alias = class_.props.cash_alias__wr if class_.props.cash_has__wr else ''
                rd_alias = class_.props.cash_alias__rd if class_.props.cash_has__rd else ''
                wr_early_alias = class_.props.cash_alias__wr_early if class_.props.cash_has__wr_early else ''
                if req_alias in d:
                    np = {i for i in d[req_alias] if int(i) == 0x0}
                    if not (len(np) == 1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    d[req_alias] = np
                if wr_alias in d:
                    np = {i for i in d[wr_alias] if int(i) == 0x7}
                    if not (len(np) == 1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    d[wr_alias] = np
                if rd_alias in d:
                    np = {i for i in d[rd_alias] if int(i) == 0x7}
                    if not (len(np) == 1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    d[rd_alias] = np
                if wr_early_alias in d:
                    np = {i for i in d[wr_early_alias] if int(i) == 0x7}
                    if not (len(np) == 1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    d[wr_early_alias] = np

            new_dom.append(d)

        # # We removed stuff, maybe we can contract the domains a little bit more? Let's try
        # new_dom = SASS_Expr_Domain_Contract.group(new_dom)
        return new_dom
