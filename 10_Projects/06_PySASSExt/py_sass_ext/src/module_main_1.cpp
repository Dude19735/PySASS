#include <nanobind/nanobind.h>
#include <nanobind/stl/bind_vector.h>
#include <nanobind/stl/bind_map.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/set.h>
// #include <nanobind/stl/unordered_map.h>
// #include <nanobind/stl/map.h>
#include <nanobind/stl/variant.h>
#include <nanobind/nb_cast.h>
#include <exception>
#include <sstream>
#include <variant>
#include <set>
#include <map>
#include <memory>
#include <tuple>
#include <vector>
#include <iostream>

#include "SASS_Bits.hpp"
#include "SASS_Range_Lib.hpp"
#include "SASS_Range.hpp"
#include "SASS_Range_Iter.hpp"
#include "SASS_Enc_Dom.hpp"
#include "SASS_Enc_Dom_Iter.hpp"
#include "SASS_Enc_Dom_Iter2.hpp"
#include "TT_Terms.hpp"
#include "TT_Instruction.hpp"

namespace nb = nanobind;

namespace nanobind::detail {
    template<typename ..._Ts>
    struct type_caster<std::variant<_Ts...>> {
        NB_INLINE bool from_python(handle src, uint8_t flags, cleanup_list *) noexcept {
    //         if constexpr (std::is_floating_point_v<T>) {
    //             if constexpr (std::is_same_v<T, double>) {
    //                 return detail::load_f64(src.ptr(), flags, &value);
    //             } else if constexpr (std::is_same_v<T, float>) {
    //                 return detail::load_f32(src.ptr(), flags, &value);
    //             } else {
    //                 double d;
    //                 if (!detail::load_f64(src.ptr(), flags, &d))
    //                     return false;
    //                 T result = (T) d;
    //                 if ((flags & (uint8_t) cast_flags::convert)
    //                         || (double) result == d
    //                         || (result != result && d != d)) {
    //                     value = result;
    //                     return true;
    //                 }
    //                 return false;
    //             }
    //         } else {
    //             if constexpr (std::is_signed_v<T>) {
    //                 if constexpr (sizeof(T) == 8)
    //                     return detail::load_i64(src.ptr(), flags, (int64_t *) &value);
    //                 else if constexpr (sizeof(T) == 4)
    //                     return detail::load_i32(src.ptr(), flags, (int32_t *) &value);
    //                 else if constexpr (sizeof(T) == 2)
    //                     return detail::load_i16(src.ptr(), flags, (int16_t *) &value);
    //                 else
    //                     return detail::load_i8(src.ptr(), flags, (int8_t *) &value);
    //             } else {
    //                 if constexpr (sizeof(T) == 8)
    //                     return detail::load_u64(src.ptr(), flags, (uint64_t *) &value);
    //                 else if constexpr (sizeof(T) == 4)
    //                     return detail::load_u32(src.ptr(), flags, (uint32_t *) &value);
    //                 else if constexpr (sizeof(T) == 2)
    //                     return detail::load_u16(src.ptr(), flags, (uint16_t *) &value);
    //                 else
    //                     return detail::load_u8(src.ptr(), flags, (uint8_t *) &value);
    //             }
    //         }
        }

        NB_INLINE static handle from_cpp(T src, rv_policy, cleanup_list *) noexcept {
    //         if constexpr (std::is_floating_point_v<T>) {
    //             return PyFloat_FromDouble((double) src);
    //         } else {
    //             if constexpr (std::is_signed_v<T>) {
    //                 if constexpr (sizeof(T) <= sizeof(long))
    //                     return PyLong_FromLong((long) src);
    //                 else
    //                     return PyLong_FromLongLong((long long) src);
    //             } else {
    //                 if constexpr (sizeof(T) <= sizeof(unsigned long))
    //                     return PyLong_FromUnsignedLong((unsigned long) src);
    //                 else
    //                     return PyLong_FromUnsignedLongLong((unsigned long long) src);
    //             }
    //         }
        }

        NB_TYPE_CASTER(T, const_name<std::is_integral_v<T>>("int", "float"))
    };
}

NB_MODULE(_sass_values, m) {
    nb::bind_vector<BitVector>(m, "BitVector")
    .def("__getstate__", 
        [](const BitVector& bits){
            nb::list tt;
            for(int i=0; i<bits.size(); ++i) tt.append(bits[i]);
            return nb::tuple(nb::cast(tt));
        })
    .def("__setstate__", 
        [](BitVector& bits, const nb::tuple& state){
            new(&bits) BitVector();
            size_t size = state.size();
            bits.reserve(size);
            for(size_t i=0; i<size; ++i) bits.push_back(nb::cast<uint8_t>(state[i]));
        });

    nb::bind_vector<IntVector>(m, "IntVector")
    .def("__getstate__", 
        [](const IntVector& vec){
            nb::list tt;
            for(int i=0; i<vec.size(); ++i) tt.append(vec[i]);
            return nb::tuple(nb::cast(tt));
        })
    .def("__setstate__", 
        [](IntVector& vec, const nb::tuple& state){
            new(&vec) IntVector();
            size_t size = state.size();
            vec.reserve(size);
            for(size_t i=0; i<size; ++i) vec.push_back(nb::cast<int>(state[i]));
        });
    nb::bind_vector<SASS::TOpsVec>(m, "OpsVector");
    nb::bind_vector<SASS::TListVec>(m, "ListVector");
    nb::bind_vector<StrVector>(m, "StrVector");
    nb::bind_vector<FixedPickVector>(m, "FixedPickVector");
    nb::bind_vector<std::vector<std::string>>(m, "AliasVector");
    nb::bind_vector<std::vector<SASS::TT_Ext>>(m, "ExtVector");
    nb::bind_vector<std::vector<SASS::TT_AtOp>>(m, "OpVector");

    // nb::bind_vector<SASS::TCashComponentsVec>(m, "CashComponentsVector");
    // nb::bind_vector<SASS::TOperandVec>(m, "OperandVector");
    nb::bind_vector<SASS::TTestVec>(m, "TestVec");
    nb::bind_vector<SASS::TCashVec>(m, "CashVector");
    nb::bind_vector<SASS::TParamVec>(m, "ParamVector");
    nb::bind_map<SASS::TOptions>(m, "OptionsDict");
    nb::bind_map<SASS::TEvalDict>(m, "EvalDict");

    nb::class_<SASS::SASS_Bits>(m, "SASS_Bits")
    .def(nb::init<const BitVector&, int, bool>(),
        nb::arg("bits"), nb::arg("bit_len")=0, nb::arg("signed")=true)
    .def_prop_ro("version", [](){ return "0.0.4"; })
    .def_prop_ro("bits", &SASS::SASS_Bits::bits)
    .def_prop_ro("bit_len", &SASS::SASS_Bits::bit_len)
    .def_prop_ro("signed", &SASS::SASS_Bits::signed_)
    .def("__hash__", &SASS::SASS_Bits::__hash__)
    .def("__getstate__", 
        [](const SASS::SASS_Bits& bits){
            std::stringstream ss;
            for(const auto& b : bits.bits()) ss << static_cast<int>(b);
            return std::make_tuple(ss.str(), bits.bit_len(), bits.signed_());
        })
    .def("__setstate__", 
        [](SASS::SASS_Bits& bits, const std::tuple<std::string, int, bool>& state){
            std::string bb = std::get<0>(state);
            int bit_len = std::get<1>(state);
            bool sign = std::get<2>(state);
            BitVector b;
            b.reserve(bit_len);
            for(const auto& c : bb) b.push_back(static_cast<uint8_t>(c) - 48);
            new (&bits) SASS::SASS_Bits(b, bit_len, sign);
        })
    .def_static("enable_warnings", &SASS::SASS_Bits::enable_warnings)
    .def_static("disable_warnings", &SASS::SASS_Bits::disable_warnings)
    .def_static("enable_copy_warnings", &SASS::SASS_Bits::enable_copy_warnings)
    .def_static("disable_copy_warnings", &SASS::SASS_Bits::disable_copy_warnings)
    .def("__int__", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::__int__(x));
        })
    .def("__bool__", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::__bool__(x));
        })
    .def("__str__", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::__str__(x));
        })
    .def("__add__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__add__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__add__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__add__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__sub__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__sub__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__sub__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__sub__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__mul__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__mul__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__mul__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__mul__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: bool | int");
        })
    .def("__matmul__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__matmul__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__matmul__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__matmul__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__floordiv__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__floordiv__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__floordiv__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__floordiv__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__mod__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__mod__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__mod__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__mod__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__and__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__and__(x, nb::cast<SASS::SASS_Bits>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits");
        })
    .def("__xor__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__xor__(x, nb::cast<SASS::SASS_Bits>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits");
        })
    .def("__or__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__or__(x, nb::cast<SASS::SASS_Bits>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits");
        })
    .def("__neg__", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::__neg__(x));
        })
    .def("__pos__", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::__pos__(x));
        })
    .def("__abs__", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::__abs__(x));
        })
    .def("__lshift__", 
        [](const SASS::SASS_Bits& x, const int& num){
            return std::move(SASS::SASS_Bits::__lshift__(x, num));
        })
    .def("__rshift__", 
        [](const SASS::SASS_Bits& x, const int& num){
            return std::move(SASS::SASS_Bits::__rshift__(x, num));
        })
    .def("__lt__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__lt__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__lt__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__lt__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__le__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__le__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__le__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__le__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__eq__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__eq__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__eq__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__eq__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__ne__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__ne__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__ne__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__ne__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__gt__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__gt__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__gt__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__gt__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__ge__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            if(nb::isinstance<SASS::SASS_Bits>(other)){
                return std::move(SASS::SASS_Bits::__ge__sb(x, nb::cast<SASS::SASS_Bits>(other)));
            } else if(nb::isinstance<int64_t>(other)){
                return std::move(SASS::SASS_Bits::__ge__i(x, nb::cast<int64_t>(other)));
            } else if(nb::isinstance<bool>(other)){
                return std::move(SASS::SASS_Bits::__ge__b(x, nb::cast<bool>(other)));
            } else throw std::invalid_argument("Required: SASS_Bits | bool | int");
        })
    .def("__truediv__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            std::runtime_error("Truediv [a / b] is not supported in SASS_Bits");
        })
    .def("__divmod__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            std::runtime_error("Divmod [divmod(a,b)] is not supported in SASS_Bits");
        })
    .def("__pow__", 
        [](const SASS::SASS_Bits& x, const nb::object& other){
            std::runtime_error("Divmod [a**b] is not supported in SASS_Bits");
        })
    .def("scale", 
        [](const SASS::SASS_Bits& x, const int& val){
            return std::move(SASS::SASS_Bits::scale(x, val));
        })
    .def("multiply", 
        [](const SASS::SASS_Bits& x, const int& val){
            return std::move(SASS::SASS_Bits::multiply(x, val));
        })
    .def("as_unsigned", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::as_unsigned(x));
        })
    .def("as_signed", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::as_signed(x));
        })
    .def("to_unsigned", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::to_unsigned(x));
        })
    .def("to_signed", 
        [](const SASS::SASS_Bits& x){
            return std::move(SASS::SASS_Bits::to_signed(x));
        })
    .def("cast", 
        [](const SASS::SASS_Bits& x, int new_bit_len){
            return std::move(SASS::SASS_Bits::cast(x, new_bit_len));
        })
    .def("assemble", 
        [](const SASS::SASS_Bits& b, const BitVector& instr_bits, const IntVector& enc_inds, const int& sm_nr){
            return std::move(SASS::SASS_Bits::assemble(b, instr_bits, enc_inds, sm_nr));
        })
    .def_static("from_int", 
        [](const int64_t value, int bit_len, int signed_) -> SASS::SASS_Bits {
            return std::move(SASS::SASS_Bits::from_int(value, bit_len, signed_));
        }, nb::arg("val"), nb::arg("bit_len")=0, nb::arg("signed")=-1)
    .def_static("from_uint", 
        [](const uint64_t value, int bit_len) -> SASS::SASS_Bits {
            return std::move(SASS::SASS_Bits::from_uint(value, bit_len));
        }, nb::arg("val"), nb::arg("bit_len")=0)
    .def("encode", 
        [](const SASS::SASS_Bits& self) -> nb::bytes {
            bool s = self.signed_();
            uint8_t data[11] = {11, static_cast<uint8_t>(s), static_cast<uint8_t>(self.bit_len()), 0, 0, 0, 0, 0, 0, 0, 0};
            if(s){
                int64_t v = SASS::SASS_Bits::__int__(self);
                memcpy(&data[3], &v, 8);
            }
            else{
                int64_t v = SASS::SASS_Bits::__uint__(self);
                memcpy(&data[3], &v, 8);
            }
            nb::bytes b(reinterpret_cast<void*>(data), 11);
            
            return std::move(b);
        }, nb::rv_policy::move)
    .def_static("decode", 
        [](const nb::bytes& b) -> SASS::SASS_Bits {
            const uint8_t* data = reinterpret_cast<const uint8_t*>(b.c_str());
            int signed_ = static_cast<int>(data[1]);
            int bit_len = static_cast<int>(data[2]);
            if(signed_ == 1) {
                const int64_t value = *reinterpret_cast<const int64_t*>(&data[3]);
                return std::move(SASS::SASS_Bits::from_int(value, bit_len, signed_));
            }
            const uint64_t value = *reinterpret_cast<const uint64_t*>(&data[3]);
            return std::move(SASS::SASS_Bits::from_uint(value, bit_len));
        }, nb::arg("encoded_bytes"), nb::rv_policy::move);

    nb::class_<SASS::SASS_Range_Limits>(m, "SASS_Range_Limits")
    .def_ro("range_min", &SASS::SASS_Range_Limits::range_min)
    .def_ro("effective_min", &SASS::SASS_Range_Limits::effective_min)
    .def_ro("range_max", &SASS::SASS_Range_Limits::range_max)
    .def_ro("effective_max", &SASS::SASS_Range_Limits::effective_max)
    .def_ro("size", &SASS::SASS_Range_Limits::size)
    .def_ro("size_overflow", &SASS::SASS_Range_Limits::size_overflow);

    nb::class_<SASS::SASS_Range>(m, "SASS_Range")
    .def(nb::init<int64_t, uint64_t, uint8_t, uint8_t, uint64_t>(),
        nb::arg("range_min"), nb::arg("range_max"), nb::arg("bit_len"), nb::arg("signed"), nb::arg("bit_mask"))
    .def("__getstate__", 
        [](const SASS::SASS_Range& r){
            return SASS::SASS_Range::to_tuple(r);
        })
    .def("__setstate__", 
        [](SASS::SASS_Range& range, const std::tuple<int64_t, uint64_t, uint64_t, uint8_t, uint8_t>& state){
            int64_t range_min = std::get<0>(state);
            uint64_t range_max = std::get<1>(state);
            uint64_t bit_mask = std::get<2>(state);
            uint8_t bit_len = std::get<3>(state);
            uint8_t signed_ = std::get<4>(state);
            new (&range) SASS::SASS_Range(range_min, range_max, bit_len, signed_, bit_mask);
        })
    .def("enable_size_warnings", &SASS::SASS_Range::enable_size_warnings)
    .def("disable_size_warnings", &SASS::SASS_Range::disable_size_warnings)
    .def_prop_ro("range_min", &SASS::SASS_Range::range_min)  
    .def_prop_ro("range_max", &SASS::SASS_Range::range_max)  
    .def_prop_ro("bit_len", &SASS::SASS_Range::bit_len)    
    .def_prop_ro("bit_mask", &SASS::SASS_Range::bit_mask)
    .def_prop_ro("max_val", &SASS::SASS_Range::max_val)
    .def_prop_ro("signed", &SASS::SASS_Range::signed_)
    .def_prop_ro("limits", &SASS::SASS_Range::limits)
    .def("__bool__", 
        [](const SASS::SASS_Range& x){
            return std::move(SASS::SASS_Range::__bool__(x));
        })
    .def("__str__", 
        [](const SASS::SASS_Range& x){
            return std::move(SASS::SASS_Range::pretty(x));
        })
    .def("__len__", 
        [](const SASS::SASS_Range& x){
            if(x.limits().size_overflow){
                if(SASS::SASS_RANGE_SIZE_WARNINGS) std::cout << "[WARNING] SASS_Range size overflow due to max range. Cap len to int64::max!" << std::endl;
                return std::numeric_limits<int64_t>::max();
            }
            uint64_t s = std::move(SASS::SASS_Range::size(x));
            if(s > std::numeric_limits<int64_t>::max()) {
                if(SASS::SASS_RANGE_SIZE_WARNINGS) std::cout << "[WARNING] SASS_Range size [" << s << "] too large for Python. Capping to int64::max!" << std::endl;
                return std::numeric_limits<int64_t>::max();
            }
            return static_cast<int64_t>(s);
        })
    .def("__eq__", 
        [](const SASS::SASS_Range& x, const SASS::SASS_Range& other){
            return x == other;
        })
    .def("__max__", 
        [](const SASS::SASS_Range& x){
            return std::move(SASS::SASS_Range::__max__(x));
        })
    .def("__min__", 
        [](const SASS::SASS_Range& x){
            return std::move(SASS::SASS_Range::__min__(x));
        })
    .def("__contains__", 
        [](const SASS::SASS_Range& x, const SASS::SASS_Bits& b){
            return SASS::SASS_Range::__contains__(x, b);
        })
    .def("__iter__", 
        [](SASS::SASS_Range& x){
            return std::move(SASS::SASS_Range::__iter__(x));
        })
    .def("sized_iter", 
        [](SASS::SASS_Range& x, uint64_t sample_size){
            return std::move(SASS::SASS_Range::__sized_iter__(x, sample_size));
        }, nb::arg("sample_size"))
    .def("size", 
        [](const SASS::SASS_Range& x){
            return std::move(SASS::SASS_Range::size(x));
        })
    .def("add_bit_mask", 
        [](SASS::SASS_Range& x, uint64_t bit_mask){
            SASS::SASS_Range::add_bit_mask(x, bit_mask);
            return std::move(x);
        })
    .def("empty", 
        [](const SASS::SASS_Range& x){
            return std::move(SASS::SASS_Range::empty(x));
        })
    .def("pick", 
        [](SASS::SASS_Range& x){
            return std::move(SASS::SASS_Range::pick(x));
        })
    .def("intersection", 
        [](const SASS::SASS_Range& x, const SASS::SASS_Range& other){
            return std::move(SASS::SASS_Range::intersection_r(x, other));
        })
    .def("intersection", 
        [](const SASS::SASS_Range& x, const std::set<SASS::SASS_Bits>& other){
            return std::move(SASS::SASS_Range::intersection_s(x, other));
        })
    .def("encode", 
        [](const SASS::SASS_Range& self) -> nb::bytes {
            /*8*/int64_t range_min = self.range_min();
            /*16*/uint64_t range_max = self.range_max();
            /*24*/uint64_t bit_mask = self.bit_mask();
            /*25*/uint8_t bit_len = self.bit_len();
            /*26*/uint8_t signed_ = self.signed_();
            uint8_t data[27];
            data[0] = 27;
            data[1] = signed_;
            data[2] = bit_len;
            memcpy(&data[3], &range_min, 8);
            memcpy(&data[11], &range_max, 8);
            memcpy(&data[19], &bit_mask, 8);
            
            nb::bytes b(reinterpret_cast<void*>(data), 27);
            return std::move(b);
        }, nb::rv_policy::move)
    .def_static("decode", 
        [](const nb::bytes& b) -> SASS::SASS_Range {
            const uint8_t* data = reinterpret_cast<const uint8_t*>(b.c_str());
            uint8_t signed_ = data[1];
            uint8_t bit_len = data[2];
            int64_t range_min = *reinterpret_cast<const int64_t*>(&data[3]);
            uint64_t range_max = *reinterpret_cast<const uint64_t*>(&data[11]);
            uint64_t bit_mask = *reinterpret_cast<const uint64_t*>(&data[19]);

            return std::move(SASS::SASS_Range(range_min, range_max, bit_len, signed_, bit_mask));
        }, nb::arg("encoded_bytes"), nb::rv_policy::move);

    nb::class_<SASS::SASS_Range_Iter>(m, "SASS_Range_Iter")
    .def("__finished__", &SASS::SASS_Range_Iter::__finished__)
    .def("__iter__", [](SASS::SASS_Range_Iter& x){ return std::move(x); })
    .def("__next__", 
    [](SASS::SASS_Range_Iter& x){
        if(x.__finished__()) throw nb::stop_iteration();
        bool finished;
        return std::move(x.__next__(finished));
    });

    nb::class_<SASS::SASS_Enc_Dom>(m, "SASS_Enc_Dom")
    .def(nb::init<std::string, bool, bool, bool>(),
        nb::arg("filename"), nb::arg("show_progress")=false, nb::arg("compressed")=true, nb::arg("as_txt")=false)
    .def("dump", &SASS::SASS_Enc_Dom::dump,
        nb::arg("filename"), nb::arg("compressed")=true, nb::arg("as_txt")=false)
    .def_static("create_new_empty", &SASS::SASS_Enc_Dom::create_new_empty)
    .def("add_instr_class", &SASS::SASS_Enc_Dom::add_instr_class, nb::arg("instr_class"))
    .def("add_instr_class_enc", &SASS::SASS_Enc_Dom::add_instr_class_enc, nb::arg("instr_class_ind"))
    .def("add_instr_class_enc_set", &SASS::SASS_Enc_Dom::add_instr_class_enc_set, nb::arg("instr_class_ind"), nb::arg("enc_ind"), nb::arg("enc_name"), nb::arg("enc_values"))
    .def("add_instr_class_enc_range", &SASS::SASS_Enc_Dom::add_instr_class_enc_range, nb::arg("instr_class_ind"), nb::arg("enc_ind"), nb::arg("enc_name"), nb::arg("enc_values"))
    .def("check_instr_class_enc_len", &SASS::SASS_Enc_Dom::check_instr_class_enc_len, nb::arg("instr_class_ind"), nb::arg("enc_ind"), nb::arg("required_len"))
    .def("add_nok_instr_classes", &SASS::SASS_Enc_Dom::add_nok_instr_classes, nb::arg("nok_instr_classes"), nb::arg("clear_first")=true)
    .def("nok_classes_to_str", &SASS::SASS_Enc_Dom::nok_classes_to_str)
    .def("enable_compare_output", &SASS::SASS_Enc_Dom::enable_compare_output)
    .def("disable_compare_output", &SASS::SASS_Enc_Dom::disable_compare_output)
    .def("domp", &SASS::SASS_Enc_Dom::domp)
    .def("domp_nok", &SASS::SASS_Enc_Dom::domp_nok)
    .def("__str__", &SASS::SASS_Enc_Dom::pretty)
    .def("instr_class_to_str", &SASS::SASS_Enc_Dom::instr_class_to_str, nb::arg("instr_class"))
    .def("instr_class_variant_to_str", &SASS::SASS_Enc_Dom::instr_class_variant_to_str, nb::arg("instr_class"), nb::arg("variant_ind"))
    .def("__eq__", [](SASS::SASS_Enc_Dom& self, SASS::SASS_Enc_Dom& other) -> bool { return self == other; } )
    .def("__ne__", [](SASS::SASS_Enc_Dom& self, SASS::SASS_Enc_Dom& other) -> bool { return !(self == other); } ) 
    .def_prop_ro("last_variant_index", &SASS::SASS_Enc_Dom::last_variant_index)
    .def_prop_ro("last_instruction_class", &SASS::SASS_Enc_Dom::last_instruction_class)
    .def_prop_ro("last_pick_result", &SASS::SASS_Enc_Dom::last_pick_result)
    .def("pick", &SASS::SASS_Enc_Dom::pick, nb::arg("instr_class"))
    .def("get", &SASS::SASS_Enc_Dom::get, nb::arg("instr_class"), nb::arg("variant_index"))
    .def("instr_exists", &SASS::SASS_Enc_Dom::instr_exists, nb::arg("instr_class"))
    .def("fix", &SASS::SASS_Enc_Dom::fix, nb::arg("instr_class"), nb::arg("ankers"), nb::arg("exceptions"))
    .def("fixed_iter", &SASS::SASS_Enc_Dom::__fixed_iter, nb::arg("instr_class"))
    .def("fixed_iter2", &SASS::SASS_Enc_Dom::__fixed_iter2, nb::arg("instr_class"), nb::arg("ankers"));

    nb::class_<SASS::SASS_Enc_Dom_Iter>(m, "SASS_Enc_Dom_Iter")
    .def("__iter__", [](SASS::SASS_Enc_Dom_Iter& x){ return std::move(x); })
    .def("__next__", 
        [](SASS::SASS_Enc_Dom_Iter& x){
            bool finished;
            const auto& res = x.__next__(finished);
            if(finished) throw nb::stop_iteration();
            else return std::move(res);
    });

    nb::class_<SASS::SASS_Enc_Dom_Iter2>(m, "SASS_Enc_Dom_Iter2")
    .def("__iter__", [](SASS::SASS_Enc_Dom_Iter2& x){ return std::move(x); })
    .def("__next__", 
        [](SASS::SASS_Enc_Dom_Iter2& x){
            bool finished;
            const auto& res = x.__next__(finished);
            if(finished) throw nb::stop_iteration();
            else return std::move(res);
    });

    nb::class_<SASS::TT_Alias>(m, "TT_Alias")
    .def(nb::init<std::string>())
    .def_prop_ro("alias", &SASS::TT_Alias::alias)
    .def_prop_ro("value", &SASS::TT_Alias::value)
    .def("__str__", &SASS::TT_Alias::__str__)
    .def("__getstate__", &SASS::TT_Alias::__getstate__)
    .def("__setstate__", &SASS::TT_Alias::__setstate__);

    nb::enum_<SASS::AtOp>(m, "AtOp")
    .value("Not", SASS::AtOp::Not)
    .value("Abs", SASS::AtOp::Abs)
    .value("Invert", SASS::AtOp::Invert)
    .value("Negate", SASS::AtOp::Negate)
    .value("Sign", SASS::AtOp::Sign);

    nb::class_<SASS::TT_AtOp>(m, "TT_AtOp")
    .def(nb::init<std::string, std::string, std::string, uint8_t>(), nb::arg("op_name"), nb::arg("op_sign"), nb::arg("reg_alias"), nb::arg("op_type"))
    .def_prop_ro("alias", &SASS::TT_AtOp::alias)
    .def_prop_ro("op_type", &SASS::TT_AtOp::op_type)
    .def_prop_ro("value", &SASS::TT_AtOp::value)
    .def_prop_ro("op_name", &SASS::TT_AtOp::op_name)
    .def("get_domain", &SASS::TT_AtOp::get_domain, nb::arg("to_limit"), nb::arg("filter_invalid")=false)
    .def("get_enc_alias", &SASS::TT_AtOp::get_enc_alias)
    .def("__str__", &SASS::TT_AtOp::__str__)
    .def("__getstate__", &SASS::TT_AtOp::__getstate__)
    .def("__setstate__", &SASS::TT_AtOp::__setstate__);

    nb::class_<SASS::TT_OpAtNot, SASS::TT_AtOp>(m, "TT_OpAtNot")
    .def(nb::init<std::string>(), nb::arg("reg_alias"));
    nb::class_<SASS::TT_OpAtNegate, SASS::TT_AtOp>(m, "TT_OpAtNegate")
    .def(nb::init<std::string>(), nb::arg("reg_alias"));
    nb::class_<SASS::TT_OpAtAbs, SASS::TT_AtOp>(m, "TT_OpAtAbs")
    .def(nb::init<std::string>(), nb::arg("reg_alias"));
    nb::class_<SASS::TT_OpAtSign, SASS::TT_AtOp>(m, "TT_OpAtSign")
    .def(nb::init<std::string>(), nb::arg("reg_alias"));
    nb::class_<SASS::TT_OpAtInvert, SASS::TT_AtOp>(m, "TT_OpAtInvert")
    .def(nb::init<std::string>(), nb::arg("reg_alias"));

    nb::class_<SASS::TT_CashComponent>(m, "TT_CashComponent")
    .def(nb::init<std::string>(), nb::arg("cash_value"))
    .def_prop_ro("value", &SASS::TT_CashComponent::value)
    .def("__str__", &SASS::TT_CashComponent::__str__)
    .def("__getstate__", &SASS::TT_CashComponent::__getstate__ )
    .def("__setstate__", &SASS::TT_CashComponent::__setstate__ );
    nb::class_<SASS::TT_OpCashQuestion, SASS::TT_CashComponent>(m, "TT_OpCashQuestion").def(nb::init<>());
    nb::class_<SASS::TT_OpCashAnd, SASS::TT_CashComponent>(m, "TT_OpCashAnd").def(nb::init<>());
    nb::class_<SASS::TT_OpCashAssign, SASS::TT_CashComponent>(m, "TT_OpCashAssign").def(nb::init<>());

    nb::class_<SASS::TT_Default>(m, "TT_Default")
    .def(nb::init<SASS::TValue, bool, SASS::TOptions>(), nb::arg("def_name"), nb::arg("has_print"), nb::arg("options"))
    .def_prop_ro("exists", &SASS::TT_Default::exists)
    .def_prop_ro("options", &SASS::TT_Default::options)
    .def_prop_ro("has_print", &SASS::TT_Default::has_print)
    .def_prop_ro("value", &SASS::TT_Default::value)
    .def("__str__", &SASS::TT_Default::__str__)
    .def("__getstate__", &SASS::TT_Default::__getstate__ )
    .def("__setstate__", &SASS::TT_Default::__setstate__ );

    nb::class_<SASS::TT_NoDefault, SASS::TT_Default>(m, "TT_NoDefault").def(nb::init<>());

    nb::class_<SASS::TT_FuncArg>(m, "TT_FuncArg")
    .def(nb::init<SASS::TValue, bool, bool, int, bool, int, bool, int>(), nb::arg("arg_val"), nb::arg("has_star"), nb::arg("has_print"), nb::arg("bit_len"), nb::arg("has_default"), nb::arg("default_val"), nb::arg("has_max_val"), nb::arg("max_val"))
    .def_prop_ro("value", &SASS::TT_FuncArg::value)
    .def_prop_ro("bit_len", [&](const SASS::TT_FuncArg& self) { return SASS::TT_FuncArg::bit_len(self); })
    .def_prop_ro("has_default", [&](const SASS::TT_FuncArg& self) { return SASS::TT_FuncArg::has_default(self); })
    .def_prop_ro("default_val", [&](const SASS::TT_FuncArg& self) { return SASS::TT_FuncArg::default_val(self); })
    .def_prop_ro("has_max_val", [&](const SASS::TT_FuncArg& self) { return SASS::TT_FuncArg::has_max_val(self); })
    .def_prop_ro("max_val", [&](const SASS::TT_FuncArg& self) { return SASS::TT_FuncArg::max_val(self); })
    .def("set_max_val", &SASS::TT_FuncArg::set_max_val, nb::arg("max_val"))
    .def("__str__", &SASS::TT_FuncArg::__str__)
    .def("__getstate__", &SASS::TT_FuncArg::__getstate__ )
    .def("__setstate__", &SASS::TT_FuncArg::__setstate__ );

    nb::class_<SASS::TT_Func>(m, "TT_Func")
    .def(nb::init<std::string, SASS::TStrOptionsSet, SASS::TT_FuncArg, bool, bool, SASS::TT_Alias>(), nb::arg("func_name"), nb::arg("options"), nb::arg("arg_default"), nb::arg("star"), nb::arg("is_address"), nb::arg("alias"))
    .def_prop_ro("alias", &SASS::TT_Func::alias)
    .def_prop_ro("value", &SASS::TT_Func::value)
    .def_prop_ro("options", &SASS::TT_Func::options)
    .def_prop_ro("arg_default", &SASS::TT_Func::arg_default)
    .def_prop_ro("star", &SASS::TT_Func::star)
    .def_prop_ro("is_address", &SASS::TT_Func::is_address)
    .def_prop_ro("func", &SASS::TT_Func::func)
    .def("get_domain", &SASS::TT_Func::get_domain, nb::arg("to_limit"), nb::arg("filter_invalid"))
    .def("sass_from_bits", &SASS::TT_Func::sass_from_bits, nb::arg("bits"))
    .def("__str__", &SASS::TT_Func::__str__)
    .def("__getstate__", &SASS::TT_Func::__getstate__ )
    .def("__setstate__", &SASS::TT_Func::__setstate__ );

    nb::class_<SASS::TT_Reg>(m, "TT_Reg")
    .def(nb::init<std::string, SASS::TT_Default, SASS::TOptions, SASS::TT_Alias>(), nb::arg("value"), nb::arg("default_val"), nb::arg("options"), nb::arg("alias"))
    .def_prop_ro("alias", &SASS::TT_Reg::alias)
    .def_prop_ro("value", &SASS::TT_Reg::value)
    .def_prop_ro("default", &SASS::TT_Reg::default_)
    .def_prop_ro("options", &SASS::TT_Reg::options)
    .def_prop_ro("min_bit_len", &SASS::TT_Reg::min_bit_len)
    .def("get_domain", &SASS::TT_Reg::get_domain, nb::arg("to_limit"), nb::arg("filter_invalid"))
    .def("sass_from_bits", &SASS::TT_Reg::sass_from_bits, nb::arg("bits"))
    .def("__str__", &SASS::TT_Reg::__str__)
    .def("__getstate__", &SASS::TT_Reg::__getstate__ )
    .def("__setstate__", &SASS::TT_Reg::__setstate__ );

    nb::class_<SASS::TT_ICode>(m, "TT_ICode")
    .def(nb::init<std::string, IntVector, IntVector>(), nb::arg("bin_str"), nb::arg("bin_ind"), nb::arg("bin_tup"))
    .def_prop_ro("value", &SASS::TT_ICode::value)
    .def_prop_ro("bin_str", &SASS::TT_ICode::bin_str)
    .def_prop_ro("bin_ind", &SASS::TT_ICode::bin_ind)
    .def_prop_ro("bin_tup", &SASS::TT_ICode::bin_tup)
    .def("get_opcode_bin", &SASS::TT_ICode::get_opcode_bin)
    .def("__str__", &SASS::TT_ICode::__str__)
    .def("__getstate__", &SASS::TT_ICode::__getstate__ )
    .def("__setstate__", &SASS::TT_ICode::__setstate__ );

    nb::class_<SASS::TT_Pred>(m, "TT_Pred")
    .def(nb::init<SASS::TT_Alias, SASS::TT_Reg, SASS::TT_OpAtNot>(), nb::arg("alias"), nb::arg("reg"), nb::arg("op"))
    .def_prop_ro("value", &SASS::TT_Pred::value)
    .def_prop_ro("alias", &SASS::TT_Pred::alias)
    .def_prop_ro("reg", &SASS::TT_Pred::reg)
    .def_prop_ro("op", &SASS::TT_Pred::op)
    .def_prop_ro("is_none", &SASS::TT_Pred::is_none)
    .def_prop_ro("eval", &SASS::TT_Pred::eval)
    .def("get_enc_alias", &SASS::TT_Pred::get_enc_alias)
    .def("__str__", &SASS::TT_Pred::__str__)
    .def("__getstate__", &SASS::TT_Pred::__getstate__ )
    .def("__setstate__", &SASS::TT_Pred::__setstate__ );

    nb::class_<SASS::TT_NoPred, SASS::TT_Pred>(m, "TT_NoPred").def(nb::init<>());

    nb::class_<SASS::TT_Ext>(m, "TT_Ext")
    .def(nb::init<SASS::TT_Alias, SASS::TT_Reg, bool>(), nb::arg("alias"), nb::arg("reg"), nb::arg("is_at_alias"))
    .def_prop_ro("value", &SASS::TT_Ext::value)
    .def_prop_ro("alias", &SASS::TT_Ext::alias)
    .def_prop_ro("reg", &SASS::TT_Ext::reg)
    .def_prop_ro("is_at_alias", &SASS::TT_Ext::is_at_alias)
    .def_prop_ro("eval", &SASS::TT_Ext::eval)
    .def("get_enc_alias", &SASS::TT_Ext::get_enc_alias)
    .def("__str__", &SASS::TT_Ext::__str__)
    .def("__getstate__", &SASS::TT_Ext::__getstate__ )
    .def("__setstate__", &SASS::TT_Ext::__setstate__ );

    nb::class_<SASS::TT_Opcode>(m, "TT_Opcode")
    .def(nb::init<SASS::TT_Alias, SASS::TT_ICode, SASS::TExtVec>(), nb::arg("alias"), nb::arg("icode"), nb::arg("extensions"))
    .def_prop_ro("value", &SASS::TT_Opcode::value)
    .def_prop_ro("alias", &SASS::TT_Opcode::alias)
    .def_prop_ro("icode", &SASS::TT_Opcode::icode)
    .def_prop_ro("eval", &SASS::TT_Opcode::eval)
    .def_prop_ro("extensions", &SASS::TT_Opcode::extensions)
    .def("get_enc_alias", &SASS::TT_Opcode::get_enc_alias)
    .def("__str__", &SASS::TT_Opcode::__str__)
    .def("__getstate__", &SASS::TT_Opcode::__getstate__ )
    .def("__setstate__", &SASS::TT_Opcode::__setstate__ );

    nb::class_<SASS::TT_None>(m, "TT_None").def(nb::init<>());

    nb::class_<SASS::TT_Param>(m, "TT_Param")
    .def(nb::init<SASS::TT_Alias, SASS::TOpsVec, SASS::TT_Reg, SASS::TExtVec, bool, bool>(), nb::arg("alias"), nb::arg("ops"), nb::arg("value"), nb::arg("extensions"), nb::arg("is_at_alias"), nb::arg("has_attr_star"))
    .def(nb::init<SASS::TT_Alias, SASS::TOpsVec, SASS::TT_Func, SASS::TExtVec, bool, bool>(), nb::arg("alias"), nb::arg("ops"), nb::arg("value"), nb::arg("extensions"), nb::arg("is_at_alias"), nb::arg("has_attr_star"))
    .def_prop_ro("value", &SASS::TT_Param::value)
    .def_prop_ro("alias", &SASS::TT_Param::alias)
    .def_prop_ro("ops", &SASS::TT_Param::ops)
    .def_prop_ro("extensions", &SASS::TT_Param::extensions)
    .def_prop_ro("is_at_alias", &SASS::TT_Param::is_at_alias)
    .def_prop_ro("has_attr_star", &SASS::TT_Param::has_attr_star)
    .def_prop_ro("eval", &SASS::TT_Param::eval)
    .def_prop_ro("attr", [&](SASS::TT_Param& self) { return SASS::TListVec{}; })
    .def("get_enc_alias", &SASS::TT_Param::get_enc_alias)
    .def("__str__", &SASS::TT_Param::__str__)
    .def("__getstate__", &SASS::TT_Param::__getstate__ )
    .def("__setstate__", &SASS::TT_Param::__setstate__ );

    nb::class_<SASS::TT_List>(m, "TT_List")
    .def(nb::init<SASS::TParamVec, SASS::TExtVec>(), nb::arg("params"), nb::arg("extensions"))
    .def_prop_ro("value", &SASS::TT_List::value)
    .def_prop_ro("eval", &SASS::TT_List::eval)
    .def_prop_ro("params", &SASS::TT_List::params)
    .def_prop_ro("extensions", &SASS::TT_List::extensions)
    .def("get_enc_alias", &SASS::TT_List::get_enc_alias)
    .def("__str__", &SASS::TT_List::__str__)
    .def("__getstate__", &SASS::TT_List::__getstate__ )
    .def("__setstate__", &SASS::TT_List::__setstate__ );

    nb::class_<SASS::TT_AttrParam, SASS::TT_Param>(m, "TT_AttrParam")
    .def(nb::init<SASS::TT_Alias, SASS::TOpsVec, SASS::TT_Reg, SASS::TListVec, SASS::TExtVec, bool, bool>(), nb::arg("alias"), nb::arg("ops"), nb::arg("value"), nb::arg("attr"), nb::arg("extensions"), nb::arg("is_at_alias"), nb::arg("has_attr_star"))
    .def(nb::init<SASS::TT_Alias, SASS::TOpsVec, SASS::TT_Func, SASS::TListVec, SASS::TExtVec, bool, bool>(), nb::arg("alias"), nb::arg("ops"), nb::arg("value"), nb::arg("attr"), nb::arg("extensions"), nb::arg("is_at_alias"), nb::arg("has_attr_star"))
    .def_prop_ro("attr", &SASS::TT_AttrParam::attr)
    .def_prop_ro("eval", &SASS::TT_AttrParam::eval);

    nb::class_<SASS::TT_Cash>(m, "TT_Cash")
    .def(nb::init<SASS::TCashComponentsVec, bool>(), nb::arg("cash_vals"), nb::arg("added_later")=false)
    .def("__str__", &SASS::TT_Cash::__str__)
    .def_prop_ro("values", &SASS::TT_Cash::values)
    .def_prop_ro("cash_components", &SASS::TT_Cash::cash_components)
    .def_prop_ro("added_later", &SASS::TT_Cash::added_later)
    .def_prop_ro("eval", &SASS::TT_Cash::eval)
    .def("get_enc_alias", &SASS::TT_Cash::get_enc_alias)
    .def("__getstate__", &SASS::TT_Cash::__getstate__ )
    .def("__setstate__", &SASS::TT_Cash::__setstate__ );

    nb::class_<SASS::TT_Instruction>(m, "TT_Instruction")
    .def(nb::init<std::string, SASS::TT_Pred, SASS::TT_Opcode, SASS::TOperandVec, SASS::TCashVec>(), nb::arg("class_name"), nb::arg("pred"), nb::arg("opcode"), nb::arg("regs"), nb::arg("cashs"))
    .def_prop_ro("class_name", &SASS::TT_Instruction::class_name)
    .def_prop_ro("pred", &SASS::TT_Instruction::pred)
    .def_prop_ro("opcode", &SASS::TT_Instruction::opcode)
    .def_prop_ro("regs", &SASS::TT_Instruction::regs)
    .def_prop_ro("cashs", &SASS::TT_Instruction::cashs)
    .def_prop_ro("eval", &SASS::TT_Instruction::eval)
    .def("__str__", &SASS::TT_Instruction::__str__)
    .def("__getstate__", &SASS::TT_Cash::__getstate__ )
    .def("__setstate__", &SASS::TT_Cash::__setstate__ );
}
