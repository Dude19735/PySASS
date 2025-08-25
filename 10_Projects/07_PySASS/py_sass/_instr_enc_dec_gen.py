import pickle
import typing
import itertools as itt
from . import _config as sp
from ._sass_expression import SASS_Expr
from ._tt_terms import TT_Reg, TT_List, TT_Param
from ._instr_enc_dec_lookup import Instr_EncDec_Lookup
from .sm_cu_details import SM_Cu_Details
from .sass_class import SASS_Class

class Instr_EncDec_Gen:
    @staticmethod
    def __sortby_encs(expr:SASS_Expr) -> int:
        val = 0
        if expr.startswith_register(): return val
        val += 1
        if expr.startswith_int(): return val
        val += 1
        if expr.startswith_constant(): return val
        val += 1
        if expr.startswith_table(): return val
        val += 1
        return val

    @staticmethod
    def __table_lookup_check(expr:SASS_Expr) -> set:
        table = expr.get_first_op().table # type: ignore
        t_args = expr.get_table_args()
        dom = [set({tt}) if isinstance(tt, int) else set(int(i) for i in tt.get_domain({})) for tt in t_args['all']]
        t_ind_combs = list(itt.product(*dom))

        # Keep for reference:
        #  => the inversion of tables for these kinds of key parts o instructions is not necessarily invertible
        #  => for example table 'IntegerSigned':
        #      details.TABLES_DICT['IntegerSigned'] == 
        #       {(2,): 0, (3,): 1, (0,): 0, (1,): 1, (4,): 0, (5,): 1, (6,): 0, (7,): 1}
        #     in combination with register 'UInteger':
        #      details.REGISTERS.UInteger == 
        #       {'U8': {0}, 'U16': {2}, 'U32': {4}, 'U64': {6}}
        #     => all the unsigned ones map to 0, all the signed ones to 1
        # inv = dict()
        # for k in t_ind_combs:
        #     if not k in table: continue
        #     val = table[k]
        #     if val in inv: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        #     inv[val] = k

        return set(table[k] for k in t_ind_combs if k in table)

    @staticmethod
    def __class_lookup_gen_entry(non_zero_reg_names:dict, ext_names:set, ext_values:dict, class_:SASS_Class, details:SM_Cu_Details) -> typing.Tuple[dict, dict]:
        if not isinstance(non_zero_reg_names, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ext_names, set): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(ext_values, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(class_, SASS_Class): raise Exception(sp.CONST__ERROR_ILLEGAL)

        required_enc_values = dict()
        required_code_values = dict()
        for i in sorted(class_.ENCODING, key=lambda x: Instr_EncDec_Gen.__sortby_encs(x['alias'])):
            if i['code_name'][0] == '!': continue
            expr:SASS_Expr
            expr = i['alias']
            code_name = i['code_name']

            # Skip the bits that designate WR and RD barriers. On SM 50 to 62, they are OEVarLatDest and OEVarLatSrc, on SM 70 to SM 120
            # they are BITS_3_115_113_src_rel_sb and BITS_3_112_110_dst_wr_sb
            if code_name in ['OEVarLatDest', 'OEVarLatSrc', 'BITS_3_115_113_src_rel_sb', 'BITS_3_112_110_dst_wr_sb']: continue

            t_names = set(expr.get_alias_names())
            unique_src = t_names.intersection(ext_names)
            if unique_src:
                if expr.startswith_table():
                    # These are table lookups, for example
                    #   BITS_8_124_122_109_105_opex=TABLES_opex_2(batch_t,usched_info,reuse_src_a);
                    if not len(i['code_ind']) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)

                    # need to get all table values for the given input (again -.-)
                    dom = dict()
                    for e in unique_src: dom[e] = ext_values[e]
                    # this is a set of decimal values
                    res = Instr_EncDec_Gen.__table_lookup_check(expr)
                    # if res == set(), the instruction can't exist
                    # Some instructions inside of SM 50 to 62 are unfullfillable. But at this stage, we don't have that
                    # information => just skip
                    if not res: return dict(),dict()

                    # transform to binary tupple set and store it with the encoding indices
                    enc_ind = i['code_ind'][0]
                    bin_res = set()
                    for s in res:
                        value_bin = [int(i) for i in bin(s)[2:]]
                        value_bin_ext = (len(enc_ind) - len(value_bin))*[0] + value_bin
                        bin_res.add(tuple(value_bin_ext))
                    # store as { enc_ind tuple : {.. set of binary tuples ..} }
                    required_enc_values[enc_ind] = bin_res
                    required_code_values[code_name] = bin_res

                elif expr.startswith_ConstBankAddressX():
                    # These are constBank address accesses, for example
                    #   BITS_5_58_54_Sc_bank,BITS_14_53_40_Sc_addr =  ConstBankAddress2(Sb_bank,Sb_addr);
                    if not len(i['code_ind']) == 2: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    # If we force addresses to be something specific, we have a problem...
                    raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                else:
                    # These are extension values that have to be one of a specific set of values
                    # These are OPCODE extensions, like the /bla in
                    #   FORMAT PREDICATE @[!]Predicate(PT):Pg Opcode /E("noe"):e /COP("EN"):cop /SIZE3("32"):sz /SEM("WEAK"):sem /SCO:sco /PRIVATE("noprivate"):private
                    # or REGISTER extensions like the /bla in
                    #   ','Register:Ra SImm(50/0)*:Ra_offset /RelOpt:rel
                    # NOTE: only extensions that are used in the ENCODING stage are taken into account.
                    # NOTE: not all extensions are encoded!
                    if not len(i['code_ind']) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    enc_ind = i['code_ind'][0]
                    for e in unique_src:
                        bin_res = set()
                        for s in ext_values[e]:
                            value_bin = [int(i) for i in bin(s)[2:]]
                            value_bin_ext = (len(enc_ind) - len(value_bin))*[0] + value_bin
                            bin_res.add(tuple(value_bin_ext))
                        required_enc_values[enc_ind] = bin_res
                        required_code_values[code_name] = bin_res

            elif expr.startswith_int() or expr.startswith_register() or expr.startswith_constant():
                # These are fixed values, for example
                #   BITS_2_80_79_sem=*0;
                #   BITS_1_81_81_andC=*0;
                # NOTE: only extensions that are used in the ENCODING stage are taken into account.
                # NOTE: not all fixed values have a '*' in their definition
                if not len(i['code_ind']) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)

                value:int = expr.get_first_value() # type: ignore
                value_bin = [int(b) for b in bin(value)[2:]]
                enc_ind = i['code_ind'][0]
                value_bin_ext = tuple((len(enc_ind) - len(value_bin))*[0] + value_bin)
                bin_res = set({value_bin_ext})
                required_enc_values[enc_ind] = bin_res 
                required_code_values[code_name] = bin_res
                
            elif expr.startswith_alias():
                # These are regular aliases that point to a ZeroRegister or ZeroUniformRegister. For example
                #   in the FORMAT:   ',' [ NonZeroRegister:Ra + SImm(32/0)*:Ra_offset ]
                #   in the ENCODING: BITS_8_31_24_Ra=*Ra;
                if not len(i['code_ind']) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                enc_ind = i['code_ind'][0]
                alias = str(expr.get_first_value().alias) # type: ignore
                if alias in non_zero_reg_names:
                    if non_zero_reg_names[alias] == 0:
                        bin_res = set({tuple(len(enc_ind)*[1])})
                        required_enc_values[enc_ind] = bin_res 
                        required_code_values[code_name] = bin_res
                    else:
                        bin_res = set(tuple(i.bits) for i in expr.get_first_value().get_domain({})) # type: ignore
                        required_enc_values[enc_ind] = bin_res 
                        required_code_values[code_name] = bin_res

            elif expr.startswith_opcode():
                required_enc_values[class_.get_opcode_encoding()[0]] = set([class_.get_opcode_bin()])
                required_code_values[code_name] = set([class_.get_opcode_bin()])

        return required_enc_values, required_code_values

    @staticmethod
    def __check_non_zero_reg(reg_name:str, reg_alias:str, non_zero_regs:dict) -> dict:
        if reg_name == 'ZeroRegister': non_zero_regs[reg_alias] = 0
        elif reg_name == 'ZeroUniformRegister': non_zero_regs[reg_alias] = 0
        elif reg_name == 'NonZeroRegister': non_zero_regs[reg_alias] = 1
        elif reg_name == 'NonZeroUniformRegister': non_zero_regs[reg_alias] = 1
        elif reg_name == 'NonZeroRegisterFAU': non_zero_regs[reg_alias] = 1
        elif reg_name == 'Predicate_vimnmx': non_zero_regs[reg_alias] = 1
        return non_zero_regs

    @staticmethod
    def __class_lookup_gen(class_:SASS_Class, details:SM_Cu_Details) -> typing.Dict:
        opcode_ext_names = [(str(x.value.value), str(x.value.alias)) for x in class_.FORMAT.opcode.extensions]
        regs_ext_names = []
        non_zero_regs = dict()

        for i in class_.FORMAT.regs:
            # The registers follow the following format:
            if isinstance(i, TT_List):
                # What kinds exactly?
                #  - all lists of stuff: [ZeroRegister(RZ):Ra + UImm(20/0)*:uImm]
                for j in i.value:
                    # lists always contain TT_Param
                    if not isinstance(j, TT_Param): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    # TT_Param contain either TT_Reg or TT_Func
                    if isinstance(j.value, TT_Reg):
                        regs_ext_names.extend([(str(ext.value.value), str(ext.value.alias)) for ext in j.extensions])
                        non_zero_regs = Instr_EncDec_Gen.__check_non_zero_reg(str(j.value.value), str(j.value.alias), non_zero_regs)

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
                            regs_ext_names.extend([(str(ext.value.value), str(ext.value.alias)) for ext in a.extensions])
                            non_zero_regs = Instr_EncDec_Gen.__check_non_zero_reg(str(a.value.value), str(a.value.alias), non_zero_regs)

                non_zero_regs = Instr_EncDec_Gen.__check_non_zero_reg(str(i.value.value), str(i.value.alias), non_zero_regs)
            regs_ext_names.extend([(str(x.value.value), str(x.value.alias)) for x in i.extensions])
        
        ext_names = set(itt.chain.from_iterable(opcode_ext_names + regs_ext_names))
        ext_values = dict(itt.chain.from_iterable([[(x[0],x[2]), (x[1],x[2])] for x in [(i[0],i[1], set(itt.chain.from_iterable(getattr(details.REGISTERS, i[0]).values()))) for i in opcode_ext_names + regs_ext_names]]))

        lookup_entry, lookup_code = Instr_EncDec_Gen.__class_lookup_gen_entry(non_zero_regs, ext_names, ext_values, class_, details)
        if not lookup_entry: return dict()

        lks = dict(sorted(lookup_code.items(), key=lambda x: x[0].lower()))
        return lks

    @staticmethod
    def lookup_gen(sm:int, classes_dict:dict, opcode_multiples:dict, desc:dict, details:SM_Cu_Details) -> dict:
        multiples = [(len(v), k, v) for k,v in opcode_multiples.items() if len(v) > 1]

        # bin_code_map = dict()
        identifiers_alternate = dict()
        identifiers_main = dict()
        classes_main = dict()
        classes_alternate = dict()
        m_ind_tot = len(multiples)
        class_name:str = ""
        for m_ind,(class_count, bin_code, class_names) in enumerate(multiples):
            # unique_hashes = dict()
            for c_ind, class_name in enumerate(class_names):
                print(100*" ",'\r', "Gen Lookup: SM{5}: [{0}/{1} | {2}/{3}] {4}".format(c_ind, class_count, m_ind, m_ind_tot , class_name, sm), end='\r')
                identifier:dict = Instr_EncDec_Gen.__class_lookup_gen(classes_dict[class_name], details)
                # If the instruction can't exist => skip
                if identifier == dict(): continue

                # unique_hashes = { h1: [ ... {'cn':cn, 'lk':lk} ... ], h2: ... }
                # unique_hashes = Instr_EncDec_Gen.update_unique_hashes(unique_hashes, new_unique_hashes)
                if classes_dict[class_name].IS_ALTERNATE:    
                    if bin_code in identifiers_alternate: identifiers_alternate[bin_code].append(identifier)
                    else: identifiers_alternate[bin_code] = [identifier]
                    if bin_code in classes_alternate: classes_alternate[bin_code].append(class_name)
                    else: classes_alternate[bin_code] = [class_name]
                else:
                    if bin_code in identifiers_main: identifiers_main[bin_code].append(identifier)
                    else: identifiers_main[bin_code] = [identifier]
                    if bin_code in classes_main: classes_main[bin_code].append(class_name)
                    else: classes_main[bin_code] = [class_name]

            # bin_code_map[bin_code] = unique_hashes
            print(100*" ",'\r', "Gen Lookup: SM{5}: [{0}/{1} | {2}/{3}] {4}".format(class_count, class_count, m_ind_tot, m_ind_tot, class_name, sm))

        if any(k not in identifiers_main for k in identifiers_alternate):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        # unify with alternates last if they exist
        lks = {k:identifiers_main[k] + (identifiers_alternate[k] if k in identifiers_alternate else []) for k in identifiers_main}
        classes = {k:classes_main[k] + (classes_alternate[k] if k in classes_alternate else []) for k in classes_main}
        lookup = {opcode:Instr_EncDec_Lookup.from_multiples(opcode, lks[opcode], classes[opcode], classes_dict, desc) for opcode in lks}
        lookup.update({opcode:Instr_EncDec_Lookup.from_singles(opcode, class_names[0], classes_dict, desc) for opcode,class_names in opcode_multiples.items() if len(class_names) == 1})

        return lookup
    
    @staticmethod
    def lookup_load(pp:str) -> dict:
        res:dict
        with open(pp, 'rb') as f:
            res = pickle.load(f)
        return res

if __name__ == '__main__':
    from .sm_sass import SM_SASS
    sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90, 100, 120]
    sms = [70, 72, 75, 80, 86, 90, 100, 120] #, 72]
    for sm in sms:
        sass = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=True, web_crawl=False)
        sass.lu_to_md("__auto_generated_sm_{0}_lu.md".format(sm))
        pass

        
                            
