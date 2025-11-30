#pragma once

#include <set>
#include <string>

namespace SASS {
    class SASS_Op {
    private:
        const std::set<char> AN = std::set<char>({'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'});
        int _state;

    public:
        std::set<std::string> CASH_OP = {"=", "?", "&"};
        std::set<std::string> OP = {"+", "-", "!", "~", "*", "/", "%", ">>", "<<", "<", ">", "<=", ">=", "==", "!=", "&", "^", "|", "&&", "||"};

        SASS_Op() : _state(0) { 
            // self.specials = {
            //     'ConstBankAddress0': Op_ConstBankAddress0,
            //     'ConstBankAddress2': Op_ConstBankAddress2,
            //     'IDENTICAL') Op_Identical,
            //     'convertFloatType': Op_convertFloatType,
            //     'IsEven': Op_IsEven,
            //     'IsOdd': Op_IsOdd,
            //     'Reduce': Op_Reduce
            // }
        }

        bool parse_next(char c, std::vector<Op_Base>& ops, std::stringstream& entry) {
            if(_state == 0) {
                if(c == '(') ops.push_back(Op_LBrace());
                else if(c == '{') ops.push_back(Op_LCBrace());
                else if(c == '}') ops.push_back(Op_RCBrace());
                else if(c == ')') ops.push_back(Op_RBrace());
                else if(c == '+') ops.push_back(Op_Plus());
                else if(c == '-') _state = 14;
                else if(c == '!') _state = 1;
                else if(c == '~') ops.push_back(Op_BNot());
                else if(c == '*') ops.push_back(Op_Mult());
                else if(c == '/') ops.push_back(Op_Div());
                else if(c == '%') _state = 15;
                else if(c == '<') _state = 3;
                else if(c == '>') _state = 6;
                else if(c == '&') _state = 9;
                else if(c == '^') ops.push_back(Op_BXor());
                else if(c == '|') _state = 11;
                else if(c == '=') _state = 13;
                else if(c == '?') ops.push_back(Op_If()); // ? ... => eval bool term
                else if(c == ':') ops.push_back(Op_IfElse()); // ... => if(not last bool term, eval this one
                // else if(c == '@') ops.push_back(Op_At();
                else return c;
            }
            else {
                int state = _state;
                _state = 0;
                if(state == 1) {
                    if(c == '=') 
                        ops.push_back(Op_NotEqual()); // !=,
                    else if(c == '(') {
                        ops.push_back(Op_Not());
                        ops.push_back(Op_LBrace());
                    }
                    else {
                        ops.push_back(Op_Not());
                        entry << c; // !
                        return false;
                    }
                }
                else if(state == 3) {
                    if(c == '<') 
                        ops.push_back(Op_LShift()); // <<,
                    else if(c == '=') 
                        ops.push_back(Op_SmallerOrEqual()); // <=,
                    else if(c == '(') {
                        ops.push_back(Op_Smaller());
                        ops.push_back(Op_LBrace());
                    }
                    else { 
                        ops.push_back(Op_Smaller());
                        entry << c;  // <
                        return false;
                    }
                }
                else if(state == 6) {
                    if(c == '>') 
                        ops.push_back(Op_RShift()); // >>,
                    else if(c == '=') 
                        ops.push_back(Op_GreaterOrEqual()); // >=,
                    else if(c == '(') {
                        ops.push_back(Op_Greater());
                        ops.push_back(Op_LBrace());
                    }
                    else { 
                        ops.push_back(Op_Greater());
                        entry << c; // >
                        return false;
                    }
                }
                else if(state == 9) {
                    if(c == '&') 
                        ops.push_back(Op_And()); // &&
                    else if(c == '(') {
                        ops.push_back(Op_BAnd());
                        ops.push_back(Op_LBrace());
                    }
                    else {
                        ops.push_back(Op_BAnd());
                        entry << c; // &
                        return false;
                    }
                }
                else if(state == 11) {
                    if(c == '|') 
                        ops.push_back(Op_Or()); // ||,
                    else if(c == '(') {
                        ops.push_back(Op_BOr());
                        ops.push_back(Op_LBrace());
                    }
                    else {
                        ops.push_back(Op_BOr());
                        entry << c; // |
                        return false;
                    }
                }
                else if(state == 13) {
                    if(c == '=') 
                        ops.push_back(Op_Equal()); // ==
                    // raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    // if(c == '(') return  [[Op_Assign(), Op_LBrace()], '']
                    // else) { return  [[Op_Assign()], c]
                }
                else if(state == 14) {
                    if(c == '>') 
                        ops.push_back(Op_Implication());
                    else if(c == '(') {
                        ops.push_back(Op_Minus());
                        ops.push_back(Op_LBrace());
                    }
                    else { 
                        ops.push_back(Op_Minus());
                        entry << c;
                        return false;
                    }
                }
                else if(state == 15) {
                    // this one has to be more nuanced:
                    //  this one '%SHADER_TYPE' means, we have a parameter SHADER_TYPE somewhere
                    //  this one '%2' or '% 2' means the actual modulo operator
                    if(c == ' ') 
                        ops.push_back(Op_Mod());
                    else if(c == '(') {
                        ops.push_back(Op_Mod());
                        ops.push_back(Op_LBrace());
                    }
                    else {
                        // vv = su.try_convert(c, convert_hex=True, convert_bin=True)
                        if(AN.find(c) != AN.end()) {
                            entry << '%' << c;
                            return false;
                        }
                        else { 
                            ops.push_back(Op_Mod());
                            entry << c;
                            return false;
                        }
                    }
                }

                return true;
            }
        }

    private:
        void sub_2(const std::string& e, std::vector<std::string>& res) {
                // val = su.try_convert(e, convert_bin=True, convert_hex=True)
                FArgs val = Utils::try_convert(e, false, true, false, false);

                if(std::holds_alternative<TConvertInt>(val))
                    res.push_back(Op_Int(e.strip(), val))
                else if(val in self.specials.keys():
                    res.append(self.specials[val]())
                else if(val in tables.keys():
                    res.append(Op_Table(val, tables[val], tables_inv[val]))
                else if(val.startswith('$'):
                    vv = val[1:]
                    if vv in constants.keys():
                        res.append(Op_Constant(val, constants[vv]))
                    else:
                        raise Exception("Expression evaluation: term {0} starting with '$' does not represent a constant".format(val))
                else if(val.startswith('%'):
                    vv = val[1:]
                    if vv in parameters.keys():
                        res.append(Op_Parameter(vv, parameters[vv]))
                    else:
                        raise Exception("Expression evaluation: term {0} starting with '%' does not represent a parameter".format(val))
                else if(val.startswith('`'):
                    acc,reg = val[1:].split('@')
                    r = su.try_convert(reg)
                    reg = r
                    reg_val = None
                    if not acc in registers.keys():
                        # Some registers are misspelled
                        if acc == 'Chkmode': 
                            print("ERROR: {0} not found in REGISTERS. Rename {0} to {1} in instructions.txt".format('Chkmode', 'ChkMode'))
                        else if(acc == 'RedOP':
                            print("ERROR: {0} not found in REGISTERS. Rename {0} to {1} in instructions.txt".format('RedOP', 'RedOp'))
                        else: raise Exception("Expression evaluation: term {0} starting with '`' does not represent a register".format(val))
                    else if(not reg in registers[acc].keys():
                        # # Some register values are used but never defined. This seems to be an Nvidia bug. Since there is sometimes such a thing as
                        # # INVALIDMUFUOPCODE8 with enum value 8, we set this one to 9
                        # if reg == 'INVALIDMUFUOPCODE9':
                        #     reg_val = 9
                        #     print("WARNING: {0} not found in {1}. Set value to 9 because it seems like the most apparent fix".format(reg, acc))
                        raise Exception("Expression evaluation: term {0} starting with '`' does not represent a register".format(val))

                    if not reg_val: reg_val = registers[acc][reg]
                    res.append(Op_Register(acc, reg, reg_val))
                else if(val in constants.keys():
                    # these are the properties that have constants that don't start with a ($ => giant mess again)
                    res.append(Op_Constant(val, constants[val]))
                else:
                    res.append(Op_Value(val))
        }


        // def split(self, t:str, tables, constants, registers, parameters, tables_inv):

        //     def sub(ee:str, res:typ.List):
        //         ees = ee.split(',')
        //         rem = ''
        //         if len(ees) == 1:
        //             ees = [i for i in ees[0].split(' ',1) if i.strip()]
        //             if len(ees) == 2:
        //                 rem = ees[1]
        //                 ees = [ees[0]]
        //         for ind,e in enumerate(ees):
        //             if ind > 0 and ind < len(ees):
        //                 res.append(Op_Comma())
        //             if e.strip():
        //                 sub_2(e.strip(), res)
        //         return len(ee) - len(rem)

        //     ii = itt.islice(t, 0, None)
        //     res = []
        //     entry = []
        //     cc = 0
        //     stop = False
        //     counter = 0
        //     while True:
        //         if counter > 70000: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        //         c = next(ii, False)
        //         if stop: break
        //         if not c:
        //             # use this to get everything out of the parser that is still in there
        //             c = ' '
        //             stop = True
        //         else: cc += 1
        //         if c == '\n': continue

        //         obj, c = self.parse_next(c)
        //         if c:
        //             entry.append(c)
        //         else: 
        //             if entry: 
        //                 ee = "".join(entry).strip()
        //                 # ee = "".join([i for i in entry if i.strip()]).strip()
        //                 # if ee == 'Sb convertFloatType':
        //                 #     pass
        //                 passed = sub(ee, res)
        //                 entry = []
        //                 if passed != len(ee):
        //                     # if we don't parse the entire thing, for example, if we have something like this
        //                     # DEFINED TABLES_opex_0(batch_t,usched_info)
        //                     # where DEFINED is separate and then we have the table entry, we need to split the expression
        //                     # into two parts => return one with DEFINES and one with the rest
        //                     ll_obj = 0
        //                     if obj:
        //                         ll_obj = sum([len(str(o)) for o in obj])
        //                     cc = cc - len(ee) + passed - ll_obj
        //                     break
        //         if obj:
        //             res.extend(obj)
        //             obj = []
        //         counter += 1

        //     if entry: 
        //         ee = "".join(entry).strip()
        //         passed = sub(ee, res)
        //         if passed != len(ee):
        //             cc = cc - len(ee) + passed
        //     return cc, res
    };
}