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
#include "SASS_Enc_Dom_Iter.hpp"
#include "SASS_Enc_Dom_Iter2.hpp"

using StrVector = std::vector<std::string>;
using FixedPickVector = std::vector<std::map<std::string, SASS::SASS_Bits>>;

namespace SASS {
    bool SASS_ENC_DOM_COMPARE_OUTPUT = false;

    class SASS_Enc_Dom {
        size_t _last_variant_index;
        std::string _last_instruction_class;
        std::map<std::string, SASS_Bits> _last_pick_result;
        TDomp _domp;
        TAllVariantsBR _domp_v;
        std::vector<std::string> _domp_nok;
        std::unique_ptr<std::default_random_engine> _generator;
        std::string _fixed_instr_class;
        TFixedIter _fixed_inputs;
        TVariantVectorBR _fixed_class_no_exceptions;

        public:
        /* regular constructor */
        SASS_Enc_Dom()
        : 
        _last_variant_index(0), _last_instruction_class(""), _last_pick_result({}),
        _domp({}), _domp_v({}), _domp_nok({}),
        _generator(std::make_unique<std::default_random_engine>()),
        _fixed_instr_class(""),
        _fixed_inputs({}),
        _fixed_class_no_exceptions({})
        {}

        // Static method to emphasize creation on python side
        static SASS_Enc_Dom create_new_empty(){ return SASS_Enc_Dom(); }

        /* regular constructor */
        SASS_Enc_Dom(const std::string& filename, bool show_progress, bool compressed, bool as_txt)
        : 
        _last_variant_index(0), _last_instruction_class(""), _last_pick_result({}),
        _generator(std::make_unique<std::default_random_engine>()),
        _fixed_instr_class(""),
        _fixed_inputs({}),
        _fixed_class_no_exceptions({})
        {
            if(as_txt) {
                if(show_progress) std::cout << "[Warning] No progress report available. Loading may take a while..." << std::endl;
                DeserilalizeResult res = SASS_Enc_Dom_Lib::deserialize(filename);
                _domp = std::move(res.domp);
                _domp_v = std::move(res.domp_v);
                _domp_nok = std::move(res.domp_nok);
            }
            else {
                auto t1 = std::chrono::high_resolution_clock::now();
                
                DeserilalizeResult res = SASS_Enc_Dom_Lib::deserialize_bin(filename, compressed, show_progress);
                _domp = std::move(res.domp);
                _domp_v = std::move(res.domp_v);
                _domp_nok = std::move(res.domp_nok);

                auto t2 = std::chrono::high_resolution_clock::now();
                if(show_progress){
                    auto diff = std::chrono::duration_cast<std::chrono::milliseconds>(t2-t1).count();
                    std::cout << " = Loading completed [" << diff << "]ms" << std::endl;
                }
            }
            
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
        }
        /* copy constructor */
        SASS_Enc_Dom(const SASS_Enc_Dom& other) noexcept  
        :
        _last_variant_index(other._last_variant_index), _last_instruction_class(other._last_instruction_class), 
        _last_pick_result(other._last_pick_result),
        _domp(other._domp), _domp_v(other._domp_v), _domp_nok(other._domp_nok),
        _generator(std::make_unique<std::default_random_engine>()),
        _fixed_instr_class(other._fixed_instr_class),
        _fixed_inputs(other._fixed_inputs),
        _fixed_class_no_exceptions(other._fixed_class_no_exceptions)
        {
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
        }
        /* move constructor */
        SASS_Enc_Dom(SASS_Enc_Dom&& other) noexcept
        :
        _last_variant_index(std::move(other._last_variant_index)), _last_instruction_class(std::move(other._last_instruction_class)),
        _last_pick_result(std::move(other._last_pick_result)),
        _domp(std::move(other._domp)), _domp_v(std::move(other._domp_v)), 
        _domp_nok(std::move(other._domp_nok)),
        _generator(std::move(other._generator)),
        _fixed_instr_class(std::move(other._fixed_instr_class)),
        _fixed_inputs(std::move(other._fixed_inputs)),
        _fixed_class_no_exceptions(std::move(other._fixed_class_no_exceptions))
        {}
        /* copy assignment constructor */
        SASS_Enc_Dom operator=(const SASS_Enc_Dom& other) noexcept { 
            if(this == &other) return *this;
            _last_variant_index = other._last_variant_index;
            _last_instruction_class = other._last_instruction_class;
            _last_pick_result = other._last_pick_result;
            _domp = other._domp;
            _domp_v = other._domp_v;
            _domp_nok = other._domp_nok;
            _generator = std::make_unique<std::default_random_engine>();
            auto t = std::chrono::high_resolution_clock::now();
            auto seed = static_cast<uint32_t>(static_cast<uint64_t>(t.time_since_epoch().count()) & 0xFFFFFFFF);
            _generator->seed(seed);
            _fixed_instr_class = other._fixed_instr_class;
            _fixed_inputs = other._fixed_inputs;
            _fixed_class_no_exceptions = other._fixed_class_no_exceptions;
            return *this;
        }
        /* move assignment constructor */
        SASS_Enc_Dom operator=(SASS_Enc_Dom&& other) noexcept { 
            if(this == &other) return *this;
            _last_variant_index = std::move(other._last_variant_index);
            _last_instruction_class = std::move(other._last_instruction_class);
            _last_pick_result = std::move(other._last_pick_result);
            _domp = std::move(other._domp);
            _domp_v = std::move(other._domp_v);
            _domp_nok = std::move(other._domp_nok);
            _generator = std::move(other._generator);
            _fixed_instr_class = std::move(other._fixed_instr_class);
            _fixed_inputs = std::move(other._fixed_inputs);
            _fixed_class_no_exceptions = std::move(other._fixed_class_no_exceptions);
            return *this;
        }

        bool operator==(const SASS_Enc_Dom& other) const {
            if(_domp.size() != other._domp.size()) {
                if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << "_domp.size()=" << _domp.size() << " != other._domp.size()=" << other._domp.size() << std::endl;
                return false;
            }
            if(_domp_nok.size() != other._domp_nok.size()) {
                if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << "_domp_nok.size()=" << _domp_nok.size() << " != other._domp_nok.size()=" << other._domp_nok.size() << std::endl;
                return false;
            }
            if(_domp_v.size() != other._domp_v.size()) {
                if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << "_domp_v.size()=" << _domp_v.size() << " != other._domp_v.size()=" << other._domp_v.size() << std::endl;
                return false;
            }

            TDomp::const_iterator domp_ii = _domp.cbegin();
            TDomp::const_iterator odomp_ii = other._domp.cbegin();
            while(domp_ii != _domp.cend()){
                const std::pair<std::string, size_t>& v = *domp_ii;
                const std::pair<std::string, size_t>& ov = *odomp_ii;
                if(v.first.compare(ov.first) != 0) return false;
                if(_domp_v.at(v.second).size() != other._domp_v.at(ov.second).size()) {
                    if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << ov.first << " :_domp_v.at(v.second).size()=" << _domp_v.at(v.second).size() << " != other._domp_v.at(ov.second).size()=" << other._domp_v.at(ov.second).size() << std::endl;
                    return false;
                }

                std::vector<TVariantMapBR>::const_iterator v_ii = _domp_v.at(v.second).cbegin();
                std::vector<TVariantMapBR>::const_iterator ov_ii = other._domp_v.at(ov.second).cbegin();
                while(v_ii != _domp_v.at(v.second).cend()){
                    const TVariantMapBR& m = *v_ii;
                    const TVariantMapBR& om = *ov_ii;
                    if(m.size() != om.size()) {
                        if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << ov.first << ": m.size()=" << m.size() << " != other._domp_v.at(ov.second).size()=" << om.size() << std::endl;
                        return false;
                    }
                    
                    TVariantMapBR::const_iterator m_ii = m.cbegin();
                    TVariantMapBR::const_iterator om_ii = om.cbegin();
                    while(m_ii != m.cend()){
                        const std::pair<std::string, TVariantBR>& mv = *m_ii;
                        const std::pair<std::string, TVariantBR>& omv = *om_ii;
                        if(mv.first.compare(omv.first) != 0) {
                            if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << ov.first << ": mv.first=" << mv.first << " != omv.first=" << omv.first << std::endl;
                            return false;
                        }

                        if(mv.second.index() != omv.second.index()) {
                            if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << ov.first << ": mv.second.index()=" << mv.second.index() << " != omv.second.index()=" << omv.second.index() << std::endl;
                            return false;
                        }
                        if(mv.second.index() == 0){
                            const std::set<SASS_Bits>& sass_bits_set_m = std::get<std::set<SASS_Bits>>(mv.second);
                            const std::set<SASS_Bits>& sass_bits_set_om = std::get<std::set<SASS_Bits>>(omv.second);
                            for(const SASS_Bits& b : sass_bits_set_m){
                                if(!sass_bits_set_om.contains(b)) {
                                    if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << ov.first << ":" << mv.first << ": !sass_bits_set_om.contains(b)" << std::endl;
                                    return false;
                                }
                            }
                        }
                        else if(mv.second.index() == 1){
                            const SASS_Range& sass_range_m = std::get<SASS_Range>(mv.second);
                            const SASS_Range& sass_range_om = std::get<SASS_Range>(omv.second);
                            if(sass_range_m != sass_range_om) {
                                if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << SASS_Range::pretty(sass_range_m) << " != " << SASS_Range::pretty(sass_range_om) << std::endl;
                                return false;
                            }
                        }
                        else {
                            if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << ov.first << ": Unknown type in enc_dom" << std::endl;
                            return false;
                        }

                        m_ii++;
                        om_ii++;
                    }
                    v_ii++;
                    ov_ii++;
                }
                domp_ii++;
                odomp_ii++;
            }

            if(_domp_nok.size() != other._domp_nok.size()) return false;
            std::vector<std::string>::const_iterator nok_ii = _domp_nok.cbegin();
            std::vector<std::string>::const_iterator onok_ii = other._domp_nok.cbegin();
            while(nok_ii != _domp_nok.cend()){
                if((*nok_ii).compare(*onok_ii) != 0) {
                    if(SASS_ENC_DOM_COMPARE_OUTPUT) std::cout << "NOK list not identical: " << *nok_ii << " != " << *onok_ii << std::endl;
                    return false;
                }
                nok_ii++;
                onok_ii++;
            }

            return true;
        }

        bool operator!=(const SASS_Enc_Dom& other) const { return !operator==(other); }
        static void enable_compare_output(){ SASS_ENC_DOM_COMPARE_OUTPUT = true; }
        static void disable_compare_output(){ SASS_ENC_DOM_COMPARE_OUTPUT = false; }
        const size_t last_variant_index() { return _last_variant_index; }
        const std::string& last_instruction_class() { return _last_instruction_class; }
        const std::map<std::string, SASS_Bits> last_pick_result() { return _last_pick_result; }
        const TDomp& domp(){ return _domp; }
        const TAllVariantsBR& domp_v() { return _domp_v; }
        const TDompNok& domp_nok(){ return _domp_nok; }
        const bool instr_exists(const std::string& instr_class) const { return _domp.contains(instr_class); }

        // SASS_Enc_Dom_Iter __var_iter__(const std::string& instr_class, const std::vector<std::string>& keys){
        //     return SASS_Enc_Dom_Iter(keys);
        // }

        std::string instr_class_to_str(const std::string& instr_class){
            if(!_domp.contains(instr_class)) return std::vformat("Instr class [{0}] not found", std::make_format_args(instr_class));
            size_t ind = _domp.at(instr_class);
            const auto& vec = _domp_v.at(ind);
            std::stringstream ss;
            ss << instr_class << " count: " << vec.size() << std::endl;
            size_t counter = 0;
            for(const auto& c : vec) {
                ss << "  Variant " << counter << ": " << c.size();
                auto& var_map = vec.at(counter);

                size_t set_count = 0;
                size_t range_count = 0;
                for(const auto& enc : var_map) {
                    if(enc.second.index() == 0) set_count++;
                    else if(enc.second.index() == 1) range_count++;
                    else throw std::runtime_error("Unexpected: variant map contains something invalid");
                }
                counter++;
                ss << " [#sets=" << set_count << ", #range=" << range_count << "]" << std::endl;
            }
            return ss.str();
        }

        std::string instr_class_variant_to_str(const std::string& instr_class, const size_t& var_ind){
            if(!_domp.contains(instr_class)) return std::vformat("Instr class [{0}] not found", std::make_format_args(instr_class));
            size_t ind = _domp.at(instr_class);
            const auto& vec = _domp_v.at(ind);
            if(vec.size() <= var_ind) return std::vformat("Instr class [{0}(ind={1})] not found", std::make_format_args(instr_class, var_ind));
            auto& var_map = vec.at(var_ind);

            std::stringstream ss;
            ss << instr_class << "(ind=" << var_ind << ") count: " << var_map.size() << std::endl;
            size_t max_len = 0;
            for(const auto& enc : var_map) {
                if(enc.first.size() > max_len) max_len = enc.first.size();
            }
            for(const auto& enc : var_map) {
                if(enc.second.index() == 0) {
                    ss << "   [set<SASS_Bits>] ";
                    ss << std::right << std::setw(max_len) << enc.first << " = {";
                    const std::set<SASS_Bits>& bb = std::get<std::set<SASS_Bits>>(enc.second);
                    size_t cc = 0;
                    for(const auto& b : bb){
                        ss << SASS_Bits::__str__(b);
                        if(cc < bb.size()-1) ss << ", ";
                        cc++;
                    }
                    ss << "}" << std::endl;
                }
                else if(enc.second.index() == 1) {
                    ss << "       [SASS_Range] ";
                    ss << std::right << std::setw(max_len) << enc.first << " = ";
                    const SASS_Range& bb = std::get<SASS_Range>(enc.second);
                    ss << SASS_Range::pretty(bb) << std::endl;
                }
                else throw std::runtime_error("Unexpected: variant map contains something invalid");
            }
            return ss.str();
        }

        void add_nok_instr_classes(const StrVector& nok_instr_classes, bool clear_first=true){
            if(clear_first) _domp_nok.clear();
            for(const auto& c : nok_instr_classes){
                _domp_nok.push_back(c);
            }
        }

        std::string nok_classes_to_str(){
            std::stringstream ss;
            ss << "NOK Class Count: " << _domp_nok.size() << std::endl;
            if(_domp_nok.size() > 0) ss << "  [";
            size_t counter = 0;
            for(auto c=_domp_nok.cbegin(); c!=_domp_nok.cend(); ++c) {
                ss << *c;
                if(counter < _domp_nok.size()-1) ss << ", ";
                counter++;
            }
            if(_domp_nok.size() > 0) ss << "]" << std::endl;
            return ss.str();
        }

        std::string pretty(){
            std::stringstream ss;
            ss << "Instr Class Count: " << _domp.size() << std::endl;

            for(const auto& c : _domp) ss << "  " << c.first << ": " << _domp_v.at(c.second).size() << " variants" << std::endl;
            ss << nok_classes_to_str();
            return ss.str();
        }

        void dump(const std::string& filename, bool compressed, bool as_txt){ 
            if(as_txt) SASS_Enc_Dom_Lib::serialize(filename, _domp, _domp_v, _domp_nok);
            else SASS_Enc_Dom_Lib::serialize_bin(filename, _domp, _domp_v, _domp_nok, compressed);
        }

        size_t add_instr_class(const std::string& instr_class){
            size_t location = 0;
            if(!_domp.contains(instr_class)){
                size_t ind = _domp_v.size();
                _domp.insert({instr_class, ind});
                _domp_v.push_back({});
                location = ind;
            }
            else {
                location = _domp.at(instr_class);
            }
            return location;
        }

        size_t add_instr_class_enc(const size_t& instr_class_ind){
            if(_domp_v.size() <= instr_class_ind) throw std::runtime_error("Illegal: _domp_v.size() <= instr_class_ind");
            auto& vec = _domp_v.at(instr_class_ind);
            vec.push_back({});
            return vec.size()-1;
        }

        size_t add_instr_class_enc_set(const size_t& instr_class_ind, const size_t& enc_ind, const std::string& enc_name, const std::set<SASS::SASS_Bits>& enc_values){
            if(_domp_v.size() <= instr_class_ind) throw std::runtime_error("Illegal: _domp_v.size() <= instr_class_ind");
            if(_domp_v.at(instr_class_ind).size() <= enc_ind) throw std::runtime_error("Illegal: _domp_v.size() <= instr_class_ind");
            TVariantMapBR& var_map = _domp_v.at(instr_class_ind).at(enc_ind);
            if(var_map.contains(enc_name)) throw std::runtime_error(std::vformat("Illegal: tried to add existing enc_name [{0}]", std::make_format_args(enc_name)));
            var_map.insert({enc_name, std::move(enc_values)});
            return var_map.size();
        }

        size_t add_instr_class_enc_range(const size_t& instr_class_ind, const size_t& enc_ind, const std::string& enc_name, const SASS_Range& enc_values){
            if(_domp_v.size() <= instr_class_ind) throw std::runtime_error("Illegal: _domp_v.size() <= instr_class_ind");
            if(_domp_v.at(instr_class_ind).size() <= enc_ind) throw std::runtime_error("Illegal: _domp_v.size() <= instr_class_ind");
            TVariantMapBR& var_map = _domp_v.at(instr_class_ind).at(enc_ind);
            if(var_map.contains(enc_name)) throw std::runtime_error(std::vformat("Illegal: tried to add existing enc_name [{0}]", std::make_format_args(enc_name)));
            var_map.insert({enc_name, std::move(enc_values)});
            return var_map.size();
        }

        bool check_instr_class_enc_len(const size_t& instr_class_ind, const size_t& enc_ind, const size_t& required_len){
            if(_domp_v.size() <= instr_class_ind) throw std::runtime_error("Illegal: _domp_v.size() <= instr_class_ind");
            if(_domp_v.at(instr_class_ind).size() <= enc_ind) throw std::runtime_error("Illegal: _domp_v.size() <= instr_class_ind");
            if(_domp_v.at(instr_class_ind).at(enc_ind).size() != required_len) return false;
            return true;
        }

        std::map<std::string, SASS_Bits> pick(const std::string& instr_class){
            if(!_domp.contains(instr_class)) throw std::runtime_error(std::vformat("Illegal: instruction class [{0}] not found!", std::make_format_args(instr_class)));

            size_t ind = _domp.at(instr_class);
            // get vector of variants
            const std::vector<TVariantMapBR>& p = _domp_v.at(ind);

            // select an entry in that variant vector
            // (uniform_int_distribution goes onto closed interval [a,b] => subtract 1)
            auto dist = std::uniform_int_distribution<size_t>(0, p.size()-1);
            size_t variant_ind = dist(*_generator);
            
            std::map<std::string, SASS_Bits> res = get(instr_class, variant_ind);

            // store the last result to simplify potential debugging
            _last_pick_result = res;
            _last_instruction_class = instr_class;
            _last_variant_index = variant_ind;
            
            return res;
        }

        static std::vector<std::vector<SASS_Bits>> cart_product (const std::vector<std::vector<SASS_Bits>>& in) {
            // note: this creates a vector containing one empty vector
            std::vector<std::vector<SASS_Bits>> results = {{}};
            for (const auto& new_values : in) {
                // helper vector so that we don't modify results while iterating
                std::vector<std::vector<SASS_Bits>> next_results;
                for (const auto& result : results) {
                    for (const auto& value : new_values) {
                        next_results.push_back(result);
                        next_results.back().push_back(value);
                    }
                }
                results = std::move(next_results);
            }
            return std::move(results);
        }

        static std::vector<std::vector<int>> cart_product_by_inds (const std::vector<std::vector<SASS_Bits>>& in) {
            // note: this creates a vector containing one empty vector
            std::vector<std::vector<int>> results = {{}};
            int in_size = static_cast<int>(in.size());
            for (int new_values=0; new_values<in_size; ++new_values) {
                // helper vector so that we don't modify results while iterating
                std::vector<std::vector<int>> next_results;
                int results_size = static_cast<int>(results.size());
                for (int result=0; result<results_size; ++result) {
                    int new_values_size = static_cast<int>(in.at(new_values).size());
                    for (int value=0; value<new_values_size; ++value) {
                        next_results.push_back(results.at(result));
                        next_results.back().push_back(value);
                    }
                }
                results = std::move(next_results);
            }
            return std::move(results);
        }

        SASS_Enc_Dom_Iter __fixed_iter(const std::string& instr_class){
            if(_fixed_instr_class.compare("") == 0) throw std::runtime_error(std::vformat("Illegal: fixed instruction class not set! Use SASS_Enc_Dom.fix('{0}', map(..fixed_keys..)) first!", std::make_format_args(instr_class)));
            if(_fixed_instr_class.compare(instr_class) != 0) throw std::runtime_error(std::vformat("Illegal: given instr_class [{0}] doesn't match fixed instruction class [{1}]! Use SASS_Enc_Dom.fix('{0}', map(..fixed_keys..)) first!", std::make_format_args(instr_class, _fixed_instr_class)));
            return SASS_Enc_Dom_Iter(_fixed_instr_class, _fixed_inputs.cbegin(), _fixed_inputs.cend(), &_fixed_class_no_exceptions);
        }

        bool check_contains(const std::vector<std::string>& keys, const std::vector<SASS_Bits>& values, const TVariantMapBR& var_map){
            size_t k_size = keys.size();
            for(size_t ks=0; ks<k_size; ++ks){
                const auto& variant = var_map.at(keys.at(ks));

                if(variant.index() == 0){
                    const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(variant);
                    // for each possible set, check if all the anker values are contained.
                    //  => if they are, store the index
                    const std::set<SASS_Bits> cur = { values.at(ks) };
                    std::vector<SASS_Bits> v_intersection;
                    // need this cumbersome way, because otherwise it doesn't work
                    std::set_intersection(sass_bits_set.begin(), sass_bits_set.end(), cur.begin(), cur.end(), std::back_inserter(v_intersection));

                    if(v_intersection.size() == 0)
                        return false;
                }
                else {
                    const SASS_Range& sass_range = std::get<SASS_Range>(variant);
                    if(!SASS_Range::__contains__(sass_range, values.at(ks)))
                        return false;
                }
            }
            return true;
        }

        SASS_Enc_Dom_Iter2 __fixed_iter2(const std::string& instr_class, const std::map<std::string, std::set<SASS_Bits>>& ankers){
            if(!_domp.contains(instr_class)) throw std::runtime_error(std::vformat("Illegal: instruction class [{0}] not found!", std::make_format_args(instr_class)));

            // if(_fixed_instr_class.compare("") == 0) throw std::runtime_error(std::vformat("Illegal: fixed instruction class not set! Use SASS_Enc_Dom.fix('{0}', map(..fixed_keys..)) first!", std::make_format_args(instr_class)));
            // if(_fixed_instr_class.compare(instr_class) != 0) throw std::runtime_error(std::vformat("Illegal: given instr_class [{0}] doesn't match fixed instruction class [{1}]! Use SASS_Enc_Dom.fix('{0}', map(..fixed_keys..)) first!", std::make_format_args(instr_class, _fixed_instr_class)));
            std::vector<std::string> keys;
            std::vector<std::vector<SASS_Bits>> values;
            for(const auto& p : ankers){
                keys.push_back(p.first);
                values.push_back(std::vector<SASS_Bits>(p.second.begin(), p.second.end()));
            }

            auto product = cart_product_by_inds(values);

            size_t ind = _domp.at(instr_class);
            // get vector of variants
            const std::vector<TVariantMapBR>& p = _domp_v.at(ind);

            std::vector<std::vector<size_t>> product_inds_into_domains;
            size_t size = product.size();
            size_t set_size = keys.size();
            size_t p_size = p.size();
            // Iterate all anker-cross-products
            for(size_t i=0; i<size; ++i){
                // initialize the result vector
                std::vector<size_t> res;
                const std::vector<int>& i_values = product.at(i);
                std::vector<SASS_Bits> sass_i_values;

                // auto product_inds = SASS::SASS_Enc_Dom::cart_product_by_inds(values);
                // bool same = true;
                // for(size_t outer_ind=0; outer_ind<product_inds.size(); ++outer_ind){
                for(size_t col_ind=0; col_ind<i_values.size(); ++col_ind){
                    // int row_ind = outer_ind;
                    int value_ind = i_values.at(col_ind);

                    sass_i_values.push_back(values.at(col_ind).at(value_ind));
                    // auto bb2 = product.at(row_ind).at(col_ind);
                    // if(bb1 != bb2) same = false;
                }
                // }

                // for each anker-cross-product, iterate all possible sets of sets
                for(size_t p_ind=0; p_ind<p_size; ++p_ind){
                    // var_map is an std::map<std::string, std::variant> === TVariantMapBR
                    const auto& var_map = p.at(p_ind);

                    if(check_contains(keys, sass_i_values, var_map)){
                        res.push_back(p_ind);
                    }
                }

                // add the result vector to the product possibilities
                product_inds_into_domains.push_back(res);
            }
            
            return SASS_Enc_Dom_Iter2(std::move(instr_class), std::move(keys), std::move(product), std::move(values), std::move(product_inds_into_domains), ind, &_domp_v);
        }

        FixedPickVector fix(const std::string& instr_class, const std::map<std::string, std::set<SASS_Bits>>& ankers, const std::map<std::string, std::set<SASS_Bits>>& exceptions){
            if(!_domp.contains(instr_class)) throw std::runtime_error(std::vformat("Illegal: instruction class [{0}] not found!", std::make_format_args(instr_class)));
            _fixed_instr_class = instr_class;

            size_t ind = _domp.at(instr_class);
            // get vector of variants
            const std::vector<TVariantMapBR>& p = _domp_v.at(ind);
            
            // std::map<std::string, std::set<SASS_Bits>> key_bits;
            // for(const auto& kv : ankers){
            //     std::set<SASS_Bits> bb;
            //     for(const auto& v : kv.second){
            //         bb.insert(v);
            //     }
            //     key_bits.insert({kv.first, bb});
            // }

            // transfer all sets excluding the exceptions
            _fixed_class_no_exceptions.clear();
            for(size_t var_ind=0; var_ind < p.size(); ++var_ind){
                TVariantMapBR cur = p.at(var_ind);
                TVariantMapBR cur_res;
                for(auto& c : cur){
                    const auto& alias = c.first;
                    const auto& variant = c.second;
                    if(exceptions.contains(alias)) {
                        if(variant.index() == 0){
                            const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(variant);
                            const std::set<SASS_Bits>& loc_exceptions = exceptions.at(alias);
                            std::set<SASS_Bits> res;
                            std::set_difference(sass_bits_set.begin(), sass_bits_set.end(), loc_exceptions.begin(), loc_exceptions.end(), std::inserter(res, res.begin()));
                            cur_res.insert({alias, res});
                        }
                        else if (variant.index() == 1){
                            throw std::runtime_error(std::vformat("Entry {0} in [exceptions] is a SASS_Range. Can't make exceptions for SASS_Range!", std::make_format_args(alias)));
                        }
                        else {
                            throw std::runtime_error(std::vformat("Entry {0} in [exceptions] of unknown format. All entries must be either SASS_Range or set[SASS_Bits]", std::make_format_args(alias)));
                        }
                    }
                    else{
                        cur_res.insert({alias, variant});
                    }
                }
                _fixed_class_no_exceptions.push_back(cur_res);
            }

            _fixed_inputs.clear();
            for(size_t var_ind=0; var_ind < _fixed_class_no_exceptions.size(); ++var_ind){
                const auto& var = _fixed_class_no_exceptions.at(var_ind);
                bool ok=true;
                std::vector<std::string> option_names;
                std::vector<std::vector<SASS_Bits>> options;
                for(const auto& key_req : ankers){
                    const auto& variant = var.at(key_req.first);
                    std::vector<SASS_Bits> v_intersection;
                    if(variant.index() == 0){
                        const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(variant);
                        std::set_intersection(sass_bits_set.begin(), sass_bits_set.end(), key_req.second.begin(), key_req.second.end(), std::back_inserter(v_intersection));
                    }
                    else if(variant.index() == 1){
                        const SASS_Range& sass_range = std::get<SASS_Range>(variant);
                        v_intersection = SASS_Range::intersection_v(sass_range, key_req.second);
                    }

                    if(v_intersection.size() == 0) {
                        ok = false;
                        break;
                    }
                    else {
                        option_names.push_back(key_req.first);
                        options.push_back(v_intersection);
                    }
                }
                if(ok) {
                    // calculate carthesian product of all options
                    const auto c_options = cart_product(options);
                    // insert options according to their values.
                    // The result is a map that contains one carthesian product for the fixed keys and a vector
                    // of indices to all variants that fit that set of key values
                    for(const auto& option : c_options){
                        std::map<std::string, SASS_Bits> opt;
                        for(size_t ind=0; ind<option.size(); ++ind){
                            opt.insert({option_names.at(ind), option.at(ind)});
                        }
                        if(_fixed_inputs.contains(opt)){
                            _fixed_inputs.at(opt).push_back(var_ind);
                        }
                        else{
                            _fixed_inputs.insert({opt, {var_ind}});
                        }
                    }
                }
            }

            std::vector<std::map<std::string, SASS_Bits>> iter_res;
            for(const auto& i : _fixed_inputs){
                iter_res.push_back(i.first);
            }
            return iter_res;
        }

        std::map<std::string, SASS_Bits> get(const std::string& instr_class, size_t variant_index){
            if(!_domp.contains(instr_class)) throw std::runtime_error(std::vformat("Illegal: instruction class [{0}] not found!", std::make_format_args(instr_class)));
            // set some seed

            size_t ind = _domp.at(instr_class);
            // get vector of variants
            const std::vector<TVariantMapBR>& p = _domp_v.at(ind);

            // select an entry in that variant vector
            // (uniform_int_distribution goes onto closed interval [a,b] => subtract 1)
            size_t min_ind = 0;
            size_t max_ind = p.size()-1;
            if(variant_index < 0 || variant_index > max_ind){
                std::string msg = "Illegal: variant_index for instruction class [{0}] must be in [{1}, {2}] but [variant_index={3}]";
                throw std::runtime_error(std::vformat(msg, std::make_format_args(instr_class, min_ind, max_ind, variant_index)));
            }
            const TVariantMapBR& sub_var = p.at(variant_index);

            std::map<std::string, SASS_Bits> res;
            for(const auto& enc : sub_var){
                std::string enc_name = enc.first;
                if(enc.second.index() == 0){
                    // we have a set => select a random one
                    const std::set<SASS_Bits>& sass_bits_set = std::get<std::set<SASS_Bits>>(enc.second);
                    auto it = sass_bits_set.begin();
                    auto sub_dist = std::uniform_int_distribution<size_t>(0, sass_bits_set.size()-1);
                    size_t set_sel = sub_dist(*_generator);
                    std::advance(it, set_sel);
                    res.insert({enc_name, *it});
                }
                else {
                    // we have a range => pick a random one
                    SASS_Range sass_range = std::get<SASS_Range>(enc.second);
                    res.insert({enc_name, SASS_Range::pick(sass_range)});
                }
            }

            return res;
        }
    };
}