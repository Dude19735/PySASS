#include <vector>
#include <set>
#include <map>
#include "../src/SASS_Bits.hpp"
#include "../src/CPP_Faster.hpp"

void test_cart(){
    // std::vector<std::set<SASS::SASS_Bits>> in = {
    //     { SASS::SASS_Bits::from_int(0,5,0), SASS::SASS_Bits::from_int(1,5,0), SASS::SASS_Bits::from_int(2,5,0) },
    //     { SASS::SASS_Bits::from_int(3,5,0), SASS::SASS_Bits::from_int(4,5,0) },
    //     { SASS::SASS_Bits::from_int(5,5,0), SASS::SASS_Bits::from_int(6,5,0), SASS::SASS_Bits::from_int(7,5,0) },
    // };

    // std::cout << "======================================" << std::endl;
    // auto prod = ACC::CPP_Faster::cart_product(in);
    // for(const auto& s : prod){
    //     std::cout << "(";
    //     for(const auto& m : s){
    //         std::cout << SASS::SASS_Bits::__int__(m) << ',';
    //     }
    //     std::cout << ")" << std::endl;
    // }
}

int main(int argc, char** argv) {

    std::map<std::vector<int>, int> test_map = {
        {{1,2,3}, 0},
        {{1,3,4}, 1},
        {{1,4,5}, 2},
    };

    std::cout << static_cast<bool>(test_map.contains({1,2,3})) << std::endl;
    std::cout << static_cast<bool>(test_map.contains({1,2,4})) << std::endl;
    std::cout << static_cast<bool>(test_map.contains({1,3,4})) << std::endl;

    std::vector<int> x;
    x.reserve(5);
    for(int i=0; i<5; ++i) x.emplace_back(i);
    for(const auto& v : x) std::cout << v << std::endl;

    return 0;
}