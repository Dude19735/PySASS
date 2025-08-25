#pragma once
#include <functional>
#include <set>
#include <string>
#include <string_view>
#include <format>
#include <cmath>
#include <numeric>
#include <iostream>
#include <utility>
#include <type_traits>
#include <tuple>
#include <algorithm>

#include "SASS_Func.hpp"
#include "Utils.hpp"
#include "SASS_Bits.hpp"
#include "SASS_Range.hpp"
#include "Pickle.hpp"

namespace SASS {
    using TLimiter = std::function<TOptionsVec(const TOptionsSet& m_options, int m_max)>;
    using TToLimit = std::unordered_map<std::string, TLimiter>;
    using TValue = std::variant<std::string, int>;

    // ==================================================================================================================
    // = Token Properties ===============================================================================================
    // ==================================================================================================================

    class _TT_HasClassName {
        std::string _class_name;
    public:
        _TT_HasClassName(const std::string& class_name) noexcept : _class_name(class_name) {}
        std::string class_name() const noexcept { return _class_name; }
    };

    class _TT_IsPrintable {
    public:
        virtual std::string __str__() const = 0;
    };

    /// @brief Most basic token class: all of them are one of these too.
    class _TT_Base : public _TT_IsPrintable{
        TValue _value;
    public:
        _TT_Base(const TValue& value) noexcept : _value(value) {}
        TValue value() const noexcept { return _value; }
        std::string __str__() const override { return std::holds_alternative<std::string>(_value) ? std::get<std::string>(_value) : std::to_string(std::get<int>(_value)); }
    };

    class _TT_Domain : public _TT_Base {
    public:
        _TT_Domain(const TValue& value) noexcept : _TT_Base(value) {}
        virtual TDomain get_domain(const TToLimit& to_limit = {}, bool filter_invalid = false) const = 0;
    };

    class _TT_Assemblable : public _TT_Domain, public _TT_HasClassName {
    public:
        _TT_Assemblable(const std::string& class_name, const TValue& value) noexcept : _TT_Domain(value), _TT_HasClassName(class_name) {}
        virtual SASS_Bits sass_from_bits(const BitVector& bits) const = 0;
    };

    class _TT_QueriableAlias { public: virtual std::vector<std::string> get_enc_alias() const noexcept = 0; };

    // ==================================================================================================================
    // = Token Implementations ==========================================================================================
    // ==================================================================================================================

    using TT_Alias_State_0 = std::tuple<std::string>;
    using TT_Alias_State = std::variant<TT_Alias_State_0>;
    constexpr size_t tt_alias_state_size = std::tuple_size<TT_Alias_State_0>::value;
    class TT_Alias : public _TT_Base, public Picklable<TT_Alias, TT_Alias_State, tt_alias_state_size> {
    public:
        TT_Alias(const std::string& alias_name) noexcept : _TT_Base(alias_name) {}
        virtual std::string alias() const noexcept { return std::get<std::string>(value()); };
        const TT_Alias_State get_state(TT_Alias* selfp=nullptr) const override { return std::make_tuple(alias()); }
    };

    class _TT_WithAlias { public: virtual const TT_Alias& alias() const noexcept = 0; };

    /// @brief Base class for all @op classes.
    /// AtOps are the things in front of operands, like the [-] before [-]Register:Ra.
    /// The eval_value for this one is {1,0} where 1==operation_is_there, 0==no_operation
    using TT_AtOp_State_0 = std::tuple<std::string, std::string, std::string>;
    using TT_AtOp_State = std::variant<TT_AtOp_State_0>;
    constexpr size_t tt_atop_state_size = std::tuple_size<TT_AtOp_State_0>::value;
    class TT_AtOp : public _TT_Domain, public _TT_QueriableAlias, public Picklable<TT_AtOp, TT_AtOp_State, tt_atop_state_size> {
        std::string _op_name;
        std::string _reg_alias;
    public:
        TT_AtOp(const std::string& op_name, const std::string& op_sign, const std::string& reg_alias) noexcept : _TT_Domain(op_sign), _op_name(op_name), _reg_alias(reg_alias) {}
        std::string op_name() const noexcept { return _op_name; }
        TDomain get_domain(const TToLimit& to_limit = {}, bool filter_invalid = false) const override { return std::set<SASS_Bits>{SASS_Bits::from_int(0, 1, 0), SASS_Bits::from_int(1, 1, 0)}; }
        std::string alias() const noexcept { return _reg_alias + _op_name; }
        std::string reg_alias() const noexcept { return _reg_alias; }
        std::vector<std::string> get_enc_alias() const noexcept override { return { alias() }; }
        const TT_AtOp_State get_state(TT_AtOp* selfp=nullptr) const override { return std::make_tuple(op_name(), std::get<std::string>(value()), reg_alias()); }
    };
    using TOpsVec = std::vector<TT_AtOp>;
    using TOpsStateVec = std::vector<TT_AtOp_State>;

    /// @brief This one represents [!]
    class TT_OpAtNot : public TT_AtOp { public: 
        TT_OpAtNot(const std::string& reg_alias) noexcept : TT_AtOp("@not", "!", reg_alias) {} 
        TT_OpAtNot(const TT_AtOp& op) noexcept : TT_AtOp(op) {}
    };
    /// @brief This one represents [-]
    class TT_OpAtNegate : public TT_AtOp { public: TT_OpAtNegate(const std::string& reg_alias) noexcept : TT_AtOp("@negate", "-", reg_alias) {} };
    /// @brief This one represents [||]
    class TT_OpAtAbs : public TT_AtOp { public: TT_OpAtAbs(const std::string& reg_alias) noexcept : TT_AtOp("@absolute", "||", reg_alias) {} };
    /// @brief This one represents [&&]
    /// NOTE: @sign exists for SASS_Func only and only on platforms older than and including SM 62! On newer platforns this one is ignored.
    class TT_OpAtSign : public TT_AtOp { public: TT_OpAtSign(const std::string& reg_alias) noexcept : TT_AtOp("@sign", "&&", reg_alias) {} };
    /// @brief This one represents [~]
    class TT_OpAtInvert : public TT_AtOp { public: TT_OpAtInvert(const std::string& reg_alias) noexcept : TT_AtOp("@invert", "~", reg_alias) {} };

    /// @brief Base for all cash token classes
    /// Cash ops are the ones in the scheduling assignments like in
    /// $( { '&' RD:rd '=' UImm(3/0x7):src_rel_sb } )$.
    /// They don't hold a value. They are just there.
    using TT_CashComponent_State_0 = std::tuple<std::string>;
    using TT_CashComponent_State = std::variant<TT_CashComponent_State_0>;
    constexpr size_t tt_cashcomponent_state_size = std::tuple_size<TT_CashComponent_State_0>::value;
    class TT_CashComponent : public _TT_Base, public Picklable<TT_CashComponent, TT_CashComponent_State, tt_cashcomponent_state_size> {
    public: 
        TT_CashComponent(const std::string& cash_value) noexcept : _TT_Base(cash_value) {}
        const TT_CashComponent_State get_state(TT_CashComponent* selfp=nullptr) const override { return std::make_tuple<std::string>(std::get<std::string>(value())); }
    };
    /// @brief This one represents '?'
    class TT_OpCashQuestion : public TT_CashComponent { public: TT_OpCashQuestion() noexcept : TT_CashComponent("?") {} };
    /// @brief This one represents '&'
    class TT_OpCashAnd : public TT_CashComponent { public: TT_OpCashAnd() noexcept : TT_CashComponent("&") {} };
    /// @brief This one represents '='
    class TT_OpCashAssign : public TT_CashComponent { public: TT_OpCashAssign() noexcept : TT_CashComponent("=") {} };

    using TT_Default_State_0 = std::tuple<int, bool, TOptions>;
    using TT_Default_State_1 = std::tuple<std::string, bool, TOptions>;
    using TT_Default_State = std::variant<TT_Default_State_0, TT_Default_State_1>;
    constexpr size_t tt_default_state_size = std::tuple_size<TT_Default_State_0>::value;
    class TT_Default : public _TT_Base, public Picklable<TT_Default, TT_Default_State, tt_default_state_size> {
        bool _has_print;
        TOptions _options;
    protected:
        bool _exists;
    public:
        TT_Default(const TValue& def_name, bool has_print, const TOptions& options) noexcept : _TT_Base(def_name), _has_print(has_print), _options(options), _exists(true) {}
        std::string __str__() const override { return (std::holds_alternative<std::string>(value()) ? std::get<std::string>(value()) : std::to_string(std::get<int>(value()))) + (_has_print ? "/PRINT" : ""); }
        bool exists() const noexcept { return _exists; }
        bool has_print() const noexcept { return _has_print; }
        const TOptions& options() const noexcept { return _options; }
        const TT_Default_State get_state(TT_Default* selfp=nullptr) const override { 
            TValue val = value();
            if(std::holds_alternative<int>(val)) return std::make_tuple(std::get<int>(val), _has_print, _options);
            return std::make_tuple(std::get<std::string>(val), _has_print, _options);
        }
    };

    class TT_NoDefault : protected TT_Default { public: TT_NoDefault() : TT_Default(0, false, {}) { TT_Default::_exists = false; } };

    /// @brief This one represents the default arguments of a function token. For example in UImm(12/0), the TT_FuncArg contains the 12/0.
    using TT_FuncArg_State_0 = std::tuple<int, bool, bool, uint8_t, bool, int, bool, int>;
    using TT_FuncArg_State_1 = std::tuple<std::string, bool, bool, uint8_t, bool, int, bool, int>;
    using TT_FuncArg_State = std::variant<TT_FuncArg_State_0, TT_FuncArg_State_1>;
    constexpr size_t tt_funcarg_state_size = std::tuple_size<TT_FuncArg_State_0>::value;
    class TT_FuncArg : public _TT_Base, public Picklable<TT_FuncArg, TT_FuncArg_State, tt_funcarg_state_size> {
        bool _has_star;
        bool _has_print;
        uint8_t _bit_len;
        bool _has_default;
        int _default_val;
        bool _has_max_val;
        int _max_val;
    public:
        TT_FuncArg() noexcept : _TT_Base(0) {}
        TT_FuncArg(const TValue& arg_val, bool has_star, bool has_print, int bit_len, bool has_default, int default_val, bool has_max_val, int max_val) noexcept : _TT_Base(arg_val), _has_star(has_star), _has_print(has_print), _bit_len(static_cast<uint8_t>(bit_len)), _has_default(has_default), _default_val(default_val), _has_max_val(has_max_val), _max_val(max_val) {}
        void set_max_val(int max_val) noexcept { _max_val = max_val; _has_max_val = true; }
        const TT_FuncArg_State get_state(TT_FuncArg* selfp=nullptr) const override { 
            TValue val = value();
            if(std::holds_alternative<int>(val)) return std::make_tuple(std::get<int>(val), _has_star, _has_print, _bit_len, _has_default, _default_val, _has_max_val, _max_val);
            return std::make_tuple(std::get<std::string>(val), _has_star, _has_print, _bit_len, _has_default, _default_val, _has_max_val, _max_val);
         }

        static int bit_len(const TT_FuncArg& arg) noexcept { return static_cast<int>(arg._bit_len); }
        static bool has_default(const TT_FuncArg& arg) noexcept { return arg._has_default; }
        static int default_val(const TT_FuncArg& arg) noexcept { return arg._default_val; }
        static bool has_max_val(const TT_FuncArg& arg) noexcept { return arg._has_max_val; }
        static uint64_t max_val(const TT_FuncArg& arg) noexcept { return arg._max_val; }
    };

    using TT_Func_State_0 = std::tuple<std::string, std::string, TStrOptionsSet, TT_FuncArg_State, bool, bool, TT_Alias_State>;
    using TT_Func_State = std::variant<TT_Func_State_0>;
    constexpr size_t tt_func_state_size = std::tuple_size<TT_Func_State_0>::value;
    class TT_Func : public _TT_Assemblable, public _TT_WithAlias, public Picklable<TT_Func, TT_Func_State, tt_func_state_size> {
        TStrOptionsSet _options;
        TT_FuncArg _arg_default;
        bool _star;
        bool _is_address;
        TT_Alias _alias;
        Imm _func;

        static Imm _init_func(const TT_Func& func, const std::string& func_name) {
            if(FIXED_BIT_FUNC.find(func_name) != FIXED_BIT_FUNC.end()){
                if(func_name.compare(func_fb_F16Imm) == 0) return F16Imm();
                else if(func_name.compare(func_fb_F32Imm) == 0) return F32Imm();
                else if(func_name.compare(func_fb_F64Imm) == 0) return F64Imm();
                else if(func_name.compare(func_fb_E6M9Imm) == 0) return E6M9Imm();
                else if(func_name.compare(func_fb_E8M7Imm) == 0) return E8M7Imm();
                else throw std::runtime_error("TFunc: unkonwn function name!");
            }
            else {
                if(func_name.compare(func_SImm) == 0) return SImm(TT_FuncArg::bit_len(func._arg_default));
                else if(func_name.compare(func_SSImm) == 0) return SSImm(TT_FuncArg::bit_len(func._arg_default));
                else if(func_name.compare(func_BITSET) == 0) return BITSET(TT_FuncArg::bit_len(func._arg_default));
                else if(func_name.compare(func_RSImm) == 0) return RSImm(TT_FuncArg::bit_len(func._arg_default));
                else if(func_name.compare(func_UImm) == 0) return UImm(TT_FuncArg::bit_len(func._arg_default));
                else throw std::runtime_error("TFunc: unkonwn function name!");
            }
        }
    public:
        TT_Func(const std::string& class_name, const std::string& func_name, const TStrOptionsSet& options, const TT_FuncArg& arg_default, bool star, bool is_address, const TT_Alias& alias)
          : _TT_Assemblable(class_name, func_name), _options(options), _arg_default(arg_default), _star(star), _is_address(is_address), _alias(alias), _func(_init_func(*this, func_name)) {}
        TT_Func(const std::string& class_name, const std::string& func_name, const TStrOptionsSet& options, const TT_FuncArg_State& arg_default, bool star, bool is_address, const TT_Alias_State& alias)
          : _TT_Assemblable(class_name, func_name), _options(options), _arg_default(TT_FuncArg::muh(arg_default)), _star(star), _is_address(is_address), _alias(TT_Alias::muh(alias)), _func(_init_func(*this, func_name)) {}
        std::string __str__() const override { 
            // NOTE: we have the alias here, but we don't print it. Printing the alias is a thing of TT_Param
            return std::get<std::string>(value()) + "(" + _arg_default.__str__() + ")" + (_star ? "*" : "");
        }
        TDomain get_domain(const TToLimit& to_limit = {}, bool filter_invalid = false) const override {
            SASS_Range dom = get<SASS_Range>(_func.get_domain(_is_address, TT_FuncArg::bit_len(_arg_default), TT_FuncArg::has_default(_arg_default), TT_FuncArg::default_val(_arg_default), TT_FuncArg::bit_len(_arg_default)));

            if(SASS_Range::size(dom) <= 5) {
                std::set<SASS_Bits> bb = {};
                auto iter = SASS::SASS_Range::__iter__(dom);
                bool finished = false;
                while(!finished){
                    const auto& val = iter.__next__(finished);
                    if(!finished) bb.insert(val);
                }
                return bb;
            }
            return dom;
        }
        SASS_Bits sass_from_bits(const BitVector& bits) const override {
            int bl = _func.get_bit_len();
            int acc = std::accumulate(bits.begin(), bits.end()-bl, 0);
            if(acc != 0) throw std::runtime_error("TT_Func: expected all non used bits to be 0, but some of them are not!");
            return _func.sass_from_bits(BitVector(bits.end() - bl, bits.end()));
        }
        const TT_Alias& alias() const noexcept override { return _alias; }
        const TT_Func_State get_state(TT_Func* selfp=nullptr) const override { return std::make_tuple(class_name(), std::get<std::string>(value()), _options, _arg_default.get_state(), _star, _is_address, _alias.get_state()); }
    };

    using TT_Reg_State_0 = std::tuple<std::string, int, TT_Default_State, TOptions, TT_Alias_State>;
    using TT_Reg_State_1 = std::tuple<std::string, std::string, TT_Default_State, TOptions, TT_Alias_State>;
    using TT_Reg_State = std::variant<TT_Reg_State_0, TT_Reg_State_1>;
    constexpr size_t tt_reg_state_size = std::tuple_size<TT_Reg_State_0>::value;
    class TT_Reg : public _TT_Assemblable, public _TT_WithAlias, public Picklable<TT_Reg, TT_Reg_State, tt_reg_state_size> {
        TT_Default _default;
        TOptions _options;
        TT_Alias _alias;
        uint8_t _min_bit_len;
    public:
        TT_Reg(const std::string& class_name, const TValue& value, const TT_Default& default_val, const TOptions& options, const TT_Alias& alias) noexcept
          : _TT_Assemblable(class_name, value), _default(default_val), _options(options), _alias(alias), _min_bit_len(Utils::bit_len(Utils::max_option( _options))) {}
        TT_Reg(const std::string& class_name, const TValue& value, const TT_Default_State& default_val, const TOptions& options, const TT_Alias_State& alias) noexcept
          : _TT_Assemblable(class_name, value), _default(TT_Default::muh(default_val)), _options(options), _alias(TT_Alias::muh(alias)), _min_bit_len(Utils::bit_len(Utils::max_option( _options))) {}
        
          std::string __str__() const override {
            std::stringstream res;
            res << (std::holds_alternative<std::string>(value()) ? std::get<std::string>(value()) : std::to_string(std::get<int>(value())));
            if(_default.exists()) res << "(" << _default.__str__() << ")";
            // NOTE: we have the alias here, but we don't print it. Printing the alias is a thing of TT_Param
            return res.str();
        }
        TDomain get_domain(const TToLimit& to_limit = {}, bool filter_invalid = false) const override {
            // if self.value in to_limit.keys():
            std::set<SASS_Bits> res = {};
            auto tl = to_limit.find(std::get<std::string>(value()));
            if(tl != to_limit.end()) {
                if(filter_invalid) throw std::runtime_error("TT_Reg: mixing 'filter_invalid' and 'to_limit' is not allowed!");
                int m_vals = Utils::max_option(_options);
                TOptionsSet vals = Utils::options_to_set(_options);
                TLimiter ll = tl->second;
                TOptionsVec vals2 = ll(vals, m_vals);
                for(const auto x : vals2) res.insert(SASS_Bits::from_int(x, _min_bit_len, 0));
            }
            else {
                TOptionsSet vals2 = Utils::options_to_set(_options, filter_invalid);
                for(const auto x : vals2) res.insert(SASS_Bits::from_int(x, _min_bit_len, 0));
            }
            return res;
        }
        SASS_Bits sass_from_bits(const BitVector& bits) const override {
            int bit_len = static_cast<int>(_min_bit_len);
            if(bit_len < bits.size()) bit_len = static_cast<int>(bits.size());
            return SASS_Bits(bits, bit_len, false);
        }
        const TT_Alias& alias() const noexcept override { return _alias; }
        const TT_Reg_State get_state(TT_Reg* selfp=nullptr) const override { 
            TValue val = value();
            if(std::holds_alternative<int>(val)) return std::make_tuple(class_name(), std::get<int>(val), _default.get_state(), _options, _alias.get_state()); 
            return std::make_tuple(class_name(), std::get<std::string>(val), _default.get_state(), _options, _alias.get_state()); 
        }
    };

    using TT_ICode_State_0 = std::tuple<std::string, IntVector, IntVector>;
    using TT_ICode_State = std::variant<TT_ICode_State_0>;
    constexpr size_t tt_icode_state_size = std::tuple_size<TT_ICode_State_0>::value;
    class TT_ICode : public _TT_Base, public Picklable<TT_ICode, TT_ICode_State, tt_icode_state_size>  {
        std::string _bin_str;
        IntVector _bin_ind;
        IntVector _bin_tup;
    public:
        TT_ICode(const std::string& bin_str, const IntVector& bin_ind, const IntVector& bin_tup) noexcept : _TT_Base("Opcode"), _bin_str(bin_str), _bin_ind(bin_ind), _bin_tup(bin_tup) {}
        IntVector get_opcode_bin() const noexcept { return _bin_tup; }
        const TT_ICode_State get_state(TT_ICode* selfp=nullptr) const override { return std::make_tuple(_bin_str, _bin_ind, _bin_tup); }
    };

    using TT_Pred_State_0 = std::tuple<std::string, TT_Alias_State, TT_Reg_State, TT_AtOp_State>;
    using TT_Pred_State = std::variant<TT_Pred_State_0>;
    constexpr size_t tt_pred_state_size = std::tuple_size<TT_Pred_State_0>::value;
    class TT_Pred : public _TT_HasClassName, public _TT_WithAlias, public _TT_QueriableAlias, public _TT_IsPrintable, public Picklable<TT_Pred, TT_Pred_State, tt_pred_state_size> {
        TT_Alias _alias;
        TT_Reg _reg;
        TT_OpAtNot _op;
    public:
        TT_Pred(const std::string& class_name, const TT_Alias& alias, const TT_Reg& reg, const TT_OpAtNot& op) noexcept
          : _TT_HasClassName(class_name), _alias(alias), _reg(reg), _op(op) {}
        TT_Pred(const std::string& class_name, const TT_Alias_State& alias, const TT_Reg_State& reg, const TT_AtOp_State& op) noexcept
          : _TT_HasClassName(class_name), _alias(TT_Alias::muh(alias)), _reg(TT_Reg::muh(reg)), _op(TT_AtOp::muh(op)) {}
        const TT_Reg& value() const noexcept { return _reg; }
        std::string __str__() const override { return std::string("@[") + _op.__str__() + "]" + _reg.__str__() + ":" + _alias.__str__(); }
        const TT_Alias& alias() const noexcept override { return _alias; }
        std::vector<std::string> get_enc_alias() const noexcept override { return { _alias.alias(), _op.alias() }; }
        const TT_Pred_State get_state(TT_Pred* selfp=nullptr) const override { return std::make_tuple(class_name(), _alias.get_state(), _reg.get_state(), _op.get_state()); }
    };

    using TT_Ext_State_0 = std::tuple<std::string, TT_Alias_State, TT_Reg_State, TT_Default_State, bool>;
    using TT_Ext_State = std::variant<TT_Ext_State_0>;
    constexpr size_t tt_ext_state_size = std::tuple_size<TT_Ext_State_0>::value;
    class TT_Ext : public _TT_HasClassName, public _TT_WithAlias, public _TT_QueriableAlias, public _TT_IsPrintable, public Picklable<TT_Ext, TT_Ext_State, tt_ext_state_size> {
        TT_Alias _alias;
        TT_Reg _reg;
        TT_Default _default;
        bool _is_at_alias;
    public:
        TT_Ext(const std::string& class_name, const TT_Alias& alias, const TT_Reg& reg, const TT_Default& default_val, bool is_at_alias) noexcept 
            : _TT_HasClassName(class_name), _alias(alias), _reg(reg), _default(default_val), _is_at_alias(is_at_alias) {}
        TT_Ext(const std::string& class_name, const TT_Alias_State& alias, const TT_Reg_State& reg, const TT_Default_State& default_val, bool is_at_alias) noexcept 
            : _TT_HasClassName(class_name), _alias(TT_Alias::muh(alias)), _reg(TT_Reg::muh(reg)), _default(TT_Default::muh(default_val)), _is_at_alias(is_at_alias) {}
        std::string __str__() const override { return std::string("/") + _reg.__str__() + (_is_at_alias ? "@" : "") + ":" + _alias.__str__(); }
        const TT_Reg& value() const noexcept { return _reg; }
        const TT_Alias& alias() const noexcept override { return _alias; }
        std::vector<std::string> get_enc_alias() const noexcept override { return { _alias.alias() }; }
        const TT_Ext_State get_state(TT_Ext* selfp=nullptr) const override { return std::make_tuple(class_name(), _alias.get_state(), _reg.get_state(), _default.get_state(), _is_at_alias); }
    };
    using TExtVec = std::vector<TT_Ext>;
    using TExtStateVec = std::vector<TT_Ext_State>;

    using TT_Opcode_State_0 = std::tuple<std::string, TT_Alias_State, TT_ICode_State, TExtStateVec>;
    using TT_Opcode_State = std::variant<TT_Opcode_State_0>;
    constexpr size_t tt_opcode_state_size = std::tuple_size<TT_Opcode_State_0>::value;
    class TT_Opcode : public _TT_HasClassName, public _TT_WithAlias, public _TT_IsPrintable, public _TT_QueriableAlias, public Picklable<TT_Opcode, TT_Opcode_State, tt_opcode_state_size> {
        TT_Alias _alias;
        TT_ICode _icode;
        TExtVec _extensions;

    public:
        TT_Opcode(const std::string& class_name, const TT_Alias& alias, const TT_ICode& icode, const TExtVec& extensions) noexcept 
          : _TT_HasClassName(class_name), _alias(alias), _icode(icode), _extensions(extensions) {}
        TT_Opcode(const std::string& class_name, const TT_Alias_State& alias, const TT_ICode_State& icode, const TExtStateVec& extensions) noexcept 
          : _TT_HasClassName(class_name), _alias(TT_Alias::muh(alias)), _icode(TT_ICode::muh(icode)), _extensions(TT_Ext::from_state_vec(extensions)) {}
        std::string __str__() const override {
            std::stringstream res;
            res << _icode.__str__();
            for(const TT_Ext& ext : _extensions){
                res << " " << ext.__str__();

            }
            return res.str();
        }
        const TT_ICode& value() const noexcept { return _icode; }
        const TT_Alias& alias() const noexcept override { return _alias; }
        IntVector get_opcode_bin() { return _icode.get_opcode_bin(); }
        std::vector<std::string> get_enc_alias() const noexcept override {
            std::vector<std::string> res = { _alias.alias() };
            for(const TT_Ext& ext : _extensions) {
                const auto& v = ext.get_enc_alias();
                res.insert(res.end(), v.begin(), v.end());
            }
            res.shrink_to_fit();
            return res;
        }
        const TT_Opcode_State get_state(TT_Opcode* selfp=nullptr) const override { return std::make_tuple(class_name(), _alias.get_state(), _icode.get_state(), TT_Ext::to_state_vec(_extensions)); }
    };

    // // using TT_Attr_State = std::tuple<>;
    // // class TT_Attr : public _TT_QueriableAlias, public _TT_IsPrintable {
    // // public:
    // //     TT_Attr() noexcept {}
    // //     std::vector<std::string> get_enc_alias() const noexcept override { return {}; }
    // //     std::string __str__() const override { return ""; }

    // //     static const BitVector __getstate__(const TT_Attr& self) { return {}; }
    // //     static void __setstate__(TT_Attr& self, const BitVector& state) { new(&self) TT_Attr(); }
    // // };
    // // using TAttrVec = std::vector<TT_Attr>;

    using TParamFuncReg = std::variant<TT_Reg, TT_Func>;

    using TT_Param_State_0 = std::tuple<std::string, TT_Alias_State, TOpsStateVec, TT_Reg_State, TExtStateVec, bool, bool>;
    using TT_Param_State_1 = std::tuple<std::string, TT_Alias_State, TOpsStateVec, TT_Func_State, TExtStateVec, bool, bool>;
    using TT_Param_State = std::variant<TT_Param_State_0, TT_Param_State_1>;
    constexpr size_t tt_param_state_size = std::tuple_size<TT_Param_State_0>::value;
    class TT_Param : public _TT_HasClassName, public _TT_QueriableAlias, public _TT_IsPrintable, public Picklable<TT_Param, TT_Param_State, tt_param_state_size> {
        TT_Alias _alias;
        TOpsVec _ops;
        TParamFuncReg _value;
        TExtVec _extensions;
        bool _is_at_alias;
        bool _has_attr_star;
    public:
        TT_Param(const std::string& class_name, const TT_Alias& alias, const TOpsVec& ops, const TParamFuncReg& value, const TExtVec& extensions, bool is_at_alias, bool has_attr_star) noexcept 
          : _TT_HasClassName(class_name), _alias(alias), _ops(ops), _value(value), _extensions(extensions), _is_at_alias(is_at_alias), _has_attr_star(has_attr_star) {}
        TT_Param(const std::string& class_name, const TT_Alias_State& alias, const TOpsStateVec& ops, const TT_Reg_State& value, const TExtStateVec& extensions, bool is_at_alias, bool has_attr_star) noexcept 
          : _TT_HasClassName(class_name), _alias(TT_Alias::muh(alias)), _ops(TT_AtOp::from_state_vec(ops)), _value(TT_Reg::muh(value)), _extensions(TT_Ext::from_state_vec(extensions)), _is_at_alias(is_at_alias), _has_attr_star(has_attr_star) {}
        TT_Param(const std::string& class_name, const TT_Alias_State& alias, const TOpsStateVec& ops, const TT_Func_State& value, const TExtStateVec& extensions, bool is_at_alias, bool has_attr_star) noexcept 
          : _TT_HasClassName(class_name), _alias(TT_Alias::muh(alias)), _ops(TT_AtOp::from_state_vec(ops)), _value(TT_Func::muh(value)), _extensions(TT_Ext::from_state_vec(extensions)), _is_at_alias(is_at_alias), _has_attr_star(has_attr_star) {}

          const TParamFuncReg& value() { return _value; }
        const TT_Alias& alias() { return _alias; }
        std::vector<std::string> get_enc_alias() const noexcept override {
            std::vector<std::string> res = { _alias.alias() };
            for(const TT_AtOp& op : _ops) {
                const auto& v = op.get_enc_alias();
                res.insert(res.end(), v.begin(), v.end());
            }
            for(const TT_Ext& ext : _extensions) {
                const auto& v = ext.get_enc_alias();
                res.insert(res.end(), v.begin(), v.end());
            }
            // for(const TT_Attr& attr : _attr) {
            //     const auto& v = attr.get_enc_alias();
            //     res.insert(res.end(), v.begin(), v.end());
            // }
            res.shrink_to_fit();
            return res;
        }
        std::string __str__() const override {
            std::stringstream res;
            for(const TT_AtOp& op : _ops){
                res << "[" << op.__str__() << "]";
            }
            res << (std::holds_alternative<TT_Reg>(_value) ? std::get<TT_Reg>(_value).__str__() : std::get<TT_Func>(_value).__str__());
            if(_is_at_alias) res << "@";
            res << ":" << _alias.alias();
            // for(auto iter = _attr.cbegin(); iter!=_attr.cend(); iter++) {
            //     res << iter->__str__();
            //     if(_has_attr_star && iter!=_attr.cend()-1) res << "*";
            // }
            for(const TT_Ext& ext : _extensions) {
                res << " " << ext.__str__();
            }

            return res.str();
        }
        const TT_Param_State get_state(TT_Param* selfp=nullptr) const override {
            if(std::holds_alternative<TT_Reg>(_value)) return std::make_tuple(class_name(), _alias.get_state(), TT_AtOp::to_state_vec(_ops), std::get<TT_Reg>(_value).get_state(), TT_Ext::to_state_vec(_extensions), _is_at_alias, _has_attr_star);
            return std::make_tuple(class_name(), _alias.get_state(), TT_AtOp::to_state_vec(_ops), std::get<TT_Func>(_value).get_state(), TT_Ext::to_state_vec(_extensions), _is_at_alias, _has_attr_star);
        }
    };
    using TParamVec = std::vector<TT_Param>;
    using TParamStateVec = std::vector<TT_Param_State>;

    using TT_List_State_0 = std::tuple<std::string, TParamStateVec, TExtStateVec>;
    using TT_List_State = std::variant<TT_List_State_0>;
    constexpr size_t tt_list_state_size = std::tuple_size<TT_List_State_0>::value;
    class TT_List : public _TT_HasClassName, public _TT_IsPrintable, public _TT_QueriableAlias, public Picklable<TT_List, TT_List_State, tt_list_state_size> {
        TParamVec _value;
        TExtVec _extensions;
    public:
        TT_List(const std::string& class_name, const TParamVec& params, const TExtVec& extensions) noexcept : _TT_HasClassName(class_name), _value(params), _extensions(extensions) {}
        TT_List(const std::string& class_name, const TParamStateVec& params, const TExtStateVec& extensions) noexcept : _TT_HasClassName(class_name), _value(TT_Param::from_state_vec(params)), _extensions(TT_Ext::from_state_vec(extensions)) {}
        const TParamVec& value() { return _value; }
        std::vector<std::string> get_enc_alias() const noexcept override {
            std::vector<std::string> res;
            for(const TT_Param& param : _value) {
                const auto& v = param.get_enc_alias();
                res.insert(res.end(), v.begin(), v.end());
            }
            for(const TT_Ext& ext : _extensions) {
                const auto& v = ext.get_enc_alias();
                res.insert(res.end(), v.begin(), v.end());
            }

            res.shrink_to_fit();
            return res;
        }
        std::string __str__() const override {
            std::stringstream res;
            res << "[";
            for(auto iter = _value.cbegin(); iter!=_value.cend(); iter++) {
                res << iter->__str__();
                if(iter!=_value.cend()-1) res << "+";
            }
            res << "]";
            for(const TT_Ext& ext : _extensions) {
                res << " " << ext.__str__();
            }

            return res.str();
        }
        const TT_List_State get_state(TT_List* selfp=nullptr) const override { return std::make_tuple(class_name(), TT_Param::to_state_vec(_value), TT_Ext::to_state_vec(_extensions)); }
    };
    using TListVec = std::vector<TT_List>;
    using TListStateVec = std::vector<TT_List_State>;

    using TT_AttrParam_State_0 = std::tuple<TT_Param_State, TListStateVec>;
    using TT_AttrParam_State = std::variant<std::tuple<TT_Param_State, TListStateVec>>;
    constexpr size_t tt_attrparam_state_size = std::tuple_size<TT_AttrParam_State_0>::value;
    class TT_AttrParam : public TT_Param, public Picklable<TT_AttrParam, TT_AttrParam_State, tt_attrparam_state_size> {
        TListVec _attr;
    public:
        TT_AttrParam(const std::string& class_name, const TT_Alias& alias, const TOpsVec& ops, const TParamFuncReg& value, const TListVec& attr, const TExtVec& extensions, bool is_at_alias, bool has_attr_star) noexcept 
          : TT_Param(class_name, alias, ops, value, extensions, is_at_alias, has_attr_star), _attr(attr) {}
        TT_AttrParam(const TT_Param_State& param, const TListStateVec& attr) noexcept 
          : TT_Param(TT_Param::muh(param)), _attr(TT_List::from_state_vec(attr)) {}

        const TT_AttrParam_State get_state(TT_AttrParam* selfp=nullptr) const override {
            return std::make_tuple(TT_Param::get_state(), TT_List::to_state_vec(_attr));
        }
    };

    // using TCashVal = std::variant<TT_CashComponent, TT_Param>;
    // using TCashVec = std::vector<TCashVal>;
    // using TT_Cash_State_0 = std::tuple<std::string, std::vector<TCashVec>, bool>;
    // using TT_Cash_State = std::variant<TCashVal_0>
    // constexpr size_t tt_cash_state_size = std::tuple_size<TT_Cash_State_0>::value;
    // class TT_Cash : public _TT_HasClassName, public _TT_IsPrintable, public _TT_QueriableAlias, public Picklable<TT_Cash, TT_Cash_State, tt_cash_state_size> {
    //     TCashVec _values;
    //     bool _added_later;
    // public:
    //     TT_Cash(const std::string& class_name, const TCashVec cash_vals, bool added_later=false) noexcept 
    //       : _TT_HasClassName(class_name), _values(cash_vals), _added_later(added_later) {}
    //     std::vector<std::string> get_enc_alias() const noexcept override {
    //         std::vector<std::string> res;
    //         for(const TCashVal& val : _values){
    //             if(std::holds_alternative<TT_Param>(val)) {
    //                 const auto& v = std::get<TT_Param>(val).get_enc_alias();
    //                 res.insert(res.begin(), v.begin(), v.end());
    //             }
    //         }
    //         return res;
    //     }
    //     const TCashVec& values() { return _values; }
    //     std::string __str__() const override {
    //         std::stringstream res;
    //         res << "$( { ";
    //         for(const TCashVal& val : _values){
    //             if(std::holds_alternative<TT_OpCashAnd>(val)) res << std::get<TT_OpCashAnd>(val).__str__();
    //             else if(std::holds_alternative<TT_OpCashQuestion>(val)) res << std::get<TT_OpCashQuestion>(val).__str__();
    //             else if(std::holds_alternative<TT_OpCashAssign>(val)) res << std::get<TT_OpCashAssign>(val).__str__();
    //             else if(std::holds_alternative<TT_Param>(val)) res << std::get<TT_Param>(val).__str__();
    //         }
    //         res << " } )$";
    //         return res.str();
    //     }
    //     const TT_Cash_State get_state(TT_Cash* selfp=nullptr) {
    //         return std::make_tuple(class_name(),  _values )
    //     }
    // };

    // // using TT_Test_State = std::tuple<TValue, TT_Alias_State, TParamFuncRegState, BitVector>;
    // // constexpr size_t tt_test_state_size = std::tuple_size<TT_Test_State>::value;
    // // class TT_Test : public _TT_Base {
    // //     TT_Alias _alias;
    // //     TParamFuncReg _fr;
    // //     TOpsVec _ops;
    // // public:
    // //     TT_Test(const TValue& value, const TT_Alias& alias, const TT_Reg& reg, const TOpsVec& ops) noexcept : _TT_Base(value), _alias(alias), _fr(reg), _ops(ops) {}
    // //     TT_Test(const TValue& value, const TT_Alias& alias, const TT_Func& func, const TOpsVec& ops) noexcept : _TT_Base(value), _alias(alias), _fr(func), _ops(ops) {}
    // //     const TT_Alias& alias() const { return _alias; };
    // //     std::string __str__() const override {
    // //         std::stringstream res;
    // //         for(const TT_AtOp& op : _ops) {
    // //             res << "[" << op.__str__() << "]";
    // //         }
    // //         res << "test[";
    // //         const TValue val = value();
    // //         if(std::holds_alternative<std::string>(val)){
    // //             res << "str(" << std::get<std::string>(val) << ")";
    // //         }
    // //         else {
    // //             res << "int(" << std::get<int>(val) << ")";
    // //         }
    // //         res << ":" << _alias.__str__() << ", ";
            
    // //         if(std::holds_alternative<TT_Reg>(_fr)){
    // //             res << std::get<TT_Reg>(_fr).__str__();
    // //         }
    // //         else {
    // //             res << std::get<TT_Func>(_fr).__str__();
    // //         }
    // //         res << "]";
    // //         return res.str();
    // //     }
    // //     static const auto __getstate__(const TT_Test& self) { 
    // //         return std::make_tuple(self.value(), TT_Alias::__getstate__(self._alias), 
    // //                std::holds_alternative<TT_Reg>(self._fr) 
    // //                     ? TParamFuncRegState{TT_Reg::__getstate__(std::get<TT_Reg>(self._fr))} 
    // //                     : TParamFuncRegState{TT_Func::__getstate__(std::get<TT_Func>(self._fr))}, 
    // //                BitVector{}); }
    // //     static void __setstate__(TT_Test& self, const TT_Test_State& state) {
    // //         if(std::holds_alternative<TT_Reg_State>(std::get<2>(state))) new(&self) TT_Test(std::get<0>(state), TT_Alias(std::get<1>(state)), TT_Reg(std::get<TT_Reg_State>(std::get<2>(state))), {}); 
    // //         else new(&self) TT_Test(std::get<0>(state), TT_Alias(std::get<1>(state)), TT_Func(std::get<TT_Func_State>(std::get<2>(state))), {});
    // //     }
    // // };
}