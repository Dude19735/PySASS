import os
import itertools as itt
from . import _config as sp
from ._sass_expression import SASS_Expr
if not sp.SWITCH__USE_TT_EXT:
    from ._tt_terms import TT_Reg, TT_List, TT_Param
else:
    from py_sass_ext import TT_Reg, TT_List, TT_Param
from .sm_sass import SM_SASS
from .sass_class import SASS_Class
from .sass_class import SASS_Class

"""
This script was used to determine how different instruction classes can be distinguished from one another. It's outdated now
but still kept for reference. Check out _instr_enc_dec_gen.py for the final version.
"""

def sortby(class_:SASS_Class):
    return " ".join([class_.class_name] + [str(i) for i in class_.FORMAT.opcode.extensions])

def sortby_encs(expr:SASS_Expr):
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

def print_class(sass:SM_SASS, class_name:str, lines:list, ljust=20):
    class_ = sass.__sm.classes_dict[class_name]
    opcode_ext_names = [(str(x.value.value), str(x.value.alias)) for x in class_.FORMAT.opcode.extensions]
    regs_ext_names = []
    zero_regs = dict()

    if class_name == 'I_ATOMS_CAS_RZ_and_Rc' or class_name == 'I_ATOMS_CAS_RZ_and_Rc': # 'st__sImmOffset':
        pass

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
                    if str(j.value.value) == 'ZeroRegister': zero_regs[str(j.value.alias)] = 1
                    elif str(j.value.value) == 'ZeroUniformRegister': zero_regs[str(j.value.alias)] = 1
                    else: zero_regs[str(j.value.alias)] = 0

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
                        if str(a.value.value) == 'ZeroRegister': zero_regs[str(a.value.alias)] = 1
                        elif str(a.value.value) == 'ZeroUniformRegister': zero_regs[str(a.value.alias)] = 1
                        else: zero_regs[str(a.value.alias)] = 0

            if str(i.value.value) == 'ZeroRegister': zero_regs[str(i.value.alias)] = 1
            elif str(i.value.value) == 'ZeroUniformRegister': zero_regs[str(i.value.alias)] = 1
            else: zero_regs[str(i.value.alias)] = 0
        regs_ext_names.extend([(str(x.value.value), str(x.value.alias)) for x in i.extensions])
    
    ext_names = set(itt.chain.from_iterable(opcode_ext_names + regs_ext_names))
    ext_values = dict(itt.chain.from_iterable([[(x[0],x[2]), (x[1],x[2])] for x in [(i[0],i[1], set(itt.chain.from_iterable(getattr(sass.__sm.details.REGISTERS, i[0]).values()))) for i in opcode_ext_names + regs_ext_names]]))

    ext_vals = dict()
    zero_bits = sass.__sm.details.FUNIT.encoding_width*[0] # type: ignore
    for i in sorted(class_.ENCODING, key=lambda x: sortby_encs(x['alias'])):
        if i['code_name'][0] == '!': continue
        expr:SASS_Expr
        expr = i['alias']

        unique_src = set(expr.get_alias_names()).intersection(ext_names)
        if unique_src:
            for e in unique_src: ext_vals[e] = ext_values[e]
        if expr.startswith_int() or expr.startswith_register() or expr.startswith_constant():
            ext_vals[i['code_name']] = {expr.get_first_value()}
        if expr.startswith_alias():
            alias = str(expr.get_first_value().alias) # type: ignore
            if alias in zero_regs:
                if zero_regs[alias] == 1:
                    for i in i['code_ind'][0]: zero_bits[i] = 1

    unique_hashes = enc_unique_to_hash(class_.funit_mask_hash, ext_vals, tuple(zero_bits), class_.class_name)
    return unique_hashes

def dict_to_hash(reg_vals:dict):
    if not isinstance(reg_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
    hh = tuple(itt.chain.from_iterable((i[0],) + tuple(i[1]) for i in reg_vals.items())).__hash__()

    return (hh, reg_vals)

def enc_unique_to_hash(pattern_hash:int, ext_vals:dict, zero_bits:tuple, class_name:str) -> tuple:
    if not isinstance(pattern_hash, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
    if not isinstance(ext_vals, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
    if not isinstance(zero_bits, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)
    if not isinstance(class_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)

    ll = sorted(ext_vals.items(), key=lambda x: x[0])
    ext_vals_hh = tuple(tuple(i[1]).__hash__() for i in ll).__hash__()

    return ((ext_vals_hh, zero_bits), class_name)

def update_unique_hashes(unique_hashes:dict, new_unique_hashes:tuple, class_name:str, sass:SM_SASS) -> dict:
    if not isinstance(unique_hashes, dict): raise Exception(sp.CONST__ERROR_ILLEGAL)
    if not isinstance(new_unique_hashes, tuple): raise Exception(sp.CONST__ERROR_ILLEGAL)

    nh:int = new_unique_hashes[0]
    cn:str = new_unique_hashes[1]

    if nh in unique_hashes:
        unique_hashes[nh].append(cn)
    else:
        unique_hashes[nh] = [cn]
    return unique_hashes

if __name__ == '__main__':
    location = os.path.dirname(os.path.realpath(__file__))
    pp = location + "/DocumentSASS/sm_{0}_domains.lz4"

    sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90]
    for sm in sms:
        sass:SM_SASS
        sass = SM_SASS(sm)
        # sedom = SASS_Enc_Dom(pp.format(sm))

        multiples = [i for i in sorted([(len(i[1]), i[0], i[1]) for i in itt.chain.from_iterable([[(bin_code,class_names) for bin_code,class_names in v.items() if len(class_names) > 1] for k,v in sass.__sm.opcode_ref.items()])], key=lambda x: x[0], reverse=True)]

        same_hash_instr_classes = dict()

        # lines = []
        bin_code_map = dict()
        m_ind_tot = len(multiples)
        for m_ind,(class_count, bin_code, class_names) in enumerate(multiples):
            vals = []
            unique_hashes = dict()
            global_alternate_n_to_n = {}
            class_name = ""
            for c_ind, class_name in enumerate(class_names):
                print("SM{5}: [{0}/{1} | {2}/{3}] {4}".format(c_ind, class_count, m_ind, m_ind_tot , class_name, sm), end='\r')
                new_unique_hashes:tuple = print_class(sass, class_name, [], 20)
                unique_hashes = update_unique_hashes(unique_hashes, new_unique_hashes, class_name, sass)

            bin_code_map[bin_code] = unique_hashes
            print("SM{5}: [{0}/{1} | {2}/{3}] {4}".format(class_count, class_count, m_ind_tot, m_ind_tot, class_name, sm))
        print()

        shell_commands = []
        with open('CLASSES_decode_analysis_{0}.md'.format(sm), 'w') as f:
            for bc,ic in bin_code_map.items():
                if any(len(i)>1 for i in ic.values()):
                    f.write("##### {0}:\n".format(bc))
                    for ind, (h, g) in enumerate(ic.items()):
                        if len(g) > 1:
                            alts = []
                            reg = None
                            p = "temp/sm_{0}_{1}.class"
                            for c in g:
                                with open(p.format(sm, c), 'w') as ccc:
                                    ccc.write(str(sass.__sm.classes_dict[c]))
                                if sass.__sm.classes_dict[c].IS_ALTERNATE:
                                    alts.append(c)
                                else:
                                    if reg is not None: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                                    reg = c

                            if reg is None:
                                shell_commands.append('bcompare {0} {1}'.format(p.format(sm, alts[0]), p.format(sm, alts[1])))
                            else:
                                for alt in alts:
                                    shell_commands.append('bcompare {0} {1}'.format(p.format(sm, reg), p.format(sm, alt)))
                            
                            if reg is None: reg = '[.....]'
                            f.write("   {0}\n".format(reg))
                            f.write("      {0}\n".format("\n      ".join(alts)))

                            
        with open("__auto_generated_sm_{0}_cmp.sh".format(sm), 'w') as f:
            f.write("\n".join(shell_commands))

    
