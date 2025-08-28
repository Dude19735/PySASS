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

#include "CPP.hpp"

namespace nb = nanobind;

NB_MODULE(_cpp, m) {
nb::class_<ACC::CPP>(m, "CPP")
    .def(nb::init<>())
    .def_static("test_t_map", [&](const nb::dict vals){
        for(const auto& p : vals){
            std::cout << "(";
            for(const auto& k : p.first) std::cout << nb::cast<int>(k) << ',';
            std::cout << ") : " << nb::cast<int>(p.second) << std::endl;
        }
    }, nb::rv_policy::move)
    .def_static("test_replace", [&](const nb::dict& vals){
        for(const auto& k : vals.keys()){
            if(nb::cast<std::string>(k).compare("hello") == 0) vals[k] = "lol";
        }
    }, nb::rv_policy::move)
    .def_static("create", [&](nb::list& vals, int from, int to){
        for(int i=from; i<to; ++i){
            vals.append(i);
        }
    }, nb::rv_policy::move)
    .def_static("create_float", [&](nb::list& vals, int from, int to){
        for(int i=from; i<to; ++i){
            vals.append(nb::cast<float>(i));
        }
    }, nb::rv_policy::move)
    .def("__str__", [&](const ACC::CPP& self){
        return "CPP LOL";
    }, nb::rv_policy::move);
}
