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
    /**
     * Define it like this:
     *  - TOperationVal = all the types that parsed tokens can have that are used in expressions
     *  - the operations of every single one of the operation classes converts a TOperationVal to an FArgs
     *  - the TOp_.... structs aret the input pattern that is passed ot the operations functions
     *  - TOperationVAl can be empty if the value is the same as the string
     */
    using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode>;

    struct TOp_EncVals {
        TEncVals arg0;
    };

    struct TOp_Var_Var {
        TOperationVal arg0;
        TOperationVal arg1;
    };

    struct TOp_Var {
        TOperationVal arg0;
    };

    struct TOp_Var_Var_EncVals {
        TOperationVal arg0;
        TOperationVal arg1;
        TEncVals arg2;
    };

    struct TOp_List_EncVals {
        std::vector<TOperationVal> arg0;
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
        TOperationVal _value;
    protected:
        FArgs undefined(const TOp_Void& x){ throw std::runtime_error("Called undefined operation function!"); }
    public:
        static std::string err_msg(const std::string& obj_name, const std::string& type_name){
            return std::vformat("Invalid Argument: [{}] must be called with [{}]", std::make_format_args(obj_name, type_name));
        }
        static FArgs operations_val_to_fargs(const TOperationVal& val) {
            // std::variant<SASS::FArgInt, SASS::FArgSASSBits, SASS::FArgBool, SASS::FArgSet, SASS::FArgString, SASS::FArgFloat>
            if(std::holds_alternative<FArgInt>(val)) return std::get<FArgInt>(val);
            if(std::holds_alternative<FArgSASSBits>(val)) return std::get<FArgSASSBits>(val);
            if(std::holds_alternative<FArgBool>(val)) return std::get<FArgBool>(val);
            if(std::holds_alternative<FArgSet>(val)) return std::get<FArgSet>(val);
            if(std::holds_alternative<FArgString>(val)) return std::get<FArgString>(val);
            if(std::holds_alternative<FArgFloat>(val)) return std::get<FArgFloat>(val);
            throw std::runtime_error("Invalid type for TOperationsVal to FArgs");
        }
        Op_Base(FOperation op_f, const std::string& op_str) : _next(nullptr), _op_str(op_str), _op_f(op_f), _value(std::monostate()) {}
        Op_Base(FOperation op_f, const std::string& op_str, const TOperationVal& value) : _next(nullptr), _op_str(op_str), _op_f(op_f), _value(value) {}

        std::string __str__() const { return _op_str; }
        std::string signature() const { return std::string(typeid(Op_Base).name()); }
        void set_next(Op_Base* next) { _next = next; }
        Op_Base* get_next() { return _next; }
        bool is_op() { return true; }

        FArgs op(const VArg& args){
            return false;
        }

        virtual TOperationVal value() const { return _value; }
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
        Op_Function(FOperation op_f, const FUNC& func) : Op_Base(op_f, FUNC_to_str(func)) {}
    };
    class Op_Control : public Op_Base {
    public:
        Op_Control(FOperation op_f, const std::string& op_str) : Op_Base(op_f, op_str) {}
    };
    class Op_Operand : public Op_Base {
    public:
        // ['int', 'str', 'TT_AtOp', 'TT_Func', 'set', 'TT_Reg']
        Op_Operand(FOperation op_f, const std::string& name, const TOperationVal& val) : Op_Base(op_f, name, val) {}
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
        FArgs value_operation(const TOp_Var& arg) { 
            return Op_Base::operations_val_to_fargs(arg.arg0);
        }
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
        Op_AtOperand(const std::string& name, const TT_AtOp& term) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_EncVals>(p)) throw std::runtime_error(err_msg("Op_AtOperand", "TOp_EncVals"));
            return operation_at(std::get<TOp_EncVals>(p));
        }, name, term) {}
    };

    /// @brief All the op token classes that have an @
    class Op_AtNot : public Op_AtOperand { public: Op_AtNot(const std::string& name, const TT_AtOp& term) : Op_AtOperand(name, term) {} };
    class Op_AtNegate : public Op_AtOperand { public: Op_AtNegate(const std::string& name, const TT_AtOp& term) : Op_AtOperand(name, term) {} };
    class Op_AtAbs : public Op_AtOperand { public: Op_AtAbs(const std::string& name, const TT_AtOp& term) : Op_AtOperand(name, term) {} };
    class Op_AtSign : public Op_AtOperand { public: Op_AtSign(const std::string& name, const TT_AtOp& term) : Op_AtOperand(name, term) {} };
    class Op_AtInvert : public Op_AtOperand { public: Op_AtInvert(const std::string& name, const TT_AtOp& term) : Op_AtOperand(name, term) {} };
    class Op_Int : public Op_Operand {
        FArgs int_operation(const TOp_Var& arg) {
            if(!std::holds_alternative<FArgInt>) throw std::runtime_error(err_msg("Op_int::int_operation", "TOp_Var_Operand::FArgInt"));
            return std::get<FArgInt>(arg.arg0); 
        } 
    public: 
        Op_Int(const std::string& str_value, int val) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var>(p))  throw std::runtime_error(err_msg("Op_Int", "TOp_Var_Operand"));
            return int_operation(std::get<TOp_Var>(p));
        }, str_value, val) {} 
    };
    class Op_Opcode : public Op_Operand {
        FArgs opcode_operation() {
            TOperationVal val = value();
            if(!std::holds_alternative<TT_ICode>(val)) throw std::runtime_error(err_msg("Op_Opcode::opcode_operation", "TOperationVal::TT_ICode"));
            const TT_ICode& icode = std::get<TT_ICode>(val);
            const auto bb = BitVector(icode.bin_tup().begin(), icode.bin_tup().end());
            return SASS_Bits(bb, bb.size(), false);
        }
    public:
        Op_Opcode(const std::string& name, const TT_ICode& term) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_EncVals>(p))  throw std::runtime_error(err_msg("Op_Opcode", "TOp_EncVals"));
            return opcode_operation();
        }, name, term) {}
    };
    class Op_Alias : public Op_Operand {
        FArgs alias_operation(const TOp_EncVals& enc_vals) {
            TEncVals ev = enc_vals.arg0;
            TOperationVal val = value();
            if(std::holds_alternative<TT_Func>(val)){
                const TT_Func& func =  std::get<TT_Func>(val);
                const std::string func_str = func.__str__();
                if(enc_vals.arg0.find(func_str) == enc_vals.arg0.end()) throw std::runtime_error("Op_Alias: unexpected function name!");
                return enc_vals.arg0.at(func_str);
            }
            else if(std::holds_alternative<TT_Reg>(val)){
                const TT_Reg& reg =  std::get<TT_Reg>(val);
                const std::string reg_str = reg.__str__();
                if(enc_vals.arg0.find(reg_str) == enc_vals.arg0.end()) throw std::runtime_error("Op_Alias: unexpected register name!");
                return enc_vals.arg0.at(reg_str);
            }
            else {
                throw std::runtime_error("Op_Alias: unexpected operand type!");
            }
        }
    public:
        Op_Alias(const std::string& name, TOperationVal term) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_EncVals>(p)) throw std::runtime_error(err_msg("Op_Alias", "TOp_EncVals"));
            return alias_operation(std::get<TOp_EncVals>(p));
        }, name, term) {}
    };
    class Op_Set : public Op_Operand {
        FArgs set_operation(const TOp_EncVals& arg) {
            TOperationVal val = value();
            if(!std::holds_alternative<FArgSet>(val)) throw std::runtime_error("Op_Set requires FArgSet in args");
            return std::get<FArgSet>(val);
        }
    public:
        Op_Set(const std::string& name, FArgSet set) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_EncVals>(p)) throw std::runtime_error(err_msg("Op_Set", "TOp_EncVals"));
            return set_operation(std::get<TOp_EncVals>(p));
        }, name, set) {}
    };
    class Op_Parameter : public Op_Operand {
        FArgs param_operation(const TOp_EncVals& arg) {
            TOperationVal val = value();
            if(!std::holds_alternative<FArgInt>(val)) throw std::runtime_error("Op_Parameter requires FArgInt in args");
            int64_t ival = std::get<FArgInt>(val);
            return SASS_Bits::from_int(ival, 0, 0);
        }
    public:
        Op_Parameter(const std::string& name, FArgInt val) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_EncVals>(p)) throw std::runtime_error(err_msg("Op_Parameter", "TOp_EncVals"));
            return param_operation(std::get<TOp_EncVals>(p));
        }, name, val) {}
    };
    class Op_Constant : public Op_Operand {
        FArgs constant_operation(const TOp_EncVals& arg) {
            TOperationVal val = value();
            if(!std::holds_alternative<FArgInt>(val)) throw std::runtime_error("Op_Constant requires FArgInt in args");
            int64_t ival = std::get<FArgInt>(val);
            return SASS_Bits::from_int(ival, 0, 0);
        }
    public:
        Op_Constant(const std::string& name, FArgInt val) : Op_Operand([this](const VArg& p) {
            if(!std::holds_alternative<TOp_EncVals>(p)) throw std::runtime_error(err_msg("Op_Constant", "TOp_EncVals"));
            return constant_operation(std::get<TOp_EncVals>(p));
        }, name, val) {}
    };
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
// class Op_TypeCast(Op_Function):
//     """If we have a convertFloatType, this one will be the first argument, containing the type things get typecasted to."""
//     A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
//     P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
//     def operation_cast(self, args, enc_vals:dict) -> SASS_Bits:
//         if not len(args) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
//         return self.__TC_FF(args[0])
//     def __init__(self, tc_ff:F16Imm|F32Imm|F64Imm|E6M9Imm|E8M7Imm): 
//         if not (type(tc_ff) in _sass_func.CONVERT_FUNC.values()): raise Exception(sp.CONST__ERROR_UNEXPECTED)
//         super().__init__(self.operation_cast, str(tc_ff))
//         self.__TC_FF:typ.Callable
//         self.__TC_FF = tc_ff
    class Op_TypeCast : public Op_Function {
        FArgs tp_operation(const TOp_List_EncVals& args) {
            if(!args.arg0.size() == 1) throw std::runtime_error("Op_TypeCast requires TOp_List_EncVals with one thing in args.arg0");
            TOperationVal val = args.arg0.at(0);
            int64_t ival = std::get<FArgInt>(val);
            return  SASS_Bits::from_int(ival, 0, 0);
        }
    public:
        Op_TypeCast(CONVERT_FUNC tc_ff) : Op_Function([this](const VArg& p) {
            if(!std::holds_alternative<TOp_List_EncVals>(p)) throw std::runtime_error(err_msg("Op_TypeCast", "TOp_List_EncVals"));
            return tp_operation(std::get<TOp_List_EncVals>(p));
        }, CONVERT_FUNC_to_FUNC(tc_ff)) {}
    };
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

    
}