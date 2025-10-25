#pragma once

#include <variant>
#include <string>
#include <sstream>
#include <format>
#include <set>
#include <unordered_map>
#include <map>
#include <bitset>
#include <variant>
#include <type_traits>
#include <utility>
#include <array>
#include <vector>
#include <cstring>
#include <cinttypes>

#include "Utils.hpp"
#include "TypeTraits.hpp"

namespace SASS {
    using TSize = uint16_t;
    using TData = uint8_t;
    using TVec = std::vector<TData>;
    using TSpan = std::span<const TData>;
    using SSpan = std::span<const TSize>;
    using TVecPair = std::pair<TSize, TVec>;

    class ToBytes {
        static TVec size_to_vec(TSize size) {
            TVec res(sizeof(TSize));
            memcpy(res.data(), &size, sizeof(TSize));
            return res;
        }

        static TVec intvec_to_vec(const std::vector<int>& vals) {
            size_t s = static_cast<size_t>(vals.size() * sizeof(int));
            TVec res(s);
            memcpy(res.data(), vals.data(), s);
            return res;
        }

        static TVecPair to_bytes(const IntVector& val) {
            std::vector<uint8_t> res;
            std::vector<std::vector<uint8_t>> vec;
            vec.reserve(val.size());
            std::transform(val.begin(), val.end(), std::back_inserter(vec), [&](const int s) { 
                TVecPair v = to_bytes(s);
                return std::vector<uint8_t>(v.second.begin(), v.second.end());
            });
            for(const auto& v : vec) res.insert(res.end(), v.begin(), v.end());
            return { static_cast<TSize>(res.size()), res };
        }

        static TVecPair to_bytes(const std::string& val) {
            return { static_cast<TSize>(val.size()),  TVec(val.begin(), val.end())};
        }

        template<typename TVal>
        static TVecPair to_bytes(const std::unordered_map<std::string, TVal>& val){
            std::vector<uint8_t> res = size_to_vec(static_cast<TSize>(val.size()));
            for(const std::pair<std::string, TVal> v : val) {
                TVec size = size_to_vec(static_cast<TSize>(v.first.size()));
                res.insert(res.end(), size.begin(), size.end());
                res.insert(res.end(), v.first.begin(), v.first.end());
                
                TVecPair val_vec = to_bytes(v.second);
                TVec size2 = size_to_vec(val_vec.first);
                res.insert(res.end(), size2.begin(), size2.end());
                res.insert(res.end(), val_vec.second.begin(), val_vec.second.end());
            }
            return { static_cast<TSize>(res.size()), res };
        }

        template<typename TVal>
        static TVecPair to_bytes(const std::unordered_map<TValue, TVal>& val){
            std::vector<uint8_t> res = size_to_vec(static_cast<TSize>(val.size()));
            for(const std::pair<TValue, TVal> v : val) {
                TVec key_vec = variant_to_vec(v.first);
                TVec size1 = size_to_vec(key_vec.size());
                res.insert(res.end(), size1.begin(), size1.end());
                res.insert(res.end(), key_vec.begin(), key_vec.end());
                
                TVecPair val_vec = to_bytes(v.second);
                TVec size2 = size_to_vec(val_vec.first);
                res.insert(res.end(), size2.begin(), size2.end());
                res.insert(res.end(), val_vec.second.begin(), val_vec.second.end());
            }
            return { static_cast<TSize>(res.size()), res };
        }

        static TVecPair to_bytes(const TOptionsSet& val) {
            std::vector<uint8_t> res = size_to_vec(static_cast<TSize>(val.size()));
            std::vector<std::vector<uint8_t>> vec;
            vec.reserve(val.size());
            std::transform(val.begin(), val.end(), std::back_inserter(vec), [&](const int s) { 
                TVecPair v = to_bytes(s);
                return std::vector<uint8_t>(v.second.begin(), v.second.end());
            });
            for(const auto& v : vec) res.insert(res.end(), v.begin(), v.end());
            return { static_cast<TSize>(res.size()), res };
        }

        static TVecPair to_bytes(const TStrOptionsSet& val) {
            std::vector<uint8_t> res = size_to_vec(static_cast<TSize>(val.size()));
            std::vector<std::vector<uint8_t>> vec;
            vec.reserve(val.size());
            std::transform(val.begin(), val.end(), std::back_inserter(vec), [&](const std::string& s) { 
                TVecPair v = to_bytes(s);
                std::vector<uint8_t> r = size_to_vec(v.first);
                r.insert(r.end(), v.second.begin(), v.second.end());
                return r;
            });
            for(const auto& v : vec) res.insert(res.end(), v.begin(), v.end());
            return { static_cast<TSize>(res.size()), res };
        }

        template<typename TNum>
        static std::enable_if_t<std::is_integral_v<TNum> || std::is_floating_point_v<TNum>, TVecPair> to_bytes(const TNum& val) {
            TVec res(sizeof(TNum));
            memcpy(res.data(), &val, sizeof(TNum));
            return { static_cast<TSize>(sizeof(TNum)), res};
        }

        template<typename SubType>
        static TVecPair to_bytes(const std::vector<SubType>& tvec) {
            TVec res = size_to_vec(static_cast<TSize>(tvec.size()));
            for(const SubType& tt : tvec){
                TVecPair vv = to_bytes(tt);
                TVec size_vec = size_to_vec(vv.first);
                res.insert(res.end(), size_vec.begin(), size_vec.end());
                res.insert(res.end(), vv.second.begin(), vv.second.end());
            }
            return { static_cast<TSize>(res.size()),  res};
        }

        template<typename ..._TArgs>
        static TVecPair to_bytes(const std::tuple<_TArgs...>& tuple)
        {
            typedef typename std::remove_reference<decltype(tuple)>::type tuple_type;

            constexpr auto ts = std::tuple_size<tuple_type>::value;
            std::vector<TVecPair> data = to_vector_helper<tuple_type>(tuple, std::make_index_sequence<ts>{});
            TVec res = size_to_vec(static_cast<TSize>(data.size()));
            
            // +1 for the initial count and another +1 for the end offset that also corresponds to the length
            TSize offset = 0;
            for(const TVecPair& p : data){
                TVec x = size_to_vec(offset);
                res.insert(res.end(), x.begin(), x.end());
                offset += p.first;
            }
            TVec x = size_to_vec(offset);
            res.insert(res.end(), x.begin(), x.end());
            for(const TVecPair& p : data){
                res.insert(res.end(), p.second.begin(), p.second.end());
            }
            res.shrink_to_fit();
            return { static_cast<TSize>(res.size()), res };
        }

        template<typename ..._TArgs>
        static TVecPair to_bytes(const std::variant<_TArgs...>& val) {
            TVec res = variant_to_vec(val);
            return { static_cast<TSize>(res.size()), res};
        }

        template<typename TElse>
        static std::enable_if_t<!(std::is_integral_v<TElse> || std::is_floating_point_v<TElse> || std::is_same_v<TElse, std::string>), TElse> to_bytes(const TElse& val) {
            static_assert(false && "Unsuported type for packing!");
            throw std::runtime_error("");
        }

        template<typename tuple_type, size_t ...index>
        static std::vector<TVecPair> to_vector_helper(const tuple_type &t, std::index_sequence<index...>)
        {
            return std::vector<TVecPair>{to_bytes(std::get<index>(t))...};
        }

    public:
        template<typename ..._TArgs>
        static TVec transform_2_vector(const std::tuple<_TArgs...>& tuple)
        {
            TVecPair res = to_bytes(tuple);
            return res.second;
        }

        template<typename TNum> requires(std::is_integral_v<TNum> || std::is_floating_point_v<TNum>)
        static TVec transform_2_vector(const TNum& nn)
        {
            TVecPair res = to_bytes(nn);
            return res.second;
        }

        static TVec transform_2_vector(const std::string& nn)
        {
            TVecPair res = to_bytes(nn);
            return res.second;
        }

        template<typename TVariant> requires (IsVariant<TVariant>)
        static TVec transform_2_vector(const TVariant& variant)
        {
            return variant_to_vec(variant);
        }

        template<typename ...TStateTuple>
        static TVec variant_to_vec(const std::variant<TStateTuple...>& state) {
            size_t index = state.index();
            TVec res = { static_cast<uint8_t>(index) };
            TVec data = std::visit([&](const auto& k) { return ToBytes::transform_2_vector(k); }, state);
            res.insert(res.end(), data.begin(), data.end());
            return res;
        }

        template<typename ..._TArgs>
        static TVec tuple_vec_to_vector(const std::vector<std::tuple<_TArgs...>>& tvec){
            TVecPair rr = to_bytes(tvec);
            return rr.second;
        }
    };

    class ToData {
        template<typename T=std::string>
        static std::enable_if_t<std::is_same_v<T, std::string>, std::string> to_data(const size_t index, const SSpan& sspan, const TSpan& tspan) {
            const size_t from = static_cast<const size_t>(sspan[index]);
            const size_t to = static_cast<const size_t>(sspan[index+1]);
            return std::string(tspan.begin() + from, tspan.begin() + to);
        }

        template<typename T>
        struct unpack_unordered_map {
            static T to_data_set(size_t count, const TSpan& tspan) {
                static_assert(false && "Unsupported std::set type: only std::string and int are suported at this time!");
                return {};
            }
        };
        template<typename TVal>
        struct unpack_unordered_map<std::unordered_map<std::string, TVal>> {
            static std::unordered_map<std::string, TVal> to_data_unordered_map(const size_t index, const SSpan& sspan, const TSpan& tspan){
                std::unordered_map<std::string, TVal> res;
                TSize from = sspan[index];
                TSize to = sspan[index+1];
                const TSpan range(tspan.begin()+from, tspan.begin()+to);
                const TSize count = *reinterpret_cast<const TSize*>(range.data());
                TSpan::const_iterator iter = range.begin() + sizeof(TSize);
                TSize counter = 0;
                while(iter != range.end()) {
                    const TSize strs = *reinterpret_cast<const TSize*>(&*iter);
                    iter += sizeof(TSize);
                    std::string strval = std::string(iter, iter+strs);
                    iter += strs;
                    const TSize vals = *reinterpret_cast<const TSize*>(&*iter);
                    iter += sizeof(TSize);
                    TVal ival = to_data<TVal>(0, std::vector<TSize>{0, vals}, TSpan(iter, iter + vals));
                    res.insert({strval, ival});
                    iter += vals;
                    counter++;
                }
                if(counter != count) throw std::runtime_error(std::vformat("Invalid depacking of TOptions: [{}] entries recovered, but should be [{}]", std::make_format_args(counter, count)));
                return res;
            }
        };
        template<typename TVal>
        struct unpack_unordered_map<std::unordered_map<TValue, TVal>> {
            static std::unordered_map<TValue, TVal> to_data_unordered_map(const size_t index, const SSpan& sspan, const TSpan& tspan){
                std::unordered_map<TValue, TVal> res;
                TSize from = sspan[index];
                TSize to = sspan[index+1];
                const TSpan range(tspan.begin()+from, tspan.begin()+to);
                const TSize count = *reinterpret_cast<const TSize*>(range.data());
                TSpan::const_iterator iter = range.begin() + sizeof(TSize);
                TSize counter = 0;
                while(iter != range.end()) {
                    const TSize tval_size = *reinterpret_cast<const TSize*>(&*iter);
                    iter += sizeof(TSize);
                    TValue tval = to_data<TValue>(0, std::vector<TSize>{0, tval_size}, TSpan(iter, iter+tval_size));
                    iter += tval_size;
                    const TSize vals = *reinterpret_cast<const TSize*>(&*iter);
                    iter += sizeof(TSize);
                    TVal ival = to_data<TVal>(0, std::vector<TSize>{0, vals}, TSpan(iter, iter + vals));
                    res.insert({tval, ival});
                    iter += vals;
                    counter++;
                }
                if(counter != count) throw std::runtime_error(std::vformat("Invalid depacking of TOptions: [{}] entries recovered, but should be [{}]", std::make_format_args(counter, count)));
                return res;
            }
        };

        template<typename T> requires (UnorderedMap<T>)
        static T to_data(const size_t index, const SSpan& sspan, const TSpan& tspan) {
            return unpack_unordered_map<T>::to_data_unordered_map(index, sspan, tspan);
        }

        template<typename T>
        struct unpack_set {
            static T to_data_set(size_t count, const TSpan& tspan) {
                static_assert(false && "Unsupported std::set type: only std::string and int are suported at this time!");
                return {};
            }
        };
        template<typename TArg> requires (IsString<TArg>)
        struct unpack_set<std::set<TArg>> {
            static TStrOptionsSet to_data_set(size_t count, const TSpan& tspan){
                TStrOptionsSet res;
                TSpan::const_iterator iter = tspan.begin();
                TSize counter = 0;
                while(iter != tspan.end()) {
                    const TSize size = *reinterpret_cast<const TSize*>(&*iter);
                    iter += sizeof(TSize);
                    std::string val = std::string(iter, iter + size);
                    res.insert(val);
                    iter += size;
                    counter++;
                }
                if(counter != count) throw std::runtime_error(std::vformat("Invalid depacking of TStrOptionsSet: [{}] entries recovered, but should be [{}]", std::make_format_args(counter, count)));
                return res;
            }
        };
        template<typename TArg> requires (IsInteger<TArg>)
        struct unpack_set<std::set<TArg>> {
            static TOptionsSet to_data_set(size_t count, const TSpan& tspan) {
                TOptionsSet res;
                TSpan::const_iterator iter = tspan.begin();
                TSize counter = 0;
                while(iter != tspan.end()) {
                    const int val = *reinterpret_cast<const int*>(&*iter);
                    res.insert(val);
                    iter += sizeof(int);
                    counter++;
                }
                if(counter != count) throw std::runtime_error(std::vformat("Invalid depacking of TOptionsSet: [{}] entries recovered, but should be [{}]", std::make_format_args(counter, count)));
                return res;
            }
        };

        template<typename T> requires (StdSet<T>)
        static T to_data(const size_t index, const SSpan& sspan, const TSpan& tspan) {
            T res;
            TSize from = sspan[index];
            TSize to = sspan[index+1];
            const TSpan range(tspan.begin()+from, tspan.begin()+to);
            const TSize count = *reinterpret_cast<const TSize*>(range.data());
            const TSpan range2(range.begin() + sizeof(TSize), range.end());

            res = unpack_set<T>::to_data_set(static_cast<size_t>(count), range2);
            return res;
        }

        template<typename TNum> requires (!IsVector<TNum>)
        static std::enable_if_t<std::is_integral_v<TNum> || std::is_floating_point_v<TNum>, TNum> to_data(const size_t index, const SSpan& sspan, const TSpan& tspan) {
            const size_t from = static_cast<const size_t>(sspan[index]);
            const TNum v = *reinterpret_cast<const TNum*>(tspan.data() + from);
            return v;
        }

        template<typename T> requires (IsVector<T>)
        static T to_data(const size_t index, const SSpan& sspan, const TSpan& tspan) {
            const size_t from = static_cast<const size_t>(sspan[index]);
            const size_t to = static_cast<const size_t>(sspan[index+1]);
            TSpan x(tspan.data() + from, to - from);
            T res = unpack_vector<T>::t_vector_2_tuple_vec(x);
            return res;
        }

        template<typename T> requires (IsVariant<T>)
        static T to_data(const size_t index, const SSpan& sspan, const TSpan& tspan) {
            const size_t from = static_cast<const size_t>(sspan[index]);
            const size_t to = static_cast<const size_t>(sspan[index+1]);
            TSpan x(tspan.data() + from, to - from);
            return unpack_variant<0, T>(static_cast<size_t>(x[0]), TSpan(x.begin()+1, x.end()));
        }

        template<typename ..._TArgs, size_t ...index>
        static std::tuple<_TArgs...> to_data_helper(const SSpan& sizes, const TSpan& data, std::index_sequence<index...>)
        {
            return std::make_tuple<_TArgs...>(to_data<_TArgs>(index, sizes, data)...);
        }

    public:
        template <std::size_t I = 0, typename Var>
        static constexpr Var unpack_variant(std::size_t variant_index, const TSpan& bytes) {
            if constexpr (I >= std::variant_size_v<Var>) { 
                throw std::out_of_range("Invalid variant index: out of bounds");
            } else {
                if (I == variant_index) {
                    using TCurVar = std::variant_alternative_t<I, Var>;
                    if constexpr (IsVariant<TCurVar>){
                        return unpack_variant<0, TCurVar>(static_cast<size_t>(bytes[0]), TSpan(bytes.begin()+1, bytes.end()));
                    }
                    else if constexpr (IsTuple<TCurVar>) {
                        return ToData::unpack_args<TCurVar>::vector_2_tuple(bytes);
                    }
                    else {
                        const std::vector<TSize> ssize = { 0 };
                        return to_data<TCurVar>(0, ssize, bytes);
                    }
                }
                else return unpack_variant<I + 1, Var>(variant_index, bytes);
            }
            throw std::runtime_error("This point should never be reached: faulty recursion!");
            return Var();
        }

        template <typename Tuple>
        struct unpack_args;
        template<typename ..._TArgs>
        struct unpack_args<std::tuple<_TArgs...>> {
            static std::tuple<_TArgs...> vector_2_tuple(const TSpan& vec){
                constexpr TSize ts = static_cast<TSize>(std::tuple_size<std::tuple<_TArgs...>>::value);
                const TSize size = *reinterpret_cast<const TSize*>(vec.data());
                if(size != ts) throw std::runtime_error("Incompatible tuple and vector: non-matching element count!");

                const TSize len = *reinterpret_cast<const TSize*>(vec.data());
                const TSize* bb = reinterpret_cast<const TSize*>(vec.data());
                const TData* dd = reinterpret_cast<const TData*>(vec.data());
                SSpan sspan(bb + 1, bb + (len+2));
                TSpan tspan(dd + (len+2)*sizeof(TSize), vec.size() - (sspan.size()+1)*sizeof(TSize));
                
                if(sspan.back() != tspan.size()) throw std::runtime_error("Incompatible tuple and vector: non-matching length!");
                
                std::tuple<_TArgs...> tuple = to_data_helper<_TArgs...>(sspan, tspan, std::make_index_sequence<ts>{});
                return tuple;
            }
        };

        template<typename TType> requires (IsTuple<TType>)
        static std::vector<TType> vector_2_tuple_vec(const TSpan& vec){
            std::vector<TType> res;
            const TSize size = *reinterpret_cast<const TSize*>(vec.data());
            TSize counter = 0;
            TSpan::const_iterator iter = vec.begin() + sizeof(TSize);
            while(iter != vec.end()){
                const TSize c_size = *reinterpret_cast<const TSize*>(&*iter);
                TType tt = unpack_args<TType>::vector_2_tuple(TSpan(iter+sizeof(TSize), iter+sizeof(TSize)+c_size));
                res.push_back(tt);
                iter += (c_size+sizeof(TSize));
                counter++;
            }

            if(counter != size) throw std::runtime_error("Invalid translation of bytes to vector of tuples!");
            return res;
        }

        template<typename TNum> requires (IsInteger<TNum>)
        static std::vector<TNum> vector_2_tuple_vec(const TSpan& vec){
            std::vector<TNum> res;
            size_t size = sizeof(TNum);
            TSpan::const_iterator iter = vec.begin();
            while(iter != vec.end()){
                const TNum tt = *reinterpret_cast<const TNum*>(&*iter);
                res.push_back(tt);
                iter += size;
            }
            return res;
        }

        template<typename V> requires (IsVariant<V>)
        static std::vector<V> vector_2_tuple_vec(const TSpan& vec){
            std::vector<V> res;
            const TSize vec_size = *reinterpret_cast<const TSize*>(vec.data());
            TSpan::const_iterator iter = vec.begin() + sizeof(TSize);

            TSize counter = 0;
            while(iter != vec.end()){
                const TSize var_size = *reinterpret_cast<const TSize*>(&*iter);
                iter += sizeof(TSize);
                TSpan x = TSpan(iter, iter + var_size);
                res.push_back(unpack_variant<0, V>(static_cast<size_t>(x[0]), TSpan(x.begin()+1, x.end())));
                iter += var_size;
                counter++;
            }

            if(counter != vec_size) throw std::runtime_error("Invalid translation of bytes to vector of variants!");
            return res;
        }

        template <typename Vector>
        struct unpack_vector;
        template<typename TType>
        struct unpack_vector<std::vector<TType>> {
            static std::vector<TType> t_vector_2_tuple_vec(const TSpan& vec){
                return vector_2_tuple_vec<TType>(vec);
            }
        };
    };

    class Pickle {
        static constexpr size_t max_variants = 10;

    public:
        template<typename ...TStateTuple>
        static TVec dumps(const std::variant<TStateTuple...>& state) {
            return ToBytes::variant_to_vec(state);
        }

        template<typename Var>
        static Var loads(const TVec& bytes) {
            static_assert(std::variant_size_v<Var> < max_variants);
            return ToData::unpack_variant<0, Var>(static_cast<size_t>(bytes[0]), TSpan(bytes.begin()+1, bytes.end()));
        }
    };

    template<typename T, typename TState, size_t tt_state_size>
    class Picklable {
        template <typename TOut, typename Tuple>
        struct tunpack_args;
        template<typename TOut, typename ..._TArgs>
        struct tunpack_args<TOut, std::tuple<_TArgs...>> {
            template<typename Ts, Ts... I>
            static TOut targs_to_obj(const std::tuple<_TArgs...>& args, const std::integer_sequence<Ts, I...>& int_seq){
                return TOut(std::get<I>(args)...);
            }
        };

        template <typename TOut, typename TStateVariantIn, std::size_t I = 0>
        static constexpr TOut _tunpack_state_variant(std::size_t variant_index, const TStateVariantIn& state) {
            if constexpr (I >= std::variant_size_v<TStateVariantIn>) { 
                throw std::out_of_range("Invalid variant index: out of bounds");
            } else {
                if (I == variant_index) {
                    using TCurState = std::variant_alternative_t<I, TStateVariantIn>;
                    static_assert(IsTuple<TCurState>);
                    constexpr size_t state_size = std::tuple_size_v<TCurState>;
                    return tunpack_args<TOut, TCurState>::targs_to_obj(std::get<TCurState>(state), std::make_index_sequence<state_size>{});
                }
                else return _tunpack_state_variant<TOut, TStateVariantIn, I + 1>(variant_index, state);
            }
            throw std::runtime_error("This point should never be reached: faulty recursion!");
            using TCurState = std::variant_alternative_t<0, TStateVariantIn>;
            static_assert(IsTuple<TCurState>);
            constexpr size_t state_size = std::tuple_size_v<TCurState>;
            return tunpack_args<TOut, TCurState>::targs_to_obj(std::get<TCurState>(state), std::make_index_sequence<state_size>{});
        }

        template <typename TVInState, typename TVOutReal, std::size_t I = 0, size_t variant_type_size>  requires (IsVariant<TVInState> && IsVariant<TVOutReal>)
        static constexpr TVOutReal _tunpack_variant(std::size_t variant_index, const TVInState& state) {
            if constexpr (I >= variant_type_size) { 
                throw std::out_of_range("Invalid variant index: out of bounds");
            } else {
                if (I == variant_index) {
                    using TCurState = std::variant_alternative_t<I, TVInState>;
                    using TCurReal = std::variant_alternative_t<I, TVOutReal>;
                    TCurState var = std::get<TCurState>(state);

                    if constexpr (IsVariant<TCurState>){
                        if constexpr (IsVariant<TCurReal>) {
                            throw std::runtime_error("Invalid variant contents: the state is always an std::variant, but one entry in a state has to be transferable to a real type. The real type is not allowed to be an std::variant again!");
                        }
                        else {
                            return _tunpack_state_variant<TCurReal, TCurState, 0>(var.index(), var);
                        }
                    }
                    else {
                        if constexpr (!IsTuple<TCurState>) {
                            throw std::runtime_error("Invalid variant contents: if the state is not an std::variant, it must be an std::tuple!");
                        }
                        static_assert(!IsVariant<TCurReal>);
                        constexpr size_t state_size = std::tuple_size_v<TCurState>;
                        return tunpack_args<TCurReal, TCurState>::targs_to_obj(std::get<TCurState>(state), std::make_index_sequence<state_size>{});
                    }
                }
                else return _tunpack_variant<TVInState, TVOutReal, I + 1, variant_type_size>(variant_index, state);
            }
        }

        template <typename TVInReal, typename TVOutState, std::size_t I = 0, size_t variant_type_size>  requires (IsVariant<TVInReal> && IsVariant<TVOutState>)
        static constexpr TVOutState _tpack_variant(std::size_t variant_index, const TVInReal& real_obj) {
            if constexpr (I >= variant_type_size) { 
                throw std::out_of_range("Invalid variant index: out of bounds");
            } else {
                if (I == variant_index) {
                    using TCurState = std::variant_alternative_t<I, TVOutState>;
                    using TCurReal = std::variant_alternative_t<I, TVInReal>;
                    TCurReal var = std::get<TCurReal>(real_obj);

                    if constexpr (!(IsVariant<TCurState> && !IsVariant<TCurReal>)){
                        throw std::runtime_error("Invalid variant contents: the state is always an std::variant, but one entry in a state has to be transferable to a real type. The real type is not allowed to be an std::variant again!");
                    }
                    return var.get_state(); // _tunpack_state_variant<TCurReal, TCurState, std::variant_size_v<TCurState>>(var.index(), var);
                }
                else return _tpack_variant<TVInReal, TVOutState, I + 1, variant_type_size>(variant_index, real_obj);
            }
        }

    public:
        virtual const TState get_state(T* selfp=nullptr) const = 0;

        static std::vector<T> from_state_vec(const std::vector<TState>& state_vec) {
            std::vector<T> vec; 
            vec.reserve(state_vec.size());
            std::transform(state_vec.begin(), state_vec.end(), std::back_inserter(vec), [&](const TState& state) { return muh(state); });
            return vec;
        }
        
        static std::vector<TState> to_state_vec(const std::vector<T>& vec) {
            std::vector<TState> state_vec;
            state_vec.reserve(vec.size());
            std::transform(vec.begin(), vec.end(), std::back_inserter(state_vec), [&](const T& ext) { return ext.get_state(); });
            return state_vec;
        }
        
        template<typename TVReal, typename TVState, size_t variant_type_size> requires (IsVariant<TVReal> && IsVariant<TVState>)
        static std::vector<TVReal> muv_vec_h(const std::vector<TVState>& state_vec) {
            std::vector<TVReal> vec; 
            vec.reserve(state_vec.size());
            std::transform(state_vec.begin(), state_vec.end(), std::back_inserter(vec), 
                [&](const TVState& state) { 
                    return _tunpack_variant<TVState, TVReal, 0, variant_type_size>(static_cast<size_t>(state.index()), state); 
                }
            );
            return vec;
        }

        template<typename TVState, typename TVReal, size_t variant_type_size> requires (IsVariant<TVReal> && IsVariant<TVState>)
        static std::vector<TVState> mpv_vec_h(const std::vector<TVReal>& vec) {
            std::vector<TVState> state_vec; 
            state_vec.reserve(vec.size());
            std::transform(vec.begin(), vec.end(), std::back_inserter(state_vec), 
                [&](const TVReal& real_obj) { 
                    return _tpack_variant<TVReal, TVState, 0, variant_type_size>(static_cast<size_t>(real_obj.index()), real_obj); 
                }
            );
            return state_vec;
        }
        
        template<typename TKey, typename TVReal, typename TVState, size_t variant_type_size> requires (IsVariant<TVReal> && IsVariant<TVState>)
        static std::unordered_map<TKey, TVReal> muv_umap_h(const std::unordered_map<TKey, TVState>& state_map) {
            std::unordered_map<TKey, TVReal> map; 
            for(const std::pair<TKey, TVState>& state : state_map) {
                map.insert(std::pair<TKey, TVReal>{ state.first, _tunpack_variant<TVState, TVReal, 0, variant_type_size>(static_cast<size_t>(state.second.index()), state.second) }); 
            }
            return map;
        }

        template<typename TKey, typename TVState, typename TVReal, size_t variant_type_size> requires (IsVariant<TVReal> && IsVariant<TVState>)
        static std::unordered_map<TKey, TVState> mpv_umap_h(const std::unordered_map<TKey, TVReal>& map) {
            std::unordered_map<TKey, TVState> state_map; 
            for(const std::pair<TKey, TVReal>& real_obj : map) {
                state_map.insert(std::pair<TKey, TVState>{ real_obj.first, _tpack_variant<TVReal, TVState, 0, variant_type_size>(static_cast<size_t>(real_obj.second.index()), real_obj.second) }); 
            }
            return state_map;
        }

        template<typename Ts, Ts... I>
        static void unpack(T& self, const BitVector& state, const std::integer_sequence<Ts, I...>& int_seq) {
            new(&self) T(std::visit([&](const auto& obj) { 
                return T( std::get<I>(obj)... ); },  Pickle::loads<TState>(state))
            );
        }

        static T muh(const TState& state){ 
            return _tunpack_state_variant<T, TState, 0>(static_cast<size_t>(state.index()), state);
        }

        static const BitVector __getstate__(const T& self) { return Pickle::dumps(self.get_state()); }
        static void __setstate__(T& self, const BitVector& state) { T::unpack(self, state, std::make_index_sequence<tt_state_size>{}); }
    };
}