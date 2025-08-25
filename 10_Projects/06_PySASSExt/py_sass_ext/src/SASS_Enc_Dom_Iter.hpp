#pragma once
#include <stdint.h>
#include <exception>
#include <iostream>
#include <vector>
#include <format>
#include <cmath>
#include <random>
#include <time.h>
#include <bitset>
#include <fstream>
#include <numeric>
#include <memory>
#include <variant>
#include <algorithm>
#include <sstream>
#include <map>
#include <set>
#include <chrono>
#include <random>
#include <time.h>
#include <type_traits>
#include "SASS_Enc_Dom_Lib.hpp"
#include "SASS_Bits.hpp"
#include "SASS_Range.hpp"

using TFixedIter = std::map<std::map<std::string, SASS::SASS_Bits>, std::vector<size_t>>;

namespace SASS {
    class SASS_Enc_Dom_Iter {
        const std::string _fixed_instr_class;
        TFixedIter::const_iterator _fixed_iter;
        TFixedIter::const_iterator _fixed_iter_end;
        TVariantVectorBR* _fixed_no_exceptions;
        std::unique_ptr<std::default_random_engine> _generator;

        public:
        /* regular constructor */
        SASS_Enc_Dom_Iter(const std::string fixed_instr_class, TFixedIter::const_iterator fixed_iter, TFixedIter::const_iterator fixed_iter_end, TVariantVectorBR* fixed_no_exceptions)
        :
        _fixed_instr_class(fixed_instr_class),
        _fixed_iter(fixed_iter),
        _fixed_iter_end(fixed_iter_end),
        _fixed_no_exceptions(fixed_no_exceptions),
        _generator(std::make_unique<std::default_random_engine>())
        {
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
        }
        /* copy constructor */
        SASS_Enc_Dom_Iter(const SASS_Enc_Dom_Iter& other) noexcept
        :
        _fixed_instr_class(other._fixed_instr_class),
        _fixed_iter(other._fixed_iter),
        _fixed_iter_end(other._fixed_iter_end),
        _fixed_no_exceptions(other._fixed_no_exceptions),
        _generator(std::make_unique<std::default_random_engine>())
        {
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
        }
        /* move constructor */
        SASS_Enc_Dom_Iter(SASS_Enc_Dom_Iter&& other) noexcept
        :
        _fixed_instr_class(other._fixed_instr_class),
        _fixed_iter(other._fixed_iter),
        _fixed_iter_end(other._fixed_iter_end),
        _fixed_no_exceptions(other._fixed_no_exceptions),
        _generator(std::move(other._generator))
        {}
        /* copy assignment constructor */
        SASS_Range_Iter& operator=(const SASS_Enc_Dom_Iter& other) = delete;
        /* move assignment constructor */
        SASS_Range_Iter& operator=(SASS_Enc_Dom_Iter&& other) = delete;

        std::map<std::string, SASS_Bits> pick() const {
            std::map<std::string, SASS_Bits> sample;
            auto& fixed = *_fixed_iter;
            std::set<std::string> fixed_keys;
            for(const auto& a : fixed.first) {
                sample.insert({a.first, a.second});
                fixed_keys.insert(a.first);
            }
            const auto& vals = fixed.second;
            size_t var_size = vals.size();
            auto it = vals.begin();
            auto sub_dist = std::uniform_int_distribution<size_t>(0, var_size-1);
            size_t set_sel = sub_dist(*_generator);
            std::advance(it, set_sel);
            
            const auto& cur_class = *_fixed_no_exceptions;
            const auto& sub_var = cur_class.at(*it);
            for(const auto& enc : sub_var){
                // skip the fixed values
                if(sample.contains(enc.first)) continue;

                // add one random one for all others
                std::string enc_name = enc.first;
                if(enc.second.index() == 0){
                    // we have a set => select a random one
                    const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(enc.second);
                    auto it = sass_bits_set.begin();
                    auto sub_dist = std::uniform_int_distribution<size_t>(0, sass_bits_set.size()-1);
                    size_t set_sel = sub_dist(*_generator);
                    std::advance(it, set_sel);
                    sample.insert({enc_name, *it});
                }
                else {
                    // we have a range => pick a random one
                    SASS_Range sass_range = std::get<SASS_Range>(enc.second);
                    sample.insert({enc_name, SASS_Range::pick(sass_range)});
                }
            }
            
            return std::move(sample);
        }

        std::map<std::string, SASS_Bits> __next__(bool& finished){
            if(_fixed_iter == _fixed_iter_end) {
                finished = true;
                return {};
            }
            finished = false;
            std::map<std::string, SASS_Bits> res = pick();
            _fixed_iter++;
            return std::move(res);
        }
    };
}