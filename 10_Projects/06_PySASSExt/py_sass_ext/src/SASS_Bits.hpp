#pragma once
#include <stdint.h>
#include <memory>
#include <vector>
#include <exception>
#include <sstream>
#include <tuple>
#include <iostream>
#include <format>
#include <bitset>
#include <type_traits>
#include <utility>
#include <cmath>
#include <string.h>
#include "SASS_Bits_Lib.hpp"

// Use to run the tests
// #define OVERRIDE_BIT

using BitVector = std::vector<uint8_t>;
using IntVector = std::vector<int32_t>;

namespace SASS {
    bool SASS_BITS_WARNINGS = false;
    bool SASS_BITS_COPY_WARNINGS = false;

    class SASS_Bits {
        uint8_t _bit_len;
        bool _signed;
        BitVector _bits;
        int64_t _hash;
        
        public:

        /** 
        * This one covers integers as bits with two's complement, variable number
        * of bits and capped overflow:
        * for bit_len = 3: 100 => -4 but 4 = 011+1 == 0 because of overflow 
        */
        /* regular constructor */
        SASS_Bits(const BitVector& bits, int bit_len, bool signed_) 
        : _bit_len(0), _signed(signed_), _bits(bits), _hash(0)
        {
            if(bit_len == 0) bit_len = static_cast<int>(bits.size());
            if(bit_len < 2 && signed_) throw std::runtime_error("One bit signed value not allowed");
            if(bit_len < bits.size()) throw std::runtime_error("Value must be tuple of at least bit_len length");
            BitVector b(bit_len, 0);
            BitVector::const_iterator i_bits = bits.begin();
            int rem = bit_len - static_cast<int>(bits.size());
            BitVector::iterator ib = b.begin() + rem;
            BitVector::iterator ib_end = b.end();
            while(ib != ib_end){
#ifndef OVERRIDE_BIT
                if(*i_bits != 0 && *i_bits != 1) throw std::runtime_error("Value must be tuple with only 0 and 1");
#endif
                *ib = *i_bits;
                ib++; i_bits++;
            }
            if(b.capacity() != bit_len) throw std::runtime_error("Unexpected: b.capacity() != bit_len");
            _bit_len = bit_len;
            _bits = b;
            _hash = SASS_Bits::__int__(*this);
            if(_bits.size() != bit_len) throw std::runtime_error("Unexpected: _bits.size() != bit_len");

            if(SASS_BITS_COPY_WARNINGS) std::cout << "[WARNING] regular constructor" << std::endl;
        }
        /* copy constructor */
        SASS_Bits(const SASS_Bits& other) noexcept 
        : _bit_len(other._bit_len), _signed(other._signed), _bits(other._bits), _hash(other._hash)
        {
            if(SASS_BITS_COPY_WARNINGS) std::cout << "[WARNING] copy constructor" << std::endl;
        }
        /* move constructor */
        SASS_Bits(const SASS_Bits&& other) noexcept 
        : _bit_len(std::move(other._bit_len)), _signed(std::move(other._signed)), _bits(std::move(other._bits)), _hash(std::move(other._hash))
        {
            if(SASS_BITS_COPY_WARNINGS) std::cout << "[WARNING] move constructor" << std::endl;
        }
        /* copy assignment constructor */
        SASS_Bits operator=(const SASS_Bits& other) noexcept {
            if(SASS_BITS_COPY_WARNINGS) std::cout << "[WARNING] copy assignment" << std::endl;

            if(this == &other) return *this;
            _bits = other._bits;
            _bit_len = other._bit_len;
            _signed = other._signed;
            _hash = other._hash;
            return *this;
        }
        /* move assignment constructor */
        SASS_Bits& operator=(const SASS_Bits&& other) noexcept { 
            if(SASS_BITS_COPY_WARNINGS) std::cout << "[WARNING] move assignment" << std::endl;
            if(this == &other) return *this;
            _bits = std::move(other._bits);
            _bit_len = std::move(other._bit_len);
            _signed = std::move(other._signed);
            _hash = std::move(other._hash);
            return *this;
        }

        bool operator==(const SASS_Bits& other) const {
            if(other._signed != _signed) return false;
            if(other._bit_len != _bit_len) return false;
            if(other._hash != _hash) return false;
            return true;
        }

        bool operator<(const SASS_Bits& other) const {
            return _hash < other._hash;
        }

        static void enable_warnings(){ SASS_BITS_WARNINGS = true; }
        static void disable_warnings(){ SASS_BITS_WARNINGS = false; }
        static void enable_copy_warnings(){ SASS_BITS_COPY_WARNINGS = true; }
        static void disable_copy_warnings(){ SASS_BITS_COPY_WARNINGS = false; }

        /**
         * Get BitVector containing all bits as uint8
         */
        const BitVector& bits() const { return _bits; }
        /**
         * Get bit_len cast as int.
         */
        int bit_len() const { return static_cast<int>(_bit_len); }
        /**
         * Get signed/unsigned cast as bool.
         */
        bool signed_() const { return _signed; }
        /**
         * Get hash value as uint64
         */
        int64_t __hash__() { return _hash; }

        /**
         * Return the size required by the SASS_Bits in bytes if packed into a
         * SASS_Bits_Lib::State.
         */
        static size_t get_bin_state_size(const SASS_Bits& s){
            return static_cast<size_t>(2*sizeof(uint8_t) + sizeof(uint8_t) * s._bits.size());
        }
        
        /**
         * Return the SASS_Bits packed as SASS_Bits_Lib::State.
         */
        static SASS_Bits_Lib::State get_bin_state(const SASS_Bits& s){
            uint8_t len = static_cast<uint8_t>(SASS_Bits::get_bin_state_size(s));
            return SASS_Bits_Lib::State {
                .sign=static_cast<uint8_t>(s._signed ? 1 : 0),
                .bit_len=static_cast<uint8_t>(s._bits.size()),
                .bits = s._bits.data()
            };
        }

        /**
         * Create a SASS_Bits from a SASS_Bits_Lib::State.
         */
        static SASS_Bits set_from_bin_state(const uint8_t* ptr){
            SASS_Bits_Lib::State s = *reinterpret_cast<const SASS_Bits_Lib::State*>(ptr);
            s.bits = ptr+2*sizeof(uint8_t);
            bool sign = (s.sign == 1 ? true : false);
            size_t bit_len = static_cast<size_t>(s.bit_len);
            BitVector bits(bit_len, 0);
            memcpy(bits.data(), s.bits, bit_len);
            return SASS_Bits(bits, static_cast<uint8_t>(bit_len), sign);
        }

        /**
         * Cast the current bits into a new format that is new_bit_len int64_t.
         * - If new_bit_len > bit_len
         *     - If signed     => fill up with msb
         *     - If not signed => fill up with msb
         * - If new_bit_len < bit_len
         *     - If signed
         *     - If val < 0: take abs val, then empty to new_bit_len-1 bits, take the negative value of that
         *     - If val >= 0: empty to new_bit_len-1, return [0] + those bits
         *     - If not signed => take new_bit_len bits
         * - If new_bit_len == bit_len: return a copy of the current one
         */
        static SASS_Bits cast(const SASS_Bits& b, int new_bit_len) {
            SASS_Bits n = b;
            if(new_bit_len > b._bit_len){
                if(n._signed){
                    BitVector new_b(new_bit_len, n._bits[0]);
                    int start = new_bit_len - n._bit_len;
                    for(int i=start; i<new_bit_len; ++i) new_b[i] = n._bits[i-start]; 
                    n._bits = new_b;
                    n._bit_len = new_bit_len;
                }
                else{
                    BitVector new_b(new_bit_len, 0);
                    int start = new_bit_len - n._bit_len;
                    for(int i=start; i<new_bit_len; ++i) new_b[i] = n._bits[i-start]; 
                    n._bits = new_b;
                    n._bit_len = new_bit_len;
                }
            }
            else if(new_bit_len < b._bit_len){
                if(b._signed){
                    n = SASS_Bits::__abs__(n);
                    int old_len = n._bit_len;
                    BitVector::const_iterator beg = n._bits.begin() + (old_len - new_bit_len + 1);
                    BitVector::const_iterator end = n._bits.end();
                    n._bits = BitVector(beg, end);
                    if(b._bits[0] == 1){
                        n._bit_len = new_bit_len - 1;
                        n = SASS_Bits::__neg__(n);
                    }
                    else {
                        n._bit_len = new_bit_len;
                        n._bits.insert(n._bits.begin(), 0);
                        n._bits.shrink_to_fit();
                    }
                }
                else {
                    int old_len = n._bit_len;
                    BitVector::const_iterator beg = n._bits.begin() + (old_len - new_bit_len);
                    BitVector::const_iterator end = n._bits.end();
                    n._bits = BitVector(beg, end);
                    n._bit_len = new_bit_len;
                }
                n._hash = SASS_Bits::__int__(n);
            }
            if(n._bit_len != n._bits.size() || n._bit_len != new_bit_len) throw std::runtime_error("Unexpected: n._bit_len != n._bits.size() || n._bit_len != new_bit_len");
            return n;
        }

        /**
         * Converts SASS_Bits to string with two integers.
         *  - int 1 == bit_len << 8 | signed
         *  - int 2 == value as int64
         */
        static std::string serialize(const SASS_Bits& b){
            uint32_t bb = 0;
            bb = ((b._bit_len & 0b11111111) << 8) | (b._signed & 0b11111111);
            int64_t val = SASS_Bits::__int__(b);
            return std::vformat("{0},{1}", std::make_format_args(bb, val));
        }

        /**
         * Reverse SASS_Bits::serialize into a SASS_Bits
         */
        static SASS_Bits deserialize(const std::string& vals){
            const std::set<char> expected = {'-','1','2','3','4','5','6','7','8','9','0'};
            uint32_t bb = 0;
            int64_t val = 0;
            std::stringstream ss;
            std::vector<std::string> p_vals;
            for(const auto& c : vals){
                if(c == ','){
                    p_vals.push_back(ss.str());
                    ss.str("");
                }
                else{
                    if(!expected.contains(c)) throw std::runtime_error("Unexpected: found character that is not between 0 and 9 and a number");
                    ss << c;
                }
            }
            p_vals.push_back(ss.str());
            ss.str("");

            if(p_vals.size() == 2){
                // cover the new stuff
                int p_vals_0 = std::stoi(p_vals[0]);
                int p_vals_1 = std::stoi(p_vals[1]);
                bb = static_cast<uint32_t>(p_vals_0);
                val = static_cast<int64_t>(p_vals_1);
            }
            else throw std::runtime_error("Unexpected: too many input values for a SASS_Bits");

            int bit_len = static_cast<int>(bb >> 8);
            int signed_ = static_cast<int>(bb & 0b11111111);
            return SASS_Bits::from_int(val, bit_len, signed_);
        }

        /**
         * Interpret the UNCHANGED bits in SASS_Bits as 'unsigned'. Meaning
         * 1101 with bit_len = 4 goes from being -3 to 13.
         */
        static SASS_Bits as_unsigned(const SASS_Bits& b) {
            SASS_Bits n = b;
            n._signed = false;
            n._hash = n.__hash__();
            return n;
        }

        /**
         * Interpret the UNCHANGED bits in SASS_Bits as 'signed'. Meaning
         * 1101 with bit_len = 4 goes from being 13 to -3.
         */
        static SASS_Bits as_signed(const SASS_Bits& b) {
            if(b._bit_len == 1) throw std::runtime_error("Signed value with only 1 bit is not allowed");
            SASS_Bits n = b;
            n._signed = true;
            n._hash = n.__hash__();
            return n;
        }

        /**
         * Change bit representation to unsigned.
         * Negative numbers can't be converted to unsigned. Use at_negate first.
         * This will shorten the bit representation by one bit if the input is signed.
         */
        static SASS_Bits to_unsigned(const SASS_Bits& b) {
            if(b._bits[0] == 1) throw std::runtime_error("Can't convert negative number to unsigned representation. Use abs first!");
            SASS_Bits n = b;
            if(!n._signed) return n;
            n._bits = BitVector(n._bits.begin()+1, n._bits.end());
            n._signed = false;
            n._bit_len--;
            n._hash = n.__hash__();
            return n;
        }

        /**
         * Change bit representation to signed.
         * This will extend the bit representation by one bit if the input is unsigned.
         */
        static SASS_Bits to_signed(const SASS_Bits& b) {
            SASS_Bits n = b;
            if(n._signed) return n;
            n._bits.insert(n._bits.begin(), 0);
            n._bits.shrink_to_fit();
            n._signed = true;
            n._bit_len++;
            n._hash = n.__hash__();
            return n;
        }

        /**
         * Converts int64 to SASS_Bits utilizing two's complement.
         *  - bit_len == 0 => determine automatically
         *  - bit_len < 0 => at least bit_len but more if necessary
         *  - bit_len > 0 => exactly bit_len, throws exception if it doesn't fit
         */
        static SASS_Bits from_int(int64_t val, int bit_len=0, int signed_=-1){
            if(signed_ == 0 && val < 0L) throw std::runtime_error("Can't create unsigned bits for negative value");
            SASS_Bits_Lib::BitPair rr = SASS_Bits_Lib::val_to_bit_vector(val, bit_len, signed_);
            SASS_Bits res = SASS_Bits(rr.bv, rr.bit_len, rr.is_signed);
            return res;
        }

        /**
         * Converts uint64 to SASS_Bits.
         *  - bit_len == 0 => determine automatically
         *  - bit_len < 0 => at least bit_len but more if necessary
         *  - bit_len > 0 => exactly bit_len, throws exception if it doesn't fit
         */
        static SASS_Bits from_uint(uint64_t val, int bit_len=0){
            int signed_ = 0;
            SASS_Bits_Lib::BitPair rr = SASS_Bits_Lib::val_to_bit_vector(val, bit_len, signed_);
            SASS_Bits res = SASS_Bits(rr.bv, rr.bit_len, rr.is_signed);
            return res;
        }

        /**
         * Prints SASS_Bits using _pretty.
         */
        static std::string __str__(const SASS_Bits& b) { 
            return _pretty(b); 
        }

        /**
         * Convert SASS_Bits to signed int64. Wraps around to negative if the value is too large.
         */
        static int64_t __int__(const SASS_Bits& b) {
            if(SASS_BITS_WARNINGS && !b._signed && b._bit_len ==64) std::cout << "[WARNING] Converted uint with 64 bit to int64 => sign overflow, better use __uint__!" << std::endl;
            return SASS_Bits_Lib::to_int(b._bits, b._signed, static_cast<int>(b._bit_len));
        }
        /**
         * Convert SASS_Bits to uint64. Utilizes two's complement.
         */
        static uint64_t __uint__(const SASS_Bits& b) {
            if(SASS_BITS_WARNINGS && b._signed) std::cout << "[WARNING] Converted int64 to uint64 => better use __int__!" << std::endl;
            return SASS_Bits_Lib::to_uint(b._bits, b._signed, static_cast<int>(b._bit_len));
        }
        /**
         * Convert SASS_Bits to bool. True if != 0, False if == 0.
         */
        static bool __bool__(const SASS_Bits& b) {
            if(__int__(b) != 0) return true;
            return false;
        }
        /**
         * Compares if two SASS_Bits are equal.
         * Equal if:
         *  - signed/unsigned is the same
         *  - bit_len is the same
         *  - hash is the same
         */
        static bool __eq__(const SASS_Bits& b, const SASS_Bits& other) {
            return b == other;
        }
        
        static SASS_Bits __add__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return SASS_Bits::from_int(__int__(b) + __int__(other), -std::max(b._bit_len, other._bit_len)); }
        static SASS_Bits __add__i(const SASS_Bits& b, const int& other){ 
            return SASS_Bits::from_int(__int__(b) + other, -b._bit_len); }
        static SASS_Bits __add__b(const SASS_Bits& b, const bool& other){ 
            return SASS_Bits::from_int(__int__(b) + int(other), -b._bit_len); }

        static SASS_Bits __sub__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return SASS_Bits::from_int(__int__(b) - __int__(other), -std::max(b._bit_len, other._bit_len)); }
        static SASS_Bits __sub__i(const SASS_Bits& b, const int& other){ 
            return SASS_Bits::from_int(__int__(b) - other, -b._bit_len); }
        static SASS_Bits __sub__b(const SASS_Bits& b, const bool& other){ 
            return SASS_Bits::from_int(__int__(b) - int(other), -b._bit_len); }

        static SASS_Bits __mul__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return SASS_Bits::from_int(__int__(b) * __int__(other), -std::max(b._bit_len, other._bit_len)); }
        static SASS_Bits __mul__i(const SASS_Bits& b, const int& other){ 
            return SASS_Bits::from_int(__int__(b) * other, -b._bit_len); }
        static SASS_Bits __mul__b(const SASS_Bits& b, const bool& other){ 
            return SASS_Bits::from_int(__int__(b) * int(other), -b._bit_len); }

        static SASS_Bits __matmul__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return SASS_Bits::from_int(__int__(b) * __int__(other), -std::max(b._bit_len, other._bit_len)); }
        static SASS_Bits __matmul__i(const SASS_Bits& b, const int& other){ 
            return SASS_Bits::from_int(__int__(b) * other, -b._bit_len); }
        static SASS_Bits __matmul__b(const SASS_Bits& b, const bool& other){ 
            return SASS_Bits::from_int(__int__(b) * int(other), -b._bit_len); }

        static SASS_Bits __truediv__(const SASS_Bits& b, const SASS_Bits& other){ 
            throw std::runtime_error("Truediv [a / b] is not supported in SASS_Bits"); }

        static SASS_Bits __floordiv__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return SASS_Bits::from_int(__int__(b) / __int__(other), -std::max(b._bit_len, other._bit_len)); }
        static SASS_Bits __floordiv__i(const SASS_Bits& b, const int& other){ 
            return SASS_Bits::from_int(__int__(b) / other, -b._bit_len); }
        static SASS_Bits __floordiv__b(const SASS_Bits& b, const bool& other){ 
            return SASS_Bits::from_int(__int__(b) / int(other), -b._bit_len); }

        static SASS_Bits __mod__sb(const SASS_Bits& b, const SASS_Bits& other){
            int64_t res = SASS_Bits_Lib::mod_f(__int__(b), __int__(other));
            return SASS_Bits::from_int(res, -std::max(b._bit_len, other._bit_len)); }
        static SASS_Bits __mod__i(const SASS_Bits& b, const int& other){ 
            int64_t res = SASS_Bits_Lib::mod_f(__int__(b), other);
            return SASS_Bits::from_int(res, -b._bit_len); }
        static SASS_Bits __mod__b(const SASS_Bits& b, const bool& other){ 
            int64_t res = SASS_Bits_Lib::mod_f(__int__(b), int(other));
            return SASS_Bits::from_int(res, -b._bit_len); }

        static SASS_Bits __divmod__(const SASS_Bits& b, const SASS_Bits& other){ 
            throw std::runtime_error("Divmod [divmod(a,b)] is not supported in SASS_Bits"); }
        static SASS_Bits __pow__(const SASS_Bits& b, const SASS_Bits& other){ 
            throw std::runtime_error("Pow [a**b] is not supported in SASS_Bits"); }

        static SASS_Bits __and__(const SASS_Bits& b, const SASS_Bits& other){ 
            int req_bit_len = std::max(b._bit_len, other._bit_len);
            return SASS_Bits::from_int(SASS_Bits::__int__(b) & SASS_Bits::__int__(other), req_bit_len, b._signed || other._signed);
        }

        static SASS_Bits __xor__(const SASS_Bits& b, const SASS_Bits& other){ 
            int req_bit_len = std::max(b._bit_len, other._bit_len);
            return SASS_Bits::from_int(SASS_Bits::__int__(b) ^ SASS_Bits::__int__(other), req_bit_len, b._signed || other._signed);
        }

        static SASS_Bits __or__(const SASS_Bits& b, const SASS_Bits& other){ 
            int req_bit_len = std::max(b._bit_len, other._bit_len);
            return SASS_Bits::from_int(SASS_Bits::__int__(b) | SASS_Bits::__int__(other), req_bit_len, b._signed || other._signed);
        }
        
        static SASS_Bits __neg__(const SASS_Bits& b) {
            if(b._signed){
                return SASS_Bits::from_int(-SASS_Bits::__int__(b), -b._bit_len);
            }
            else {
                int64_t val = SASS_Bits::__int__(b);
                if(val >= 0) return SASS_Bits::from_int(-val, -(b._bit_len+1));
                else throw std::runtime_error("It's not possible to make an unsigned value negative => unexpected");
            }
        }

        static SASS_Bits __pos__(const SASS_Bits& b){ 
            return b;
        }

        static SASS_Bits __abs__(const SASS_Bits& b) {
            int64_t val = static_cast<int64_t>(std::abs(SASS_Bits::__int__(b)));
            return SASS_Bits::from_int(val, -(b._bit_len-1), 0);
        }

        /**
         * Bitwise left-shift by keeping signed/unsigned properties while increasing
         * bit_len to match if necessary.
         */
        static SASS_Bits __lshift__(const SASS_Bits& b, const int& num){ 
            if(b._signed) throw std::runtime_error("Bitshift is not defined for negative numbers");
            if(num < 0) throw std::runtime_error("Bitshift is not defined for negative offsets");
            return SASS_Bits::from_int(__int__(b) << num, -b._bit_len);
        }

        /**
         * Bitwise right-shift by keeping signed/unsigned properties while also keeping
         * bit_len the same. For example: 4 >> 1 == 2, -4 >> 1 == -66 (Note: this is different
         * from the regular Python >>. For the equivalent Python >> for negative numbers,
         * use int(-(SASS_Bits.from_int(-4, bit_len=8).at_abs() >> 1)))
         */
        static SASS_Bits __rshift__(const SASS_Bits& b, const int& num){ 
            if(b._signed) throw std::runtime_error("Bitshift is not defined for negative numbers");
            if(num < 0) throw std::runtime_error("Bitshift is not defined for negative offsets");
            return SASS_Bits::from_int(__int__(b) >> num, -b._bit_len);
        }

        static bool __lt__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return __int__(b) < __int__(other); }
        static bool __lt__i(const SASS_Bits& b, const int& other){ 
            return __int__(b) < other; }
        static bool __lt__b(const SASS_Bits& b, const bool& other){ 
            return __int__(b) < int(other); }

        static bool __le__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return __int__(b) <= __int__(other); }
        static bool __le__i(const SASS_Bits& b, const int& other){ 
            return __int__(b) <= other; }
        static bool __le__b(const SASS_Bits& b, const bool& other){ 
            return __int__(b) <= int(other); }

        static bool __eq__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return __int__(b) == __int__(other); }
        static bool __eq__i(const SASS_Bits& b, const int& other){ 
            return __int__(b) == other; }
        static bool __eq__b(const SASS_Bits& b, const bool& other){ 
            return __int__(b) == int(other); }

        static bool __ne__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return __int__(b) != __int__(other); }
        static bool __ne__i(const SASS_Bits& b, const int& other){ 
            return __int__(b) != other; }
        static bool __ne__b(const SASS_Bits& b, const bool& other){ 
            return __int__(b) != int(other); }

        static bool __gt__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return __int__(b) > __int__(other); }
        static bool __gt__i(const SASS_Bits& b, const int& other){ 
            return __int__(b) > other; }
        static bool __gt__b(const SASS_Bits& b, const bool& other){ 
            return __int__(b) > int(other); }

        static bool __ge__sb(const SASS_Bits& b, const SASS_Bits& other){ 
            return __int__(b) >= __int__(other); }
        static bool __ge__i(const SASS_Bits& b, const int& other){ 
            return __int__(b) >= other; }
        static bool __ge__b(const SASS_Bits& b, const bool& other){ 
            return __int__(b) >= int(other); }

        /**
         * Fill instruction bits back-to-front (or maybe Nvidia's front-to-back??)
         */
        static BitVector assemble(SASS_Bits b, BitVector instr_bits, const IntVector& enc_inds, const int& sm_nr) {
            if(enc_inds.size() == 0) throw std::runtime_error("Illegal: len(enc_inds) > 0 required but [len(enc_inds) == 0]");
            BitVector::const_iterator ib_begin = b._bits.begin();
            BitVector::const_iterator ib = b._bits.end()-1;
            IntVector::const_iterator ie_begin = enc_inds.begin();
            IntVector::const_iterator ie = enc_inds.end()-1;
            int sanity_counter = 0;
            while(true) {
                if(sanity_counter > 200) throw std::runtime_error("Unexpected: sanity_counter out of range");
                if(*ie < 0 || *ie >= instr_bits.size()) throw std::runtime_error("Unexpected: *ie < 0 || *ie >= nn.size()");
                instr_bits[*ie] = *ib;
                if(ie == ie_begin || ib == ib_begin) break;
                ie--;
                ib--;
                sanity_counter++;
            };
            return instr_bits;
        }

        /**
         * Emulate the MULTIPLY thing in the definition of the SASS that occurs sometimes in the
         * encodings.
         * Like "TidB = tid MULTIPLY 4 SCALE 4;"
         *
         * This is a left-shift by log2(val) bits without changing the bit length.
         */
        static SASS_Bits multiply(const SASS_Bits& b, const int& val) {
            // if not isinstance(val, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            // if not val % 2 == 0: raise ValueError("Invalid argument")
            // if val <= 0: raise ValueError("Invalid argument")
            // shift = int(math.log(val,2))
            if(val % 2 != 0) throw std::runtime_error(std::vformat("Illegal: val must be multiple of 2 but is {0}", std::make_format_args(val)));
            if(val <= 0) throw std::runtime_error(std::vformat("Illegal: val must be greater than 0 but is {0}", std::make_format_args(val))); 
            int shift = static_cast<int>(std::log2(val));
            if(b._signed && b._bits[0] == 1){
                // this will shave off the signed bit
                SASS_Bits n = SASS_Bits::__abs__(b);
                BitVector nb = BitVector(n._bit_len, 0);
                auto bb = n._bits.begin() + shift;
                if(bb < n._bits.end())
                    std::copy(bb, n._bits.end(), nb.begin());
                n._bits = nb;
                n = SASS_Bits::__neg__(n);
                return n;
            } else {
                SASS_Bits n = b;
                n._bits = BitVector(n._bit_len, 0);
                auto bb = b._bits.begin() + shift;
                if(bb < b._bits.end())
                    std::copy(bb, b._bits.end(), n._bits.begin());
                return n;
            }
        }

        /**
         * Emulate the SCALE thing in the definition of the SASS that occurs sometimes in the
         * encodings.
         * Like "TidB = tid MULTIPLY 4 SCALE 4;"
         *
         * This is a right-shift by log2(val) bits without changing the bit length.
         */
        static SASS_Bits scale(const SASS_Bits& b, const int& val) {
            if(val % 2 != 0) throw std::runtime_error(std::vformat("Illegal: val must be multiple of 2 but is {0}", std::make_format_args(val)));
            if(val <= 0) throw std::runtime_error(std::vformat("Illegal: val must be greater than 0 but is {0}", std::make_format_args(val))); 
            int shift = static_cast<int>(std::log2(val));
            if(b._signed && b._bits[0] == 1){
                // this will shave off the signed bit
                SASS_Bits n = SASS_Bits::__abs__(b);
                BitVector nb = BitVector(n._bit_len, 0);
                auto bb = nb.begin() + shift;
                if(bb < nb.end())
                    std::copy(n._bits.begin(), n._bits.end()-shift, bb);
                n._bits = nb;
                n = SASS_Bits::__neg__(n);
                return n;
            } else {
                SASS_Bits n = b;
                n._bits = BitVector(n._bit_len, 0);
                auto bb = n._bits.begin() + shift;
                if(bb < n._bits.end())
                    std::copy(b._bits.begin(), b._bits.end()-shift, bb);
                return n;
            }
        }

        private:
        /**
         * Print SASS_Bits in some pretty way, including all relevant information
         */
        static std::string _pretty(const SASS_Bits& sb) {
            int val = SASS_Bits::__int__(sb);
            char s = sb.signed_() ? 'S' : 'U';
            int len = sb.bit_len();
            return std::vformat("{0}{1}:{2}b", std::make_format_args(val, s, len));
        }
    };
}

namespace std {
    template <>
    struct less<SASS::SASS_Bits> {
        bool operator()(const SASS::SASS_Bits& lhs, const SASS::SASS_Bits& rhs) const {
            return SASS::SASS_Bits::__le__sb(lhs, rhs);
        }
    };
}