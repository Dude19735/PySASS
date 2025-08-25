#pragma once
#include <stdint.h>
#include <memory>
#include <vector>
#include <exception>
#include <tuple>
#include <iostream>
#include <format>
#include <bitset>
#include <type_traits>
#include <utility>
#include <cmath>
#include <string.h>

// Use to run the tests
// #define OVERRIDE_BIT

using BitVector = std::vector<uint8_t>;
using IntVector = std::vector<int32_t>;

namespace SASS {
    class SASS_Bits_Lib {
        public:

        struct BitPair {
            int bit_len;
            bool is_signed;
            BitVector bv;
        };

        struct State {
            const uint8_t sign;
            const uint8_t bit_len;
            const uint8_t* bits;
        };

        static BitVector uval_to_bit_vector(uint64_t val, size_t bit_len) {
            std::string val_b = std::bitset<sizeof(uint64_t) * 8>(val).to_string();
            val_b = val_b.substr(val_b.size()-bit_len);
            BitVector bv;
            for(const auto& b : val_b) bv.push_back(static_cast<uint8_t>(b) - 48);
            return bv;
        }

        static BitVector sval_to_bit_vector(int64_t val, size_t bit_len) {
            std::string val_b = std::bitset<sizeof(int64_t) * 8>(val).to_string();
            val_b = val_b.substr(val_b.size()-bit_len);
            BitVector bv;
            for(const auto& b : val_b) bv.push_back(static_cast<uint8_t>(b) - 48);
            return bv;
        }

        static BitPair val_to_bit_vector(int64_t val, int bit_len=0, int signed_=-1) {
            if(signed_ != -1 && signed_ != 0 && signed_ != 1) throw std::runtime_error("Signed must be a value in {-1,0,1}");
            if(bit_len == 1 && signed_ == 1) throw std::runtime_error("Signed representation requires at least 2 bits!");

            bool is_neg = val < 0;
            bool val_signed = false;
            if(is_neg){
                if(signed_ == -1) val_signed = true;
                else if(signed_ == 1) val_signed = true;
                else if(signed_ == 0) val_signed = false;
                else throw std::runtime_error("Non covered signed case");
            }
            else{
                if(signed_ == 1) val_signed = true;
                else val_signed = false;
            }

            std::string val_b = std::bitset<sizeof(int64_t) * 8>(val).to_string();
            int req_bit_len = SASS_Bits_Lib::req_bit_len(val, val_signed);
            if(bit_len == 0) bit_len = req_bit_len;
            else if(bit_len < 0) bit_len = std::max(std::abs(bit_len), req_bit_len);
            else if(bit_len > 0) {
                if (req_bit_len > bit_len) throw std::runtime_error(std::vformat("Insufficient bit_len {0} for value {1}", std::make_format_args(bit_len, val)));
            }
            else throw std::runtime_error("This never happens");

            val_b = val_b.substr(val_b.size()-bit_len);
            BitVector bv;
            for(const auto& b : val_b){
                bv.push_back(static_cast<uint8_t>(b) - 48);
            }
            return BitPair{.bit_len=bit_len, .is_signed=val_signed, .bv=bv};
        }

        static int64_t to_int(const BitVector& bv, bool signed_, int bit_len){
            int64_t res = 0;
            for(int i=0; i<bit_len-1; ++i) 
                res += static_cast<int64_t>(bv[bit_len - i - 1]) << i;
            if(signed_ && bv[0] == 1)
                res = res - (1UL << (bit_len-1));
            else res += static_cast<int64_t>(bv[0]) << (bit_len-1);
            return res;
        }

        static uint64_t to_uint(const BitVector& bv, bool signed_, int bit_len){
            uint64_t res = 0;
            for(int i=0; i<bit_len-1; ++i) 
                res += static_cast<int64_t>(bv[bit_len - i - 1]) << i;
            if(signed_ && bv[0] == 1)
                res = res - (1UL << (bit_len-1));
            else res += static_cast<int64_t>(bv[0]) << (bit_len-1);
            return res;
        }

        static int req_bit_len(int64_t val, bool val_signed) {
            int counter = 1;
            if(val > 0){
                // take the at least 1 bit
                counter = std::max(1, static_cast<int>(std::floor(std::log2(val) + 1.f)));
                if(val_signed) counter++;
            } else if(val < 0){
                // find framing power of two of the positive number starting with 2
                int64_t valp = -val;
                int64_t bla = 1;
                while(bla < valp && bla > 0) {
                    bla <<= 1;
                    counter++;
                }
                // we have one signed bit no matter what.
                counter = std::max(2, counter);
            } else {
                if(val_signed) counter = 2;
                else counter = 1;
            }
            return counter;
        }

        static int64_t mod(const int64_t a, const int64_t b) {
            if(b == 0) throw std::runtime_error(std::vformat("[other] operand of modulo operation must be non-zero but is {0}", std::make_format_args(b)));
            if(a == 0) return 0;
            // ((n % M) + M) % M
            auto abs_res = std::abs(a) % std::abs(b);
            int64_t res = 0;
            if(a < 0 && b > 0) res = b-abs_res;
            else if(a < 0 && b < 0) res = -abs_res;
            else if(a > 0 && b < 0) res = b+abs_res;
            else res = abs_res;
            return res;
        }

        static int64_t mod_f(const int64_t a, const int64_t b) {
            if(b == 0) throw std::runtime_error(std::vformat("[other] operand of modulo operation must be non-zero but is {0}", std::make_format_args(b)));
            if(a == 0) return 0;
            return ((a % b) + b) % b;
        }

        static int64_t mod_uf(const uint64_t a, const uint64_t b) {
            if(b == 0) throw std::runtime_error(std::vformat("[other] operand of modulo operation must be non-zero but is {0}", std::make_format_args(b)));
            if(a == 0) return 0;
            return ((a % b) + b) % b;
        }
    };
}