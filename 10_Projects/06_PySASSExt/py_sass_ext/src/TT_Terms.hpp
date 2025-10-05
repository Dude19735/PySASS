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

    // ==================================================================================================================
    // = Token Properties ===============================================================================================
    // ==================================================================================================================

    class _TT_IsPrintable { public: virtual std::string __str__() const = 0; };
    class _TT_QueriableAlias { public: virtual std::vector<std::string> get_enc_alias() const noexcept = 0; };

    /// @brief Most basic token class: all of them are one of these too.
    class _TT_Base : public _TT_IsPrintable{
        TValue _value;
    public:
        _TT_Base(const TValue& value) noexcept : _value(value) {}
        _TT_Base(const _TT_Base& other) noexcept : _value(other._value) {}
        _TT_Base(_TT_Base&& other) noexcept : _value(std::move(other._value)) {}
        _TT_Base& operator=(const _TT_Base& other) noexcept { if(this == &other) return *this; _value = other._value; return *this; }
        _TT_Base& operator=(_TT_Base&& other) noexcept { if(this == &other) return *this; _value = std::move(other._value); return *this; }
        bool operator==(const _TT_Base& other) const noexcept { if(this == &other) return true; return _value == other._value; }
        TValue value() const noexcept { return _value; }
        std::string __str__() const override { return std::holds_alternative<std::string>(_value) ? std::get<std::string>(_value) : std::to_string(std::get<int>(_value)); }
    };

    class _TT_Domain : public _TT_Base {
    public:
        _TT_Domain(const TValue& value) noexcept : _TT_Base(value) {}
        _TT_Domain(const _TT_Domain& other) noexcept : _TT_Base(other) {}
        _TT_Domain(_TT_Domain&& other) noexcept : _TT_Base(other) {}
        _TT_Domain& operator=(const _TT_Domain& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); return *this; }
        _TT_Domain& operator=(_TT_Domain&& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); return *this; }
        bool operator==(const _TT_Domain& other) const noexcept { if(this == &other) return true; return _TT_Base::operator==(other); }
        virtual TDomain get_domain(const TToLimit& to_limit = {}, bool filter_invalid = false) const = 0;
    };

    class _TT_Assemblable : public _TT_Domain {
    public:
        _TT_Assemblable(const TValue& value) noexcept : _TT_Domain(value) {}
        _TT_Assemblable(const _TT_Assemblable& other) noexcept : _TT_Domain(other) {}
        _TT_Assemblable(_TT_Assemblable&& other) noexcept : _TT_Domain(other) {}
        _TT_Assemblable& operator=(const _TT_Assemblable& other)  noexcept{ if(this == &other) return *this; _TT_Domain::operator=(other); return *this;}
        _TT_Assemblable& operator=(_TT_Assemblable&& other) noexcept { if(this == &other) return *this; _TT_Domain::operator=(other); return *this;}
        bool operator==(const _TT_Assemblable& other) const noexcept { if(this == &other) return true; return (_TT_Domain::operator==(other)); }
        virtual SASS_Bits sass_from_bits(const BitVector& bits) const = 0;
    };

    // ==================================================================================================================
    // = Token Implementations ==========================================================================================
    // ==================================================================================================================

    using TT_Alias_State_0 = std::tuple<std::string>;
    using TT_Alias_State = std::variant<TT_Alias_State_0>;
    constexpr size_t tt_alias_state_size = std::tuple_size<TT_Alias_State_0>::value;
    class TT_Alias : public _TT_Base, public Picklable<TT_Alias, TT_Alias_State, tt_alias_state_size> {
    public:
        TT_Alias(const std::string& alias_name) noexcept : _TT_Base(alias_name) {}
        TT_Alias(const TT_Alias& other) noexcept : _TT_Base(other) {}
        TT_Alias(TT_Alias&& other) noexcept : _TT_Base(other) {}
        TT_Alias& operator=(const TT_Alias& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); return *this; }
        TT_Alias& operator=(TT_Alias&& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); return *this; }
        bool operator==(const TT_Alias& other) const noexcept { if(this == &other) return true; return (_TT_Base::operator==(other)); }
        virtual std::string alias() const noexcept { return std::get<std::string>(value()); };
        const TT_Alias_State get_state(TT_Alias* selfp=nullptr) const override { return std::make_tuple(alias()); }
    };

    class _TT_WithAlias { public: virtual const TT_Alias& alias() const noexcept = 0; };


    /// @brief Base class for all @op classes.
    /// AtOps are the things in front of operands, like the [-] before [-]Register:Ra.
    /// The eval_value for this one is {1,0} where 1==operation_is_there, 0==no_operation
    enum class AtOp { Not, Negate, Abs, Sign, Invert };
    using TT_AtOp_State_0 = std::tuple<std::string, std::string, std::string, uint8_t>;
    using TT_AtOp_State = std::variant<TT_AtOp_State_0>;
    constexpr size_t tt_atop_state_size = std::tuple_size<TT_AtOp_State_0>::value;
    class TT_AtOp : public _TT_Domain, public _TT_WithAlias, public _TT_QueriableAlias, public Picklable<TT_AtOp, TT_AtOp_State, tt_atop_state_size> {
        std::string _op_name;
        std::string _reg_alias;
        TT_Alias _alias;
        AtOp _op_type;
    public:
        TT_AtOp(const std::string& op_name, const std::string& op_sign, const std::string& reg_alias, const uint8_t& op_type) noexcept : _TT_Domain(op_sign), _op_name(op_name), _reg_alias(reg_alias), _alias(TT_Alias(_reg_alias + _op_name)), _op_type(static_cast<AtOp>(static_cast<int>(op_type))) {}
        TT_AtOp(const TT_AtOp& other) noexcept : _TT_Domain(other), _op_name(other._op_name), _reg_alias(other._reg_alias), _alias(other._alias), _op_type(other._op_type) {}
        TT_AtOp(TT_AtOp&& other) noexcept : _TT_Domain(other), _op_name(std::move(other._op_name)), _reg_alias(std::move(other._reg_alias)), _alias(std::move(other._alias)), _op_type(std::move(other._op_type)) {}
        TT_AtOp& operator=(const TT_AtOp& other) noexcept { if(this == &other) return *this; _TT_Domain::operator=(other); _op_name = other._op_name; _reg_alias = other._reg_alias; _alias = other._alias, _op_type = other._op_type; return *this; }
        TT_AtOp& operator=(TT_AtOp&& other) noexcept { if(this == &other) return *this; _TT_Domain::operator=(other); _op_name = std::move(other._op_name); _reg_alias = std::move(other._reg_alias); _alias = std::move(other._alias), _op_type = std::move(other._op_type); return *this; }
        bool operator==(const TT_AtOp& other) const noexcept { if(this == &other) return true; return (_TT_Domain::operator==(other) && (_op_name.compare(other._op_name) == 0) && (_reg_alias.compare(other._reg_alias) == 0)) && _op_type == other._op_type; }
        std::string op_name() const noexcept { return _op_name; }
        const TT_Alias& alias() const noexcept { return _alias; }
        AtOp op_type() const noexcept { return _op_type; }

        std::string reg_alias() const noexcept { return _reg_alias; }
        TDomain get_domain(const TToLimit& to_limit = {}, bool filter_invalid = false) const override { return std::set<SASS_Bits>{SASS_Bits::from_int(0, 1, 0), SASS_Bits::from_int(1, 1, 0)}; }
        std::vector<std::string> get_enc_alias() const noexcept override { return { alias().alias() }; }
        const TT_AtOp_State get_state(TT_AtOp* selfp=nullptr) const override { return std::make_tuple(op_name(), std::get<std::string>(value()), reg_alias(), static_cast<uint8_t>(std::to_underlying(_op_type))); }
    };
    using TOpsVec = std::vector<TT_AtOp>;
    using TOpsStateVec = std::vector<TT_AtOp_State>;

    /// @brief This one represents [!]
    class TT_OpAtNot : public TT_AtOp { 
    public: 
        TT_OpAtNot(const std::string& reg_alias) noexcept : TT_AtOp("@not", "!", reg_alias, static_cast<uint8_t>(std::to_underlying(AtOp::Not))) {} 
        TT_OpAtNot(const TT_AtOp& op) noexcept : TT_AtOp(op) {} /* extra convenience constructor for this one */
        TT_OpAtNot(const TT_OpAtNot& op) noexcept : TT_AtOp(op) {}
        TT_OpAtNot(TT_OpAtNot&& op) noexcept : TT_AtOp(op) {}
        TT_OpAtNot& operator=(const TT_OpAtNot& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; }
        TT_OpAtNot& operator=(TT_OpAtNot&& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; }
        bool operator==(const TT_OpAtNot& other) const noexcept { if(this == &other) return true; return TT_AtOp::operator==(other); }
    };
    /// @brief This one represents [-]
    class TT_OpAtNegate : public TT_AtOp {
    public: 
        TT_OpAtNegate(const std::string& reg_alias) noexcept : TT_AtOp("@negate", "-", reg_alias, static_cast<uint8_t>(std::to_underlying(AtOp::Negate))) {} 
        TT_OpAtNegate(const TT_AtOp& op) noexcept : TT_AtOp(op) {} /* extra convenience constructor for this one */
        TT_OpAtNegate(const TT_OpAtNegate& other) noexcept : TT_AtOp(other) {} 
        TT_OpAtNegate(TT_OpAtNegate&& other) noexcept : TT_AtOp(other) {} 
        TT_OpAtNegate& operator=(const TT_OpAtNegate& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; } 
        TT_OpAtNegate& operator=(TT_OpAtNegate&& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; } 
        bool operator==(const TT_OpAtNegate& other) const noexcept { if(this == &other) return true; return TT_AtOp::operator==(other); }
    };
    /// @brief This one represents [||]
    class TT_OpAtAbs : public TT_AtOp { 
    public:
        TT_OpAtAbs(const std::string& reg_alias) noexcept : TT_AtOp("@absolute", "||", reg_alias, static_cast<uint8_t>(std::to_underlying(AtOp::Abs))) {} 
        TT_OpAtAbs(const TT_AtOp& op) noexcept : TT_AtOp(op) {} /* extra convenience constructor for this one */
        TT_OpAtAbs(const TT_OpAtAbs& other) noexcept : TT_AtOp(other) {} 
        TT_OpAtAbs(TT_OpAtAbs&& other) noexcept : TT_AtOp(other) {} 
        TT_OpAtAbs& operator=(const TT_OpAtAbs& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; } 
        TT_OpAtAbs& operator=(TT_OpAtAbs&& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; }
        bool operator==(const TT_OpAtAbs& other) const noexcept { if(this == &other) return true; return TT_AtOp::operator==(other); }
    };
    /// @brief This one represents [&&]
    /// NOTE: @sign exists for SASS_Func only and only on platforms older than and including SM 62! On newer platforns this one is ignored.
    class TT_OpAtSign : public TT_AtOp { 
    public: 
        TT_OpAtSign(const std::string& reg_alias) noexcept : TT_AtOp("@sign", "&&", reg_alias, static_cast<uint8_t>(std::to_underlying(AtOp::Sign))) {} 
        TT_OpAtSign(const TT_AtOp& op) noexcept : TT_AtOp(op) {} /* extra convenience constructor for this one */
        TT_OpAtSign(const TT_OpAtSign& other) noexcept : TT_AtOp(other) {} 
        TT_OpAtSign(TT_OpAtSign&& other) noexcept : TT_AtOp(other) {} 
        TT_OpAtSign& operator=(const TT_OpAtSign& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; } 
        TT_OpAtSign& operator=(TT_OpAtSign&& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; }
        bool operator==(const TT_OpAtSign& other) const noexcept { if(this == &other) return true; return TT_AtOp::operator==(other); }
    };
    /// @brief This one represents [~]
    class TT_OpAtInvert : public TT_AtOp { 
    public: 
        TT_OpAtInvert(const std::string& reg_alias) noexcept : TT_AtOp("@invert", "~", reg_alias, static_cast<uint8_t>(std::to_underlying(AtOp::Invert))) {} 
        TT_OpAtInvert(const TT_AtOp& op) noexcept : TT_AtOp(op) {} /* extra convenience constructor for this one */
        TT_OpAtInvert(const TT_OpAtInvert& other) noexcept : TT_AtOp(other) {} 
        TT_OpAtInvert(TT_OpAtInvert&& other) noexcept : TT_AtOp(other) {} 
        TT_OpAtInvert& operator=(const TT_OpAtInvert& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; } 
        TT_OpAtInvert& operator=(TT_OpAtInvert&& other) noexcept { if(this == &other) return *this; TT_AtOp::operator=(other); return *this; }
        bool operator==(const TT_OpAtInvert& other) const noexcept { if(this == &other) return true; return TT_AtOp::operator==(other); }
    };

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
        TT_Default(const TT_Default& other) noexcept : _TT_Base(other), _has_print(other._has_print), _options(other._options), _exists(other._exists) {}
        TT_Default(TT_Default&& other) noexcept : _TT_Base(other), _has_print(std::move(other._has_print)), _options(std::move(other._options)), _exists(std::move(other._exists)) {}
        TT_Default& operator=(const TT_Default& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); _has_print = other._has_print; _options = other._options; _exists = other._exists; return *this; }
        TT_Default& operator=(TT_Default&& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); _has_print = std::move(other._has_print); _options = std::move(other._options); _exists = std::move(other._exists); return *this; }
        bool operator==(const TT_Default& other) const noexcept { if(this == &other) return true; return _TT_Base::operator==(other) && (_has_print == other._has_print) && (_options == other._options) && (_exists == other._exists); }
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

    class TT_NoDefault : public TT_Default { 
    public: 
        TT_NoDefault() : TT_Default(0, false, {}) { TT_Default::_exists = false; } 
        TT_NoDefault(const TT_NoDefault& other) : TT_Default(other) {} 
        TT_NoDefault(TT_NoDefault&& other) : TT_Default(other) {} 
        TT_NoDefault& operator=(const TT_NoDefault& other) noexcept { if(this == &other) return *this; TT_Default::operator=(other); return *this; }
        TT_NoDefault& operator=(TT_NoDefault&& other) noexcept { if(this == &other) return *this; TT_Default::operator=(other); return *this; }
        bool operator==(const TT_NoDefault& other) const noexcept { if(this == &other) return true; return TT_Default::operator==(other); }
    };

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
        TT_FuncArg(const TT_FuncArg& other) noexcept : _TT_Base(other), _has_star(other._has_star), _has_print(other._has_print), _bit_len(other._bit_len), _has_default(other._has_default), _default_val(other._default_val), _has_max_val(other._has_max_val), _max_val(other._max_val) {}
        TT_FuncArg(TT_FuncArg&& other) noexcept : _TT_Base(other), _has_star(std::move(other._has_star)), _has_print(std::move(other._has_print)), _bit_len(std::move(other._bit_len)), _has_default(std::move(other._has_default)), _default_val(std::move(other._default_val)), _has_max_val(std::move(other._has_max_val)), _max_val(std::move(other._max_val)) {}
        TT_FuncArg& operator=(const TT_FuncArg& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); _has_star = other._has_star; _has_print = other._has_print; _bit_len = other._bit_len; _has_default = other._has_default; _default_val = other._default_val; _has_max_val = other._has_max_val; _max_val = other._max_val; return *this; }
        TT_FuncArg& operator=(TT_FuncArg&& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); _has_star = std::move(other._has_star); _has_print = std::move(other._has_print); _bit_len = std::move(other._bit_len); _has_default = std::move(other._has_default); _default_val = std::move(other._default_val); _has_max_val = std::move(other._has_max_val); _max_val = std::move(other._max_val); return *this; }
        bool operator==(const TT_FuncArg& other) const noexcept { if(this == &other) return true; return _TT_Base::operator==(other) && (_has_star == other._has_star) && (_has_print == other._has_print) && (_bit_len == other._bit_len) && (_has_default == other._has_default) && (_default_val == other._default_val) && (_has_max_val == other._has_max_val) && (_max_val == other._max_val); }
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

    using TT_Func_State_0 = std::tuple<std::string, TStrOptionsSet, TT_FuncArg_State, bool, bool, TT_Alias_State>;
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
        TT_Func(const std::string& func_name, const TStrOptionsSet& options, const TT_FuncArg& arg_default, bool star, bool is_address, const TT_Alias& alias) noexcept 
          : _TT_Assemblable(func_name), _options(options), _arg_default(arg_default), _star(star), _is_address(is_address), _alias(alias), _func(_init_func(*this, func_name)) {}
        TT_Func(const std::string& func_name, const TStrOptionsSet& options, const TT_FuncArg_State& arg_default, bool star, bool is_address, const TT_Alias_State& alias) noexcept
          : _TT_Assemblable(func_name), _options(options), _arg_default(TT_FuncArg::muh(arg_default)), _star(star), _is_address(is_address), _alias(TT_Alias::muh(alias)), _func(_init_func(*this, func_name)) {}
        TT_Func(const TT_Func& other) noexcept
          : _TT_Assemblable(other), _options(other._options), _arg_default(other._arg_default), _star(other._star), _is_address(other._is_address), _alias(other._alias), _func(other._func) {}
        TT_Func(TT_Func&& other) noexcept
          : _TT_Assemblable(other), _options(std::move(other._options)), _arg_default(std::move(other._arg_default)), _star(std::move(other._star)), _is_address(std::move(other._is_address)), _alias(std::move(other._alias)), _func(std::move(other._func)) {}
        TT_Func& operator=(const TT_Func& other) noexcept { if(this == &other) return *this; _TT_Assemblable::operator=(other); _options = other._options; _arg_default = other._arg_default; _star = other._star; _is_address = other._is_address; _alias = other._alias; _func = other._func; return *this; }
        TT_Func& operator=(TT_Func&& other) noexcept { if(this == &other) return *this; _TT_Assemblable::operator=(other); _options = std::move(other._options); _arg_default = std::move(other._arg_default); _star = std::move(other._star); _is_address = std::move(other._is_address); _alias = std::move(other._alias); _func = std::move(other._func); return *this; }
        bool operator==(const TT_Func& other) const noexcept { if(this == &other) return true; return _TT_Assemblable::operator==(other) && (_options == other._options) && (_arg_default == other._arg_default) && (_star == other._star) && (_is_address == other._is_address) && (_alias == other._alias) && (_func == other._func); }
        std::string __str__() const override { 
            // NOTE: we have the alias here, but we don't print it. Printing the alias is a thing of TT_Param
            return std::get<std::string>(value()) + "(" + _arg_default.__str__() + ")" + (_star ? "*" : "");
        }
        static std::unordered_map<std::string, TT_Func> get_eval(const TT_Func& func) {
            std::unordered_map<std::string, TT_Func> res = {{func.alias().__str__(), func}};
            return res;
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
        const TT_Func_State get_state(TT_Func* selfp=nullptr) const override { return std::make_tuple(std::get<std::string>(value()), _options, _arg_default.get_state(), _star, _is_address, _alias.get_state()); }
        
        const TStrOptionsSet& options() const noexcept { return _options; }
        const TT_FuncArg& arg_default() const noexcept { return _arg_default; }
        const bool& star() const noexcept { return _star; }
        const bool& is_address() const noexcept { return _is_address; }
        const TT_Alias& alias() const noexcept override { return _alias; }
        const Imm& func() const noexcept { return _func; }
    };

    using TT_Reg_State_0 = std::tuple<int, TT_Default_State, TOptions, TT_Alias_State>;
    using TT_Reg_State_1 = std::tuple<std::string, TT_Default_State, TOptions, TT_Alias_State>;
    using TT_Reg_State = std::variant<TT_Reg_State_0, TT_Reg_State_1>;
    constexpr size_t tt_reg_state_size = std::tuple_size<TT_Reg_State_0>::value;
    class TT_Reg : public _TT_Assemblable, public _TT_WithAlias, public Picklable<TT_Reg, TT_Reg_State, tt_reg_state_size> {
        TT_Default _default;
        TOptions _options;
        TT_Alias _alias;
        uint8_t _min_bit_len;
    public:
        TT_Reg(const TValue& value, const TT_Default& default_val, const TOptions& options, const TT_Alias& alias) noexcept
          : _TT_Assemblable(value), _default(default_val), _options(options), _alias(alias), _min_bit_len(Utils::bit_len(Utils::max_option( _options))) {}
        TT_Reg(const TValue& value, const TT_Default_State& default_val, const TOptions& options, const TT_Alias_State& alias) noexcept
          : _TT_Assemblable(value), _default(TT_Default::muh(default_val)), _options(options), _alias(TT_Alias::muh(alias)), _min_bit_len(Utils::bit_len(Utils::max_option( _options))) {}
        TT_Reg(const TT_Reg& other) noexcept
          : _TT_Assemblable(other), _default(other._default), _options(other._options), _alias(other._alias), _min_bit_len(other._min_bit_len) {}
        TT_Reg(TT_Reg&& other) noexcept
          : _TT_Assemblable(other), _default(std::move(other._default)), _options(std::move(other._options)), _alias(std::move(other._alias)), _min_bit_len(std::move(other._min_bit_len)) {}
        TT_Reg& operator=(const TT_Reg& other) noexcept { if(this == &other) return *this; _TT_Assemblable::operator=(other); _default = other._default; _options = other._options; _alias = other._alias; _min_bit_len = other._min_bit_len; return *this; }
        TT_Reg& operator=(TT_Reg&& other) noexcept { if(this == &other) return *this; _TT_Assemblable::operator=(other); _default = std::move(other._default); _options = std::move(other._options); _alias = std::move(other._alias); _min_bit_len = std::move(other._min_bit_len); return *this; }
        bool operator==(const TT_Reg& other) const noexcept { if(this == &other) return true; return _TT_Assemblable::operator==(other) && (_default == other._default) && (_options == other._options) && (_alias == other._alias) && (_min_bit_len == other._min_bit_len); }
        
        const TT_Alias& alias() const noexcept override { return _alias; }
        const TT_Default& default_() const noexcept { return _default; }
        const TOptions& options() const noexcept { return _options; }
        const uint8_t min_bit_len() const noexcept { return _min_bit_len; }
        
        std::string __str__() const override {
            std::stringstream res;
            res << (std::holds_alternative<std::string>(value()) ? std::get<std::string>(value()) : std::to_string(std::get<int>(value())));
            if(_default.exists()) res << "(" << _default.__str__() << ")";
            // NOTE: we have the alias here, but we don't print it. Printing the alias is a thing of TT_Param
            return res.str();
        }
        static std::unordered_map<std::string, TT_Reg> get_eval(const TT_Reg& reg) {
            std::unordered_map<std::string, TT_Reg> res = {{reg.alias().__str__(), reg}};
            // if(std::holds_alternative<int>(reg.value())) res.insert({std::to_string(std::get<int>(reg.value())), reg});
            // else res.insert({std::get<std::string>(reg.value()), reg});
            return res;
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
        const TT_Reg_State get_state(TT_Reg* selfp=nullptr) const override { 
            TValue val = value();
            if(std::holds_alternative<int>(val)) return std::make_tuple(std::get<int>(val), _default.get_state(), _options, _alias.get_state()); 
            return std::make_tuple(std::get<std::string>(val), _default.get_state(), _options, _alias.get_state()); 
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
        TT_ICode(const TT_ICode& other) noexcept : _TT_Base(other), _bin_str(other._bin_str), _bin_ind(other._bin_ind), _bin_tup(other._bin_tup) {}
        TT_ICode(TT_ICode&& other) noexcept : _TT_Base(other), _bin_str(std::move(other._bin_str)), _bin_ind(std::move(other._bin_ind)), _bin_tup(std::move(other._bin_tup)) {}
        TT_ICode operator=(const TT_ICode& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); _bin_str = other._bin_str; _bin_ind = other._bin_ind; _bin_tup = other._bin_tup; return *this; }
        TT_ICode operator=(TT_ICode&& other) noexcept { if(this == &other) return *this; _TT_Base::operator=(other); _bin_str = std::move(other._bin_str); _bin_ind = std::move(other._bin_ind); _bin_tup = std::move(other._bin_tup); return *this; }
        bool operator==(const TT_ICode& other) const noexcept { if(this == &other) return true; return _TT_Base::operator==(other) && (_bin_str.compare(other._bin_str) == 0) && (_bin_ind == other._bin_ind) && (_bin_tup == other._bin_tup); }
        
        const std::string bin_str() const noexcept { return _bin_str; }
        const IntVector& bin_ind() const noexcept { return _bin_ind; }
        const IntVector& bin_tup() const noexcept { return _bin_tup; }
        
        IntVector get_opcode_bin() const noexcept { return _bin_tup; }
        const TT_ICode_State get_state(TT_ICode* selfp=nullptr) const override { return std::make_tuple(_bin_str, _bin_ind, _bin_tup); }
    };

    class TT_None {
    public:
        TT_None() noexcept {}
        TT_None(const TT_None& other) noexcept {}
        TT_None(TT_None&& other) noexcept {}
        TT_None operator=(const TT_None& other) noexcept { return *this; }
        TT_None operator=(TT_None&& other) noexcept { return *this; }
        bool operator==(const TT_None& other) const noexcept { return true; }
    };

    // The first entry in this variant has to be default constructible... This is why we have TT_None
    using TEvalType = std::variant<TT_None, TT_Reg, TT_Func, TT_AtOp, TT_ICode>;
    // using TEvalStateType = std::variant<TT_Reg_State, TT_Func_State, TT_AtOp_State, TT_ICode_State>;
    // constexpr size_t eval_type_size = std::variant_size_v<TEvalType>;
    // static_assert(std::variant_size_v<TEvalType> == std::variant_size_v<TEvalStateType>);

    using TEvalDict = std::unordered_map<std::string, TEvalType>;
    // using TEvalStateDict = std::unordered_map<std::string, TEvalStateType>;

    // using TT_Eval_State_0 = std::tuple<TEvalStateDict>;
    // using TT_Eval_State = std::variant<TT_Eval_State_0>;
    // constexpr size_t tt_eval_state_size = std::variant_size_v<TT_Eval_State>;
    class TT_Eval { //: public Picklable<TT_Eval, TT_Eval_State, tt_eval_state_size> {
        TEvalDict _eval;
    public:
        TT_Eval() noexcept : _eval({}) {}
        TT_Eval(const TEvalDict& eval) noexcept : _eval(eval) {}
        // TT_Eval(const TEvalStateDict& eval) noexcept : _eval(TT_Eval::muv_umap_h<std::string, TEvalType, TEvalStateType, eval_type_size>(eval)) {}
        TT_Eval(const TT_Eval& other) noexcept : _eval(other._eval) {}
        TT_Eval(TT_Eval&& other) noexcept : _eval(std::move(other._eval)) {}
        TT_Eval operator=(const TT_Eval& other) noexcept { if(this == &other) return *this; _eval = other._eval; return *this; }
        TT_Eval operator=(TT_Eval&& other) noexcept { if(this == &other) return *this; _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_Eval& other) const noexcept { if(this == &other) return true; return (_eval == other._eval); }
        const TEvalDict& eval() const noexcept { return _eval; }
        // const TT_Eval_State get_state(TT_Eval* selfp=nullptr) const override { return std::make_tuple(TT_Eval::mpv_umap_h<std::string, TEvalStateType, TEvalType, eval_type_size>(_eval)); }
    };

    // ==================================================================================================================
    // = Following are the actual instruction components ================================================================
    // ==================================================================================================================

    using TT_Pred_State_0 = std::tuple<TT_Alias_State, TT_Reg_State, TT_AtOp_State>;
    using TT_Pred_State = std::variant<TT_Pred_State_0>;
    constexpr size_t tt_pred_state_size = std::tuple_size<TT_Pred_State_0>::value;
    class TT_Pred : public _TT_WithAlias, public _TT_QueriableAlias, public _TT_IsPrintable, public Picklable<TT_Pred, TT_Pred_State, tt_pred_state_size> {
        TT_Alias _alias;
        TT_Reg _reg;
        TT_OpAtNot _op;
        TT_Eval _eval;
    public:
        TT_Pred(const TT_Alias& alias, const TT_Reg& reg, const TT_OpAtNot& op) noexcept
          : _alias(alias), _reg(reg), _op(op), _eval({{_alias.__str__(), _reg}, {_op.alias().alias(), _op}}) {}
        TT_Pred(const TT_Alias_State& alias, const TT_Reg_State& reg, const TT_AtOp_State& op) noexcept
          : _alias(TT_Alias::muh(alias)), _reg(TT_Reg::muh(reg)), _op(TT_OpAtNot::muh(op)), _eval({{_alias.__str__(), _reg}, {_op.alias().alias(), _op}}) {}
        TT_Pred(const TT_Pred& other) noexcept
          : _alias(other._alias), _reg(other._reg), _op(other._op), _eval(other._eval) {}
        TT_Pred(TT_Pred&& other) noexcept
          : _alias(std::move(other._alias)), _reg(std::move(other._reg)), _op(std::move(other._op)), _eval(std::move(other._eval)) {}
        TT_Pred& operator=(const TT_Pred& other) noexcept { if(this == &other) return *this; _alias = other._alias; _reg = other._reg; _op = other._op, _eval = other._eval; return *this; }
        TT_Pred& operator=(TT_Pred&& other) noexcept { if(this == &other) return *this; _alias = std::move(other._alias); _reg = std::move(other._reg); _op = std::move(other._op); _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_Pred& other) const noexcept { if(this == &other) return true; return (_alias == other._alias) && (_reg == other._reg) && (_op == other._op); }
        const TT_Reg& value() const noexcept { return _reg; }
        const TT_Reg& reg() const noexcept { return _reg; }
        const TT_OpAtNot& op() const noexcept { return _op; }
        virtual bool is_none() const noexcept { return false; }
        const TEvalDict& eval() const noexcept { return _eval.eval(); }
        const TT_Alias& alias() const noexcept override { return _alias; }

        std::string __str__() const override { return std::string("@[") + _op.__str__() + "]" + _reg.__str__() + ":" + _alias.__str__(); }
        std::vector<std::string> get_enc_alias() const noexcept override { return { _alias.alias(), _op.alias().alias() }; }
        const TT_Pred_State get_state(TT_Pred* selfp=nullptr) const override { return std::make_tuple(_alias.get_state(), _reg.get_state(), _op.get_state()); }
    };

    class TT_NoPred : public TT_Pred { 
    public: 
        TT_NoPred() : TT_Pred(TT_Alias("none"), TT_Reg(0, TT_NoDefault(), {}, TT_Alias("none")), TT_OpAtNot("none")) {} 
        bool is_none() const noexcept override { return true; }
    };

    using TT_Ext_State_0 = std::tuple<TT_Alias_State, TT_Reg_State, bool>;
    using TT_Ext_State = std::variant<TT_Ext_State_0>;
    constexpr size_t tt_ext_state_size = std::tuple_size<TT_Ext_State_0>::value;
    class TT_Ext : public _TT_WithAlias, public _TT_QueriableAlias, public _TT_IsPrintable, public Picklable<TT_Ext, TT_Ext_State, tt_ext_state_size> {
        TT_Alias _alias;
        TT_Reg _reg;
        bool _is_at_alias;
        TT_Eval _eval;

        static TEvalDict get_eval(const TT_Ext& ext) {
            TEvalDict res;
            const auto& b = TT_Reg::get_eval(ext._reg);
            res.insert(b.begin(), b.end());
            res.insert({std::get<std::string>(ext._reg.value()), ext._reg});
            return res;
        }
    public:
        TT_Ext(const TT_Alias& alias, const TT_Reg& reg, bool is_at_alias) noexcept 
            : _alias(alias), _reg(reg), _is_at_alias(is_at_alias), _eval(TT_Ext::get_eval(*this)) {}
        TT_Ext(const TT_Alias_State& alias, const TT_Reg_State& reg, bool is_at_alias) noexcept 
            : _alias(TT_Alias::muh(alias)), _reg(TT_Reg::muh(reg)), _is_at_alias(is_at_alias), _eval(TT_Ext::get_eval(*this)) {}
        TT_Ext(const TT_Ext& other) noexcept 
            : _alias(other._alias), _reg(other._reg), _is_at_alias(other._is_at_alias), _eval(other._eval) {}
        TT_Ext(TT_Ext&& other) noexcept 
            : _alias(std::move(other._alias)), _reg(std::move(other._reg)), _is_at_alias(std::move(other._is_at_alias)), _eval(std::move(other._eval)) {}
        TT_Ext& operator=(const TT_Ext& other) noexcept { if(this == &other) return *this; _alias = other._alias; _reg = other._reg; _is_at_alias = other._is_at_alias; _eval = other._eval; return *this; }
        TT_Ext& operator=(TT_Ext&& other) noexcept { if(this == &other) return *this; _alias = std::move(other._alias); _reg = std::move(other._reg); _is_at_alias = std::move(other._is_at_alias); _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_Ext& other) const noexcept { if(this == &other) return true; return (_alias == other._alias) && (_reg == other._reg) && (_is_at_alias == other._is_at_alias); }
        const TT_Reg& value() const noexcept { return _reg; }
        const TT_Reg& reg() const noexcept { return _reg; }
        const bool is_at_alias() const noexcept { return _is_at_alias; }
        const TEvalDict& eval() const noexcept { return _eval.eval(); }
        const TT_Alias& alias() const noexcept override { return _alias; }

        std::string __str__() const override { return std::string("/") + _reg.__str__() + (_is_at_alias ? "@" : "") + ":" + _alias.__str__(); }
        std::vector<std::string> get_enc_alias() const noexcept override { return { std::get<std::string>(_reg.value()), _alias.alias() }; }
        const TT_Ext_State get_state(TT_Ext* selfp=nullptr) const override { return std::make_tuple(_alias.get_state(), _reg.get_state(), _is_at_alias); }
    };
    using TExtVec = std::vector<TT_Ext>;
    using TExtStateVec = std::vector<TT_Ext_State>;

    using TT_Opcode_State_0 = std::tuple<TT_Alias_State, TT_ICode_State, TExtStateVec>;
    using TT_Opcode_State = std::variant<TT_Opcode_State_0>;
    constexpr size_t tt_opcode_state_size = std::tuple_size<TT_Opcode_State_0>::value;
    class TT_Opcode : public _TT_WithAlias, public _TT_IsPrintable, public _TT_QueriableAlias, public Picklable<TT_Opcode, TT_Opcode_State, tt_opcode_state_size> {
        TT_Alias _alias;
        TT_ICode _icode;
        TExtVec _extensions;
        TT_Eval _eval;

        static TEvalDict get_eval(const TT_Opcode& opcode) {
            TEvalDict res;
            for(const auto& e : opcode._extensions){
                const auto& t = e.eval();
                res.insert(t.begin(), t.end());
            }
            res.insert({opcode._alias.__str__(), opcode._icode});
            return res;
        }

    public:
        TT_Opcode(const TT_Alias& alias, const TT_ICode& icode, const TExtVec& extensions) noexcept 
          : _alias(alias), _icode(icode), _extensions(extensions), _eval(TT_Opcode::get_eval(*this)) {}
        TT_Opcode(const TT_Alias_State& alias, const TT_ICode_State& icode, const TExtStateVec& extensions) noexcept 
          : _alias(TT_Alias::muh(alias)), _icode(TT_ICode::muh(icode)), _extensions(TT_Ext::from_state_vec(extensions)), _eval(TT_Opcode::get_eval(*this)) {}
        TT_Opcode(const TT_Opcode& other) noexcept 
          : _alias(other._alias), _icode(other._icode), _extensions(other._extensions), _eval(other._eval) {}
        TT_Opcode(TT_Opcode&& other) noexcept 
          : _alias(std::move(other._alias)), _icode(std::move(other._icode)), _extensions(std::move(other._extensions)), _eval(std::move(other._eval)) {}
        TT_Opcode& operator=(const TT_Opcode& other) noexcept { if(this == &other) return *this; _alias = other._alias; _icode = other._icode; _extensions = other._extensions; _eval = other._eval; return *this; }
        TT_Opcode& operator=(TT_Opcode&& other) noexcept { if(this == &other) return *this; _alias = std::move(other._alias); _icode = std::move(other._icode); _extensions = std::move(other._extensions); _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_Opcode& other) const noexcept { if(this == &other) return true; return (_alias == other._alias) && (_icode == other._icode) && (_extensions == other._extensions); }
        const TT_ICode& value() const noexcept { return _icode; }
        const TT_Alias& alias() const noexcept override { return _alias; }
        const TEvalDict& eval() const noexcept { return _eval.eval(); }
        const TT_ICode& icode() const noexcept { return _icode; }
        const TExtVec& extensions() const noexcept { return _extensions; }

        
        std::string __str__() const override {
            std::stringstream res;
            res << _icode.__str__();
            for(const TT_Ext& ext : _extensions){
                res << " " << ext.__str__();
            }
            return res.str();
        }
        IntVector get_opcode_bin() { return _icode.get_opcode_bin(); }
        std::vector<std::string> get_enc_alias() const noexcept override {
            std::vector<std::string> res = {};
            for(const TT_Ext& ext : _extensions) {
                const auto& v = ext.get_enc_alias();
                res.insert(res.end(), v.begin(), v.end());
            }
            res.shrink_to_fit();
            return res;
        }
        const TT_Opcode_State get_state(TT_Opcode* selfp=nullptr) const override { return std::make_tuple(_alias.get_state(), _icode.get_state(), TT_Ext::to_state_vec(_extensions)); }
    };

    using TParamFuncReg = std::variant<TT_Reg, TT_Func>;
    class _TT_CashBase : public _TT_QueriableAlias, public _TT_IsPrintable {};

    using TT_Param_State_0 = std::tuple<TT_Alias_State, TOpsStateVec, TT_Reg_State, TExtStateVec, bool, bool>;
    using TT_Param_State_1 = std::tuple<TT_Alias_State, TOpsStateVec, TT_Func_State, TExtStateVec, bool, bool>;
    using TT_Param_State = std::variant<TT_Param_State_0, TT_Param_State_1>;
    constexpr size_t tt_param_state_size = std::tuple_size<TT_Param_State_0>::value;
    class TT_Param : public _TT_CashBase, public Picklable<TT_Param, TT_Param_State, tt_param_state_size> {
    protected:
        TT_Alias _alias;
        TOpsVec _ops;
        TParamFuncReg _value;
        TExtVec _extensions;
        bool _is_at_alias;
        bool _has_attr_star;
        TT_Eval _eval;

        static TEvalDict get_eval(const TT_Param& param) {
            TEvalDict res;
            if(std::holds_alternative<TT_Reg>(param._value)) {
                const auto& temp = TT_Reg::get_eval(std::get<TT_Reg>(param._value));
                res.insert(temp.begin(), temp.end());
            }
            else if(std::holds_alternative<TT_Func>(param._value)) {
                const auto& temp = TT_Func::get_eval(std::get<TT_Func>(param._value));
                res.insert(temp.begin(), temp.end());
            }
            
            for(const auto& e : param._extensions){
                const auto& t = e.eval();
                res.insert(t.begin(), t.end());
            }
            for(const auto& e : param._ops){
                res.insert({e.alias().alias(), e});
            }
            
            return res;
        }
    public:
        TT_Param(const TT_Alias& alias, const TOpsVec& ops, const TParamFuncReg& value, const TExtVec& extensions, bool is_at_alias, bool has_attr_star) noexcept 
          : _alias(alias), _ops(ops), _value(value), _extensions(extensions), _is_at_alias(is_at_alias), _has_attr_star(has_attr_star), _eval(TT_Param::get_eval(*this)) {}
        TT_Param(const TT_Alias_State& alias, const TOpsStateVec& ops, const TT_Reg_State& value, const TExtStateVec& extensions, bool is_at_alias, bool has_attr_star) noexcept 
          : _alias(TT_Alias::muh(alias)), _ops(TT_AtOp::from_state_vec(ops)), _value(TT_Reg::muh(value)), _extensions(TT_Ext::from_state_vec(extensions)), _is_at_alias(is_at_alias), _has_attr_star(has_attr_star), _eval(TT_Param::get_eval(*this)) {}
        TT_Param(const TT_Alias_State& alias, const TOpsStateVec& ops, const TT_Func_State& value, const TExtStateVec& extensions, bool is_at_alias, bool has_attr_star) noexcept 
          : _alias(TT_Alias::muh(alias)), _ops(TT_AtOp::from_state_vec(ops)), _value(TT_Func::muh(value)), _extensions(TT_Ext::from_state_vec(extensions)), _is_at_alias(is_at_alias), _has_attr_star(has_attr_star), _eval(TT_Param::get_eval(*this)) {}
        TT_Param(const TT_Param& other) noexcept 
          : _alias(other._alias), _ops(other._ops), _value(other._value), _extensions(other._extensions), _is_at_alias(other._is_at_alias), _has_attr_star(other._has_attr_star), _eval(other._eval) {}
        TT_Param(TT_Param&& other) noexcept 
          : _alias(std::move(other._alias)), _ops(std::move(other._ops)), _value(std::move(other._value)), _extensions(std::move(other._extensions)), _is_at_alias(std::move(other._is_at_alias)), _has_attr_star(std::move(other._has_attr_star)), _eval(std::move(other._eval)) {}
        TT_Param& operator=(const TT_Param& other) noexcept { if(this == &other) return *this; _alias = other._alias; _ops = other._ops; _value = other._value; _extensions = other._extensions; _eval = other._eval; return *this; }
        TT_Param& operator=(TT_Param&& other) noexcept { if(this == &other) return *this; _alias = std::move(other._alias); _ops = std::move(other._ops); _value = std::move(other._value); _extensions = std::move(other._extensions); _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_Param& other) const noexcept { if(this == &other) return true; return (_alias == other._alias) && (_ops == other._ops) && (_value == other._value) && (_extensions == other._extensions) && (_is_at_alias == other._is_at_alias) && (_has_attr_star == other._has_attr_star); }
        
        const TParamFuncReg& value() const noexcept { return _value; }
        const TT_Alias& alias() const noexcept { return _alias; }
        const TOpsVec& ops() const noexcept { return _ops; }
        const TExtVec& extensions() const noexcept { return _extensions; }
        const TEvalDict& eval() const noexcept { return _eval.eval(); }
        bool is_at_alias() const noexcept { return _is_at_alias; }
        bool has_attr_star() const noexcept { return _has_attr_star; }

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
            res.shrink_to_fit();
            return res;
        }
        std::string __str__() const override {
            std::stringstream res;
            for(const TT_AtOp& op : _ops){
                if(op.op_type() == AtOp::Sign) continue;
                res << "[" << op.__str__() << "]";
            }
            res << (std::holds_alternative<TT_Reg>(_value) ? std::get<TT_Reg>(_value).__str__() : std::get<TT_Func>(_value).__str__());
            if(_is_at_alias) res << "@";
            res << ":" << _alias.alias();
            for(const TT_Ext& ext : _extensions) {
                res << " " << ext.__str__();
            }

            return res.str();
        }
        const TT_Param_State get_state(TT_Param* selfp=nullptr) const override {
            if(std::holds_alternative<TT_Reg>(_value)) return std::make_tuple(_alias.get_state(), TT_AtOp::to_state_vec(_ops), std::get<TT_Reg>(_value).get_state(), TT_Ext::to_state_vec(_extensions), _is_at_alias, _has_attr_star);
            return std::make_tuple(_alias.get_state(), TT_AtOp::to_state_vec(_ops), std::get<TT_Func>(_value).get_state(), TT_Ext::to_state_vec(_extensions), _is_at_alias, _has_attr_star);
        }
    };
    using TParamVec = std::vector<TT_Param>;
    using TParamStateVec = std::vector<TT_Param_State>;

    using TT_List_State_0 = std::tuple<TParamStateVec, TExtStateVec>;
    using TT_List_State = std::variant<TT_List_State_0>;
    constexpr size_t tt_list_state_size = std::tuple_size<TT_List_State_0>::value;
    class TT_List : public _TT_IsPrintable, public _TT_QueriableAlias, public Picklable<TT_List, TT_List_State, tt_list_state_size> {
        TParamVec _value;
        TExtVec _extensions;
        TT_Eval _eval;

        static TEvalDict get_eval(const TT_List& list) {
            TEvalDict res;
            for(const auto& v : list._value){
                const auto& t = v.eval();
                res.insert(t.begin(), t.end());
            }
            for(const auto& e : list._extensions){
                const auto& t = e.eval();
                res.insert(t.begin(), t.end());
            }
            return res;
        }

    public:
        TT_List(const TParamVec& params, const TExtVec& extensions) noexcept : _value(params), _extensions(extensions), _eval(TT_List::get_eval(*this)) {}
        TT_List(const TParamStateVec& params, const TExtStateVec& extensions) noexcept : _value(TT_Param::from_state_vec(params)), _extensions(TT_Ext::from_state_vec(extensions)), _eval(TT_List::get_eval(*this)) {}
        TT_List(const TT_List& other) noexcept : _value(other._value), _extensions(other._extensions), _eval(other._eval) {}
        TT_List(TT_List&& other) noexcept : _value(std::move(other._value)), _extensions(std::move(other._extensions)), _eval(std::move(other._eval)) {}
        TT_List& operator=(const TT_List& other) noexcept { if(this == &other) return *this; _value = other._value; _extensions = other._extensions; _eval = other._eval; return *this; }
        TT_List& operator=(TT_List&& other) noexcept { if(this == &other) return *this; _value = std::move(other._value); _extensions = std::move(other._extensions); _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_List& other) const noexcept { if(this == &other) return true; return (_value == other._value) && (_extensions == other._extensions); }
        const TParamVec& value() { return _value; }
        const TEvalDict& eval() const noexcept { return _eval.eval(); }
        const TParamVec& params() const noexcept { return _value; }
        const TExtVec& extensions() const noexcept { return _extensions; }

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
        const TT_List_State get_state(TT_List* selfp=nullptr) const override { return std::make_tuple(TT_Param::to_state_vec(_value), TT_Ext::to_state_vec(_extensions)); }
    };
    using TListVec = std::vector<TT_List>;
    using TListStateVec = std::vector<TT_List_State>;


    /// @brief Base for all cash token classes
    /// Cash ops are the ones in the scheduling assignments like in
    /// $( { '&' RD:rd '=' UImm(3/0x7):src_rel_sb } )$.
    /// They don't hold a value. They are just there.
    using TT_CashComponent_State_0 = std::tuple<std::string>;
    using TT_CashComponent_State = std::variant<TT_CashComponent_State_0>;
    constexpr size_t tt_cashcomponent_state_size = std::tuple_size<TT_CashComponent_State_0>::value;
    class TT_CashComponent : public _TT_CashBase, public Picklable<TT_CashComponent, TT_CashComponent_State, tt_cashcomponent_state_size> {
        std::string _value;
    public: 
        TT_CashComponent(const std::string& cash_value) noexcept : _value(cash_value) {}
        TT_CashComponent(const TT_CashComponent& other) noexcept : _value(other._value) {}
        TT_CashComponent(TT_CashComponent&& other) noexcept : _value(std::move(other._value)) {}
        TT_CashComponent& operator=(const TT_CashComponent& other) noexcept { if(this == &other) return *this; _value = other._value; return *this; }
        TT_CashComponent& operator=(TT_CashComponent&& other) noexcept { if(this == &other) return *this; _value = std::move(other._value); return *this; }
        bool operator==(const TT_CashComponent& other) const noexcept { if(this == &other) return true; return (_value.compare(other._value) == 0); }
        const std::string& value() const { return _value; }
        std::string __str__() const override { return _value; }
        std::vector<std::string> get_enc_alias() const noexcept override { return {}; }
        const TT_CashComponent_State get_state(TT_CashComponent* selfp=nullptr) const override { return std::make_tuple(_value); }
    };
    /// @brief This one represents '?'
    class TT_OpCashQuestion : public TT_CashComponent { public: TT_OpCashQuestion() noexcept : TT_CashComponent("?") {} };
    /// @brief This one represents '&'
    class TT_OpCashAnd : public TT_CashComponent { public: TT_OpCashAnd() noexcept : TT_CashComponent("&") {} };
    /// @brief This one represents '='
    class TT_OpCashAssign : public TT_CashComponent { public: TT_OpCashAssign() noexcept : TT_CashComponent("=") {} };

    using TT_AttrParam_State_0 = std::tuple<TT_Param_State, TListStateVec>;
    using TT_AttrParam_State = std::variant<TT_AttrParam_State_0>;
    constexpr size_t tt_attrparam_state_size = std::tuple_size<TT_AttrParam_State_0>::value;
    class TT_AttrParam : public TT_Param, public Picklable<TT_AttrParam, TT_AttrParam_State, tt_attrparam_state_size> {
        TListVec _attr;
        TT_Eval _attr_eval;

        static TEvalDict get_eval(const TT_AttrParam& param, const TEvalDict& param_eval) {
            TEvalDict res = param_eval;
            for(const auto& a : param._attr){
                res.insert(a.eval().begin(), a.eval().end());
            }
            return res;
        }
    public:
        TT_AttrParam(const TT_Alias& alias, const TOpsVec& ops, const TParamFuncReg& value, const TListVec& attr, const TExtVec& extensions, bool is_at_alias, bool has_attr_star) noexcept 
          : TT_Param(alias, ops, value, extensions, is_at_alias, has_attr_star), _attr(attr), _attr_eval(TT_AttrParam::get_eval(*this, TT_Param::eval())) {}
        TT_AttrParam(const TT_Param_State& param, const TListStateVec& attr) noexcept 
          : TT_Param(TT_Param::muh(param)), _attr(TT_List::from_state_vec(attr)), _attr_eval(TT_AttrParam::get_eval(*this, TT_Param::eval())) {}
        TT_AttrParam(const TT_AttrParam& other) noexcept 
          : TT_Param(other), _attr(other._attr), _attr_eval(other._attr_eval) {}
        TT_AttrParam(TT_AttrParam&& other) noexcept 
          : TT_Param(other), _attr(std::move(other._attr)), _attr_eval(std::move(other._attr_eval)) {}
        TT_AttrParam& operator=(const TT_AttrParam& other) noexcept { if(this == &other) return *this; TT_Param::operator=(other); _attr = other._attr; _eval = other._eval; return *this; }
        TT_AttrParam& operator=(TT_AttrParam&& other) noexcept { if(this == &other) return *this; TT_Param::operator=(other); _attr = std::move(other._attr); _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_AttrParam& other) const noexcept { if(this == &other) return true; return TT_Param::operator==(other) && (_attr == other._attr); }
        const TEvalDict& eval() const noexcept { return _attr_eval.eval(); }
        const TListVec& attr() const noexcept { return _attr; }
        
        std::vector<std::string> get_enc_alias() const noexcept override {
            std::vector<std::string> res = TT_Param::get_enc_alias();
            for(const TT_List& attr : _attr) {
                const auto& v = attr.get_enc_alias();
                res.insert(res.end(), v.begin(), v.end());
            }
            res.shrink_to_fit();
            return res;
        }
        std::string __str__() const override {
            std::stringstream res;
            for(const TT_AtOp& op : _ops){
                if(op.op_type() == AtOp::Sign) continue;
                res << "[" << op.__str__() << "]";
            }
            res << (std::holds_alternative<TT_Reg>(_value) ? std::get<TT_Reg>(_value).__str__() : std::get<TT_Func>(_value).__str__());
            if(_is_at_alias) res << "@";
            res << ":" << _alias.alias();
            for(auto iter = _attr.cbegin(); iter!=_attr.cend(); iter++) {
                res << iter->__str__();
                if(_has_attr_star && iter!=_attr.cend()-1) res << "*";
            }
            for(const TT_Ext& ext : _extensions) {
                res << " " << ext.__str__();
            }

            return res.str();
        }
        
        const TT_AttrParam_State get_state(TT_AttrParam* selfp=nullptr) const override {
            return std::make_tuple(TT_Param::get_state(), TT_List::to_state_vec(_attr));
        }
    };

    using TCashComponentType = std::variant<TT_CashComponent, TT_Param>;
    using TCashComponentStateType = std::variant<TT_CashComponent_State, TT_Param_State>;
    constexpr size_t cash_type_size = std::variant_size_v<TCashComponentStateType>;
    static_assert(std::variant_size_v<TCashComponentType> == std::variant_size_v<TCashComponentStateType>);

    using TCashComponentsVec = std::vector<TCashComponentType>;
    using TCashComponentsStateVec = std::vector<TCashComponentStateType>;
    using TT_Cash_State_0 = std::tuple<TCashComponentsStateVec, bool>;
    using TT_Cash_State = std::variant<TT_Cash_State_0>;
    constexpr size_t tt_cash_state_size = std::tuple_size<TT_Cash_State_0>::value;
    class TT_Cash : public _TT_IsPrintable, public _TT_QueriableAlias, public Picklable<TT_Cash, TT_Cash_State, tt_cash_state_size> {
        TCashComponentsVec _values;
        bool _added_later;
        TT_Eval _eval;

        static TEvalDict get_eval(const TT_Cash& cash) {
            TEvalDict res;
            for(const auto& v : cash._values){
                if(std::holds_alternative<TT_Param>(v)) {
                    const auto& p = std::get<TT_Param>(v);
                    res.insert(p.eval().begin(), p.eval().end());
                }
            }
            return res;
        }

    public:
        TT_Cash(const TCashComponentsVec& cash_vals, bool added_later=false) noexcept : _values(cash_vals), _added_later(added_later), _eval(TT_Cash::get_eval(*this)) {}
        TT_Cash(const TCashComponentsStateVec& values, bool added_later) noexcept : _values(TT_Cash::muv_vec_h<TCashComponentType, TCashComponentStateType, cash_type_size>(values)), _added_later(added_later), _eval(TT_Cash::get_eval(*this)) {}
        TT_Cash(const TT_Cash& other) noexcept : _values(other._values), _added_later(other._added_later), _eval(other._eval) {}
        TT_Cash(TT_Cash&& other) noexcept : _values(std::move(other._values)), _added_later(std::move(other._added_later)), _eval(std::move(other._eval)) {}
        TT_Cash& operator=(const TT_Cash& other) { if(this == &other) return *this; _values = other._values; _added_later = other._added_later; _eval = other._eval; return *this; }
        TT_Cash& operator=(TT_Cash&& other) { if(this == &other) return *this; _values = std::move(other._values); _added_later = std::move(other._added_later); _eval = std::move(other._eval); return *this; }
        bool operator==(const TT_Cash& other) const noexcept { if(this == &other) return true; return (_values == other._values) && (_added_later == other._added_later); }
        const TCashComponentsVec& values() const noexcept { return _values; }
        const TCashComponentsVec& cash_components() const noexcept { return _values; }
        bool added_later() const noexcept { return _added_later; }
        const TEvalDict& eval() const noexcept { return _eval.eval(); }
        
        std::vector<std::string> get_enc_alias() const noexcept override {
            std::vector<std::string> res;
            for(const TCashComponentType& val : _values){
                if(std::holds_alternative<TT_Param>(val)){
                    const auto& v = std::get<TT_Param>(val).get_enc_alias();
                    res.insert(res.begin(), v.begin(), v.end());
                }
                else if (std::holds_alternative<TT_CashComponent>(val)){
                    const auto& v = std::get<TT_CashComponent>(val).get_enc_alias();
                    res.insert(res.begin(), v.begin(), v.end());
                }
            }
            return res;
        }
        std::string __str__() const override {
            std::stringstream res;
            res << "$( { ";
            for(const auto& val : _values){
                if(std::holds_alternative<TT_CashComponent>(val)){
                    res << std::get<TT_CashComponent>(val).__str__() << " ";
                }
                else if(std::holds_alternative<TT_Param>(val)){
                    res << std::get<TT_Param>(val).__str__() << " ";
                }
                else throw std::runtime_error("Invalid variant in Cash components!");
            }
            res << "} )$";
            return res.str();
        }
        const TT_Cash_State get_state(TT_Cash* selfp=nullptr) const override {
            return std::make_tuple(TT_Cash::mpv_vec_h<TCashComponentStateType, TCashComponentType, cash_type_size>(_values), _added_later );
        }
    };
}