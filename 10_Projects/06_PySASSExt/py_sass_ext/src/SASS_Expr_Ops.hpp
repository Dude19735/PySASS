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
#include "SASS_Func.hpp"
#include "TT_Terms.hpp"

namespace SASS {
    /**
     * Define it like this:
     *  - TOperationVal = all the types that parsed tokens can have that are used in expressions
     *  - the operations of every single one of the operation classes converts a TOperationVal to an FArgs
     *  - the TOp_.... structs aret the input pattern that is passed ot the operations functions
     *  - TOperationVAl can be empty if the value is the same as the string
     */
    using TOperationVal = std::variant<std::monostate, FArgInt, FArgBool, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;

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

    class Op_TypeCast : public Op_Function {
        Imm _func;

        FArgs tp_operation(const TOp_List_EncVals& args) {
            if(!args.arg0.size() == 1) throw std::runtime_error("Op_TypeCast requires TOp_List_EncVals with one thing in args.arg0");
            TOperationVal val = args.arg0.at(0);
            if(!std::holds_alternative<SASS_Bits>(val)) throw std::runtime_error("Op_TypeCast requires SASS_Bits as argument!");
            SASS_Bits ival = std::get<SASS_Bits>(val);
            return _func.__call__(ival);
        }
    public:
        Op_TypeCast(CONVERT_FUNC tc_ff) : Op_Function([this](const VArg& p) {
            if(!std::holds_alternative<TOp_List_EncVals>(p)) throw std::runtime_error(err_msg("Op_TypeCast", "TOp_List_EncVals"));
            return tp_operation(std::get<TOp_List_EncVals>(p));
        }, CONVERT_FUNC_to_FUNC(tc_ff)), _func(CONVERT_FUNC_to_Obj(tc_ff)) {}
    };
    class Op_ConstBankAddress2 : public Op_Function {
        FArgs operation_p(const TOp_Var_Var& args) {
            SASS_Bits arg1 = std::get<SASS_Bits>(args.arg0);
            SASS_Bits arg2 = std::get<SASS_Bits>(args.arg1);
            // 1st arg is UImm => unsigned
            if(arg1.signed_()) throw std::runtime_error("Op_ConstBankAddress2 requires arg1 to be unsigned");
            // 2nd arg is SImm => signed
            if(!arg2.signed_()) throw std::runtime_error("Op_ConstBankAddress2 requires arg2 to be signed");
            // we are going to shave off the trailing 2 bits with SCALE => they both have to be 0
            if(SASS_Bits::__eq__(SASS_Bits::__and__(arg2, SASS_Bits(BitVector({1,1}), 3, false)), SASS_Bits::from_int(0)))  throw std::runtime_error("Op_ConstBankAddress2 requires two lsb to be 0"); 

            // With constBankAddress2 we want to assign a full immediate value for an address, like in
            //   [-] C:srcConst[UImm(5/0*):constBank]* [SImm(17)*:immConstOffset]
            // But in the encoding portion
            //   Bcbank,Bcaddr =  ConstBankAddress2(constBank,immConstOffset);
            // Bcaddr usually has 3 fewer bits (immConstOffset has 17 bits, Bcaddr only 14 bits)
            // Since arg2 is an address, it's rightmost bits are 0. It also has to be a signed value.
            //  => apply "SCALE 4" (shave off trailing 2 bits)
            //  => apply "to_unsigned" (shave off leading bit)
            SASS_Bits arg2_a = SASS_Bits::to_unsigned(SASS_Bits::scale(arg2, 4));
            return std::array<SASS_Bits, 2>({arg1, arg2_a});
        }
    public:
        Op_ConstBankAddress2() : Op_Function([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_ConstBankAddress2", "TOp_Var_Var"));
            return operation_p(std::get<TOp_Var_Var>(p));
        }, FUNC::ConstBankAddress2) {}
    };
    class Op_ConstBankAddress0 : public Op_Function {
        FArgs operation_p(const TOp_Var_Var& args) {
            SASS_Bits arg1 = std::get<SASS_Bits>(args.arg0);
            SASS_Bits arg2 = std::get<SASS_Bits>(args.arg1);
            // 1st arg is UImm => unsigned
            if(arg1.signed_()) throw std::runtime_error("Op_ConstBankAddress2 requires arg1 to be unsigned");
            // 2nd arg is SImm => signed
            if(!arg2.signed_()) throw std::runtime_error("Op_ConstBankAddress2 requires arg2 to be signed");
            // we are going to shave off the trailing 2 bits with SCALE => they both have to be 0
            if(SASS_Bits::__eq__(SASS_Bits::__and__(arg2, SASS_Bits(BitVector({1,1}), 3, false)), SASS_Bits::from_int(0)))  throw std::runtime_error("Op_ConstBankAddress2 requires two lsb to be 0"); 

            // With constBankAddress2 we want to assign a full immediate value for an address, like in
            //   [-] C:srcConst[UImm(5/0*):constBank]* [SImm(17)*:immConstOffset]
            // But in the encoding portion
            //   Bcbank,Bcaddr =  ConstBankAddress0(constBank,immConstOffset);
            // Bcaddr usually has 3 fewer bits (immConstOffset has 17 bits, Bcaddr only 16 bits)
            // Since arg2 is an address, it has to be a signed value.
            //  => apply "to_unsigned" (shave off leading bit)
            SASS_Bits arg2_a = SASS_Bits::to_unsigned(arg2);
            return std::array<SASS_Bits, 2>({arg1, arg2_a});
        }
        Op_ConstBankAddress0() : Op_Function([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_ConstBankAddress0", "TOp_Var_Var"));
            return operation_p(std::get<TOp_Var_Var>(p));
        }, FUNC::ConstBankAddress0) {}
    };
    class Op_Identical : public Op_Function {
        FArgs operation_p(const TOp_Var_Var& args) {
            SASS_Bits arg1 = std::get<SASS_Bits>(args.arg0);
            SASS_Bits arg2 = std::get<SASS_Bits>(args.arg1);
            // Dest = IDENTICAL(Rd,Rc); means, we select one of them and assign it to both. Both args must be the same
            if(!SASS_Bits::__eq__(arg1, arg2)) throw std::runtime_error("Op_Identical requires arg1 == arg2");
            return arg1;
        }
    public:
        Op_Identical() : Op_Function([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Identical", "TOp_Var_Var"));
            return operation_p(std::get<TOp_Var_Var>(p));
        }, FUNC::IDENTICAL) {}
    };
    class Op_convertFloatType : public Op_Function {
        // args = [
        //   True, <py_sass_ext._sass_values.SASS_Bits object at 0x752f6244f9f0>,
        //   False, <py_sass_ext._sass_values.SASS_Bits object at 0x752f6244f970>,
        //   <py_sass_ext._sass_values.SASS_Bits object at 0x752f6244f8b0>
        // ]
        FArgs operation_convert(const TOp_List_EncVals& args) {
            const std::vector<TOperationVal> arg0 = args.arg0;
            size_t index = 0;
            size_t len = arg0.size()-1;
            for(size_t i=0; i<len; i+=2){
                TOperationVal p = arg0.at(i);
                if(!std::holds_alternative<bool>(p)) throw std::runtime_error("TOp_List_EncVals in Op_convertFloatType needs booleans for 0, 2, 4, ... indices");
                bool pp = std::get<bool>(p);
                if(pp) {
                    size_t xx = 2*i+1;
                    if(!std::holds_alternative<SASS_Bits>(arg0.at(xx))) throw std::runtime_error("TOp_List_EncVals in Op_convertFloatType needs SASS_Bits for 1, 3, 5, ... indices");
                    return std::get<SASS_Bits>(arg0.at(2*i+1));
                }
            }
        }
    public:
        Op_convertFloatType() : Op_Function([this](const VArg& p) {
            if(!std::holds_alternative<TOp_List_EncVals>(p)) throw std::runtime_error(err_msg("Op_convertFloatType", "TOp_List_EncVals"));
            return operation_convert(std::get<TOp_List_EncVals>(p));
        }, FUNC::convertFloatType) {}
    };

    /// @brief Dual op token classes
    class Op_Minus : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Minus() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Minus", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__sub__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 - arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(static_cast<FArgInt>(arg0) - static_cast<FArgInt>(arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__add__b(SASS_Bits::__neg__(arg1), arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__sub__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__add__b(SASS_Bits::__neg__(arg1), arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__sub__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_Minus requires both arguments to be of the same type, either SASS_Bits or FArgInt");
            }
        }, "-") {}
    };
    class Op_Plus : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Plus() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Plus", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__add__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 + arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(static_cast<FArgInt>(arg0) + static_cast<FArgInt>(arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__add__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__add__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__add__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__add__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_Plus requires both arguments to be of the same type, either SASS_Bits or FArgInt");
            }
        }, "+") {}
    };
    class Op_Mult : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        // using FArgs = std::variant<FArgInt, FArgSASSBits, FArgBool, FArgSet, FArgString, FArgFloat, std::array<SASS_Bits, 2>>;
        Op_Mult() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Mult", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__mul__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 * arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(static_cast<FArgInt>(arg0) * static_cast<FArgInt>(arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__mul__i(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__mul__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__mul__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__mul__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_Mult requires both arguments to be of the same type, either SASS_Bits or FArgInt");
            }
        }, "*") {}
    };
    class Op_Mod : public Op_DualOperator {
        public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Mod() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Mod", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__mod__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 % arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(static_cast<FArgInt>(arg0) % static_cast<FArgInt>(arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_Mod does not support first arg FArgInt and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__mod__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_Mod does not support first arg FArgBool and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__mod__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Invlalid argument types for Op_Mod");
            }
        }, "%") {}
    };
    class Op_Div : public Op_DualOperator {
        public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Div() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Div", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__floordiv__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 / arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(static_cast<FArgInt>(arg0) / static_cast<FArgInt>(arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_Div does not support first arg FArgInt and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__floordiv__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_Div does not support first arg FArgBool and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__floordiv__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Invalid argument types for Op_Div");
            }
        }, "/") {}
    };
    class Op_NotEqual : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_NotEqual() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_NotEqual", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(!SASS_Bits::__ne__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 != arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 != arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(!SASS_Bits::__ne__i(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(!SASS_Bits::__ne__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(!SASS_Bits::__ne__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(!SASS_Bits::__ne__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_NotEqual requires both arguments to be of the same type, either SASS_Bits or FArgInt or FArgBool");
            }
        }, "!=") {}
    };
    class Op_BXor : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_BXor() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_BXor", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__xor__(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 ^ arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 ^ arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__xor__(arg1, SASS_Bits::from_int(arg0)));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__xor__(arg0, SASS_Bits::from_int(arg1)));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__xor__(arg1, SASS_Bits::from_int(arg0)));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__xor__(arg0, SASS_Bits::from_int(arg1)));
            }
            else {
                throw std::runtime_error("Op_BXor requires both arguments to be of the same type, either SASS_Bits or FArgInt or FArgBool");
            }
        }, "^") {}
    };
    class Op_And : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_And() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_And", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_And does not support SASS_Bits arguments");
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 && arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 && arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_And does not support first arg FArgInt and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                throw std::runtime_error("Op_And does not support first arg SASS_Bits and second arg FArgInt");
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_And does not support first arg FArgBool and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                throw std::runtime_error("Op_And does not support first arg SASS_Bits and second arg FArgBool");
            }
            else {
                throw std::runtime_error("Op_And invalid arg types");
            }
        }, "&&") {}
    };
    class Op_SmallerOrEqual : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_SmallerOrEqual() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_SmallerOrEqual", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__le__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 <= arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 <= arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__ge__i(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__le__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__ge__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__le__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_SmallerOrEqual requires both arguments to be of the same type, either SASS_Bits or FArgInt or FArgBool");
            }
        }, "<=") {}
    };
    class Op_Smaller : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Smaller() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Smaller", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__lt__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 < arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 < arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__gt__i(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__lt__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__gt__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__lt__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_Smaller requires both arguments to be of the same type, either SASS_Bits or FArgInt or FArgBool");
            }
        }, "<") {}
    };
    class Op_GreaterOrEqual : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_GreaterOrEqual() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_GreaterOrEqual", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__ge__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 >= arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 >= arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__le__i(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__ge__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__le__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__ge__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_SmallerOrEqual requires both arguments to be of the same type, either SASS_Bits or FArgInt or FArgBool");
            }
        }, "<=") {}
    };
    class Op_Greater : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Greater() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Greater", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__gt__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 > arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 > arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__lt__i(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__gt__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__lt__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__gt__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_Greater requires both arguments to be of the same type, either SASS_Bits or FArgInt or FArgBool");
            }
        }, ">=") {}
    };
    class Op_LShift : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_LShift() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_LShift", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_LShift does not support SASS_Bits as arguments");
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 << arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 << arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_LShift does not support first arg FArgInt and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__lshift__(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_LShift does not support first arg FArgBool and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__lshift__(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_LShift requires both arguments to be of the same type, either SASS_Bits or FArgInt or FArgBool");
            }
        }, "<<") {}
    };
    class Op_RShift : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_RShift() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_RShift", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_RShift does not support SASS_Bits as arguments");
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 >> arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 >> arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_RShift does not support first arg FArgInt and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__rshift__(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_RShift does not support first arg FArgBool and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__rshift__(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_RShift requires both arguments to be of the same type, either SASS_Bits or FArgInt or FArgBool");
            }
        }, ">>") {}
    };
    class Op_BAnd : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_BAnd() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_BAnd", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__and__(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 & arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 & arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_BAnd does not support first arg FArgInt and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__and__(arg0, SASS_Bits::from_int(arg1)));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_BAnd does not support first arg FArgBool and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__and__(arg0, SASS_Bits::from_int(arg1)));
            }
            else {
                throw std::runtime_error("Op_BAnd invalid arg types");
            }
        }, "&") {}
    };
    class Op_Or : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Or() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Or", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_Or does not support SASS_Bits arguments");
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 || arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 || arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_Or does not support first arg FArgInt and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                throw std::runtime_error("Op_Or does not support first arg SASS_Bits and second arg FArgInt");
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_Or does not support first arg FArgBool and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                throw std::runtime_error("Op_Or does not support first arg SASS_Bits and second arg FArgBool");
            }
            else {
                throw std::runtime_error("Op_Or invalid arg types");
            }
        }, "||") {}
    };
    class Op_BOr : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_BOr() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_BOr", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__or__(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 | arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 | arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_BOr does not support first arg FArgInt and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__or__(arg0, SASS_Bits::from_int(arg1)));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                throw std::runtime_error("Op_BOr does not support first arg FArgBool and second arg SASS_Bits");
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__or__(arg0, SASS_Bits::from_int(arg1)));
            }
            else {
                throw std::runtime_error("Op_BOr invalid arg types");
            }
        }, "|") {}
    };
    class Op_Equal : public Op_DualOperator {
    public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Equal() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Equal", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__eq__sb(arg0, arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(arg0 == arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(arg0 == arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__eq__i(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::__eq__i(arg0, arg1));
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs(SASS_Bits::__eq__b(arg1, arg0));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs(SASS_Bits::__eq__b(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_Equal invalid arg types");
            }
        }, "==") {}
    };
    class Op_Implication : public Op_DualOperator {
        public:
        // using TOperationVal = std::variant<std::monostate, FArgInt, FArgString, TT_AtOp, TT_Func, std::set<FArgString>, TT_Reg, TT_ICode, SASS_Bits>;
        Op_Implication() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Implication", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs((!SASS_Bits::__bool__(arg0)) || SASS_Bits::__bool__(arg1));
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<FArgInt>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs((!arg0) || arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<FArgBool>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs((!arg0) || arg1);
            }
            else if(std::holds_alternative<FArgInt>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgInt arg0 = std::get<FArgInt>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs((!arg0) || SASS_Bits::__bool__(arg1));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs((!SASS_Bits::__bool__(arg0)) || arg1);
            }
            else if(std::holds_alternative<FArgBool>(val0) && std::holds_alternative<SASS_Bits>(val1)) {
                FArgBool arg0 = std::get<FArgBool>(val0);
                SASS_Bits arg1 = std::get<SASS_Bits>(val1);
                return FArgs((!arg0) || SASS_Bits::__bool__(arg1));
            }
            else if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgBool>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgBool arg1 = std::get<FArgBool>(val1);
                return FArgs((!SASS_Bits::__bool__(arg0)) || arg1);
            }
            else {
                throw std::runtime_error("Op_Implication invalid arg types");
            }
        }, "->") {}
    };
    class Op_Assign : public Op_DualOperator {
    public:
        Op_Assign() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Void>(p)) throw std::runtime_error(err_msg("Op_Assign", "TOp_Void"));
            return undefined(std::get<TOp_Void>(p));
        }, "=") {}
    };
    class Op_Scale : public Op_DualOperator {
    public:
        Op_Scale() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Scale", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::scale(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_Scale requires first argument to be SASS_Bits or FArgInt and second argument to be FArgInt");
            }
        }, "SCALE") {}
    };
    class Op_Multiply : public Op_DualOperator {
    public:
        Op_Multiply() : Op_DualOperator([this](const VArg& p) {
            if(!std::holds_alternative<TOp_Var_Var>(p)) throw std::runtime_error(err_msg("Op_Multiply", "TOp_Var_Var"));
            TOp_Var_Var args = std::get<TOp_Var_Var>(p);
            TOperationVal val0 = args.arg0;
            TOperationVal val1 = args.arg1;
            if(std::holds_alternative<SASS_Bits>(val0) && std::holds_alternative<FArgInt>(val1)) {
                SASS_Bits arg0 = std::get<SASS_Bits>(val0);
                FArgInt arg1 = std::get<FArgInt>(val1);
                return FArgs(SASS_Bits::multiply(arg0, arg1));
            }
            else {
                throw std::runtime_error("Op_Multiply requires first argument to be SASS_Bits or FArgInt and second argument to be FArgInt");
            }
        }, "MULTIPLY") {}
    };

    class Op_Reduce : public Op_Function {
        Op_DualOperator _reduce_op;
        // A=sp.EXPR_OP_ASSOCIATIV_GROUP_FUNCTION
        // P=sp.EXPR_OP_PRECEDENCE_NR_FUNCTION
        // def operation_reduce(self, args, enc_vals:dict) -> SASS_Bits|int|bool:
        //     if not len(args) >= 2: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        //     if not isinstance(self.reduce_op, Op_DualOperator): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        //     op:Op_DualOperator = self.reduce_op
        //     cur:SASS_Bits|int|bool = args[0]
        //     for p in args[1:]:
        //         cur = op.op(cur, p) # type: ignore
        //     return cur
        // def __init__(self): 
        //     super().__init__(self.operation_reduce, 'Reduce')
        //     self.reduce_op = None
        // def set_reduce_op(self, op): self.reduce_op = op
        // def __str__(self): return Op_Function.__str__(self) + (('(' + str(self.reduce_op) + ')') if self.reduce_op is not None else '')
        FArgs operation_reduce(const TOp_List_EncVals& args) {
            const std::vector<TOperationVal> arg0 = args.arg0;
            if(arg0.size() < 2)  throw std::runtime_error("TOp_List_EncVals in Op_Reduce needs at least two entries!");
            if(!std::holds_alternative<Op_DualOperator>(arg0.at(0))) throw std::runtime_error("TOp_List_EncVals  in Op_Reduce nees the first entry to be an Op_DualOperator!");

            size_t index = 0;
            size_t len = arg0.size()-1;
            TOperationVal cur = std::get<TOperationVal>(arg0.at(0));
            // cur must be one of FArgInt, FArgSASSBits
            if(!std::holds_alternative<FArgInt>(cur) && !std::holds_alternative<FArgSASSBits>(cur)) throw std::runtime_error("TOp_List_EncVals in Op_Reduce needs the first entry to be FArgInt or FArgSASSBits!");
            for(size_t i=1; i<len; i+=2){
                TOperationVal p = arg0.at(i);
                auto res = _reduce_op.op(TOp_Var_Var(cur, p));
                // res must be one of FArgInt, FArgSASSBits
                if(!std::holds_alternative<FArgInt>(res) && !std::holds_alternative<FArgSASSBits>(res)) throw std::runtime_error("Op_Reduce requires the reduce_op to return FArgInt or FArgSASSBits!");
                cur = std::get<TOperationVal>(res);
            }
            // if cur holds FArgInt, convert it to FArgSASSBits with the same bit width as the first argument
            if(std::holds_alternative<FArgInt>(cur)) {
                FArgInt ival = std::get<FArgInt>(cur);
                return FArgs(ival);
            }
            if(std::holds_alternative<FArgSASSBits>(cur)) {
                FArgSASSBits sval = std::get<FArgSASSBits>(cur);
                return FArgs(sval);
            }

            throw std::runtime_error("Op_Reduce failed to reduce the arguments with the given reduce_op!");
        }
        public:
            Op_Reduce() : Op_Function([this](const VArg& p) {
                if(!std::holds_alternative<TOp_List_EncVals>(p)) throw std::runtime_error(err_msg("Op_Reduce", "TOp_List_EncVals"));
                return operation_reduce(std::get<TOp_List_EncVals>(p));
            }, FUNC::Reduce), _reduce_op(Op_Plus()) {}
            void set_reduce(const Op_DualOperator& op) { _reduce_op = op; }
    };
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



    
}