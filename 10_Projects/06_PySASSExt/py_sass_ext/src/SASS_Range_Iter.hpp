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
#include <chrono>
#include "SASS_Bits.hpp"
#include "SASS_Range_Lib.hpp"

namespace SASS {

    class SASS_Range_Iter {
        const uint8_t _bit_len;
        const uint8_t _signed;
        const uint8_t _bm_len;
        const uint64_t _iter_limit;
        const SASS_Range_Limits _r_limits;
        const BitVector _bit_mask_bits;

        const uint64_t _step_i;
        const double _step_d;
        uint64_t _next_i;
        double _next_d;
        SASS_Bits _next_bits;
        bool _finished;

        public:

        /* regular constructor */
        SASS_Range_Iter(
            uint8_t bit_len, uint8_t signed_, uint8_t bm_len, uint64_t iter_limit, 
            const SASS_Range_Limits& r_limits, const BitVector& bit_mask_bits,
            uint64_t step_i, double step_d) 
        : 
        _bit_len(bit_len), 
        _signed(signed_), 
        _bm_len(bm_len),
        _iter_limit(iter_limit),
        _r_limits(r_limits),
        _bit_mask_bits(bit_mask_bits),
        _step_i(step_i),
        _step_d(step_d),
        _next_i(0UL),
        _next_d(0.0),
        _next_bits(SASS_Range_Lib::reverse_effective_sample(0, _r_limits, _bit_len, _bit_mask_bits, _bm_len, _signed, false)),
        _finished(false)
        {}
        /* copy constructor */
        SASS_Range_Iter(const SASS_Range_Iter& other) noexcept 
        : 
        _bit_len(other._bit_len), 
        _signed(other._signed), 
        _bm_len(other._bm_len),
        _iter_limit(other._iter_limit),
        _r_limits(other._r_limits),
        _bit_mask_bits(other._bit_mask_bits),
        _step_i(other._step_i),
        _step_d(other._step_d),
        _next_i(other._next_i),
        _next_d(other._next_d),
        _next_bits(other._next_bits),
        _finished(other._finished)
        {}
        /* move constructor */
        SASS_Range_Iter(SASS_Range_Iter&& other) noexcept 
        : 
        _bit_len(other._bit_len), 
        _signed(other._signed),
        _bm_len(other._bm_len),
        _iter_limit(other._iter_limit),
        _r_limits(std::move(other._r_limits)),
        _bit_mask_bits(std::move(other._bit_mask_bits)),
        _step_i(other._step_i),
        _step_d(other._step_d),
        _next_i(other._next_i),
        _next_d(other._next_d),
        _next_bits(std::move(other._next_bits)),
        _finished(other._finished)
        {}
        /* copy assignment constructor */
        SASS_Range_Iter& operator=(const SASS_Range_Iter& other) = delete;
        /* move assignment constructor */
        SASS_Range_Iter& operator=(SASS_Range_Iter&& other) = delete;

        void finish() { _finished = true; }
        bool __finished__() {  return _finished; }

        SASS_Bits __next__(bool& finished) {
            finished = false;
            if(_finished) {
                finished = true;
                return SASS_Bits::from_int(0, 0, _signed);
            }

            SASS_Bits res = _next_bits;
            uint64_t r_cur_r = _next_i + static_cast<uint64_t>(std::round(_next_d));
            if((!_r_limits.size_overflow && r_cur_r == _r_limits.size-1UL) || (_r_limits.size_overflow && r_cur_r == std::numeric_limits<uint64_t>::max())){
                _finished = true;
                return res;
            }

            uint64_t r_next_i = _next_i + _step_i;
            double r_next_d = _next_d + _step_d;
            uint64_t r_next_r = r_next_i + static_cast<uint64_t>(std::round(r_next_d));

            // r._next is not allowed to go over the limit of the range.
            // We are always positive => cast double to uint64 is always a floor operation
            // At this point in the code, we always add at least 1.0 to r._next
            // => if we typecast r._next to an uint64 and get a value > than the limits, we have an overflow
            // => if r._next is larger than the numeric limit of uint64_t we have an overflow
            // if(r_next > std::numeric_limits<uint64_t>::max()) throw std::runtime_error("Unexpected: iterator overflow [r._next > std::numeric_limits<uint64_t>::max()]");
            bool cond1 = (r_next_r > _r_limits.size) && (!_r_limits.size_overflow);
            bool cond2 = r_next_r == 0 && !_r_limits.size_overflow;
            if(cond1) {
                _finished = true;
                throw std::runtime_error(std::vformat("Unexpected: iterator overflow [cond1({0},{1})]", std::make_format_args(r_next_r, r_cur_r)));
            }
            if(cond2) {
                _finished = true;
                throw std::runtime_error(std::vformat("Unexpected: iterator overflow [cond2({0},{1})]", std::make_format_args(r_next_r, r_cur_r)));
            }

            uint64_t rem = uint64_t(r_next_d);
            _next_i = r_next_i + rem;
            _next_d = r_next_d - rem;
            if(_next_d >= 1.0) throw std::runtime_error("Unexpected: r._next_d >= 1.0");
            
            // }
            _next_bits = SASS_Range_Lib::reverse_effective_sample(r_next_r, _r_limits, _bit_len, _bit_mask_bits, _bm_len, _signed, false);
            
            return res;
        }
    };
}