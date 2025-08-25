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

namespace SASS {
    using TSize = uint16_t;
    using TData = uint8_t;
    using TVec = std::vector<TData>;
    using TSpan = std::span<const TData>;
    using SSpan = std::span<const TSize>;
    using TVecPair = std::pair<TSize, TVec>;

    // Trait to detect std::vector
    template<typename T>
    struct is_std_vector : std::false_type {};
    template<typename... Args>
    struct is_std_vector<std::vector<Args...>> : std::true_type {};
    template<typename T>
    inline constexpr bool is_std_vector_v = is_std_vector<T>::value;
    template<typename T>
    concept IsVector = is_std_vector_v<T>;

    // Primary template: defaults to false
    template <typename T>
    struct is_unordered_map : std::false_type {};
    // Specialization when T is std::unordered_map<K, V, ...>
    template <typename Key, typename T, typename Hash, typename Pred, typename Alloc>
    struct is_unordered_map<std::unordered_map<Key, T, Hash, Pred, Alloc>> : std::true_type {};
    template <typename T>
    inline constexpr bool is_unordered_map_v = is_unordered_map<T>::value;
    template<typename T>
    concept UnorderedMap = is_unordered_map_v<T>;

    // Primary template: defaults to false
    template <typename T>
    struct is_std_set : std::false_type {};
    // Partial specialization for std::set
    template <typename Key, typename Compare, typename Alloc>
    struct is_std_set<std::set<Key, Compare, Alloc>> : std::true_type {};
    // Helper variable template
    template <typename T>
    inline constexpr bool is_std_set_v = is_std_set<T>::value;
    // C++20 Concept version
    template <typename T>
    concept StdSet = is_std_set_v<T>;

    template <typename T>
    concept IsInteger = std::integral<T>;

    template <typename T>
    concept IsString = std::same_as<T, std::string>;

    // // Primary template: defaults to false
    // template <typename T>
    // struct is_int_set : std::false_type {};
    // // Partial specialization for std::set
    // template <int, typename Compare, typename Alloc>
    // struct is_int_set<std::set<int, Compare, Alloc>> : std::true_type {};
    // // Helper variable template
    // template <typename T>
    // inline constexpr bool is_int_set_v = is_int_set<T>::value;
    // // C++20 Concept version
    // template <typename T>
    // concept IntSet = is_int_set_v<T>;

    // // Primary template: defaults to false
    // template <typename T>
    // struct is_str_set : std::false_type {};
    // // Partial specialization for std::set
    // template <std::string, typename Compare, typename Alloc>
    // struct is_str_set<std::set<std::string, Compare, Alloc>> : std::true_type {};
    // // Helper variable template
    // template <typename T>
    // inline constexpr bool is_str_set = is_str_set<T>::value;
    // // C++20 Concept version
    // template <typename T>
    // concept StrSet = is_str_set<T>;

    template<typename T>
    struct is_variant : std::false_type {};
    template<typename... Ts>
    struct is_variant<std::variant<Ts...>> : std::true_type {};
    template<typename T>
    concept IsVariant = is_variant<T>::value;

    // Primary template: defaults to false
    template <typename T>
    struct is_tuple : std::false_type {};
    // Specialization for std::tuple instantiations: true
    template <typename... Args>
    struct is_tuple<std::tuple<Args...>> : std::true_type {};
    // Convenience variable template
    template <typename T>
    constexpr bool is_tuple_v = is_tuple<T>::value;
    template<typename T>
    concept IsTuple = is_tuple_v<T>;

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

        static TVecPair to_bytes(const TOptions& val) {
            std::vector<uint8_t> res = size_to_vec(static_cast<TSize>(val.size()));
            for(const std::pair<std::string, std::set<int>> v : val) {
                TVec size = size_to_vec(static_cast<TSize>(v.first.size()));
                res.insert(res.end(), size.begin(), size.end());
                res.insert(res.end(), v.first.begin(), v.first.end());
                TVec size2 = size_to_vec(static_cast<TSize>(v.second.size()));
                res.insert(res.end(), size2.begin(), size2.end());
                std::vector<int> vals(v.second.begin(), v.second.end());
                TVec valsvec = intvec_to_vec(vals);
                res.insert(res.end(), valsvec.begin(), valsvec.end());
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
        template<typename ...TStateTuple>
        static TVec variant_to_vec(const std::variant<TStateTuple...>& state) {
            size_t index = state.index();
            TVec res = { static_cast<uint8_t>(index) };
            TVec data = std::visit([&](const auto& k) { return ToBytes::tuple_2_vector(k); }, state);
            res.insert(res.end(), data.begin(), data.end());
            return res;
        }

        template<typename ..._TArgs>
        static TVec tuple_2_vector(const std::tuple<_TArgs...>& tuple)
        {
            TVecPair res = to_bytes(tuple);
            return res.second;
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

        template<typename T=TOptions> requires (UnorderedMap<T>)
        static TOptions to_data(const size_t index, const SSpan& sspan, const TSpan& tspan) {
            TOptions res;
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
                std::set<int> iset;
                for(TSize i=0; i<vals; ++i){
                    iset.insert(*reinterpret_cast<const int*>(&*iter));
                    iter += sizeof(int);
                }
                res.insert({strval, iset});
                counter++;
            }
            if(counter != count) throw std::runtime_error(std::vformat("Invalid depacking of TOptions: [{}] entries recovered, but should be [{}]", std::make_format_args(counter, count)));
            return res;
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
                if (I == variant_index) return ToData::unpack_args<std::variant_alternative_t<I, Var>>::vector_2_tuple(bytes);
                else return unpack_variant<I + 1, Var>(variant_index, bytes);
            }
            throw std::runtime_error("This point should never be reached: faulty recursion!");
            return ToData::unpack_args<std::variant_alternative_t<0, Var>>::vector_2_tuple(bytes);
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
        template <typename Tuple>
        struct unpack_args;
        template<typename ..._TArgs>
        struct unpack_args<std::tuple<_TArgs...>> {
            template<typename Ts, Ts... I>
            static T args_to_obj(const std::tuple<_TArgs...>& args, const std::integer_sequence<Ts, I...>& int_seq){
                return T(std::get<I>(args)...);
            }
        };

        template <std::size_t I = 0>
        static constexpr T unpack_state_variant(std::size_t variant_index, const TState& state) {
            if constexpr (I >= std::variant_size_v<TState>) { 
                throw std::out_of_range("Invalid variant index: out of bounds");
            } else {
                if (I == variant_index) return unpack_args<std::variant_alternative_t<I, TState>>::args_to_obj(std::get<I>(state), std::make_index_sequence<tt_state_size>{});
                else return unpack_state_variant<I + 1>(variant_index, state);
            }
            throw std::runtime_error("This point should never be reached: faulty recursion!");
            return unpack_args<std::variant_alternative_t<0, TState>>::args_to_obj(std::get<0>(state), std::make_index_sequence<tt_state_size>{});
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
        
        template<typename Ts, Ts... I>
        static void unpack(T& self, const BitVector& state, const std::integer_sequence<Ts, I...>& int_seq) {
            new(&self) T(std::visit([&](const auto& obj) { 
                return T( std::get<I>(obj)... ); },  Pickle::loads<TState>(state))
            );
        }

        static T muh(const TState& state){ 
            return unpack_state_variant<0>(static_cast<size_t>(state.index()), state);
        }

        static const BitVector __getstate__(const T& self) { return Pickle::dumps(self.get_state()); }
        static void __setstate__(T& self, const BitVector& state) { T::unpack(self, state, std::make_index_sequence<tt_state_size>{}); }
    };
}