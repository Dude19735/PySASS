#include <variant>
#include <vector>
#include <unordered_map>
#include <set>
#include <cstring>
#include <string>

namespace SASS {
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
}