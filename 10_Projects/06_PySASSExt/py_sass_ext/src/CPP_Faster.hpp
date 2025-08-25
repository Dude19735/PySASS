#pragma once

#include <vector>
#include <set>
#include <tuple>
#include <map>
#include <nanobind/nanobind.h>
#include <iostream>
#include "SASS_Bits.hpp"

namespace nb = nanobind;

namespace ACC {
    class CPP_Faster{
    public:
        /**
         * Compute carthesian product
         * (Thank you stackoverflow: https://stackoverflow.com/questions/5279051/how-can-i-create-the-cartesian-product-of-a-vector-of-vectors)
         */
        static std::vector<std::vector<SASS::SASS_Bits>> cart_product (const nb::list& in) {
            // note: this creates a vector containing one empty vector
            std::vector<std::vector<SASS::SASS_Bits>> results = {{}};
            for (const auto& new_values : in) {
                // helper vector so that we don't modify results while iterating
                std::vector<std::vector<SASS::SASS_Bits>> next_results;
                for (const auto& result : results) {
                    for (const auto& value : new_values) {
                        next_results.push_back(result);
                        next_results.back().push_back(nb::cast<SASS::SASS_Bits>(value));
                    }
                }
                results = std::move(next_results);
            }
            return std::move(results);
        }

        static void test_t_map(std::map<std::vector<int>, int>& vals){
            for(const auto& p : vals){
                std::cout << "(";
                for(const auto& k : p.first) std::cout << k << ',';
                std::cout << ") : " << p.second << std::endl;
            }
        }
        
        /**
         * Accelerate part of the domain encoding calculations
         */
        // static std::vector<std::vector<SASS::SASS_Bits>> check_tables(
        //     // const std::vector<std::string>& t_all,
        //     const std::vector<std::set<SASS::SASS_Bits>>& t_dom,
        //     const std::map<std::vector<int64_t>, int64_t> table
        //     // const std::vector<int> t_ind_inds
        // ){
        //     // auto t_ind_combs = ACC::CPP_Faster::cart_product(t_dom);
        //     // return std::move(t_ind_combs);
        //     return {};
        // }
    };
}