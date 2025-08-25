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
#include "SASS_Range_Iter.hpp"

namespace SASS {
    bool SASS_RANGE_SIZE_WARNINGS = false;

    class SASS_Range {
        uint64_t _max_val;
        uint64_t _bit_mask;
        uint8_t _bit_len;
        uint8_t _signed;
        int64_t _range_min;
        uint64_t _range_max;
        BitVector _bit_mask_bits;
        uint8_t _bm_len;
        int64_t _r_place_s;
        uint64_t _r_place_u;
        SASS_Range_Limits _r_limits;
        std::unique_ptr<std::default_random_engine> _generator;

        public:
        struct State {
            int64_t range_min;
            uint64_t range_max;
            uint64_t bit_mask;
            uint8_t bit_len;
            uint8_t sign;
            uint8_t fill1=0;
            uint8_t fill2=0;
            uint8_t fill3=0;
            uint8_t fill4=0;
            uint8_t fill5=0;
            uint8_t fill6=0;
        };

        /* regular constructor */
        SASS_Range(int64_t range_min, uint64_t range_max, uint8_t bit_len, uint8_t signed_, uint64_t bit_mask) 
        : 
        _max_val(SASS_Range::get_max_val(bit_len, signed_)), 
        _bit_mask(bit_mask), 
        _bit_len(bit_len), 
        _signed(signed_), 
        _range_min(SASS_Range::get_range_min(*this, range_min, range_max)), _range_max(SASS_Range::get_range_max(*this, range_min, range_max)),
        _bit_mask_bits(SASS_Bits_Lib::val_to_bit_vector(bit_mask, _bit_len, 0).bv),
        _bm_len(std::accumulate(_bit_mask_bits.begin(), _bit_mask_bits.end(), 0)),
        _r_place_s(0), _r_place_u(0),
        _r_limits(SASS_Range::calculate_limits(*this)),
        _generator(std::make_unique<std::default_random_engine>())
        {
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
        }
        /* copy constructor */
        SASS_Range(const SASS_Range& other) noexcept 
        : 
        _max_val(other._max_val), _bit_mask(other._bit_mask), _bit_len(other._bit_len), 
        _signed(other._signed), _bit_mask_bits(other._bit_mask_bits), _bm_len(other._bm_len),
        _range_min(other._range_min), _range_max(other._range_max),
        _r_place_s(other._r_place_s), _r_place_u(other._r_place_u),
        _r_limits(other._r_limits),
        _generator(std::make_unique<std::default_random_engine>())
        {
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
        }
        /* move constructor */
        SASS_Range(SASS_Range&& other) noexcept 
        : 
        _max_val(other._max_val), _bit_mask(other._bit_mask), _bit_len(other._bit_len), 
        _signed(other._signed),
        _range_min(other._range_min), _range_max(other._range_max),
        _bit_mask_bits(std::move(other._bit_mask_bits)),  
        _bm_len(other._bm_len),
        _r_place_s(other._r_place_s), 
        _r_place_u(other._r_place_u),
        _r_limits(std::move(other._r_limits)),
        _generator(std::move(other._generator))
        {}
        /* copy assignment constructor */
        SASS_Range operator=(const SASS_Range& other) noexcept { 
            if(this == &other) return *this;
            _max_val = other._max_val;
            _bit_mask = other._bit_mask;
            _bit_len = other._bit_len;
            _signed = other._signed;
            _range_min = other._range_min;
            _range_max = other._range_max;
            _bit_mask_bits = other._bit_mask_bits;
            _bm_len = other._bm_len;
            _r_place_s = other._r_place_s;
            _r_place_u = other._r_place_u;
            _r_limits = other._r_limits;
            
            _generator = std::make_unique<std::default_random_engine>();
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
            
            return *this;
        }
        /* move assignment constructor */
        SASS_Range operator=(SASS_Range&& other) noexcept { 
            if(this == &other) return *this;
            _max_val = other._max_val;
            _bit_mask = other._bit_mask;
            _bit_len = other._bit_len;
            _signed = other._signed;
            _range_min = other._range_min;
            _range_max = other._range_max;
            _bit_mask_bits = std::move(other._bit_mask_bits);
            _bm_len = other._bm_len;
            _r_place_s = other._r_place_s;
            _r_place_u = other._r_place_u;
            _r_limits = std::move(other._r_limits);
            _generator = std::move(other._generator);
            return *this;
        }
        bool operator==(const SASS_Range& other) const {
            if(other._max_val != _max_val) return false;
            if(other._bit_len != _bit_len) return false;
            if(other._signed != _signed) return false;
            if(other._bit_mask != _bit_mask) return false;
            if(other._range_min != _range_min) return false;
            if(other._range_max != _range_max) return false;
            return true;
        }

        int64_t range_min() const { return _range_min; }
        uint64_t range_max() const { return _range_max; }
        uint64_t max_val() const { return _max_val; }
        uint64_t bit_mask() const { return _bit_mask; }
        uint8_t bit_len() const { return _bit_len; }
        uint8_t signed_() const { return _signed; }
        SASS_Range_Limits limits() const { return _r_limits; }

        static void enable_size_warnings(){ SASS_RANGE_SIZE_WARNINGS = true; }
        static void disable_size_warnings(){ SASS_RANGE_SIZE_WARNINGS = false; }

        static size_t get_bin_state_size(){
            return static_cast<size_t>(sizeof(SASS_Range::State));
        }

        static SASS_Range::State get_bin_state(const SASS_Range& r){
            return SASS_Range::State {
                .range_min=r._range_min,
                .range_max=r._range_max,
                .bit_mask=r._bit_mask,
                .bit_len=r._bit_len,
                .sign=r._signed
            };
        }

        static SASS_Range set_from_bin_state(const uint8_t* ptr){
            const SASS_Range::State res = *reinterpret_cast<const SASS_Range::State*>(ptr);
            return SASS_Range(res.range_min, res.range_max, res.bit_len, res.sign, res.bit_mask);
        }

        static bool empty(const SASS_Range& r){ return SASS::SASS_Range::size(r) == 0UL; }
        static uint64_t size(const SASS_Range& r) { return r._r_limits.size; }
        static uint64_t __max__(const SASS_Range& r) { return r._range_max; }
        static int64_t __min__(const SASS_Range& r) { return r._range_min; }
        static bool __bool__(const SASS_Range& r){ return !SASS::SASS_Range::empty(r); }
        static std::tuple<int64_t, uint64_t, uint64_t, uint8_t, uint8_t> to_tuple(const SASS_Range& r){ 
            return {r._range_min, r._range_max, r._bit_mask, r._bit_len, r._signed}; }
        static uint64_t __max_bval__(const SASS_Range& r){ return r._max_val; }
        static int64_t __min_bval__(const SASS_Range& r){
            if(r._signed == 0) return 0;
            return -static_cast<int64_t>(r._max_val)-1L;
        }

        static uint64_t get_max_val(const uint8_t bit_len, uint8_t signed_){
            if(bit_len == 0) throw std::runtime_error(std::vformat("Illegal: bit_len > 0 required but [bit_len=[{0}]]", std::make_format_args(bit_len)));
            uint64_t max_val = 0;
            uint64_t bit_len_l = static_cast<uint64_t>(bit_len);
            if(signed_==1) {
                max_val = static_cast<uint64_t>((1UL<<(bit_len_l-1UL))-1UL);
            }
            else {
                max_val = static_cast<uint64_t>((((1UL << (bit_len-1UL))-1UL)<<1UL)+1UL);
            }
            return max_val;
        }

        static int64_t get_range_min(const SASS_Range& r, const int64_t& range_min, const uint64_t& range_max){
            // if(r._signed == 0 && range_min < 0) throw std::runtime_error("Illegal: unsigned range can't have negative min value");
            if(r._signed == 1 && r._bit_mask > 0){
                // if we have a signed range and our bitmask covers the sign bit:
                // we don't want that. If this is the case, tell the user to use an unsigned range
                uint64_t bla = r._bit_mask & (1UL<<(static_cast<uint64_t>(r._bit_len)-1UL));
                if(bla != 0) throw std::runtime_error("Illegal: bitmask for signed range is not allowed to cover the sign bit!");
            }
            int64_t min_bval = SASS_Range::__min_bval__(r);
            if(range_min > 0L && range_max == 0UL){
                // auto assign
                return min_bval;
            }
            // Provisionally remove these checks to allow for an empty SASS_Range
            // ==================================================================
            // if(r._signed==0 && range_min > range_max){
            //     uint64_t u_range_min = static_cast<uint64_t>(range_min);
            //     throw std::runtime_error(std::vformat("Illegal: given [unsigned] [range_min={0} > range_max={1}]", std::make_format_args(u_range_min, range_max)));                
            // }
            // else if(r._signed==1 && range_min < min_bval) {
            //     uint64_t max_bval = SASS_Range::__max_bval__(r);
            //     uint8_t bit_len = r._bit_len;
            //     std::string s = (r._signed == 1 ? "signed" : "unsigned");
            //     throw std::runtime_error(std::vformat("Illegal: given [range_min={0}] but [{1}] [bit_len={2}] only covers interval [{3},{4}]", std::make_format_args(range_min, s, bit_len, min_bval, max_bval)));
            // }
            return range_min;
        }

        static uint64_t get_range_max(const SASS_Range& r, const int64_t& range_min, const uint64_t& range_max){
            uint64_t max_bval = SASS_Range::__max_bval__(r);
            if(range_min > 0 && range_max == 0){
                // auto assign
                return max_bval;
            }
            // Provisionally remove these checks to allow for an empty SASS_Range
            // ==================================================================
            // if(range_max > max_bval) {
            //     int64_t min_bval = SASS_Range::__min_bval__(r);
            //     uint8_t bit_len = r._bit_len;
            //     std::string s = (r._signed == 1 ? "signed" : "unsigned");
            //     throw std::runtime_error(std::vformat("Illegal: given [range_max={0}] but [{1}] [bit_len={2}] only covers interval [{3},{4}]", std::make_format_args(range_max, s, bit_len, min_bval, max_bval)));
            // }
            return range_max;
        }

        static std::set<SASS_Bits> intersection_s(const SASS_Range& r, const std::set<SASS_Bits>& other) {
            std::set<SASS_Bits> res;

            // cover the case where the range is empty
            if(r._r_limits.size==0) res;

            for(const auto& b : other){
                if(SASS_Range::__contains__(r, b)) res.insert(b);
            }
            return res;
        }

        static std::vector<SASS_Bits> intersection_v(const SASS_Range& r, const std::set<SASS_Bits>& other) {
            std::vector<SASS_Bits> res;

            // cover the case where the range is empty
            if(r._r_limits.size==0) res;

            for(const auto& b : other){
                if(SASS_Range::__contains__(r, b)) res.push_back(b);
            }
            return res;
        }

        static SASS_Range intersection_r(const SASS_Range& r, const SASS_Range& other) {
            if(r._signed != other._signed) throw std::runtime_error("Illegal: signs of ranges must match for intersection!");

            uint8_t new_bit_len = std::min(r._bit_len, other._bit_len);
            uint64_t new_bit_mask = r._bit_mask | other._bit_mask;

            // quickly cover the case where one of them is empty
            if(r._r_limits.size==0 || other._r_limits.size==0){
                SASS_Range(2L, 1UL, new_bit_len, r._signed, new_bit_mask);
            }

            int64_t new_range_min = std::max(r._range_min, other._range_min);
            uint64_t new_range_max = std::min(r._range_max, other._range_max);
            return SASS_Range(new_range_min, new_range_max, new_bit_len, r._signed, new_bit_mask);
        }

        static void add_bit_mask(SASS_Range& r, uint64_t bit_mask){
            r._bit_mask_bits = SASS_Bits_Lib::val_to_bit_vector(bit_mask, r._bit_len, 0).bv;
            r._bm_len = std::accumulate(r._bit_mask_bits.begin(), r._bit_mask_bits.end(), 0);
            r._bit_mask = bit_mask;
            r._r_limits = SASS_Range::calculate_limits(r);
        }

        static std::string pretty(const SASS_Range& r){
            if(r._signed == 1){
                int64_t min_val = SASS_Range::__min__(r);
                int64_t max_val = static_cast<int64_t>(SASS_Range::__max__(r));
                auto signed_ = (r._signed ? "S" : "U");
                auto bit_len = r._bit_len;
                auto range_min = r._r_limits.range_min;
                auto range_max = r._r_limits.range_max;
                auto bit_mask = (r._bit_mask != 0 ? std::vformat("M{0}[{1},{2}]", std::make_format_args(r._bit_mask, range_min, range_max)) : "");
                auto eff_min = r._r_limits.effective_min;
                auto eff_max = r._r_limits.effective_max;
                uint64_t mm = std::numeric_limits<uint64_t>::max();
                auto size = r._r_limits.size_overflow ? std::vformat("{0}+1", std::make_format_args(mm)) : std::vformat("{0}", std::make_format_args(r._r_limits.size));
                return std::vformat("[{0},{1}]{2}{3}b{4} |Ef[{5},{6}]|={7}", std::make_format_args(min_val, max_val, signed_, bit_len, bit_mask, eff_min, eff_max, size));
            } else {
                auto min_val = static_cast<uint64_t>(SASS_Range::__min__(r));
                auto max_val = SASS_Range::__max__(r);
                auto signed_ = (r._signed ? "S" : "U");
                auto bit_len = r._bit_len;
                auto range_min = r._r_limits.range_min;
                auto range_max = r._r_limits.range_max;
                auto bit_mask = (r._bit_mask != 0 ? std::vformat("M{0}[{1},{2}]", std::make_format_args(r._bit_mask, range_min, range_max)) : "");
                auto eff_min = r._r_limits.effective_min;
                auto eff_max = r._r_limits.effective_max;
                uint64_t mm = std::numeric_limits<uint64_t>::max();
                auto size = r._r_limits.size_overflow ? std::vformat("{0}+1", std::make_format_args(mm)) : std::vformat("{0}", std::make_format_args(r._r_limits.size));
                return std::vformat("[{0},{1}]{2}{3}b{4} |Ef[{5},{6}]|={7}", std::make_format_args(min_val, max_val, signed_, bit_len, bit_mask, eff_min, eff_max, size));
            }
        }

        static bool __contains__(const SASS_Range& r, const SASS_Bits& val, bool throw_on_error=false){
            const int64_t min_val = SASS::SASS_Range::__min_bval__(r);
            const uint64_t max_val = SASS::SASS_Range::__max_bval__(r);
            return SASS_Range_Lib::contains(r._signed, min_val, max_val, r._range_min, r._range_max, r._bit_mask, val, throw_on_error);
        }

        static bool __iterable__(const SASS_Range& r) {
            return r._r_limits.size != 0 || r._r_limits.size_overflow;
        }

        static uint64_t get_iter_limit(const SASS_Range_Limits& r_limits){
            if(r_limits.size_overflow) return 0;
            else return r_limits.size;
        }

        static SASS_Range_Iter __iter__(const SASS_Range& r) {
            uint64_t iter_limit = SASS_Range::get_iter_limit(r._r_limits);
            auto iter = SASS_Range_Iter(
                r._bit_len, r._signed, r._bm_len, iter_limit, 
                r._r_limits, r._bit_mask_bits,
                1UL, 0.0);
            
            // If there is nothing to do, finish the iteration immediately
            if(!SASS_Range::__iterable__(r)) iter.finish(); // throw std::runtime_error("Illegal: can't iterate empty SASS_Range");
            return iter;
        }

        static SASS_Range_Iter __sized_iter__(SASS_Range& r, uint64_t sample_size){
            if(sample_size < 2) throw std::runtime_error("Illegal: can't iterate with [sample_size<2]");

            uint64_t iter_limit = SASS_Range::get_iter_limit(r._r_limits);
            uint64_t step_i = 1UL;
            double step_d = 0.0;
            if(r._r_limits.size_overflow){
                uint64_t s = sample_size - 1;
                uint64_t limit = std::numeric_limits<uint64_t>::max();
                const uint64_t rem = limit % s;
                step_i = (limit-rem) / s;
                step_d = static_cast<double>(rem) / (static_cast<double>(s));
            } else {
                uint64_t s = sample_size - 1UL;
                uint64_t limit = iter_limit-1UL;
                const uint64_t rem = limit % s;
                step_i = (limit-rem) / s;
                step_d = static_cast<double>(rem) / (static_cast<double>(s));
            }
            // If we pass a larger sample size than the effective size of the range
            if(step_i == 0){
                step_i = 1UL;
                step_d = 0.0;
            }

            if(step_d > 1.0) throw std::runtime_error("Unexpected: step_d > 1.0");

            auto iter = SASS_Range_Iter(
                r._bit_len, r._signed, r._bm_len, iter_limit, 
                r._r_limits, r._bit_mask_bits,
                step_i, step_d);

            // If there is nothing to iterate, finish immediately
            if(!SASS_Range::__iterable__(r)) iter.finish(); // throw std::runtime_error("Illegal: can't iterate empty SASS_Range");
            return iter;
        }

        /**
         * This method calculates how many values a SASS_Range can produce. For example, the range
         *  - [0, 255]U8b produces 0 to 255 == 256 values.
         *  - [0, 255]U8bM3 produces i = [0,255] iff (i & 3) == 0, which is 64 values. For example, it produces
         *     0b0, 0b100, 0b1000, 0b1100, ... but not 0b1, 0b10, 0b11, 0b1010, 0b1011, ... since the second
         *     batch of numbers violates the bitmask 3 = 0b11. Thus, instead of 8 bits, we can only choose 6 bits
         *     which yields 64 possible values.
         *  - [-10,10]S8bM3 produces the 5 values {-8, -4, 0, 4, 8}. All others violate the bitmask.
         */
        static SASS_Range_Limits calculate_limits(const SASS_Range& r){
            // get the max range assuming signed or unsigned
            int64_t min_val = SASS_Range::__min__(r);
            uint64_t max_val = SASS_Range::__max__(r);
            if(r._signed && min_val > static_cast<int64_t>(max_val)) return SASS_Range_Limits{.range_min=0, .effective_min=0, .range_max=0, .effective_max=0, .size=0, .size_overflow=false };
            SASS_Range_Limits limits = SASS_Range_Lib::effective_range(min_val, max_val, r._signed, r._bit_mask, r._bit_mask_bits, r._bit_len, r._bm_len);

            return limits;
        }

        static SASS_Bits pick(const SASS_Range& r, bool throw_on_error=true){
            if(r._generator == nullptr) throw std::runtime_error("Unexpected: r._generator == nullptr");

            // Not allowed to pick an empty SASS_Range
            if(r._r_limits.size == 0UL && !r._r_limits.size_overflow) throw std::runtime_error("Illegal: attempt to pick a SASS_Range with size=0");

            return SASS_Range_Lib::pick(r._generator.get(), r._r_limits, r._bit_len, r._bm_len, r._bit_mask, r._bit_mask_bits, r._signed, throw_on_error);
        }

        static std::string serialize(const SASS_Range& r){
            // recreate old SASS_Range with 5 params
            const auto range_max = r._range_max;
            const auto range_min = r._range_min;
            const auto bit_len = r._bit_len;
            const auto signed_ = r._signed;
            const auto bit_mask = r._bit_mask;
            return std::vformat("{0},{1},{2},{3},{4}", std::make_format_args(range_min, range_max, bit_len, signed_, bit_mask));
        }

        static SASS_Range deserialize(const std::string& vals){
            const std::set<char> expected = {'-','1','2','3','4','5','6','7','8','9','0'};
            uint64_t bit_mask = 0;
            uint8_t bit_len = 0;
            uint8_t signed_ = 0;
            int64_t range_min = 0;
            uint64_t range_max = 0;
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

            if(p_vals.size() == 5) {
                // cover the old stuff
                range_min = static_cast<int64_t>(std::stol(p_vals[0]));
                range_max = static_cast<uint64_t>(std::stoul(p_vals[1]));
                bit_len = static_cast<uint8_t>(std::stoi(p_vals[2]));
                signed_ = static_cast<uint8_t>(std::stoi(p_vals[3]));
                bit_mask = static_cast<uint64_t>(std::stoul(p_vals[4]));
            }
            else throw std::runtime_error("Unexpected: too many input values for a SASS_Range");

            SASS_Range r = SASS_Range(range_min, range_max, bit_len, signed_, bit_mask);
            return r;
        }
    };
}