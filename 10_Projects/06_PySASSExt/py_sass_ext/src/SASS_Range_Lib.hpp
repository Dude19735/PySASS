#pragma once
#include <stdint.h>
#include <exception>
#include <vector>
#include <format>
#include <cmath>
#include <random>
#include <time.h>
#include <numeric>
#include <algorithm>
#include <sstream>
#include "SASS_Bits.hpp"

namespace SASS {
    struct SASS_Range_Limits {
        int64_t range_min;
        int64_t effective_min;
        uint64_t range_max;
        uint64_t effective_max;
        uint64_t size;
        bool size_overflow;
    };

    struct SASS_Effective_Sample {
        int64_t s_min;
        uint64_t s_max;
    };

    /**
     * WLOG assume SASS_Range(-5, 6, 5, 1, 4).
     * Check out struct SASS_Range_Limits at the top of this file.
     * 
     * Without a mask, this range contains
     * 11011 : -5 => SASS_Range::range_min
     * 11100 : -4
     * 11101 : -3
     * 11110 : -2
     * 11111 : -1
     * 00000 :  0
     * 00001 :  1
     * 00010 :  2
     * 00011 :  3
     * 00100 :  4
     * 00101 :  5
     * 00110 :  6 => SASS_Range::range_max
     * 
     * The following metrics are calculated largely by SASS_Range_Lib::effective_range()
     * =================================================================================
     * Applying mask 4 = 00100 removes all entries that have a 1 in that location
     * 11011 : -5 => SASS_Range_Limits::range_min (calculated by SASS_Range_Lib::next_best_test_u/s)
     * 00000 :  0
     * 00001 :  1
     * 00010 :  2
     * 00011 :  3 => SASS_Range_Limits::range_min (calculated by SASS_Range_Lib::previous_best_test_u)
     * 
     * Now remove the bits that are forced to 0 by the bitmask
     * 1111 : -1 => SASS_Range_Limits::effective_min (calculated by SASS_Range_Lib::next_best_test_u/s)
     * 0000 :  0
     * 0001 :  1
     * 0010 :  2
     * 0011 :  3 => SASS_Range_Limits::effective_max (calculated by SASS_Range_Lib::previous_best_test_u)
     * 
     * SASS_Range_Limits.size = SASS_Range_Limits::effective_max - SASS_Range_Limits::effective_min + 1
     * SASS_Range_Limits.size = 3 - (-1) + 1 = 5
     * 
     * With these metrics, the SASS_Range can be uniformly sampled by simply selecting random bits.
     * The following is calculated by SASS_Range_Lib::pick()
     * =====================================================
     * 1. pick v uniformly at random in [0, SASS_Range_Limits::size-1]
     *    => v in [0,4] (inclusive)
     * 2. add v to the effective_min
     *    => val = -1 + v => val in [-1, 3]
     * 3. add back zeros where the bitmask is 1
     *    => bit_mask = 0b00100
     *    => val in [11[0]11, 00[0]00, 00[0]01, 00[0]10, 00[0]11]
     * 4. return the stuffed val as SASS_Bits
     * 
     * Inspirational sources
     * =====================
     * https://www.exploringbinary.com/twos-complement-converter/
     * https://stackoverflow.com/questions/73666911/how-can-i-quickly-find-the-smallest-integer-satisfying-a-bitmask-and-greater-tha
     * 
     */
    class SASS_Range_Lib {
        public:
        static bool contains(
            const uint8_t& signed_, 
            const int64_t& min_val, const uint64_t& max_val, const int64_t& range_min, const uint64_t& range_max,
            const uint64_t& bit_mask,
            const SASS_Bits& val, bool throw_on_error
        ){
            // sign must match
            if(static_cast<bool>(signed_) != val.signed_()) {
                return false;
            }
            // check everything else
            int64_t val_int = SASS::SASS_Bits::__int__(val);
            if(val_int < range_min) {
                if(throw_on_error) throw std::runtime_error("Unexpected: val_int < r._range_min");
                return false;
            }
            if(val_int >= 0 && static_cast<uint64_t>(val_int) > range_max) {
                if(throw_on_error) throw std::runtime_error("Unexpected: val_int >= 0 && static_cast<uint64_t>(val_int) > r._range_max");
                return false;
            }
            if(val.signed_()){
                const auto s_max_val = static_cast<int64_t>(max_val);
                bool c1 = (min_val <= val_int);
                bool c2 = (val_int <= s_max_val);
                const bool condition = (c1 && c2);
                if(!condition) {
                    if(throw_on_error) throw std::runtime_error("Unexpected: (min_val <= val_int) || (val_int <= s_max_val)");
                    return false;
                }
                if(bit_mask > 0){
                    const auto mval = (val_int & bit_mask);
                    if(mval != 0) {
                        if(throw_on_error) throw std::runtime_error("Unexpected: (val_int & r._bit_mask) != 0");
                        return false;
                    }
                }
            }
            else {
                uint64_t u_val_int = static_cast<uint64_t>(val_int);
                const bool condition = ((0 <= u_val_int) && (u_val_int <= max_val));
                if(!condition) {
                    if(throw_on_error) throw std::runtime_error("Unexpected: (0 <= u_val_int) && (u_val_int <= max_val)");
                    return false;
                }
                if(bit_mask > 0){
                    const auto mval = (u_val_int & bit_mask);
                    if(mval != 0) {
                        if(throw_on_error) throw std::runtime_error("Unexpected: (u_val_int & r._bit_mask) != 0");
                        return false;
                    }
                }
            }
            return true;
        }

        static uint64_t next_best_test_u(uint64_t floor, uint64_t max_val, uint64_t mask, bool& success, uint64_t& i){
            success = false;
            uint64_t res = floor; // NOTE: different sign to next_best_test_s
            if((floor & mask) != 0){
                int iiv = (63 - __builtin_clzll(floor & mask));
                const uint64_t ll = 1UL<<iiv;
                res = ((floor | mask) + (floor & ll)) & (~mask);
                res &= ~(ll - 1);
            }
            if(res <= max_val) success = true;
            return res;
        }

        static uint64_t previous_best_test_u(uint64_t ceil, uint64_t min_val, uint64_t mask, bool& success, uint64_t& i){
            uint64_t res = ceil;
            success = false;
            if((ceil & mask) != 0){
                uint64_t floor = (ceil & ~mask);

                res = floor;
                uint64_t iiv = 63 - __builtin_clzll(ceil & mask);
                uint64_t nmask = ~mask & ((1UL<<iiv)-1);
                res |= nmask;
            }

            if(res >= min_val) success = true;
            return res;
        }
        
        static int64_t next_best_test_s(int64_t floor, int64_t max_val, uint64_t mask, bool& success, int64_t& i){
            success = false;
            int64_t res = floor; // NOTE: different sign to next_best_test_u
            if((floor & mask) != 0){
                int iiv = (63 - __builtin_clzll(floor & mask));
                const uint64_t ll = 1UL<<iiv;
                res = ((floor | mask) + (floor & ll)) & (~mask);
                res &= ~(ll - 1);
            }
            if(res <= max_val) success = true;
            return res;
        }

        static const SASS_Effective_Sample apply_effective_sample(
            int64_t mm_min_t, uint64_t mm_max_t, 
            uint64_t bit_mask, const BitVector& bit_mask_bits, uint8_t bit_len, uint8_t bm_len, bool negative_min
        ){
            BitVector mm_min_v = SASS_Bits_Lib::uval_to_bit_vector(static_cast<uint64_t>(mm_min_t), bit_len);
                BitVector mm_max_v = SASS_Bits_Lib::uval_to_bit_vector(mm_max_t, bit_len);
                BitVector::const_iterator mm_min_v_ii = mm_min_v.begin();
                BitVector::const_iterator mm_max_v_ii = mm_max_v.begin();

                BitVector mm_min_v_nb;
                BitVector mm_max_v_nb;
                if(bit_mask == (((1UL << (bit_len-1))-1)<<1)+1){
                    // Entire bitmask is made up of 1s => only remaining value is 0
                    // If 0 doesn't exist, we never get to this stage
                    mm_min_v_nb = BitVector(bit_len, 0);
                    mm_max_v_nb = BitVector(bit_len, 0);
                } else {
                    for(const auto& b : bit_mask_bits){
                        if(b==0){
                            mm_min_v_nb.push_back(*mm_min_v_ii);
                            mm_max_v_nb.push_back(*mm_max_v_ii);
                        }
                        mm_min_v_ii++;
                        mm_max_v_ii++;
                    }
                }

                int64_t res_min = SASS_Bits_Lib::to_int(mm_min_v_nb, negative_min, bit_len-bm_len);
                uint64_t res_max = static_cast<uint64_t>(SASS_Bits_Lib::to_int(mm_max_v_nb, false, bit_len-bm_len));
            
            return SASS_Effective_Sample {
                .s_min = res_min,
                .s_max = res_max
            };
        }

        static SASS_Range_Limits effective_range(
            const int64_t& min_val, const uint64_t& max_val, const uint8_t signed_,
            const uint64_t& bit_mask, const BitVector& bit_mask_bits, 
            const uint8_t& bit_len, const uint8_t& bm_len
        ){
            if(min_val < 0 && signed_==1) {
                bool success;
                int64_t i_s;
                int64_t mm_min_t = next_best_test_s(min_val, max_val, bit_mask, success, i_s);
                if(!success) return SASS_Range_Limits{.range_min=0, .effective_min=0, .range_max=0, .effective_max=0, .size=0};
                uint64_t i_u;
                uint64_t mm_max_t = previous_best_test_u(max_val, 0, bit_mask, success, i_u);
                if(!success) return SASS_Range_Limits{.range_min=0, .effective_min=0, .range_max=0, .effective_max=0, .size=0};

                const SASS_Effective_Sample sam = apply_effective_sample(mm_min_t, mm_max_t, bit_mask, bit_mask_bits, bit_len, bm_len, true);
                
                uint64_t res = static_cast<int64_t>(sam.s_max);
                if(sam.s_min < 0){
                    res += static_cast<uint64_t>(-sam.s_min);
                }
                else{
                    res += static_cast<uint64_t>(sam.s_min);
                }
                bool size_overflow = false;
                if(res == std::numeric_limits<uint64_t>::max())
                    size_overflow = true;
                res++;

                return SASS_Range_Limits{
                    .range_min=mm_min_t, 
                    .effective_min=sam.s_min,
                    .range_max=static_cast<uint64_t>(mm_max_t), 
                    .effective_max=static_cast<uint64_t>(sam.s_max),
                    .size=static_cast<uint64_t>(res),
                    .size_overflow=size_overflow
                };
            }
            else {
                bool success;
                uint64_t i_s;
                uint64_t u_min_val = static_cast<uint64_t>(min_val);
                uint64_t mm_min_t = next_best_test_u(u_min_val, max_val, bit_mask, success, i_s);
                if(mm_min_t < u_min_val) return SASS_Range_Limits{.range_min=0, .effective_min=0, .range_max=0, .effective_max=0, .size=0};
                if(!success) return SASS_Range_Limits{.range_min=0, .effective_min=0, .range_max=0, .effective_max=0, .size=0};
                uint64_t i_u;
                uint64_t mm_max_t = previous_best_test_u(max_val, 0, bit_mask, success, i_u);
                if(!success) return SASS_Range_Limits{.range_min=0, .effective_min=0, .range_max=0, .effective_max=0, .size=0};

                const SASS_Effective_Sample sam = apply_effective_sample(mm_min_t, mm_max_t, bit_mask, bit_mask_bits, bit_len, bm_len, false);

                uint64_t res = sam.s_max - static_cast<uint64_t>(sam.s_min);
                bool size_overflow = false;
                if(res == std::numeric_limits<uint64_t>::max())
                    size_overflow = true;
                res++;
                
                return SASS_Range_Limits{
                    .range_min=static_cast<int64_t>(mm_min_t),
                    .effective_min=sam.s_min,
                    .range_max=mm_max_t,
                    .effective_max=sam.s_max,
                    .size=res,
                    .size_overflow=size_overflow
                };
            }
        }

        static SASS_Bits reverse_effective_sample(
            const uint64_t sample_val, 
            const SASS_Range_Limits& r_limits, 
            const uint8_t bit_len, const BitVector& bit_mask_bits, const uint8_t bm_len,
            const uint8_t signed_, bool throw_on_error)
        {
            bool r_signed = (signed_ == 1 ? true : false);
            if(r_limits.range_min < 0 && r_signed==1){
                int64_t mm_unstuffed = r_limits.effective_min + static_cast<int64_t>(sample_val);
                BitVector mm_unstuffed_bv = SASS_Bits_Lib::uval_to_bit_vector(static_cast<uint64_t>(mm_unstuffed), bit_len-bm_len);
                BitVector val_bv = reverse_bitmask(bit_mask_bits, bm_len, mm_unstuffed_bv, bit_len);
                if(throw_on_error){
                    int64_t res = SASS_Bits_Lib::to_int(val_bv, r_signed, bit_len);
                    if(res < r_limits.range_min || (res >= 0 && static_cast<uint64_t>(res) > r_limits.range_max)){
                        throw std::runtime_error("Unexpected: res < r_limits.range_min || (res >= 0 && static_cast<uint64_t>(res) > r_limits.range_max)");
                    }
                }
                return SASS_Bits(val_bv, bit_len, r_signed);
            }
            else{
                uint64_t mm_unstuffed = static_cast<uint64_t>(r_limits.effective_min) + sample_val;
                BitVector mm_unstuffed_bv = SASS_Bits_Lib::uval_to_bit_vector(mm_unstuffed, bit_len-bm_len);
                BitVector val_bv = reverse_bitmask(bit_mask_bits, bm_len, mm_unstuffed_bv, bit_len);
                if(throw_on_error){
                    uint64_t res = static_cast<uint64_t>(SASS_Bits_Lib::to_int(val_bv, r_signed, bit_len));
                    if(res < static_cast<uint64_t>(r_limits.range_min) || res > r_limits.range_max){
                        throw std::runtime_error("Unexpected: res < static_cast<uint64_t>(r_limits.range_min) || res > r_limits.range_max");
                    }
                }
                return SASS_Bits(val_bv, bit_len, r_signed);
            }
        }

        static SASS_Bits pick(
            std::default_random_engine* generator, 
            const SASS_Range_Limits& r_limits, 
            const uint8_t& bit_len, const uint8_t& bm_len, 
            const uint64_t& bit_mask, const BitVector& bit_mask_bits,
            const uint8_t& signed_,
            bool throw_on_error
        ){
            // this used to be:
            //   auto dist = std::uniform_int_distribution<uint64_t>(0, r_limits.size-1);
            // because of overflows in the calculate_limits, we removed it.
            uint64_t size = r_limits.size-1;
            if(r_limits.size_overflow) size = std::numeric_limits<uint64_t>::max();

            auto dist = std::uniform_int_distribution<uint64_t>(0, size);
            uint64_t val = dist(*generator);
            return reverse_effective_sample(val, r_limits, bit_len, bit_mask_bits, bm_len, signed_, throw_on_error);
        }

        static BitVector reverse_bitmask(const BitVector& bitmask, const uint8_t& bm_len, const BitVector& source, const uint8_t& bit_len){
            // If we have no bitmask, return the source vector directly
            if(bitmask.size() == 1 && bitmask.at(0) == 0) return source;

            // Generate a list that includes the bit mask bits
            BitVector target(bit_len, 0);
            BitVector::const_reverse_iterator bm_i = bitmask.rbegin();
            BitVector::const_reverse_iterator sr_i = source.rbegin();
            BitVector::reverse_iterator tr_i = target.rbegin();

            if(bitmask.size() != target.size()) {
                std::cout << bitmask.size() << " " << target.size() << std::endl;
                throw std::runtime_error("Unexpected: bitmask.size() != target.size()");
            }
            while(bm_i != bitmask.rend()){
                if(*bm_i == 0 && sr_i != source.rend()){
                    *tr_i = *sr_i;
                    ++sr_i;
                }
                ++bm_i;
                ++tr_i;
            }

            if(sr_i != source.rend()) throw std::runtime_error("Unexpected: sr_i != source.rend()");
            if(tr_i != target.rend()) throw std::runtime_error("Unexpected: tr_i != target.rend()");
            return target;
        }
    };
}