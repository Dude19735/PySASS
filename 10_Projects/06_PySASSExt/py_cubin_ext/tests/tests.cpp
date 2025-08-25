#include <bitset>
#include <type_traits>
#include <iostream>
#include <fstream>
#include <cmath>
#include <assert.h>
#include <iomanip>
#include <set>

template<typename T>
std::enable_if_t<std::is_integral_v<T>,std::string>
encode_binary(T i){
    return std::bitset<sizeof(T) * 8>(i).to_string();
}

int main(int argc, char** argv) {

    return 0;
}
