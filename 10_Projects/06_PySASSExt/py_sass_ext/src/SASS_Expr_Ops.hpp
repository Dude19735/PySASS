#pragma once
#include <set>
#include <vector>
#include <string>
#include <sstream>
#include <unordered_map>
#include <functional>
#include <variant>
#include <format>

#include "SASS_Bits.hpp"
#include "Utils.hpp"
#include "TT_Terms.hpp"

namespace SASS {
    struct TOp_EncVals {
        TEncVals arg0;
    };

    struct TOp_Var_Var {
        FArgs arg0;
        FArgs arg1;
    };

    struct TOp_Var {
        FArgs arg0;
    };

    struct TOp_Var_Var_EncVals {
        FArgs arg0;
        FArgs arg1;
        TEncVals arg2;
    };

    struct TOp_List_EncVals {
        std::vector<FArgs> arg0;
        TEncVals arg1;
    };

    struct TOp_Void {};

    using VArg = std::variant<TOp_EncVals, TOp_Var_Var, TOp_Var, TOp_Var_Var_EncVals, TOp_List_EncVals, TOp_Void>;
    using FOperation = std::function<FArgs(const VArg&)>;

    /// @brief Most basic op token class
    class Op_Base {
        Op_Base* _next;
        std::string _op_str;
        FOperation _op_f;
    protected:
        FArgs undefined(const TOp_Void& x){ throw std::runtime_error("Called undefined operation function!"); }
    public:
        static std::string err_msg(const std::string& obj_name, const std::string& type_name){
            return std::vformat("Invalid Argument: [{}] must be called with [{}]", std::make_format_args(obj_name, type_name));
        }
        Op_Base(FOperation op_f, const std::string& op_str) : _next(nullptr), _op_str(op_str), _op_f(op_f) {}

        std::string __str__() const { return _op_str; }
        std::string signature() const { return std::string(typeid(Op_Base).name()); }
        void set_next(Op_Base* next) { _next = next; }
        Op_Base* get_next() { return _next; }
        bool is_op() { return true; }

        FArgs op(const VArg& args){
            return false;
        }

        virtual FArgs value() const { throw std::runtime_error("UNDEFINED"); }
    };

    /// @brief Abstract op token classes
    class Op_DualOperator : public Op_Base {
    public:
        Op_DualOperator(FOperation op_f, const std::string& op_str) : Op_Base(op_f, op_str) {}
    };
    class Op_UnaryOperator : public Op_Base {
    public:
        Op_UnaryOperator(FOperation op_f, const std::string& op_str) : Op_Base(op_f, op_str) {}
    };
    class Op_Function : public Op_Base {
    public:
        Op_Function(FOperation op_f, const std::string& op_str) : Op_Base(op_f, op_str) {}
    };
    class Op_Control : public Op_Base {
    public:
        Op_Control(FOperation op_f, const std::string& op_str) : Op_Base(op_f, op_str) {}
    };
    class Op_Operand : public Op_Base {
        FArgs _value;
    public:
        Op_Operand(FOperation op_f, const std::string& name, const FArgs& value) : Op_Base(op_f, name), _value(value) {}
        FArgs value() const override { return _value; }
    };
    class Op_ParamSplit : public Op_Base {
    public:
        Op_ParamSplit() : Op_Base([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var>(p)) throw std::runtime_error(err_msg("Op_ParamSplit", "TOp_Void"));
            return undefined(std::get<TOp_Void>(p));
        }, "") {}
    };

    /// @brief Container for everything op token class
    class Op_Value : public Op_Base {
        FArgs value_operation(const TOp_Var& arg) { return arg.arg0; }
    public:
        Op_Value() : Op_Base([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var>(p)) throw std::runtime_error(err_msg("Op_Value", "TOp_Var"));
            return value_operation(std::get<TOp_Var>(p));
        }, "") {}
    };

    /// @brief Structural op token classes
    class Op_None : public Op_Base {
    public:
        Op_None() : Op_Base([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var>(p)) throw std::runtime_error(err_msg("Op_None", "TOp_Void"));
            return undefined(std::get<TOp_Void>(p));
        }, "") {}
    };
    class Op_LCBrace : public Op_Base {
    public:
        Op_LCBrace() : Op_Base([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var>(p)) throw std::runtime_error(err_msg("Op_LCBrace", "TOp_Void"));
            return undefined(std::get<TOp_Void>(p));
        }, "") {}
    };
    class Op_RCBrace : public Op_Base {
    public:
        Op_RCBrace() : Op_Base([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var>(p)) throw std::runtime_error(err_msg("Op_RCBrace", "TOp_Void"));
            return undefined(std::get<TOp_Void>(p));
        }, "") {}
    };
    class Op_RBrace : public Op_Base {
    public:
        Op_RBrace() : Op_Base([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var>(p)) throw std::runtime_error(err_msg("Op_RBrace", "TOp_Void"));
            return undefined(std::get<TOp_Void>(p));
        }, "") {}
    };
    class Op_LBrace : public Op_Base {
    public:
        Op_LBrace() : Op_Base([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var>(p)) throw std::runtime_error(err_msg("Op_LBrace", "TOp_Void"));
            return undefined(std::get<TOp_Void>(p));
        }, "") {}
    };

    /// @brief Splitting op token class
    class Op_Comma : public Op_ParamSplit {
    public:
        Op_Comma() : Op_ParamSplit() {}
    };
    
    /// @brief Rather generalized op token classes
    class Op_AtOperand : public Op_Operand {
        FArgs operation_at(const TOp_EncVals& arg) { 
            return arg.arg0.at(__str__()); 
        }
    public:
        // Function, 
        Op_AtOperand(const std::string& name, const TTerm& term) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_EncVals>(p)) throw std::runtime_error(err_msg("Op_AtOperand", "TOp_EncVals"));
            return operation_at(std::get<TOp_EncVals>(p));
        }, name, term) {}
    };

    /// @brief All the op token classes that have an @
    class Op_AtNot : public Op_AtOperand { public: Op_AtNot(const std::string& name, const TTerm& term) : Op_AtOperand(name, term) {} };
    class Op_AtNegate : public Op_AtOperand { public: Op_AtNegate(const std::string& name, const TTerm& term) : Op_AtOperand(name, term) {} };
    class Op_AtAbs : public Op_AtOperand { public: Op_AtAbs(const std::string& name, const TTerm& term) : Op_AtOperand(name, term) {} };
    class Op_AtSign : public Op_AtOperand { public: Op_AtSign(const std::string& name, const TTerm& term) : Op_AtOperand(name, term) {} };
    class Op_AtInvert : public Op_AtOperand { public: Op_AtInvert(const std::string& name, const TTerm& term) : Op_AtOperand(name, term) {} };

    class Op_Int : public Op_Operand {};
    class Op_Opcode : public Op_Base {};
    class Op_Alias : public Op_Operand {};
    class Op_Set : public Op_Operand {};
    class Op_Parameter : public Op_Operand {};
    class Op_Constant : public Op_Operand {};
    class Op_Register : public Op_Operand {
        std::string _parent_register;
        std::string _register;
        FArgs operation_register(const TOp_EncVals& arg) {
            if(!std::holds_alternative<int>(value())) throw std::runtime_error("Op_Register: expected value to be integer!");
            int val = std::get<int>(value());
            return SASS_Bits::from_int(val, 0, 0); 
        }
        static int _process(const std::string& parent, const std::variant<int, std::set<int>>& value) {
            if(std::holds_alternative<std::set<int>>(value)) {
                const std::set<int>& v = std::get<std::set<int>>(value);
                if(v.size() != 1) {
                    if(parent.compare("SIDL_NAMES") != 0) throw std::runtime_error("Op_Register: unexpected register name. Expected is SIDL_NAMES!");
                    return Utils::min_of_set(v);
                }
                else if(v.size() == 1) { 
                    return *v.begin(); 
                }
                else throw std::runtime_error("Op_Register has invalid value type and shape!");
            }
            else {
                return get<int>(value);
            }
            return 0;
        }
    public:
        Op_Register(const std::string& parent, const std::string& name, const std::variant<int, std::set<int>>& value) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_EncVals>(p)) throw std::runtime_error(err_msg("Op_Register", "TOp_EncVals"));
            return operation_register(std::get<TOp_EncVals>(p));
        }, name, Op_Register::_process(parent, value)), _parent_register(parent), _register(name) {}
        std::string parent_register() const { return _parent_register; }
        std::string register_() const { return _register; }
        std::string __str__() const { return std::string("`") + Op_Operand::__str__(); }
    };

    /// @brief All function-like op token classes
    class Op_TypeCast : public Op_Function {};
    class Op_ConstBankAddress2 : public Op_Function {};
    class Op_ConstBankAddress0 : public Op_Function {};
    class Op_Identical : public Op_Function {};
    class Op_convertFloatType : public Op_Function {};
    class Op_Reduce : public Op_Function {};
    class Op_Table : public Op_Function {};
    class Op_Identical : public Op_Function {};
    class Op_Index : public Op_Function {};
    class Op_IsEven : public Op_Function {};
    class Op_IsOdd : public Op_Function {};

    /// @brief Control structure token class
    class Op_If : public Op_Control {};
    class Op_IfElse : public Op_Control {};

    /// @brief Unary op token classes
    class Op_Not : public Op_UnaryOperator {};
    class Op_BNot : public Op_UnaryOperator {};
    class Op_Defined : public Op_UnaryOperator {};

    /// @brief Dual op token classes
    class Op_Minus : public Op_DualOperator {};
    class Op_Plus : public Op_DualOperator {};
    class Op_Mult : public Op_DualOperator {};
    class Op_Mod : public Op_DualOperator {};
    class Op_Div : public Op_DualOperator {};
    class Op_NotEqual : public Op_DualOperator {};
    class Op_BXor : public Op_DualOperator {};
    class Op_And : public Op_DualOperator {};
    class Op_SmallerOrEqual : public Op_DualOperator {};
    class Op_Smaller : public Op_DualOperator {};
    class Op_GreaterOrEqual : public Op_DualOperator {};
    class Op_Greater : public Op_DualOperator {};
    class Op_LShift : public Op_DualOperator {};
    class Op_RShift : public Op_DualOperator {};
    class Op_BAnd : public Op_DualOperator {};
    class Op_Or : public Op_DualOperator {};
    class Op_BOr : public Op_DualOperator {};
    class Op_Equal : public Op_DualOperator {};
    class Op_Implication : public Op_DualOperator {};
    class Op_Assign : public Op_DualOperator {};
    class Op_Scale : public Op_DualOperator {};
    class Op_Multiply : public Op_DualOperator {};

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
                TConvertVariant val = Utils::try_convert(e, false, true, false, false);

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