import typing
import itertools as itt
from . import _config as sp
from . import _tt_terms as ftt
from ._sass_util import SASS_Util as su
from ._sass_expression import SASS_Op
from ._sass_expression import SASS_Expr
from ._tt_instruction import TT_Instruction
from ._tt_term import TT_Term
from ._iterator import Iterator

class _SASS_Class:
    """
    This one is part of the instruction.txt parser.

    This is a helper class for SASS_Class. It contains all the static methods used to parse an SASS class.
    All the ..._to_string methods and the parse method are piggibacked into the real SASS_Class.
    """
    @staticmethod
    def __parse_to_next(lines_iter:Iterator, tt:dict):
        entry = []
        next_ll = []
        nn = ''
        while True:
            c = next(lines_iter, False)
            if not c: break

            if c in (' ', '\n', ';'):
                nn = "".join(entry).strip()
                if nn in tt.keys(): break
                elif nn:
                    next_ll.append(nn)
                next_ll.append(c)
                entry = []
            else:
                entry.append(c)

        return nn, "".join(next_ll)

    @staticmethod
    def parse_cash_str(class_name:str, cash_str:str, outer_res:dict):
        tt = {
            sp.CONST_NAME__FORMAT: _SASS_Class.__parse_format,
            sp.CONST_NAME__FORMAT_ALIAS: _SASS_Class.__parse_format_alias,
            sp.CONST_NAME__CONDITION: _SASS_Class.__parse_conditions,
            sp.CONST_NAME__CONDITIONS: _SASS_Class.__parse_conditions,
            sp.CONST_NAME__PROPERTIES: _SASS_Class.__parse_properties,
            sp.CONST_NAME__PREDICATES: _SASS_Class.__parse_predicates,
            sp.CONST_NAME__OPCODES: _SASS_Class.__parse_opcodes,
            sp.CONST_NAME__ENCODING: _SASS_Class.__parse_encoding,
            sp.CONST_NAME__REMAP: _SASS_Class.__parse_remap
        }
        return _SASS_Class.__parse_weird_cash(class_name, cash_str, outer_res, {}, tt)

    @staticmethod
    def __parse_weird_cash(class_name:str, cashs_str:str, outer_res:dict, inner_res:dict, tt:dict):
        cashs_parts = ['$' + i + '$' for i in cashs_str.split('$') if i.strip()]
        cash_count = sum([1 if i=='$' else 0 for i in cashs_str])

        if int(cash_count/2) != cash_count/2:
            raise Exception("Class {0}: Cashes format odd amount of $ detected: {1}".format(class_name, cashs_str))                    
        if not len(cashs_parts) == cash_count/2:
            raise Exception("Class {0}: Cashes format $ count doesn't add up: {1}".format(class_name, cashs_str))

        cashs = []
        for c in cashs_parts:
            pp = c[5:-5].split()
            if not pp[0] in ('?','&'):
                raise Exception("Class {0}: failed to parse cash {1}".format(class_name, c))
            terms = []
            for ind,p in enumerate(pp):
                if ind%2==0:
                    if not p in SASS_Op.CASH_OP:
                        raise Exception("Class {0}: failed to parse cash {1}".format(class_name, c))
                    if ind == 2 and p != '=':
                        raise Exception("Class {0}: failed to parse cash {1}".format(class_name, c))
                    terms.append(TT_Term(ftt.TT_Op.tt(), p))
                else:
                    reg = _SASS_Class.__parse_register(class_name, p, outer_res, inner_res, tt)
                    if len(reg) > 1:
                        raise Exception("Class {0}: failed to parse cash {1}".format(class_name, c))
                    if len(reg[0]) > 1:
                        raise Exception("Class {0}: failed to parse cash {1}".format(class_name, c))
                    terms.extend(reg[0])
                    
            cashs.append(TT_Term(ftt.TT_Cash.tt(), terms))
        
        if not ("".join("".join([str(i) for i in cashs]).split()) == "".join(cashs_str.split()).replace('"','')):
            raise Exception("Class {0}: Cashes format final compare test failed: {1}".format(class_name, cashs_str))

        return cashs

    # def parse_list(lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
    #     entry = []
    #     entries = []
    #     while True:
    #         c = lines_iter.current
    #         if not c: break

    #         if c in ('+', ']'):
    #             ee = "".join(entry).strip()
    #             entry = []
    #             if ee:
    #                 ii = Iterator(ee)
    #                 next(ii)
    #                 entries.extend(_SASS_Class.parse_register(ii, outer_res, inner_res, tt))
    #                 while next(ii):
    #                     if ii.current == '/':
    #                         next(ii)
    #                         entries[-1].add_ext(_SASS_Class.parse_register(ii, outer_res, inner_res, tt))
    #             if c == ']':
    #                 break
    #         else:
    #             entry.append(c)

    #         next(lines_iter, False)
        
    #     return TT_Term(ftt.TT_List.tt(), entries)

    @staticmethod
    def __parse_sqb_term(lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        entry = []
        while True:
            c = next(lines_iter)
            if not c: break

            if c == ']': break
            else: entry.append(c)

        return "".join(entry)

    @staticmethod
    def __parse_default(lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        entry = []
        ee = ''
        while True:
            c = lines_iter.current
            if not c: break

            if c == ')':
                # may contain stuff like "F32.F32"/PRINT
                # simply stripping '"' is not enough => must replace
                ee = "".join(entry).replace('"','')
                break
            else:
                entry.append(c)

            next(lines_iter, False)
        return su.try_convert(ee)

    @staticmethod
    def __parse_extension(class_name:str, ext_str:str, outer_res:dict, inner_res:dict, tt:dict):
        if not ext_str.startswith('/'):
            raise Exception("Class {0}: extension string must start with a slash: {1}".format(class_name, ext_str))
        
        terms = []

        def add_ext(entry):
            ee = "".join(entry)
            if ee and ee in outer_res['REGISTERS']:
                terms.extend([TT_Term(ftt.TT_Ext.tt(), ee)])
            elif ee and ee == '@':
                if not terms:
                    raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
                terms[-1].set_is_at_alias()
            elif ext_str == '/ONLY32:szBD:barReg':
                raise Exception("Class {0}: this appears to be a mistake in sm_86_instructions.txt. Remove the :szBD ({1})".format(class_name, ext_str))                
            else:
                raise Exception("Class {0}: parsing opcode extensions failed: {1}".format(class_name, ext_str))
            return []

        entry = []
        lines_iter = Iterator(ext_str)
        counter = 0
        while True:
            c = next(lines_iter, False)
            if not c: break

            if c == ':':
                if entry:
                    entry = add_ext(entry)
                else:
                    if not terms:
                        raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
                    if not terms[-1].default:
                        raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
            elif c == '(':
                entry = add_ext(entry)
                next(lines_iter)
                default = _SASS_Class.__parse_default(lines_iter, outer_res, inner_res, tt)
                if not default:
                    raise Exception("Class {0}: default value in extension is invalid: {1}".format(class_name, ext_str))
                if not terms:
                    raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
                default_has_print = False
                if not default in outer_res['REGISTERS'][terms[-1].val]:
                    if default.endswith('/PRINT'): # type: ignore
                        default_has_print = True
                        default = default[:(-len('/PRINT'))] # type: ignore
                        if not default in outer_res['REGISTERS'][terms[-1].val]:
                            sp.GLOBAL__ALL_DEFAULTS.append(default)
                    else:
                        sp.GLOBAL__ALL_DEFAULTS.append(default)
                    # raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
                terms[-1].add_default([TT_Term(ftt.TT_Default.tt(), default)])
                if default_has_print: terms[-1].default[0].set_default_has_print()
            elif c == '/':
                ee = "".join(entry).strip()
                entry = []
                if counter > 0 and not ee:
                    raise Exception("Class {0}: extension has no alias: {1}".format(class_name, ext_str))
                if counter > 0 and not terms:
                    raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
                if counter > 0:
                    terms[-1].add_alias(ee)
            else:
                entry.append(c)
                counter += 1

        ee = "".join(entry)
        if not ee:
            raise Exception("Class {0}: extension has no alias: {1}".format(class_name, ext_str))
        if not terms:
            raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
        terms[-1].add_alias(ee)

        if not "".join([str(i) for i in terms]) == "".join(ext_str.replace('"','').split()):
            raise Exception("Class {0}: parsing extensions final benchmark failed: {1}".format(class_name, ext_str))

        return terms


    @staticmethod
    def __parse_register(class_name:str, regs_str:str, outer_res:dict, inner_res:dict, tt:dict):
        # regs_list = [i for i in ["".join(i.strip().split()) for i in entries if i.strip()] if i]
        regs_list = [" ".join(i.strip().split()) for i in regs_str.replace('$(','').replace(')$','').replace('{','').replace('}','').split(',')]
        # benchmark = " ".join(regs_str.replace('{','').replace('}','').replace(',',' ').split())

        rr = []
        def parse_attr(class_name, sqb_term, outer_res, inner_res, tt):
            sterms = sqb_term.split('+')
            temp = []
            for s in sterms:
                temp.extend(_SASS_Class.__parse_register(class_name, s, outer_res, inner_res, tt))
            res = TT_Term(ftt.TT_List.tt(), list(itt.chain.from_iterable(temp)))
            if not "[" + "".join(sqb_term.replace('"','').split()) + "]" == str(res):
                raise Exception("Class {0}: failed to parse attribute {1}".format(class_name, sqb_term))
            return res
        
        def distinguish_funcs(ee:str, r:str):
            ind = r.find(ee)
            ff = r[ind + len(ee)]
            if ff == '(':
                sp.GLOBAL__ALL_FUNCTIONS.append(ee)
                return ftt.TT_Func.tt()
            elif ff == '[':
                sp.GLOBAL__ALL_ACCESSORS.append(ee)
                return ftt.TT_Accessor.tt()
            else:
                raise Exception("Class {0} has invalid func/accs term {1}".format(class_name, ee))

        def add_reg(entry:typing.List, r:str, terms:typing.List):
            ee = "".join(entry)
            if ee and ee in outer_res['REGISTERS']:
                terms.extend([TT_Term(ftt.TT_Reg.tt(), ee)])
            elif ee and ee == '@':
                if not terms:
                    raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
                terms[-1].set_is_at_alias()
            else:
                sp.GLOBAL__ALL_NON_REGS.append(ee)
                tt = distinguish_funcs(ee, r)
                terms.extend([TT_Term(tt, ee)])
                # raise Exception("Class {0}: parsing register failed: {1}".format(class_name, ext_str))
            return []
        
        def finalize(state:int, entry:typing.List, terms:typing.List, rr:typing.List):
            if state != 3:
                ee = "".join(entry)
                # if the last one was something like this:
                # C:srcConst[UImm(5/0*):constBank]*[SImm(17)*:immConstOffset]
                # we can complete that to something like this
                # C:srcConst[UImm(5/0*):constBank]*[SImm(17)*:immConstOffset]/H1H0(H0):bsel
                # we can have a list too, like this:
                # [ Register("RZ"):Ra + UniformRegister:Ra_URc + SImm(24/0)*:Ra_offset ]
                # Because this one may have extensions too, we can't put the parser in state 3
                # => no alias there
                if not (terms[-1].tt == ftt.TT_Accessor.tt() and terms[-1].attr != [] or terms[-1].tt == 'list') and not ee:
                    raise Exception("Class {0}: register has no alias: {1}".format(class_name, r))
                if not terms:
                    raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                if ee:
                    terms[-1].add_alias(ee)

            if len(terms) > 1:
                reg_func = []
                res = []
                ops = []
                for i in terms:
                    if i.tt == ftt.TT_Op.tt():
                        ops.append(i)
                    elif i.tt in (ftt.TT_Func.tt(), ftt.TT_Accessor.tt()):
                        reg_func.append(i)
                    else:
                        res.append(i)
                if len(res) > 1:
                    raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                if len(reg_func) > 1:
                    raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                if ops: res[-1].add_op(ops)
                if reg_func: res[-1].add_access_func(reg_func[0])
                terms = res

            target = r.replace('"','').replace(' ','')
            actual = "".join([str(i) for i in terms])
            if not target.find(actual) >= 0:
                raise Exception("Class {0}: parsing register final benchmark failed: {1}".format(class_name, r))

            rr.append(terms)
            return rr
        
        for r in regs_list:
            lines_iter = Iterator(r)
            state = 0
            entry = []
            terms = []
            new_test = False
            last = ''
            c = ''
            while True:
                last = c
                c = next(lines_iter)
                if not c: break

                if state == 3:
                    raise Exception("Class {0}: register parsing failed: {1}".format(class_name, r))

                if c == ' ':
                    if state != 0 and last != '*': new_test = True
                    continue
                
                if state == 0 and c != '[': state = 1
                if c == '[':
                    if state == 0:
                        if new_test: raise Exception("Class {0}: parser error".format(class_name))
                        if entry:
                            raise Exception("Class {0}: register parsing failed: {1}".format(class_name, r))
                        sqb_term = _SASS_Class.__parse_sqb_term(lines_iter, outer_res, inner_res, tt)
                        if sqb_term in SASS_Op.OP:
                            terms.append(TT_Term(ftt.TT_Op.tt(), sqb_term))
                        else:
                            attr = parse_attr(class_name, sqb_term, outer_res, inner_res, tt)
                            terms.append(attr)
                    else:
                        if new_test: new_test = False

                        # if not entry:
                        #     raise Exception("Class {0}: register parsing failed: {1}".format(class_name, r))                            
                        if entry:
                            entry = add_reg(entry, r, terms)
                            if not terms[-1].tt in (ftt.TT_Func.tt(), ftt.TT_Accessor.tt()):
                                raise Exception("Class {0}: register parsing failed: {1}".format(class_name, r))                            
                        
                        sqb_term = _SASS_Class.__parse_sqb_term(lines_iter, outer_res, inner_res, tt)
                        attr = parse_attr(class_name, sqb_term, outer_res, inner_res, tt)
                        terms[-1].add_attr(attr)

                elif c == ':':
                    if new_test: raise Exception("Class {0}: parser error".format(class_name))
                    if entry:
                        entry = add_reg(entry, r, terms)
                    else:
                        if not terms:
                            raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                        if not terms[-1].default:
                            raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                elif c == '(':
                    if new_test: raise Exception("Class {0}: parser error".format(class_name))
                    entry = add_reg(entry, r, terms)
                    next(lines_iter)
                    default = _SASS_Class.__parse_default(lines_iter, outer_res, inner_res, tt)
                    if not default:
                        raise Exception("Class {0}: default value in extension is invalid: {1}".format(class_name, r))
                    if not terms:
                        raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                    default_has_print = False
                    if terms[-1].val in outer_res['REGISTERS']:
                        if not default in outer_res['REGISTERS'][terms[-1].val]:
                            if default.endswith('/PRINT'): # type: ignore
                                default_has_print = True
                                default = default[:(-len('/PRINT'))] # type: ignore
                                if not default in outer_res['REGISTERS'][terms[-1].val]:
                                    sp.GLOBAL__ALL_DEFAULTS.append(default)
                            # raise Exception("Class {0}: parsing extensions failed: {1}".format(class_name, ext_str))
                        else:
                            sp.GLOBAL__ALL_DEFAULTS.append(default)
                    terms[-1].add_default([TT_Term(ftt.TT_Default.tt(), default)])
                    if default_has_print: terms[-1].default[0].set_default_has_print()
                elif c == '*':
                    if new_test: raise Exception("Class {0}: parser error".format(class_name))
                    if not terms:
                        raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                    if not terms[-1].tt in (ftt.TT_Func.tt(), ftt.TT_Accessor.tt()):
                        raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                    terms[-1].add_star("*")
                elif c == '/':
                    if new_test:
                        new_test = False

                    ee = "".join(entry)
                    # if the last one was something like this:
                    # C:srcConst[UImm(5/0*):constBank]*[SImm(17)*:immConstOffset]
                    # we can complete that to something like this
                    # C:srcConst[UImm(5/0*):constBank]*[SImm(17)*:immConstOffset]/H1H0(H0):bsel
                    # we can have a list too, like this:
                    # [ Register("RZ"):Rb + SImm(20/0)*:Rb_offset ] /EXP_DESC("noexp_desc"):e_desc
                    # this one has an extension but because it's a list, it doesn't have an alias
                    # => no alias there
                    if not (terms[-1].tt == ftt.TT_Accessor.tt() and terms[-1].attr != [] or terms[-1].tt == 'list') and not ee:
                        raise Exception("Class {0}: register has no alias: {1}".format(class_name, r))
                    if not terms:
                        raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                    terms[-1].add_alias(ee)
                    
                    ext_list = [c]
                    while next(lines_iter):
                        ext_list.append(lines_iter.current) # type: ignore
                    ext_str = "".join(ext_list) # type: ignore
                    ext = _SASS_Class.__parse_extension(class_name, ext_str, outer_res, inner_res, tt)
                    if not terms:
                        raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                    # with this if, we try to figure out which types can have extensions
                    #  => so far, it's registers, functions and lists ^^
                    if not terms[-1].tt in (ftt.TT_Reg.tt(), ftt.TT_Func.tt(), ftt.TT_Accessor.tt(), ftt.TT_List.tt()):
                        raise Exception("Class {0}: parsing register failed: {1}".format(class_name, r))
                    terms[-1].add_ext(ext)
                    state = 3
                else:
                    entry.append(c)

                if new_test:
                    rr = finalize(state, entry[:-1], terms, rr)
                    terms = []
                    state = 0
                    new_test = False
                    entry = entry[-1:]

            rr = finalize(state, entry, terms, rr)
            terms = []

        # target = "".join("".join(i.replace('"','') for i in regs_list).split())
        # actual = "".join((str(i) for i in list(itt.chain.from_iterable(rr))))
        # if not target == actual:
        #     raise Exception("Class {0}: register parsing benchmark failed".formaT(class_name))

        return rr

    @staticmethod
    def __parse_opcode(class_name:str, opcode_str:str, outer_res:dict, inner_res:dict, tt:dict):
        opcode_work = opcode_str.replace('{','').replace('}','')
        
        dind = opcode_work.find('/')
        res = TT_Term(ftt.TT_Opcode.tt(), 'Opcode')

        if dind > 0:
            ext = _SASS_Class.__parse_extension(class_name, opcode_work[dind:], outer_res, inner_res, tt)
            res.add_ext(ext)

        if not str(res) == opcode_work.replace('"',''):
            raise Exception("Class {0}: parsing opcode final benchmark failed: {1}".format(class_name, opcode_str))

        return res

    @staticmethod
    def format_to_string(format):
        return "".join([str(i) for i in format])

    @staticmethod
    def __parse_format(class_name:str, lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        nn, s = _SASS_Class.__parse_to_next(lines_iter, tt)
        backup = s

        pind = s.find('PREDICATE')
        has_pred = False
        if pind >= 0:
            s = s[(pind + len('PREDICATE')):]
            has_pred = True
        s = s.replace("'",'').replace('\n',' ')
        # remove multiple whitespaces
        s = ' '.join(s.split())

        # if we have a predicate, separate the first two parts (predicate, opcode) and recombine
        # with a comma, otherwise just the first part (opcode)
        if has_pred:
            s = s.split(' ', 2)
        else:
            s = s.split(' ', 1)

        i0 = Iterator(s[-1])
        state = 0
        counter = 0
        bcounter = 0
        while True:
            c = next(i0, False)
            if not c: break

            if c in ('{','}'):
                counter += 1
                continue 
            #     bcounter += 1

            if state == 0:
                if c == '/': state = 1
                elif c == ' ': # in ('{', '}', ' '):
                    counter += 1 
                    continue
                else: break
            elif state == 1 and c == ' ': state = 2
            elif state == 2:
                if c == ' ': state = 2
                elif not c == '/': break
                else: state = 1

            # if c == '}': 
            #     bcounter -= 1

            if bcounter < 0 or bcounter > 1:
                raise Exception("Class {0}: Preliminary class format simplification opcode extensions isolation failed".format(class_name))
            counter += 1

        if counter > 0:
            op = s[:-1][-1]
            s = s[:-2] + [op + s[-1][:counter].strip()] + [s[-1][counter:]]

        s[-1] = s[-1].strip()
        counter = s[-1].find('$( {')

        if counter > 0:
            s = s[:-1] + [s[-1][:counter].strip()] + [s[-1][counter:]]
            has_regs = True
        elif counter < 0:
            raise Exception('No cash found')
        else:
            has_regs = False

        pred_str = ''
        opcode_str = ''
        regs_str = ''
        cashs_str = ''

        s[-1] = s[-1].strip(';').strip()
        ind = 0
        if has_pred:
            pred_str = s[ind].strip()
            ind += 1
        opcode_str = "".join(s[ind].strip().split())
        ind += 1
        if has_regs:
            regs_str = s[ind].strip()
            ind += 1
        cashs_str = s[ind].strip()

        if not (ind == len(s)-1):
            raise Exception("Class {0}: Preliminary class format simplification index distribution test failed".format(class_name))

        comp = (pred_str + opcode_str + regs_str + cashs_str).replace(' ','') + ';'
        if has_pred: comp = 'PREDICATE' + comp
        benchmark = backup.replace('\n','').replace(' ','').replace("'",'')
        if not (benchmark == comp):
            raise Exception("Class {0}: Preliminary class format simplification benchmark test failed".format(class_name))

        if not (cashs_str.startswith('$( {') and cashs_str.endswith('} )$')):
                raise Exception("Class {0}: Preliminary class format simplification cashs start-end test failed".format(class_name))

        if not opcode_str.startswith('Opcode'):
            raise Exception("Class {0}: Preliminary class format simplification opcode test failed".format(class_name))

        if has_pred and not (pred_str == '@[!]Predicate(PT):Pg' or pred_str == '@[!]UniformPredicate(UPT):UPg'):
            raise Exception("Class {0}: Preliminary class format simplification predicate test failed".format(class_name))            


        if has_pred:
            pred = TT_Term(ftt.TT_Pred.tt(), pred_str)
        else:
            pred = None

        # parse opcode
        opcode = _SASS_Class.__parse_opcode(class_name, opcode_str, outer_res, inner_res, tt)

        if has_regs:
            # parse registers
            rr = _SASS_Class.__parse_register(class_name, regs_str, outer_res, inner_res, tt)
            rr = list(itt.chain.from_iterable(rr))
            if len(rr) == 0:
                raise Exception("Class {0}: Preliminary class format simplification register collection test failed".format(class_name))            
            # dst = rr[0]
            if len(rr) > 0:
                regs = rr
            else:
                regs = []
        else:
            regs = []
            # dst = None

        # parse cashes
        cashs = _SASS_Class.__parse_weird_cash(class_name, cashs_str, outer_res, inner_res, tt)

        ref = []
        if pred: ref.extend(['PREDICATE', pred])
        ref.append(opcode)
        # if dst: ref.append(dst)
        for n,i in enumerate(regs):
            if n > 0: ref.append(',') 
            ref.append(i)
        ref.extend(cashs)

        format_benchmark = benchmark.replace('$(','').replace(')$','').replace('{','').replace('}','').replace('"','').replace(',','')
        format_result = "".join(_SASS_Class.format_to_string(ref).split()).replace('$(','').replace(')$','').replace('{','').replace('}','').replace(',','') + ";"

        if not format_benchmark == format_result:
            raise Exception("Class {0}: Preliminary class format simplification final test failed".format(class_name))

        return nn, TT_Instruction(pred, opcode, regs, cashs)

    @staticmethod
    def __parse_format_alias(class_name:str, lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        nn, s = _SASS_Class.__parse_to_next(lines_iter, tt)

        return nn, [s]

    @staticmethod
    def conditions_to_string(conds):
        return "".join(["".join((i['code'] + "\n " + str(i['expr']) + " :\n " + i['msg'])) for i in conds])

    @staticmethod
    def __parse_conditions(class_name:str, lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        nn, s = _SASS_Class.__parse_to_next(lines_iter, tt)
        cc_types = outer_res['ARCHITECTURE']['CONDITION']['TYPES'].keys()

        entry = []
        c_code = None
        c_expr = None
        c_msg = None
        conds = []
        
        res = []
        aa = s
        cc = 0
        while aa:
            if cc == 0:
                ee = ''
                for ind,e in enumerate(aa):
                    ee += e
                    if ee in cc_types:
                        t = aa[:(ind+1)]
                        res.append(t.strip())
                        aa = aa[(ind+1):].strip()
                        break
            elif cc == 1:
                ee = ''
                if_counter = 0
                for ind,e in enumerate(aa):
                    if e == '?':
                        if_counter += 1
                    if e == ':':
                        if if_counter == 1:
                            if_counter = 0
                        else:
                            t = aa[:(ind+1)]
                            res.append(t.strip().strip(':'))
                            aa = aa[(ind+1):].strip()
                            break
                    ee += e
                # t = aa.split(':', 1)
                # res.append(t[0].strip())
                # aa = t[1].strip()
            elif cc == 2:
                ee = ''
                count = 0
                for ind,e in enumerate(aa):
                    ee += e
                    if e == '"':
                        count += 1
                    if count == 2:
                        t = aa[:(ind+1)]
                        res.append(t.strip())
                        aa = aa[(ind+1):].strip()
                        break
            cc = (cc + 1)%3

        # ll = [x.strip() for x in s.split('\n') if x.strip()]
        ll = res
        l:str
        for ind,l in enumerate(ll):
            if l in cc_types:
                if entry and c_code and c_msg:
                    c_expr = "".join(entry).strip(':')
                    # if ind == len(ll)-3:
                    #     pass
                    entry = []
                    conds.append({
                        'code': c_code,
                        'expr': SASS_Expr(c_expr, outer_res['TABLES'], outer_res['CONSTANTS'], outer_res['REGISTERS'], outer_res['PARAMETERS'], outer_res['TABLES_INV']),
                        'msg': c_msg
                    })
                    c_code = None
                    c_expr = None
                    c_msg = None
                c_code = l
            else:
                if l.startswith('"'):
                    c_msg = l
                else:
                    entry.extend(l)
            
        if entry and c_code and c_msg:
            c_expr = "".join(entry).strip(':')
            entry = []
            conds.append({
                'code': c_code,
                'expr': SASS_Expr(c_expr, outer_res['TABLES'], outer_res['CONSTANTS'], outer_res['REGISTERS'], outer_res['PARAMETERS'], outer_res['TABLES_INV']),
                'msg': c_msg
            })

        benchmark = "".join(s.replace('\n',' ').split()).replace('"','')
        expr_result = "".join(_SASS_Class.conditions_to_string(conds).replace('\n','').split()).replace('"','') #"".join(["".join((i['code'] + str(i['expr']) + ":" + i['msg']).split()) for i in conds])
        if not benchmark == expr_result:
            compare = "".join([((i['code'] + "\n" + str(i['expr']) + ":\n" + i['msg'] + "\n")) for i in conds])
            raise Exception("Class {0}: could not correctly parse CONDITION {1}".format(class_name, s))

        return nn, conds

    @staticmethod
    def properties_to_string(props):
        return "".join([i[0] + (' = ' + str(i[1]) if str(i[1]) != '' else '') + ";\n" for i in props.items()])

    @staticmethod
    def __parse_properties(class_name:str, lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        nn, s = _SASS_Class.__parse_to_next(lines_iter, tt)

        ll = [x.split('=', 1) for x in s.split(';') if x.strip()]

        vals = dict([(x[0].strip(), SASS_Expr(x[1] if len(x) == 2 else '', outer_res['TABLES'], outer_res['CONSTANTS'], outer_res['REGISTERS'], outer_res['PARAMETERS'], outer_res['TABLES_INV'])) for x in ll])

        benchmark = "".join(s.replace('\n','').split())
        expr_result = "".join(_SASS_Class.properties_to_string(vals).replace('\n','').split())
        if not benchmark == expr_result:
            raise Exception("Class {0}: could not correctly parse PROPERTIES {1}".format(class_name, s))

        return nn, vals

    @staticmethod
    def predicates_to_string(preds):
        return "".join([i[0] + ' = ' + str(i[1]) + ";\n" for i in preds.items()])

    @staticmethod
    def __parse_predicates(class_name:str, lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        nn, s = _SASS_Class.__parse_to_next(lines_iter, tt)
        ll = [x.split('=', 1) for x in s.split(';') if x.strip()]

        vals = dict([(x[0].strip(), SASS_Expr(x[1], outer_res['TABLES'], outer_res['CONSTANTS'], outer_res['REGISTERS'], outer_res['PARAMETERS'], outer_res['TABLES_INV'])) for x in ll])

        benchmark = "".join(s.replace('\n','').split()).replace('"','')
        expr_result = "".join(_SASS_Class.predicates_to_string(vals).replace('\n','').split())
        if not benchmark == expr_result:
            raise Exception("Class {0}: could not correctly parse PREDICATES {1}".format(class_name, s))

        return nn, vals

    @staticmethod
    def opcodes_to_string(opcodes):
        pipes = opcodes['pipes']
        opcode = opcodes['opcode']
        return "".join([i['i'] + ' = ' + i['b'] + ";\n" for i in pipes] + [opcode['i'] + ' = ' + opcode['b'] + ";"])

    @staticmethod
    def __parse_opcodes(class_name:str, lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        nn, s = _SASS_Class.__parse_to_next(lines_iter, tt)

        codes = [x.strip().split('=') for x in s.split(';') if x.strip()]
        opcode = None
        instr_code = None
        pipes = []
        for i in codes:
            instr = i[0].strip()
            code = i[1].strip()
            if instr.endswith('_pipe'):
                pipes.append({'i': instr, 'b': code})
            else:
                if opcode:
                    raise Exception('Opcode already assigned with: {0}. Trying to assign {1} too'.format(opcode, instr))
                opcode = {'i': instr, 'b': code}

        if len(pipes) > 1:
            # this one exists on older systems
            pass
        if len(opcode) != 2: # type: ignore
            raise Exception('Class {0}: too many opcodes'.format(class_name))

        res = {'pipes': pipes, 'opcode': opcode, 'set': set([i['i'] for i in pipes] + [opcode['i']])} # type: ignore

        benchmark = "".join(s.replace('\n','').split())
        eval_res = "".join(_SASS_Class.opcodes_to_string(res).replace('\n','').split())
        if not benchmark == eval_res:
            raise Exception("Class {0}: could not correctly parse OPCODES {1}".format(class_name, s))

        return nn, res

    @staticmethod
    def select_pattern(pattern_name:str, outer_res:dict, inner_res:dict, tt:dict):
        encoding = outer_res['FUNIT']['encoding']
        encoding_ind = outer_res['FUNIT']['encoding_ind']
        ccn = [c.strip() for c in pattern_name.split(',') if c.strip()]
        pn = []
        for cn in ccn:
            if cn.startswith('!'):
                pn.append((encoding[cn[1:]], encoding_ind[cn[1:]]))
                # pn.append([1 if x==0 else 0 for x in pp])
            else:
                pn.append((encoding[cn], encoding_ind[cn]))

        return pn

    @staticmethod
    def encoding_to_string(encodings):
        res = []
        for i in encodings:
            rr = i['code_name']
            alias = str(i['alias'])
            star = i['*']
            if not alias.startswith('!'): rr += ' =' + ("* " if star else ' ') + alias
            rr += ";\n"
            res.append(rr)
        return "".join(res)

    @staticmethod
    def __parse_encoding(class_name:str, lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        nn, s = _SASS_Class.__parse_to_next(lines_iter, tt)
        # encoding = outer_res['FUNIT']['encoding']
        # nop_encoding = outer_res['FUNIT']['nop_encoding']
        # issue_slots = outer_res['FUNIT']['ISSUE_SLOTS']
        encoding_width = outer_res['FUNIT']['encoding_width']
        # name = outer_res['FUNIT']['name']

        codes = [[y.strip() for y in x.split('=', 1)] for x in [x.strip('\n') for x in s.split(';')] if x.strip()]

        encodings = []
        for ind,a in enumerate(codes):
            if len(a) == 2:
                # if a[0] == 'Bcbank,Bcaddr':
                #     pass
                # if a[1] == 'Sb_offset SCALE 4':
                #     pass
                p = _SASS_Class.select_pattern(a[0], outer_res, inner_res, tt)
                
                # we may have something like this:
                # BITS_14_53_40_Sc_addr=Sb_offset SCALE 4;
                star = False
                aa = a[1]
                if aa.startswith('*'):
                    star = True
                    aa = aa[1:].strip()
                alias = SASS_Expr(aa, outer_res['TABLES'], outer_res['CONSTANTS'], outer_res['REGISTERS'], outer_res['PARAMETERS'], outer_res['TABLES_INV'])
                if str(alias).replace(' ','') != aa.replace(' ',''):
                    raise Exception("Class {0} failed to parse encodings".format(class_name))
                encodings.append({'alias': alias, 'code_name': a[0], 'code': [pp[0] for pp in p], 'code_ind': [pp[1] for pp in p], '*': star}) # SASS_Encode(p, SASS_Expr(a[1]))
                # if len(aa) == 2:
                #     encodings[a[0]]['ps'] = aa[1]

            elif len(a) == 1:
                p = _SASS_Class.select_pattern(a[0], outer_res, inner_res, tt)
                # p = [['1' if i=='0' else '0' for i in pp] for pp in p]
                alias = SASS_Expr.create_notEnc_expr(a[0])
                encodings.append({'alias': alias, 'code_name': a[0], 'code': [pp[0] for pp in p], 'code_ind': [pp[1] for pp in p], '*': False})
                # patterns.append(p)
                # for pp in p:
                #     frame = [x and int(y) for x,y in zip(frame, pp)]
            else:
                print(a)
                # raise Exception("Encoding {0} has unknown format".format(a))

        # encodings["__frame__"] = ["".join(frame)]
        benchmark = "".join(s.replace('\n','').split())
        eval_res = "".join(_SASS_Class.encoding_to_string(encodings).replace('\n','').split())
        if not benchmark == eval_res:
            raise Exception("Class {0}: could not correctly parse ENCODINGS {1}".format(class_name, s))
        
        return nn, encodings

    @staticmethod
    def __parse_remap(class_name:str, lines_iter:Iterator, outer_res:dict, inner_res:dict, tt:dict):
        nn, s = _SASS_Class.__parse_to_next(lines_iter, tt)

        return nn, [s]

    @staticmethod
    def class_to_str(class_res:dict):
        class_name = class_res[0]
        c = class_res[1]
        is_alternate = c[sp.CONST_NAME__IS_ALTERNATE]
        res = 'CLASS "' + class_name + '"\n'
        if is_alternate:
            res = 'ALTERNATE ' + res

        indent = '   '
        res += indent + str(c[sp.CONST_NAME__FORMAT]).replace('\n','\n' + indent) + '\n'

        format_alias = c[sp.CONST_NAME__FORMAT_ALIAS] if sp.CONST_NAME__FORMAT_ALIAS in c.keys() else None
        if format_alias:
            res += format_alias[0] + "\n"

        conditions = c[sp.CONST_NAME__CONDITIONS] if sp.CONST_NAME__CONDITIONS in c.keys() else []
        if conditions:
            res += sp.CONST_NAME__CONDITIONS + "\n"
            for cond in conditions:
                res += "\n".join([1*indent + cond['code'], 2*indent + str(cond['expr']) + " :", 2*indent + cond['msg'] + ";\n"])

        properties = c[sp.CONST_NAME__PROPERTIES] if sp.CONST_NAME__PROPERTIES in c.keys() else {}
        if properties:
            res += sp.CONST_NAME__PROPERTIES + "\n"
            for p in properties.items():
                prop_str = 1*indent + p[0] + ' = ' + str(p[1]) + ";"
                res += prop_str + "\n"

        predicates = c[sp.CONST_NAME__PREDICATES] if sp.CONST_NAME__PREDICATES in c.keys() else {}
        if predicates:
            res += sp.CONST_NAME__PREDICATES + "\n"
            for p in predicates.items():
                pred_str = 1*indent + p[0] + ' = ' + str(p[1]) + ";"
                res += pred_str + "\n"

        opcodes = c[sp.CONST_NAME__OPCODES] if sp.CONST_NAME__OPCODES in c.keys() else {}
        res += sp.CONST_NAME__OPCODES + '\n'
        res += indent + _SASS_Class.opcodes_to_string(opcodes).replace('\n','\n'+indent) + "\n"

        res += sp.CONST_NAME__ENCODING + '\n'
        res += _SASS_Class.encoding_to_string(c[sp.CONST_NAME__ENCODING])

        remap = c[sp.CONST_NAME__REMAP] if sp.CONST_NAME__REMAP in c.keys() else None
        if remap:
            res += remap[0] + "\n"

        return res

    @staticmethod
    def __parse_class(class_str:str, outer_res:dict):
        local_tt = {
            sp.CONST_NAME__FORMAT: _SASS_Class.__parse_format,
            sp.CONST_NAME__FORMAT_ALIAS: _SASS_Class.__parse_format_alias,
            sp.CONST_NAME__CONDITION: _SASS_Class.__parse_conditions,
            sp.CONST_NAME__CONDITIONS: _SASS_Class.__parse_conditions,
            sp.CONST_NAME__PROPERTIES: _SASS_Class.__parse_properties,
            sp.CONST_NAME__PREDICATES: _SASS_Class.__parse_predicates,
            sp.CONST_NAME__OPCODES: _SASS_Class.__parse_opcodes,
            sp.CONST_NAME__ENCODING: _SASS_Class.__parse_encoding,
            sp.CONST_NAME__REMAP: _SASS_Class.__parse_remap
        }

        lines_iter = Iterator(class_str)
        result = {}
        entry = []
        ff = None
        class_name = ''
        while True:
            c = next(lines_iter, False)
            if not c: break

            if c in (' ', '\n'):
                nn = "".join(entry).strip()
                while nn:
                    entry = []
                    if not class_name:
                        class_name = nn.strip('"')
                        nn = ''
                    elif nn in local_tt.keys():
                        ff = local_tt[nn]
                        if ff:
                            if sp.CONST__VERBOSE and nn == 'FORMAT':
                                print()
                                print(class_name)
                            # if class_name == 'AL2P': # 'bmma_88128_':
                            #     pass
                            # if class_name == 'AL2P': # "bmma_88128_":
                            #     return {class_name : {'SKIP': True}}
                            # if class_name in ('ldcu_ur_offs_') and nn == 'FORMAT':
                            #     pass
                            new_nn, res = ff(class_name, lines_iter, outer_res, result, local_tt)
                            if nn == 'FORMAT':
                                res.class_name = class_name
                                if sp.CONST__VERBOSE:
                                    print(res)
                                if result:
                                    raise Exception("FORMAT is not the first token in {0}".format(class_name))
                                result = {nn: res}
                            else:
                                if nn in result:
                                    result[nn] = su.update_dict(res, result[nn])
                                else:
                                    result = su.update_dict({nn: res}, result)
                            nn = new_nn
                        else:
                            nn = ''
                    else:
                        nn = ''
            else:
                entry.append(c)
            
        return {class_name : result}

    @staticmethod
    def parse(lines_iter:Iterator, local_res:dict, tt:dict, is_alternate:bool):
        entry = []
        class_ll = []
        nn = ''
        while True:
            c = next(lines_iter, False)
            if not c: break

            if c in (' ', '\n'):
                nn = "".join(entry).strip()
                if nn in tt.keys(): break
                elif nn:
                    class_ll.append(nn)
                    class_ll.append(c)
                    entry = []
            else:
                entry.append(c)

        _SASS_Class.c_class_n = "".join(class_ll)
        result = _SASS_Class.__parse_class("".join(class_ll), local_res)
        result[list(result.keys())[0]]['IS_ALTERNATE'] = is_alternate

        return nn, result
    
def parse_cash_str(class_name:str, cash_str:str, outer_res:dict):
    return _SASS_Class.parse_cash_str(class_name, cash_str, outer_res)