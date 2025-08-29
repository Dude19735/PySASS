#pragma once

#include <set>
#include <string_view>
#include <format>

#include "SASS_Bits.hpp"
#include "Utils.hpp"

namespace SASS {
    constexpr std::string_view func_cv_F16Imm = "F16Imm";
    constexpr std::string_view func_cv_F32Imm = "F32Imm";
    constexpr std::string_view func_cv_F64Imm = "F64Imm";
    constexpr std::string_view func_cv_E6M9Imm = "E6M9Imm";
    constexpr std::string_view func_cv_E8M7Imm = "E8M7Imm";
    constexpr std::string_view func_fb_F16Imm = "F16Imm";
    constexpr std::string_view func_fb_F32Imm = "F32Imm";
    constexpr std::string_view func_fb_F64Imm = "F64Imm";
    constexpr std::string_view func_fb_E6M9Imm = "E6M9Imm";
    constexpr std::string_view func_fb_E8M7Imm = "E8M7Imm";
    constexpr std::string_view func_F16Imm = "F16Imm";
    constexpr std::string_view func_F32Imm = "F32Imm";
    constexpr std::string_view func_F64Imm = "F64Imm";
    constexpr std::string_view func_E6M9Imm = "E6M9Imm";
    constexpr std::string_view func_E8M7Imm = "E8M7Imm";
    constexpr std::string_view func_RSImm = "RSImm";
    constexpr std::string_view func_UImm = "UImm";
    constexpr std::string_view func_SImm = "SImm";
    constexpr std::string_view func_SSImm = "SSImm";
    constexpr std::string_view func_BITSET = "BITSET";

    class Imm {
        static constexpr int FUNC_SIGNED_BIT = 1;
        static constexpr int FUNC_UNSIGNED_BIT = 0;
        static constexpr uint8_t FALSE = static_cast<uint8_t>(0);
        static constexpr uint8_t TRUE = static_cast<uint8_t>(1);
        bool _signed;
        int _bit_len;
        std::string_view _name;
    public:
        Imm(bool signed_, int bit_len, const std::string_view& name) noexcept : _signed(signed_), _bit_len(bit_len), _name(name) {}
        Imm(const Imm& other) noexcept : _signed(other._signed), _bit_len(other._bit_len), _name(other._name) {}
        Imm(Imm&& other) noexcept : _signed(std::move(other._signed)), _bit_len(std::move(other._bit_len)), _name(std::move(other._name)) {}
        Imm& operator=(const Imm& other) noexcept { if(this == &other) return *this; _signed = other._signed; _bit_len = other._bit_len; _name = other._name; return *this; }
        Imm& operator=(Imm&& other) noexcept { if(this == &other) return *this; _signed = std::move(other._signed); _bit_len = std::move(other._bit_len); _name = std::move(other._name); return *this; }
        bool operator==(const Imm& other) const noexcept { if(this == &other) return true; return (_signed == other._signed) && (_bit_len == other._bit_len) && (_name.compare(other._name) == 0); }

        static TDomain get_mock_addr_domain(uint8_t bit_len, uint8_t signed_) {
            uint64_t max_val = 0;
            if(signed_) max_val = static_cast<uint64_t>(std::pow(bit_len-1, 2) - 1);
            else max_val = static_cast<uint64_t>(std::pow(bit_len, 2) - 1);
            return SASS_Range(0L, max_val, bit_len, signed_, 0UL);
        }

        static std::string get_err_msg(const Imm& imm) { return std::vformat("{}::get_domain: [bit_len > 0] required!", std::make_format_args(imm._name)); }

        static TDomain get_func_domain_signed(bool is_address, uint8_t bit_len, bool has_max_val, uint64_t max_val) {
            if(is_address) return Imm::get_mock_addr_domain(bit_len, Imm::TRUE);
            int64_t min_v;
            uint64_t max_v;
            if(has_max_val) {
                max_v = max_val;
                min_v = -static_cast<int64_t>(max_val);
            }
            else {
                max_v = static_cast<uint64_t>(std::pow(bit_len-1, 2) - 1);
                min_v = -static_cast<int64_t>(std::pow(bit_len, 2) - 1);
            }
            return SASS_Range(min_v, max_v, bit_len, 1, 0UL);
        }
            
        static TDomain get_func_domain_unsigned(bool is_address, uint8_t bit_len, bool has_max_val, uint64_t max_val) {
            if(is_address) return Imm::get_mock_addr_domain(bit_len, Imm::FALSE);
            
            if(!has_max_val) max_val = static_cast<uint64_t>(std::pow(bit_len, 2) - 1);
            return SASS_Range(0L, max_val, bit_len, Imm::FALSE, 0UL);
        }

        static int max_addr_bit_len(int bit_len, bool signed_) {
            int res = bit_len;
            if(signed_) res -= 3;
            else res -= 2;
            if(res <= 0) throw std::runtime_error("Imm Func: Invalid bit length");
            return res;
        }

        static std::string get_func_name(const Imm& func) { return std::string(func._name); }
            
        SASS_Bits __call__(SASS_Bits input) const { return SASS_Bits::cast(input, _bit_len); }
        int get_bit_len() const { return _bit_len; }
        int max_addr_bit_len(int bit_len) const { return Imm::max_addr_bit_len(bit_len, true); }
        bool is_signed() const { return _signed; }
        SASS_Bits sign() const { return SASS_Bits::from_int(_signed ? FUNC_SIGNED_BIT : FUNC_UNSIGNED_BIT, 1, 0); }
        virtual std::string __str__() const { return v_str(); } 
        virtual std::string v_str() const { return std::string(_name); } 
        virtual TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const {
            if(is_signed()) return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
            return Imm::get_func_domain_unsigned(is_address, bit_len, has_max_val, max_val);
        }
        virtual SASS_Bits sass_from_bits(const BitVector& bits) const { return SASS_Bits(bits, get_bit_len(), is_signed()); }
    };

    class RSImm : public Imm {
    public:
        RSImm(int bit_len) noexcept : Imm(true, bit_len, func_RSImm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
        }
    };
    class UImm : public Imm {
    public:
        UImm(int bit_len) noexcept : Imm(false, bit_len, func_UImm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            if(max_bit_len > 0 && bit_len > max_bit_len) bit_len = max_bit_len;
            return Imm::get_func_domain_unsigned(is_address, bit_len, has_max_val, max_val);
        }
    };
    class F16Imm : public Imm {
    public:
        F16Imm() noexcept : Imm(true, 16, func_F16Imm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            if(max_bit_len > 0 && bit_len > max_bit_len) bit_len = max_bit_len;
            return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
        }
    };
    class SImm : public Imm {
    public:
        SImm(int bit_len) noexcept : Imm(true, bit_len, func_SImm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            if(max_bit_len > 0 && bit_len > max_bit_len) bit_len = max_bit_len;
            return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
        }
    };
    class SSImm : public Imm {
    public:
        SSImm(int bit_len) noexcept : Imm(true, bit_len, func_SSImm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            if(max_bit_len > 0 && bit_len > max_bit_len) bit_len = max_bit_len;
            return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
        }
    };
    class F64Imm : public Imm {
    public:
        F64Imm() noexcept : Imm(true, 64, func_F64Imm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            if(max_bit_len > 0 && bit_len > max_bit_len) bit_len = max_bit_len;
            return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
        }
    };
    class F32Imm : public Imm {
    public:
        F32Imm() noexcept : Imm(true, 32, func_F32Imm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            if(max_bit_len > 0 && bit_len > max_bit_len) bit_len = max_bit_len;
            return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
        }
    };
    class BITSET : public Imm {
    public:
        BITSET(int bit_len) noexcept : Imm(false, bit_len, func_BITSET) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            return Imm::get_func_domain_unsigned(is_address, bit_len, has_max_val, max_val);
        }
    };
    class E8M7Imm : public Imm {
    public:
        E8M7Imm() noexcept : Imm(true, 16, func_E8M7Imm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            if(max_bit_len > 0 && bit_len > max_bit_len) bit_len = max_bit_len;
            return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
        }
    };
    class E6M9Imm : public Imm {
    public:
        E6M9Imm() noexcept : Imm(true, 16, func_E6M9Imm) {}
        TDomain get_domain(bool is_address, int bit_len, bool has_max_val, int max_val, int max_bit_len) const override {
            if(bit_len == 0) throw std::runtime_error(Imm::get_err_msg(*this));
            if(max_bit_len > 0 && bit_len > max_bit_len) bit_len = max_bit_len;
            return Imm::get_func_domain_signed(is_address, bit_len, has_max_val, max_val);
        }
    };

    const std::set<std::string_view> CONVERT_FUNC = { func_cv_F16Imm, func_cv_F32Imm, func_cv_F64Imm, func_cv_E6M9Imm, func_cv_E8M7Imm };
    const std::set<std::string_view> FIXED_BIT_FUNC = { func_fb_F16Imm, func_fb_F32Imm, func_fb_F64Imm, func_fb_E6M9Imm, func_fb_E8M7Imm };
    const std::set<std::string_view>  FUNC = { func_RSImm, func_UImm, func_F16Imm, func_SImm, func_SSImm, func_F64Imm, func_F32Imm, func_BITSET, func_E8M7Imm, func_E6M9Imm };
    using TFunc = std::variant<RSImm, UImm, F16Imm, SImm, SSImm, F64Imm, F32Imm, BITSET, E8M7Imm, E6M9Imm>;
}