#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/unique_ptr.h>
#include <nanobind/stl/set.h>
#include <exception>
#include <sstream>
#include <set>
#include <vector>
#include <iostream>

#include "SASS_Bits.hpp"
#include "CPP_Faster.hpp"

namespace nb = nanobind;

NB_MODULE(_cpp_faster, m) {
nb::class_<ACC::CPP_Faster>(m, "CPP_Faster")
    .def_static("check_tables", [](const nb::dict& dom, const nb::dict& t_ind, const nb::dict& table, const nb::list& t_all){
        std::map<std::vector<int64_t>, int64_t> t_table;
        for(const auto& p : table){
            size_t ll = nb::len(p.first);
            std::vector<int64_t> val;
            val.reserve(ll);
            for(const auto& k : p.first) val.push_back(nb::cast<int64_t>(k));
            t_table.insert({val, nb::cast<int64_t>(p.second)});
        }

        // get the relevant portion of the domain, for example
        //   {'src1': {..}, 'src2': {..}, 'src3': {..}, 'src4': {..}} => [{....}, {....}]
        //                                                                 src1    src4
        nb::list t_dom;
        // NOTE: the 'indices' are the place a values has in the arguments list of the corresponding 'table', for example
        //   ('src1', 'src2', 0, 'src3') produces indices (0, 1, 3) for the three 'srcX' respectively.
        // get the indices into the arguments list into a vector, for example
        //   'src_name' : 0 => 0
        std::vector<int64_t> t_ind_inds;
        // get the inverse of the mapping into the domain, for example
        //   'src_name' : 0 => 0 : 'src_name'
        std::map<int64_t, std::string> t_ind_inv;
        for(const auto& ind : t_ind){
            t_dom.append(dom[ind.first]);
            int64_t value = nb::cast<int64_t>(ind.second);
            std::string key = nb::cast<std::string>(ind.first);
            t_ind_inds.push_back(value);
            t_ind_inv.insert({value, key});
        }

        // Produce the carthesian product of the sub-domain. This corresponds to Python's list(itertools.product(*t_dom))
        auto t_ind_combs = ACC::CPP_Faster::cart_product(t_dom);
        // Replace all entries of the arguments with integers, if they are not integers yet, for example
        //   t_all = ['src1', 'src2', 0, 'src3']
        // The three 'srcX' have to be replaced with their respective value in the current iteration while 0 stays constant
        std::vector<std::vector<int64_t>> t_args;
        for(const auto& comb : t_ind_combs){
            std::vector<int64_t> arg;
            size_t ci = 0;
            for(const auto& tall : t_all){
                if(nb::isinstance<std::string>(tall)){
                    // replace with current value
                    arg.push_back(SASS::SASS_Bits::__int__(comb.at(ci)));
                    ci++;
                }
                else if(nb::isinstance<int64_t>(tall)){
                    // keep the integer
                    arg.push_back(nb::cast<int64_t>(tall));
                }
            }
            t_args.push_back(std::move(arg));
        }
        // t_args is now a vector containing only vectors of integers. Each one is either a valid argument for 'table' or not.
        // There has to be one argument vector for each combination in t_ind_combs
        if(t_args.size() != t_ind_combs.size()) throw std::runtime_error("Unexpected: t_args.size() != t_ind_combs.size()");

        // Check if one arg in t_args is a valid argument.
        //  - If so, push the combination from t_ind_combs back to the list.
        //  - Otherwise, discard the sample
        auto combs_ii = t_ind_combs.cbegin();
        std::vector<std::vector<SASS::SASS_Bits>> res;
        for(const auto& arg : t_args){
            auto val_ii = t_table.find(arg);
            if(val_ii != t_table.end()){
                res.push_back(std::move(*combs_ii));
            }
            combs_ii++;
        }

        // res now only contains valid samples. Reverse it to a dictionary using the reversed index map t_ind_inv
        //  - Each entry in t_ind_combs is a x = vector<SASS:SASS_Bits> and len(x) == len(t_ind_inds)
        //  - Each entry in t_ind_inds is a key for t_ind_inv
        //  - Each value in t_ind_inv is a key into the original sub-domain t_dom
        // This reconstructs t_dom but with only the valid entries and as a Python mappable object who's ownership can then 
        // simply be passed back to Python.
        nb::list res_dicts;
        for(const auto& sassb : res){
            nb::dict dd;
            if(t_ind_inds.size() != sassb.size()) throw std::runtime_error("Unexpected: t_ind_inds.size() != sassb.size()");
            auto sbi = t_ind_inds.cbegin();
            for(const auto& sb : sassb){
                auto ii = t_ind_inv.find(*sbi);
                if(ii == t_ind_inv.end()) throw std::runtime_error("Unexpected: ii == t_ind_inv.end()");
                dd[(ii->second).c_str()] = sb;
                sbi++;
            }
            res_dicts.append(dd);
        }
        if(nb::len(res_dicts) == 0) throw std::runtime_error("Unexpected: nb::len(res_dicts) == 0");

        return std::move(res_dicts);
    }, nb::rv_policy::move)
    .def_static("test_t_map", [](const nb::dict vals){
        for(const auto& p : vals){
            std::cout << "(";
            for(const auto& k : p.first) std::cout << nb::cast<int>(k) << ',';
            std::cout << ") : " << nb::cast<int>(p.second) << std::endl;
        }
    }, nb::rv_policy::move);
}
