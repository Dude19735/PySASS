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
    class SASS_Enc_Dom_Iter2 {
        const std::string _fixed_instr_class;
        const std::vector<std::string> _fixed_keys;
        std::vector<std::vector<int>> _product_inds;
        std::vector<std::vector<SASS_Bits>> _values;
        size_t _cur_product_ind;
        std::vector<std::vector<size_t>> _product_inds_into_instr_domains;
        size_t _cur_product_inds_into_instr_domains_ind;
        const size_t _dom_ind;
        const TAllVariantsBR* _domp_v;

        std::unique_ptr<std::default_random_engine> _generator;

        public:
        /* regular constructor */
        SASS_Enc_Dom_Iter2(
            const std::string fixed_instr_class, 
            const std::vector<std::string>& fixed_keys, 
            const std::vector<std::vector<int>>& product_inds,
            const std::vector<std::vector<SASS_Bits>>& values,
            const std::vector<std::vector<size_t>>& product_inds_into_instr_domains,
            const size_t dom_ind,
            const TAllVariantsBR* domp_v
        ):
        _fixed_instr_class(fixed_instr_class),
        _fixed_keys(std::move(fixed_keys)),
        _product_inds(std::move(product_inds)),
        _values(std::move(values)),
        _cur_product_ind(0),
        _product_inds_into_instr_domains(std::move(product_inds_into_instr_domains)),
        _cur_product_inds_into_instr_domains_ind(0),
        _dom_ind(dom_ind),
        _domp_v(domp_v),
        _generator(std::make_unique<std::default_random_engine>())
        {
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
        }
        /* copy constructor */
        SASS_Enc_Dom_Iter2(const SASS_Enc_Dom_Iter2& other) noexcept
        :
        _fixed_instr_class(other._fixed_instr_class),
        _fixed_keys(other._fixed_keys),
        _product_inds(other._product_inds),
        _values(other._values),
        _cur_product_ind(other._cur_product_ind),
        _product_inds_into_instr_domains(other._product_inds_into_instr_domains),
        _cur_product_inds_into_instr_domains_ind(other._cur_product_inds_into_instr_domains_ind),
        _dom_ind(other._dom_ind),
        _domp_v(other._domp_v),
        _generator(std::make_unique<std::default_random_engine>())
        {
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
        }
        /* move constructor */
        SASS_Enc_Dom_Iter2(SASS_Enc_Dom_Iter2&& other) noexcept
        :
        _fixed_instr_class(std::move(other._fixed_instr_class)),
        _fixed_keys(std::move(other._fixed_keys)),
        _product_inds(std::move(other._product_inds)),
        _values(std::move(other._values)),
        _cur_product_ind(other._cur_product_ind),
        _product_inds_into_instr_domains(std::move(other._product_inds_into_instr_domains)),
        _cur_product_inds_into_instr_domains_ind(other._cur_product_inds_into_instr_domains_ind),
        _dom_ind(other._dom_ind),
        _domp_v(other._domp_v),
        _generator(std::move(other._generator))
        {}

        /* copy assignment constructor */
        SASS_Range_Iter& operator=(const SASS_Enc_Dom_Iter2& other) = delete;
        /* move assignment constructor */
        SASS_Range_Iter& operator=(SASS_Enc_Dom_Iter2&& other) = delete;

        std::map<std::string, SASS_Bits> __next__(bool& finished){
            // If we iterate with __next__ and we are at the end, return empty
            // and flag the parent that we are finished
            if(_cur_product_ind >= _product_inds.size()) {
                finished = true;
                return {};
            }
            finished = false;

            // _cur_product_ind points to the current index into the _product_inds
            // NOTE: this can't happen, ever, because of the previous 'if'.
            // NOTE: this is an invariant
            // if(_cur_product_ind >= _product_inds.size()) throw std::runtime_error("_cur_product_ind out of bounds of _product_inds. This is a very bad bug!");

            // This is the current row of the cross product.
            //    cur_prod == std::vector<int> contains _values.size() entries
            // where cur_prod[i] is an index into _values[i] and _values contains
            // all SASS_Bits values in the ankers.
            // For example: for _values[0] = [X, Y, Z] => X, Y, Z are the SASS_Bits
            // given as anker points for _fixed_keys[0] = 'abc' where 'abc' is an enc_vals entry.
            auto cur_prod = _product_inds.at(_cur_product_ind);
            // cur_inds == std::vector<size_t> contains the indices of all precalculated domains
            // into _domp_v vector that intersect with all the anker values of the current cur_prod.
            auto cur_inds = _product_inds_into_instr_domains.at(_cur_product_inds_into_instr_domains_ind);
            
            // If cur_inds.size() == 0, there is no matching, precalculated domain set for cur_prod.
            // If we don't have anything that matches, keep going until we can't go no more
            size_t pis = _product_inds.size()-1;
            while(_cur_product_ind < pis && cur_inds.size() == 0) {
                _cur_product_ind++;
                _cur_product_inds_into_instr_domains_ind++;
                cur_prod = _product_inds.at(_cur_product_ind);
                cur_inds = _product_inds_into_instr_domains.at(_cur_product_inds_into_instr_domains_ind);
            }

            // If we went at least one step but also as far as possible and we still don't have anything
            // we are also finished.
            if(cur_inds.size() == 0) {
                finished = true;
                return {};
            }

            // Otherwise we can keep on going.
            // _domp_v.at(_dom_ind) is the domain of the current instruction class that we pass
            // from the SASS_Dom object.
            // We uniformly at random select one index into _domp_v.at(_dom_ind) that will validly complete
            // the selected cross-product of our ankers.
            auto sub_dist = std::uniform_int_distribution<size_t>(0, cur_inds.size()-1);
            size_t set_sel = sub_dist(*_generator);

            // selected set
            // cur_inds.at(set_sel) == the index into _domp_v.at(_dom_ind) is now
            // an std::map<std::string, std::variant<std::set<SASS_Bits>>, SASS_Range>>>.
            //  - std::string == the enc_vals keys
            //  - std::variant == the value possibilities for that key
            // We now uniformly at random choose one value for each key that we don't have as 
            // anker point.
            // For the anker points, we already have fixed values.
            // 'selected' is the selected variant of the precalculated domains that fit our given
            // _fixed_keys fixed SASS_Bits.
            const auto& selected = _domp_v->at(_dom_ind).at(cur_inds.at(set_sel));
            std::map<std::string, SASS_Bits> result;
            size_t fixed_size = _fixed_keys.size();
            // fixed_size == cur_prod.size()
            std::set<std::string> contained;
            for(size_t i=0; i<fixed_size; ++i){
                // cur_prod is the current cross-product we selected (there is a whole list of them).
                // cur_prod.at(i) is the current enc_val key for the anker keys that we defined.
                int index_into_values_i = cur_prod.at(i);
                // _values.at(i).at(index_into_values_i) is a SASS_Bits value.
                // _values == std::vector<std::vector<SASS_Bits>> where each entry in the outer
                // std::vector represents one of the fixed keys in the enc_vals and the inner
                // std::vector represents the possibilities we defined.
                // For example: {'abc_enc_val_key' : {X, Y, Z}} 
                //   => _values[i] = [X, Y, Z]
                //   => _fixed_keys[i] = 'abc_enc_val_key'
                result.insert({_fixed_keys[i], _values.at(i).at(index_into_values_i)});
                contained.insert(_fixed_keys[i]);
            }

            // Now we iterate our selected enc_vals domain
            // selected == std::map<std::string, std::variant<std::set<SASS_Bits>, SASS_Range>>>.
            for(const auto& enc : selected){
                // If we have a _fixed_key for the enc_val key => skip
                if(contained.contains(enc.first)) continue;
                
                // otherwise we have to do the nitty gritty stuff of digging out the correct
                // type out of std::variant. That is done like so:
                std::string enc_name = enc.first;
                if(enc.second.index() == 0){
                    // we have the set of SASS_Bits => select a random entry into that set
                    const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(enc.second);
                    auto it = sass_bits_set.begin();
                    auto sub_dist = std::uniform_int_distribution<size_t>(0, sass_bits_set.size()-1);
                    size_t set_sel = sub_dist(*_generator);
                    std::advance(it, set_sel);
                    result.insert({enc_name, *it});
                }
                else {
                    // we have a range => pick a random one. SASS_Range can be sampled uniformly at random
                    // with it's 'pick' method.
                    SASS_Range sass_range = std::get<SASS_Range>(enc.second);
                    result.insert({enc_name, SASS_Range::pick(sass_range)});
                }
            }

            _cur_product_ind++;
            _cur_product_inds_into_instr_domains_ind++;
            return std::move(result);
        }
    };
}